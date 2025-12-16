#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


def video_publisher():
    # 初始化ROS节点
    rospy.init_node('video_publisher', anonymous=True)
    
    # 创建一个Publisher，发布图像话题
    image_pub = rospy.Publisher('video_frames', Image, queue_size=10)
    
    # 创建CvBridge对象
    bridge = CvBridge()
    
    # 打开视频文件
    video_path = "/home/nvidia/2024-11-12 13-12-58.mkv"
    cap = cv2.VideoCapture(video_path)
    
    # 设置发布频率
    rate = rospy.Rate(20)  # 30 Hz
    
    while not rospy.is_shutdown():
        # 读取视频帧
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame = cv2.resize(frame, (640, 480))
        stamp = rospy.Time.now()
        # 将OpenCV图像转换为ROS图像消息
        ros_image = bridge.cv2_to_imgmsg(frame, "bgr8")
        ros_image.header.stamp = stamp
        # 发布图像消息
        image_pub.publish(ros_image)
        
        # 按照设定的频率休眠
        rate.sleep()
    
    # 释放视频捕获对象
    cap.release()


if __name__ == '__main__':
    try:
        video_publisher()
    except rospy.ROSInterruptException:
        pass


