#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, Image
import time
import os
import numpy as np
import ros2_numpy
import cv2
from spirems import Publisher, Subscriber, def_msg, cvimg2sms


"""
依赖项安装：
pip install spirems ros2-numpy
"""

DEFAULT_IP = "127.0.0.1"


class A2RLLidar2SMSNode(Node):
    def __init__(self):
        Node.__init__(self, 'A2RLLidar2SMSNode')

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

        self.sms_lidar_front_pub = Publisher("/flyeagle/lidar_front", "memory_msgs::PointCloud", ip=DEFAULT_IP)
        self.sms_lidar_left_pub = Publisher("/flyeagle/lidar_left", "memory_msgs::PointCloud", ip=DEFAULT_IP)
        self.sms_lidar_right_pub = Publisher("/flyeagle/lidar_right", "memory_msgs::PointCloud", ip=DEFAULT_IP)
    
    def sensor_lidar_front_callback(self, msg):
        t1 = time.time()
        cloud_arr = np.frombuffer(msg.data, np.float32).reshape(-1, 6)
        pcd_ = cloud_arr.copy(order='C')  # ros2_numpy.numpify(msg)['xyz']
        # 重新解析int32部分数据
        int32_bytes = pcd_[:, [4, 5]].tobytes()
        int32_data_tof = np.frombuffer(int32_bytes, dtype=np.int32).reshape(-1, 2).astype(np.float32)
        pcd_[:, [4, 5]] = int32_data_tof
        # print(pcd_[:, 4].astype(np.int32)[:100])
        ros_time = msg.header.stamp
        sms_msg = self.sms_lidar_front_pub.pcl2sms_mem(pcd_, ["intensity", "x", "y", "z", "scan_idx", "ring"], frame_id="lidar_front", timestamp=ros_time.sec + ros_time.nanosec / 1e9)
        sms_msg['t1'] = time.time()
        self.sms_lidar_front_pub.publish(sms_msg)
        print("dt:", time.time() - t1)

    def sensor_lidar_left_callback(self, msg):
        cloud_arr = np.frombuffer(msg.data, np.float32).reshape(-1, 6)
        pcd_ = cloud_arr.copy(order='C')  # ros2_numpy.numpify(msg)['xyz']
        int32_bytes = pcd_[:, [4, 5]].tobytes()
        int32_data_tof = np.frombuffer(int32_bytes, dtype=np.int32).reshape(-1, 2).astype(np.float32)
        pcd_[:, [4, 5]] = int32_data_tof
        ros_time = msg.header.stamp
        sms_msg = self.sms_lidar_left_pub.pcl2sms_mem(pcd_, ["intensity", "x", "y", "z", "scan_idx", "ring"], frame_id="lidar_left", timestamp=ros_time.sec + ros_time.nanosec / 1e9)
        self.sms_lidar_left_pub.publish(sms_msg)

    def sensor_lidar_right_callback(self, msg):
        cloud_arr = np.frombuffer(msg.data, np.float32).reshape(-1, 6)
        pcd_ = cloud_arr.copy(order='C')  # ros2_numpy.numpify(msg)['xyz']
        int32_bytes = pcd_[:, [4, 5]].tobytes()
        int32_data_tof = np.frombuffer(int32_bytes, dtype=np.int32).reshape(-1, 2).astype(np.float32)
        pcd_[:, [4, 5]] = int32_data_tof
        ros_time = msg.header.stamp
        sms_msg = self.sms_lidar_right_pub.pcl2sms_mem(pcd_, ["intensity", "x", "y", "z", "scan_idx", "ring"], frame_id="lidar_right", timestamp=ros_time.sec + ros_time.nanosec / 1e9)
        self.sms_lidar_right_pub.publish(sms_msg)


def main(args=None):
    rclpy.init(args=args)
    node = A2RLLidar2SMSNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()