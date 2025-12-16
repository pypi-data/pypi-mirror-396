#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn
# @Date  : 2025-02-05

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class VideoPublisher(Node):
    def __init__(self):
        super().__init__('video_publisher')
        # 创建图像发布者，发布到 'video_frames' 话题，队列大小为 10
        self.publisher_ = self.create_publisher(Image, 'video_frames', 10)
        timer_period = 1 / 60  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        # 初始化 CvBridge，用于在 OpenCV 图像和 ROS 图像消息之间转换
        self.bridge = CvBridge()
        # 打开视频文件，这里需要替换为你实际的视频文件路径
        self.cap = cv2.VideoCapture('/home/jario/2024-11-12 13-12-58.mkv')

    def timer_callback(self):
        # 读取视频的一帧
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (1920, 1080))
            # 将 OpenCV 图像转换为 ROS 图像消息
            msg = self.bridge.cv2_to_imgmsg(frame, "bgr8")
            current_time = self.get_clock().now()
            # 为图像消息的 header.stamp 字段赋值当前时间戳
            msg.header.stamp = current_time.to_msg()
            # 发布图像消息
            self.publisher_.publish(msg)
            self.get_logger().info('Publishing video frame')
        else:
            # 如果视频读取结束，释放资源并停止节点
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)


def main(args=None):
    rclpy.init(args=args)
    video_publisher = VideoPublisher()
    rclpy.spin(video_publisher)
    video_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

