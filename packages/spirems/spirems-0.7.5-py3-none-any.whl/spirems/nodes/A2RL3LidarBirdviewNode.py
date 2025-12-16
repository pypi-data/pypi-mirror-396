#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn
# @Date  : 2025-02-17


import threading
import time
import cv2
import os
import json
from typing import Union
from queue import Queue
from spirems import Publisher, Subscriber, cvimg2sms, sms2cvimg, sms2pcl
from spirems.nodes.BaseNode import BaseNode
import argparse
from datetime import datetime
import numpy as np
import torch
from collections import deque


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


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


# 转换点云
def transform_points_gpu(points, rotation_matrix, translation_vector):
    # 点云坐标变换: P' = R * P + t
    return (rotation_matrix @ points.t()).t() + translation_vector


# 定义 Lidar 的参数
lidar_params = {
    "lidar_front": {"xyz": [2.199, 0.053, 0.744], "rpy": [-0.144, -1.550, -2.993]},
    "lidar_left": {"xyz": [1.691, 0.2969, 0.80634], "rpy": [-0.420, -1.553, -0.622]},
    "lidar_right": {"xyz": [1.691, -0.1969, 0.755093], "rpy": [0.625635, -1.5428, 0.424122]}
}


t_front = np.array(lidar_params["lidar_front"]["xyz"], dtype=np.float32)
t_front_gpu = torch.from_numpy(t_front).to(device)
rpy_front = lidar_params["lidar_front"]["rpy"]
R_front = rpy_to_rotation_matrix(*rpy_front)
R_front = R_front.astype(np.float32)
R_front_gpu = torch.from_numpy(R_front).to(device)

t_left = np.array(lidar_params["lidar_left"]["xyz"], dtype=np.float32)
t_left_gpu = torch.from_numpy(t_left).to(device)
rpy_left = lidar_params["lidar_left"]["rpy"]
R_left = rpy_to_rotation_matrix(*rpy_left)
R_left = R_left.astype(np.float32)
R_left_gpu = torch.from_numpy(R_left).to(device)

t_right = np.array(lidar_params["lidar_right"]["xyz"], dtype=np.float32)
t_right_gpu = torch.from_numpy(t_right).to(device)
rpy_right = lidar_params["lidar_right"]["rpy"]
R_right = rpy_to_rotation_matrix(*rpy_right)
R_right = R_right.astype(np.float32)
R_right_gpu = torch.from_numpy(R_right).to(device)


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
                           res=0.1,
                           side_range=(-60., 60.),  # left-most to right-most
                           fwd_range=(-60., 60.), # back-most to forward-most
                           height_range=(-1., 1.),  # bottom-most to upper-most
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


class A2RL3LidarBirdviewNode(threading.Thread, BaseNode):
    def __init__(
        self,
        job_name: str,
        ip: str = '127.0.0.1',
        port: int = 9094,
        param_dict_or_file: Union[dict, str] = None,
        sms_shutdown: bool = True
    ):
        threading.Thread.__init__(self)
        BaseNode.__init__(
            self,
            self.__class__.__name__,
            job_name,
            ip=ip,
            port=port,
            param_dict_or_file=param_dict_or_file,
            sms_shutdown=sms_shutdown
        )
        self._lidar_f = Subscriber('/flyeagle/lidar_front', 'memory_msgs::PointCloud', self.lidar_f_callback, ip=ip, port=port)
        self._lidar_l = Subscriber('/flyeagle/lidar_left', 'memory_msgs::PointCloud', self.lidar_l_callback, ip=ip, port=port)
        self._lidar_r = Subscriber('/flyeagle/lidar_right', 'memory_msgs::PointCloud', self.lidar_r_callback, ip=ip, port=port)
        self._birdview_pub = Publisher('/flyeagle/lidar_birdview', 'memory_msgs::RawImage', ip=ip, port=port)
        self._points_pub = Publisher('/flyeagle/lidar_points', 'memory_msgs::PointCloud', ip=ip, port=port)

        self.use_cuda = self.get_param("use_cuda", 1)

        self.lidar_front_dq = deque()
        self.lidar_front_time = 0
        self.lidar_left_dq = deque()
        self.lidar_left_time = 0
        self.lidar_right_dq = deque()
        self.lidar_right_time = 0

        self.start()

    def release(self):
        BaseNode.release(self)
        self._lidar_f.kill()
        self._lidar_l.kill()
        self._lidar_r.kill()

    def lidar_f_callback(self, msg):
        pcd = sms2pcl(msg)[:, [1,2,3]]
        # print("SMS_DT:", time.time() - msg['t1'])
        self.lidar_front_dq.append(pcd)
        self.lidar_front_time = int(msg['timestamp'] * 1000)  # % 86400000

    def lidar_l_callback(self, msg):
        pcd = sms2pcl(msg)[:, [1,2,3]]
        self.lidar_left_dq.append(pcd)
        self.lidar_left_time = int(msg['timestamp'] * 1000)  # % 86400000
    
    def lidar_r_callback(self, msg):
        pcd = sms2pcl(msg)[:, [1,2,3]]
        self.lidar_right_dq.append(pcd)
        self.lidar_right_time = int(msg['timestamp'] * 1000)  # % 86400000

    def run(self):
        lidar1_on = False
        lidar2_on = False
        lidar3_on = False
        pcd_front_t1 = 0
        pcd_front_t2 = 0
        pcd_left_t1 = 0
        pcd_right_t1 = 0
        t_cnt = 0
        avg_dt1 = 0.0
        avg_dt2 = 0.0
        while self.is_running():
            if self.lidar_front_time != 0 and self.lidar_front_time != pcd_front_t1 and len(self.lidar_front_dq) > 0:
                pcd_front_t1 = self.lidar_front_time
                pcd_front = self.lidar_front_dq.pop()
                if len(self.lidar_front_dq) > 0:
                    self.lidar_front_dq.popleft()
                lidar1_on = True

            if self.lidar_left_time != 0 and self.lidar_left_time != pcd_left_t1 and len(self.lidar_left_dq) > 0:
                pcd_left_t1 = self.lidar_left_time
                pcd_left = self.lidar_left_dq.pop()
                if len(self.lidar_left_dq) > 0:
                    self.lidar_left_dq.popleft()
                lidar2_on = True

            if self.lidar_right_time != 0 and self.lidar_right_time != pcd_right_t1 and len(self.lidar_right_dq) > 0:
                pcd_right_t1 = self.lidar_right_time
                pcd_right = self.lidar_right_dq.pop()
                if len(self.lidar_right_dq) > 0:
                    self.lidar_right_dq.popleft()
                lidar3_on = True

            if pcd_front_t2 != pcd_front_t1 and lidar1_on and lidar2_on and lidar3_on:
                if abs(pcd_front_t1 - pcd_left_t1) < 20 and abs(pcd_front_t1 - pcd_right_t1) < 20:
                    pcd_front_t2 = pcd_front_t1

                    tt1 = time.time()

                    # print("FR_T: {}, L_T: {}, R_T: {}".format(pcd_front_t1, pcd_left_t1, pcd_right_t1))
                    if self.use_cuda == 1:
                        with torch.no_grad():
                            pcd_front_gpu = torch.from_numpy(pcd_front).to(device)
                            pcd_left_gpu = torch.from_numpy(pcd_left).to(device)
                            pcd_right_gpu = torch.from_numpy(pcd_right).to(device)
                            pcd_front_gpu = transform_points_gpu(pcd_front_gpu, R_front_gpu, t_front_gpu)
                            pcd_left_gpu = transform_points_gpu(pcd_left_gpu, R_left_gpu, t_left_gpu)                            
                            pcd_right_gpu = transform_points_gpu(pcd_right_gpu, R_right_gpu, t_right_gpu)

                            pcd_gpu = torch.concat([pcd_front_gpu, pcd_left_gpu, pcd_right_gpu], dim=0)
                            pcd_cpu = pcd_gpu.cpu().numpy()
                            tt2 = time.time()
                            img = point_cloud_2_birdseye(pcd_cpu)
                    else:
                        pcd_front_cpu = transform_points(pcd_front, R_front, t_front)
                        pcd_left_cpu = transform_points(pcd_left, R_left, t_left)
                        pcd_right_cpu = transform_points(pcd_right, R_right, t_right)

                        pcd_cpu = np.concatenate((pcd_front_cpu, pcd_left_cpu, pcd_right_cpu), axis=0)
                        tt2 = time.time()
                        img = point_cloud_2_birdseye(pcd_cpu)

                    pcd_sms = self._points_pub.pcl2sms_mem(pcd_cpu, ['x', 'y', 'z'], frame_id="lidar_360", timestamp=pcd_front_t2 / 1000.0)
                    self._points_pub.publish(pcd_sms)
                    birdview_sms = self._birdview_pub.cvimg2sms_mem(img, frame_id="camera_bv", timestamp=pcd_front_t2 / 1000.0)
                    self._birdview_pub.publish(birdview_sms)

                    tt3 = time.time()
                    # print("DT1: {:.3f}, DT2: {:.3f}".format(tt3 - tt1, tt2 - tt1))
                    avg_dt1 += tt3 - tt1
                    avg_dt2 += tt2 - tt1
                    t_cnt += 1
                    if t_cnt > 1000:
                        print("DT1: {:.3f}, DT2: {:.3f}".format(avg_dt1 / t_cnt, avg_dt2 / t_cnt))
                        t_cnt = 0
                        avg_dt1 = 0.0
                        avg_dt2 = 0.0

                    # cv2.imshow('img', img)
                    # cv2.waitKey(5)

            time.sleep(0.002)

        self.release()
        print('{} quit!'.format(self.__class__.__name__))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config',
        default=None,
        help='SpireCV2 Config (.json)')
    parser.add_argument(
        '--job-name',
        type=str,
        default='live',
        help='SpireCV Job Name')
    parser.add_argument(
        '--ip',
        type=str,
        default='127.0.0.1',
        help='SpireMS Core IP')
    parser.add_argument(
        '--port',
        type=int,
        default=9094,
        help='SpireMS Core Port')
    args = parser.parse_args()
    print("config:", args.config)
    print("job-name:", args.job_name)

    node = A2RL3LidarBirdviewNode(args.job_name, param_dict_or_file=args.config)
    node.spin()
