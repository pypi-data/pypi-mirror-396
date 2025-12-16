#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


global img_cnt, dt_tot, print_dt
img_cnt = 0
dt_tot = 0.0
print_dt = False


def image_callback(msg):
    global img_cnt, dt_tot, print_dt
    try:
        # 使用cv_bridge将ROS图像消息转换为OpenCV图像格式
        bridge = CvBridge()
        cv_image = bridge.imgmsg_to_cv2(msg, "bgr8")
        
        start_time = msg.header.stamp
        end_time = rospy.Time.now()
        time_difference = end_time - start_time
        time_difference_in_seconds = time_difference.to_sec()
        dt_tot += time_difference_in_seconds
        img_cnt += 1
        if img_cnt > 600 and not print_dt:
            print("dt: {}".format(dt_tot / img_cnt))
            print_dt = True
        # 显示图像
        cv2.imshow("Image Viewer", cv_image)
        cv2.waitKey(3)
    except Exception as e:
        rospy.logerr("Error converting image: %s", str(e))


def main():
    # 初始化ROS节点
    rospy.init_node('image_viewer', anonymous=True)
    # 订阅图像话题，根据实际情况修改话题名称
    image_topic = "video_frames"
    rospy.Subscriber(image_topic, Image, image_callback)
    # 进入循环等待消息
    rospy.spin()
    # 关闭OpenCV窗口
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()


