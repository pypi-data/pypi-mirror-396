#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn
# @Date  : 2025-02-05

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from rclpy.time import Time


class ImageSubscriber(Node):
    def __init__(self):
        super().__init__('image_subscriber')
        # 订阅 'video_frames' 话题，接收到消息后调用 image_callback 函数处理
        self.subscription = self.create_subscription(
            Image,
            'video_frames',
            self.image_callback,
            10)
        self.subscription  # 防止未使用的变量警告
        # 初始化 CvBridge，用于在 OpenCV 图像和 ROS 图像消息之间转换
        self.bridge = CvBridge()
        self.img_cnt = 0
        self.dt_tot = 0.0
        self.print_dt = False

    def image_callback(self, msg):
        try:
            # 将 ROS 图像消息转换为 OpenCV 图像
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            # 获取图像消息的时间戳
            image_timestamp = Time.from_msg(msg.header.stamp)
            # 获取当前时间
            current_time = self.get_clock().now()

            # 计算时间差值
            time_diff = current_time - image_timestamp
            # 将时间差值转换为秒
            time_diff_sec = time_diff.nanoseconds / 1e9
            self.dt_tot += time_diff_sec
            self.img_cnt += 1
            if self.img_cnt > 600 and not self.print_dt:
                print("Avg Dt: {}".format(self.dt_tot / self.img_cnt))
                # self.print_dt = True

            # 显示图像
            cv2.imshow("Image window", cv_image)
            # 等待 1 毫秒，处理窗口事件
            cv2.waitKey(1)
        except Exception as e:
            self.get_logger().error(f"Error converting image: {e}")


def main(args=None):
    rclpy.init(args=args)
    image_subscriber = ImageSubscriber()
    rclpy.spin(image_subscriber)
    # 关闭 OpenCV 窗口
    cv2.destroyAllWindows()
    image_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

