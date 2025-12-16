#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn
# @Date  : 2024-07-08

import numpy as np
from spirems.exts import csms_shm  # 导入编译好的模块
from spirems import Subscriber, sms2cvimg
import cv2
import time
from queue import Queue


# # 创建一个 NumPy 数组
# arr = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float64)

# # 调用 C++ 函数
# result = csms_shm.square_array(arr)

# mat = csms_shm.random_matrix()

# print("Input array:", arr)
# print("Squared array:", result)

# print(mat)
# print(mat.dtype)


def callback_f(msg):
    t1 = time.time()
    img = sms2cvimg(msg)
    # print(time.time())
    # print(img.shape)
    # cvimg = sms2cvimg(msg)
    # img = cv2.resize(img, (1280, 720))
    cv2.imshow('img', img)
    cv2.waitKey(5)


sub = Subscriber('/share_mem/image', 'memory_msgs::RawImage', callback_f)

img2 = cv2.imread("/home/jario/dataset/2024-10-17_VID-ARD-MAV/phantom02/scaled_images/phantom02_0001.jpg")
res2 = csms_shm.cvimg2sms_uint8(img2, "/test_shm")
print(res2)
