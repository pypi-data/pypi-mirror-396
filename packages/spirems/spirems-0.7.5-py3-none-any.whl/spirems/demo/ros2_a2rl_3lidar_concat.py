#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import rclpy
from rclpy.node import Node
from a2rl_bs_msgs.msg import ControllerStatus, ControllerDebug, Localization, EgoState, VectornavIns, FlyeagleEyePlannerReport
from eav24_bsu_msgs.msg import Wheels_Speed_01, HL_Msg_01, HL_Msg_02, HL_Msg_03, ICE_Status_01, ICE_Status_02, PSA_Status_01, Tyre_Surface_Temp_Front, Tyre_Surface_Temp_Rear, Brake_Disk_Temp 
from sensor_msgs.msg import PointCloud2, Image
from std_msgs.msg import Float32MultiArray, Float32, Bool
from cv_bridge import CvBridge
import time
import os
import yaml
import json
import threading
import numpy as np
import ros2_numpy
import cv2
from spirems import Publisher, Subscriber, def_msg, cvimg2sms
import psutil


"""
依赖项安装：
pip install spirems ros2-numpy psutil pynvjpeg
"""

DEFAULT_IP = "127.0.0.1"


# 从 rpy 计算旋转矩阵
def rpy_to_rotation_matrix(roll, pitch, yaw):
    R_x = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])
    R_y = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])
    R_z = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])
    return R_z @ R_y @ R_x

# 转换点云
def transform_points(points, rotation_matrix, translation_vector):
    # 点云坐标变换: P' = R * P + t
    return (rotation_matrix @ points.T).T + translation_vector

# 定义 Lidar 的参数
lidar_params = {
    "lidar_front": {"xyz": [2.199, 0.053, 0.744], "rpy": [-0.144, -1.550, -2.993]},
    "lidar_left": {"xyz": [1.691, 0.2969, 0.80634], "rpy": [-0.420, -1.553, -0.622]},
    "lidar_right": {"xyz": [1.691, -0.1969, 0.755093], "rpy": [0.625635, -1.5428, 0.424122]}
}


t_front = np.array(lidar_params["lidar_front"]["xyz"])
rpy_front = lidar_params["lidar_front"]["rpy"]
R_front = rpy_to_rotation_matrix(*rpy_front)

t_left = np.array(lidar_params["lidar_left"]["xyz"])
rpy_left = lidar_params["lidar_left"]["rpy"]
R_left = rpy_to_rotation_matrix(*rpy_left)

t_right = np.array(lidar_params["lidar_right"]["xyz"])
rpy_right = lidar_params["lidar_right"]["rpy"]
R_right = rpy_to_rotation_matrix(*rpy_right)


def cpu_monit(sms_msg):
    cpu_cnt = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=0.1)
    sms_msg['cpu'] = cpu_percent
    # cpu_freq = psutil.cpu_freq(percpu=False)

    virtual_memory = psutil.virtual_memory()
    sms_msg['mem'] = virtual_memory.used / 1024 / 1024 / 1024

    disk_usage = psutil.disk_usage('/')
    sms_msg['disk'] = disk_usage.used / 1024 / 1024 / 1024 / 1024

    sensors_temperatures = psutil.sensors_temperatures()
    if 'coretemp' in sensors_temperatures:
        sms_msg['cpu_temp'] = sensors_temperatures['coretemp'][0].current
    elif 'k10temp' in sensors_temperatures:
        sms_msg['cpu_temp'] = sensors_temperatures['k10temp'][0].current

    return sms_msg


# ==============================================================================
#                                                                   SCALE_TO_255
# ==============================================================================
def scale_to_255(a, min, max, dtype=np.uint8):
    """ Scales an array of values from specified min, max range to 0-255
        Optionally specify the data type of the output (default is uint8)
    """
    return (((a - min) / float(max - min)) * 255).astype(dtype)


# ==============================================================================
#                                                         POINT_CLOUD_2_BIRDSEYE
# ==============================================================================
def point_cloud_2_birdseye(points,
                           res=0.2,
                           side_range=(-100., 100.),  # left-most to right-most
                           fwd_range=(-100., 100.), # back-most to forward-most
                           height_range=(-2., 2.),  # bottom-most to upper-most
                           ):
    """ Creates an 2D birds eye view representation of the point cloud data.

    Args:
        points:     (numpy array)
                    N rows of points data
                    Each point should be specified by at least 3 elements x,y,z
        res:        (float)
                    Desired resolution in metres to use. Each output pixel will
                    represent an square region res x res in size.
        side_range: (tuple of two floats)
                    (-left, right) in metres
                    left and right limits of rectangle to look at.
        fwd_range:  (tuple of two floats)
                    (-behind, front) in metres
                    back and front limits of rectangle to look at.
        height_range: (tuple of two floats)
                    (min, max) heights (in metres) relative to the origin.
                    All height values will be clipped to this min and max value,
                    such that anything below min will be truncated to min, and
                    the same for values above max.
    Returns:
        2D numpy array representing an image of the birds eye view.
    """
    # EXTRACT THE POINTS FOR EACH AXIS
    x_points = points[:, 0]
    y_points = points[:, 1]
    z_points = points[:, 2]

    # FILTER - To return only indices of points within desired cube
    # Three filters for: Front-to-back, side-to-side, and height ranges
    # Note left side is positive y axis in LIDAR coordinates
    f_filt = np.logical_and((x_points > fwd_range[0]), (x_points < fwd_range[1]))
    s_filt = np.logical_and((y_points > -side_range[1]), (y_points < -side_range[0]))
    filter = np.logical_and(f_filt, s_filt)
    indices = np.argwhere(filter).flatten()

    # KEEPERS
    x_points = x_points[indices]
    y_points = y_points[indices]
    z_points = z_points[indices]

    # CONVERT TO PIXEL POSITION VALUES - Based on resolution
    x_img = (-y_points / res).astype(np.int32)  # x axis is -y in LIDAR
    y_img = (-x_points / res).astype(np.int32)  # y axis is -x in LIDAR

    # SHIFT PIXELS TO HAVE MINIMUM BE (0,0)
    # floor & ceil used to prevent anything being rounded to below 0 after shift
    x_img -= int(np.floor(side_range[0] / res))
    y_img += int(np.ceil(fwd_range[1] / res))

    # CLIP HEIGHT VALUES - to between min and max heights
    pixel_values = np.clip(a=z_points,
                           a_min=height_range[0],
                           a_max=height_range[1])

    # RESCALE THE HEIGHT VALUES - to be between the range 0-255
    pixel_values = scale_to_255(pixel_values,
                                min=height_range[0],
                                max=height_range[1])

    # INITIALIZE EMPTY ARRAY - of the dimensions we want
    x_max = 1 + int((side_range[1] - side_range[0]) / res)
    y_max = 1 + int((fwd_range[1] - fwd_range[0]) / res)
    # im = np.zeros([y_max, x_max, 3], dtype=np.uint8)
    im = np.zeros([y_max, x_max], dtype=np.uint8)

    # FILL PIXEL VALUES IN IMAGE ARRAY
    # im[y_img, x_img, 1] = pixel_values
    # im[y_img, x_img, 2] = pixel_values
    im[y_img, x_img] = pixel_values

    return im


class A2RL3LidarConcatNode(Node, threading.Thread):
    def __init__(self):
        Node.__init__(self, 'A2RL3LidarConcatNode')
        threading.Thread.__init__(self)

        self.lidar_front_lock = threading.Lock()
        self.lidar_front_list = []
        self.lidar_front_time = 0
        self.lidar_left_lock = threading.Lock()
        self.lidar_left_list = []
        self.lidar_left_time = 0
        self.lidar_right_lock = threading.Lock()
        self.lidar_right_list = []
        self.lidar_right_time = 0

        self.sensor_lidar_front_sub = self.create_subscription(
            PointCloud2,
            "/flyeagle/lidar_front/points",
            self.sensor_lidar_front_callback,
            10
        )
        self.sensor_lidar_left_sub = self.create_subscription(
            PointCloud2,
            "/flyeagle/lidar_left/points",
            self.sensor_lidar_left_callback,
            10
        )
        self.sensor_lidar_right_sub = self.create_subscription(
            PointCloud2,
            "/flyeagle/lidar_right/points",
            self.sensor_lidar_right_callback,
            10
        )

        self.sms_lidar_pub = Publisher("/flyeagle/lidar_map", "sensor_msgs::CompressedImage", ip=DEFAULT_IP)
        self.bridge = CvBridge()
        self.start()
    
    def sensor_lidar_front_callback(self, msg):
        with self.lidar_front_lock:
            self.lidar_front_list.append(msg)
            ros_time = msg.header.stamp
            total_nanoseconds = ros_time.sec * 1e9 + ros_time.nanosec
            self.lidar_front_time = int(total_nanoseconds / 1e6) % 86400000
    
    def sensor_lidar_left_callback(self, msg):
        with self.lidar_left_lock:
            self.lidar_left_list.append(msg)
            ros_time = msg.header.stamp
            total_nanoseconds = ros_time.sec * 1e9 + ros_time.nanosec
            self.lidar_left_time = int(total_nanoseconds / 1e6) % 86400000
    
    def sensor_lidar_right_callback(self, msg):
        with self.lidar_right_lock:
            self.lidar_right_list.append(msg)
            ros_time = msg.header.stamp
            total_nanoseconds = ros_time.sec * 1e9 + ros_time.nanosec
            self.lidar_right_time = int(total_nanoseconds / 1e6) % 86400000

    def run(self):
        lidar1_on = False
        lidar2_on = False
        lidar3_on = False
        pcd_front_t1 = 0
        pcd_left_t1 = 0
        pcd_right_t1 = 0
        while True:
            t1 = time.time()
            with self.lidar_front_lock:
                if self.lidar_front_time != 0 and self.lidar_front_time != pcd_front_t1:
                    pcd_front_t1 = self.lidar_front_time
                    msg = self.lidar_front_list.pop()
                    self.lidar_front_list.clear()
                    if pcd_front_t1 > 0 and pcd_left_t1 > 0 and pcd_right_t1 > 0:
                        if pcd_front_t1 - pcd_left_t1 > -10 and pcd_front_t1 - pcd_right_t1 > -10:
                            cloud_arr = np.frombuffer(msg.data, np.float32).reshape(-1, 6)
                            pcd_front = cloud_arr[:, [1,2,3]]  # ros2_numpy.numpify(msg)['xyz']
                            lidar1_on = True
            with self.lidar_left_lock:
                if self.lidar_left_time != 0 and self.lidar_left_time != pcd_left_t1:
                    pcd_left_t1 = self.lidar_left_time
                    msg = self.lidar_left_list.pop()
                    self.lidar_left_list.clear()
                    if pcd_front_t1 > 0 and pcd_left_t1 > 0 and pcd_right_t1 > 0:
                        if pcd_left_t1 - pcd_front_t1 > -10 and pcd_left_t1 - pcd_right_t1 > -10:
                            cloud_arr = np.frombuffer(msg.data, np.float32).reshape(-1, 6)
                            pcd_left = cloud_arr[:, [1,2,3]]  # ros2_numpy.numpify(msg)['xyz']
                            lidar2_on = True
            with self.lidar_right_lock:
                if self.lidar_right_time != 0 and self.lidar_right_time != pcd_right_t1:
                    pcd_right_t1 = self.lidar_right_time
                    msg = self.lidar_right_list.pop()
                    self.lidar_right_list.clear()
                    if pcd_front_t1 > 0 and pcd_left_t1 > 0 and pcd_right_t1 > 0:
                        if pcd_right_t1 - pcd_front_t1 > -10 and pcd_right_t1 - pcd_left_t1 > -10:
                            cloud_arr = np.frombuffer(msg.data, np.float32).reshape(-1, 6)
                            pcd_right = cloud_arr[:, [1,2,3]]  # ros2_numpy.numpify(msg)['xyz']
                            lidar3_on = True

            if lidar1_on and lidar2_on and lidar3_on:
                if abs(pcd_front_t1 - pcd_left_t1) < 20 and abs(pcd_front_t1 - pcd_right_t1) < 20:
                    with self.lidar_front_lock and self.lidar_left_lock and self.lidar_right_lock:
                        lidar1_on = False
                        lidar2_on = False
                        lidar3_on = False
                        print("FR_T: {}, L_T: {}, R_T: {}".format(pcd_front_t1, pcd_left_t1, pcd_right_t1))
                        tt1 = time.time()
                        pcd_front = transform_points(pcd_front, R_front, t_front)
                        pcd_left = transform_points(pcd_left, R_left, t_left)
                        pcd_right = transform_points(pcd_right, R_right, t_right)

                        pcd = np.concatenate((pcd_front, pcd_left, pcd_right), axis=0)
                        tt2 = time.time()
                        img = point_cloud_2_birdseye(pcd)

                        tt3 = time.time()
                        print("DT1: {:.3f}, DT2: {:.3f}".format(tt3 - tt1, tt2 - tt1))

                    sms_img = cvimg2sms(img)
                    self.sms_lidar_pub.publish(sms_img)
                    cv2.imshow('img', img)
                    cv2.waitKey(5)

            time.sleep(0.005)


def main(args=None):
    rclpy.init(args=args)
    node = A2RL3LidarConcatNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()