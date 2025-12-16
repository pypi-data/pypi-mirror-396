#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import numpy as np
from spirems import Publisher, CSVLogger, def_msg
import time

# 参数定义
A = 5  # 8字的宽度
B = 3  # 8字的高度
omega_base = 0.5  # 基础角频率


# 定义位置函数
def position(t):
    omega = omega_base
    x = A * np.sin(omega * t)
    y = B * np.sin(2 * omega * t)
    return x, y

# 定义速度函数（对位置求导）
def velocity(t):
    omega = omega_base
    dx_dt = A * omega * np.cos(omega * t) - A * omega * t * 0.05 * np.cos(0.5 * t) * np.sin(omega * t)
    dy_dt = 2 * B * omega * np.cos(2 * omega * t) - 2 * B * omega * t * 0.05 * np.cos(0.5 * t) * np.sin(2 * omega * t)
    return dx_dt, dy_dt


# 定义发布器，用SpireMS发出话题
pub = Publisher('/drone/pose', 'geometry_msgs::Pose')
# 定义CSV文件记录器
logger = CSVLogger(['timestamp', 'x', 'y', 'vx', 'vy'], name='DronePose')

t = 0.0
while True:
    t += 0.01
    # 计算位置和速度
    x, y = position(t)
    vx, vy = velocity(t)
    # 定义SpireMS中的 geometry_msgs::Pose 空消息
    msg = def_msg('geometry_msgs::Pose')
    msg['timestamp'] = time.time()
    msg['position']['x'] = x
    msg['position']['y'] = y
    msg['position']['z'] = 0.0
    # 利用SpireMS灵活优势，直接把速度放进去
    msg['velocity'] = {}
    msg['velocity']['x'] = vx
    msg['velocity']['y'] = vy
    msg['velocity']['z'] = 0.0
    pub.publish(msg)

    # 写CSV文件，但实际写硬盘不在该进程
    logger.append([msg['timestamp'], x, y, vx, vy])
    # 100Hz发送
    time.sleep(0.01)
