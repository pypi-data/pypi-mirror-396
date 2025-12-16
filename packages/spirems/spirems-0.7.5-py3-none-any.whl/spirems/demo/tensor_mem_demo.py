#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn

import cv2
from spirems import sms2tensor, tensor2sms
import numpy as np


mat = cv2.imread("/home/jario/Pictures/dji_stat_2024-12-30/DJI_20241013165423_0001_V_20241222_000241.jpg").astype(np.float32) / 255.
sms_msg = tensor2sms(mat, "DJI_20241013165423_0001_V_20241222_000061")
ans = sms2tensor(sms_msg)

cv2.imshow("ans", ans)
cv2.waitKey(5000)

