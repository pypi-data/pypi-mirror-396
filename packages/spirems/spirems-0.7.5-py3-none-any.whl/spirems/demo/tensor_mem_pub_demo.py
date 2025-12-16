#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn


from spirems import Publisher, def_msg, tensor2sms, Rate
import time
import random
from datetime import datetime
import cv2


pub = Publisher(
    '/tensor_mem',
    'memory_msgs::Tensor'
)

r = Rate(20)
cap = cv2.VideoCapture('/home/amov/Downloads/MVI_0789_VIS_OB.avi')
while True:
    try:
        ret, img = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        # img = cv2.resize(img, (3840, 2160))
        msg = tensor2sms(img, "tensor_mem_url")
        pub.publish(msg)
        r.sleep()
    except KeyboardInterrupt:
        pub.kill()
        break
