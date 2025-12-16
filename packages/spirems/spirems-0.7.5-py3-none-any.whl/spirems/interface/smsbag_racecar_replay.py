#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn

import math
import cv2
import base64
import copy
import math
import argparse
import os
import numpy as np
from datetime import datetime
from spirems import SMSBagPlayer
from spirems.image_io.visual_helper import draw_charts_v3, load_a2rl_logo, track_boundary_parse, draw_track_map_v2, xyzrpy2tr, trans_pts, pcl2bev
from spirems import Publisher, Subscriber, def_msg, cvimg2sms


def smsbag_racecar_replay(smsbag_path, output_video_dir='', add_extimg=False, add_extpcl=False):
    url_img = "/sensor/camera/camera_fl/compressed"
    url_img_extra = "/sensor/camera/camera_r/compressed"
    url_pcl_f = "/sensor/lidar_front/points"
    url_pcl_l = "/sensor/lidar_left/points"
    url_pcl_r = "/sensor/lidar_right/points"
    url_ego_loc = "/flyeagle/a2rl/observer/ego_loc"
    url_ego_state = "/flyeagle/a2rl/observer/ego_state"
    url_ctl_status = "/flyeagle/a2rl/controller/status"
    url_ctl_debug = "/flyeagle/a2rl/controller/debug"
    url_brake_disk = "/flyeagle/a2rl/eav25_bsu/brake_disk_temp"
    url_tyre_surface_rear = "/flyeagle/a2rl/eav25_bsu/tyre_surface_temp_rear"
    url_tyre_surface_front = "/flyeagle/a2rl/eav25_bsu/tyre_surface_temp_front"
    url_ice_status_01 = "/flyeagle/a2rl/eav25_bsu/ice_status_01"
    url_ice_status_02 = "/flyeagle/a2rl/eav25_bsu/ice_status_02"
    url_bad_misc = "/flyeagle/a2rl/eav25_bsu/bad_misc"
    url_ref_s_dist = "/flyeagle/a2rl/planner/reference_s_distance"
    url_slip = "/flyeagle/a2rl/controller/slip"
    url_bosch_imu = "/sensor/bosch/imu"

    pcl_f_tf = {"xyz": [0.738, -0.006, -0.002], "rpy": [3.1415926, -1.5707963, 0]}
    pcl_l_tf = {"xyz": [-0.151, 0.2385, 0.2436], "rpy":[3.1415926, -1.5707963, 2.094395]}
    pcl_r_tf = {"xyz": [-0.151, -0.2508, 0.2436], "rpy":[3.1415926, -1.5707963, -2.094395]}
    pcl_f_t, pcl_f_R = xyzrpy2tr(pcl_f_tf["xyz"], pcl_f_tf["rpy"])
    pcl_l_t, pcl_l_R = xyzrpy2tr(pcl_l_tf["xyz"], pcl_l_tf["rpy"])
    pcl_r_t, pcl_r_R = xyzrpy2tr(pcl_r_tf["xyz"], pcl_r_tf["rpy"])

    player = SMSBagPlayer(smsbag_path)
    t0 = 0
    nc = 0
    visual_msg = def_msg('std_msgs::Null')
    visual_msg['timestamp'] = 0.0
    visual_msg['ego_position'] = [0, 0, 0]
    visual_msg['ego_orientation_ypr'] = [0, 0, 0]
    visual_msg['ego_velocity'] = [0, 0, 0]
    visual_msg['ego_acceleration'] = [0, 0, 0]
    visual_msg['ice_actual_gear'] = 1
    visual_msg['ice_actual_throttle'] = 0.0
    visual_msg['ice_engine_speed_rpm'] = 0.0
    visual_msg['ice_water_temp_deg_c'] = 0.0
    visual_msg['ice_oil_temp_deg_c'] = 0.0
    visual_msg['brake_f'] = 0.0
    visual_msg['brake_r'] = 0.0
    visual_msg['slip_f'] = 0.0
    visual_msg['slip_r'] = 0.0
    visual_msg['steering'] = 0.0
    visual_msg['tyre_temp_fl'] = [0, 0, 0]
    visual_msg['tyre_temp_fr'] = [0, 0, 0]
    visual_msg['tyre_temp_rl'] = [0, 0, 0]
    visual_msg['tyre_temp_rr'] = [0, 0, 0]
    visual_msg['brake_disk_temp_fl'] = 0.0
    visual_msg['brake_disk_temp_fr'] = 0.0
    visual_msg['brake_disk_temp_rl'] = 0.0
    visual_msg['brake_disk_temp_rr'] = 0.0
    visual_msg['error_lateral'] = 0.0
    visual_msg['error_yaw'] = 0.0
    visual_msg['error_speed'] = 0.0
    visual_msg['lap_count'] = 1
    visual_msg['lap_time'] = 0
    visual_msg['ref_s_dist'] = 0.0

    if len(output_video_dir) > 0:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4格式编码器
        img_show_h = 720
        if add_extimg:
            img_show_h += 720
        if add_extpcl:
            img_show_h += 1280
        output_video = cv2.VideoWriter(
            os.path.join(output_video_dir, datetime.now().strftime("smsreplay_%Y-%m-%d_%H-%M-%S.mp4")),  # 输出文件名
            fourcc,
            60,
            (1280, img_show_h)  # 必须与帧尺寸一致
        )

    img_extra_raw = None
    while 1:
        msg = player.next()
        if msg is None:
            break
        url = msg['msg']['url']
        tim = msg['msg']['timerec']
        if url == url_img:
            img_raw = msg['raw']
            img_raw = img_raw[:, 5: -5]
            img_raw = cv2.resize(img_raw, (1280, 720))
            assert img_raw.shape[0] == 720 and img_raw.shape[1] == 1280
            if t0 == 0:
                t0 = tim
        elif url == url_img_extra:
            img_extra_raw = msg['raw']
            img_extra_raw = img_extra_raw[:, 5: -5]
            img_extra_raw = cv2.resize(img_extra_raw, (1280, 720))
            assert img_extra_raw.shape[0] == 720 and img_extra_raw.shape[1] == 1280
        elif url == url_pcl_f:
            pcl_f = msg['raw'][:, [0, 1, 2]]
        elif url == url_pcl_l:
            pcl_l = msg['raw'][:, [0, 1, 2]]
        elif url == url_pcl_r:
            pcl_r = msg['raw'][:, [0, 1, 2]]
        elif url == url_ego_state:
            """
            visual_msg['ego_acceleration'] = [
                msg['msg']['acceleration']['x'], msg['msg']['acceleration']['y'], msg['msg']['acceleration']['z']
            ]
            """
            visual_msg['ego_velocity'] = [
                msg['msg']['velocity']['x'], msg['msg']['velocity']['y'], msg['msg']['velocity']['z']
            ]
        elif url == url_ego_loc:
            visual_msg['ego_position'] = [
                msg['msg']['position']['x'], msg['msg']['position']['y'], msg['msg']['position']['z']
            ]
        elif url == url_ctl_status:
            visual_msg['ice_actual_gear'] = msg['msg']['gear']
            visual_msg['ice_actual_throttle'] = msg['msg']['throttle']
            visual_msg['steering'] = msg['msg']['steering']
            visual_msg['brake_f'] = msg['msg']['front_brake']
            visual_msg['brake_r'] = msg['msg']['rear_brake']
            # visual_msg['slip_f'] = msg['msg']['slip_f']
            # visual_msg['slip_r'] = msg['msg']['slip_r']
        elif url == url_slip:
            visual_msg['slip_f'] = (msg['msg']['data'][2] + msg['msg']['data'][3]) / 200
            visual_msg['slip_r'] = (msg['msg']['data'][4] + msg['msg']['data'][5]) / 200
        elif url == url_ctl_debug:
            visual_msg['error_lateral'] = msg['msg']['lateral_error']
            visual_msg['error_yaw'] = msg['msg']['yaw_error']
            visual_msg['error_speed'] = msg['msg']['speed_error']
        elif url == url_brake_disk:
            visual_msg['brake_disk_temp_fl'] = round(msg['msg']['brake_disk_temp_fl'], 1)
            visual_msg['brake_disk_temp_fr'] = round(msg['msg']['brake_disk_temp_fr'], 1)
            visual_msg['brake_disk_temp_rl'] = round(msg['msg']['brake_disk_temp_rl'], 1)
            visual_msg['brake_disk_temp_rr'] = round(msg['msg']['brake_disk_temp_rr'], 1)
        elif url == url_tyre_surface_rear:
            visual_msg['tyre_temp_rl'] = [round(msg['msg']['outer_rl'], 1), round(msg['msg']['center_rl'], 1), round(msg['msg']['inner_rl'], 1)]
            visual_msg['tyre_temp_rr'] = [round(msg['msg']['outer_rr'], 1), round(msg['msg']['center_rr'], 1), round(msg['msg']['inner_rr'], 1)]
        elif url == url_tyre_surface_front:
            visual_msg['tyre_temp_fl'] = [round(msg['msg']['outer_fl'], 1), round(msg['msg']['center_fl'], 1), round(msg['msg']['inner_fl'], 1)]
            visual_msg['tyre_temp_fr'] = [round(msg['msg']['outer_fr'], 1), round(msg['msg']['center_fr'], 1), round(msg['msg']['inner_fr'], 1)]
        elif url == url_ice_status_01:
            pass
            # visual_msg['ice_actual_gear'] = msg['msg']['ice_actual_gear']
            # visual_msg['ice_actual_throttle'] = msg['msg']['ice_actual_throttle']
        elif url == url_ice_status_02:
            visual_msg['ice_water_temp_deg_c'] = msg['msg']['ice_water_temp_deg_c']
            visual_msg['ice_oil_temp_deg_c'] = msg['msg']['ice_oil_temp_deg_c']
            visual_msg['ice_engine_speed_rpm'] = msg['msg']['ice_engine_speed_rpm']
        elif url == url_bad_misc:
            visual_msg['lap_count'] = msg['msg']['bad_lap_number']
            visual_msg['lap_time'] = msg['msg']['bad_lap_time']
        elif url == url_ref_s_dist:
            visual_msg['ref_s_dist'] = round(msg['msg']['data'][3], 2)
        elif url == url_bosch_imu:
            visual_msg['ego_acceleration'] = [
                -msg['msg']['linear_acceleration']['x'], -msg['msg']['linear_acceleration']['y'], msg['msg']['linear_acceleration']['z']
            ]

        if t0 > 0:
            n_img = int((tim - t0) * 1000 / 16.666667)
            if n_img != nc:
                nc = n_img
                visual_msg['timestamp'] = tim
                img_show = draw_charts_v3(img_raw, visual_msg, 1)

                if add_extimg and img_extra_raw is not None:
                    img_show = cv2.vconcat([img_show, img_extra_raw])
                
                if add_extpcl and pcl_f is not None and pcl_l is not None and pcl_r is not None:
                    pcl_f_cpu = trans_pts(pcl_f, pcl_f_R, pcl_f_t)
                    pcl_l_cpu = trans_pts(pcl_l, pcl_l_R, pcl_l_t)
                    pcl_r_cpu = trans_pts(pcl_r, pcl_r_R, pcl_r_t)
                    pcl_cpu = np.concatenate((pcl_f_cpu, pcl_l_cpu, pcl_r_cpu), axis=0)
                    img_bev = pcl2bev(pcl_cpu)[:1280, :1280]
                    img_bev = cv2.cvtColor(img_bev, cv2.COLOR_GRAY2BGR)
                    img_show = cv2.vconcat([img_show, img_bev])

                if len(output_video_dir) > 0 and img_show.shape[0] == img_show_h and img_show.shape[1] == 1280:
                    output_video.write(img_show)

                cv2.imshow("img_raw", img_show)
                cv2.waitKey(5)

    if len(output_video_dir) > 0:
        output_video.release()

def main():
    parser = argparse.ArgumentParser(description="SMSBag A2RL RaceCar 回放程序")
    parser.add_argument(
        '-s', '--sms-bag',
        type=str,
        default='/home/amov/Pictures/smsbag_2025-10-18_20-01-42',
        help='输入的smsbag路径'
    )
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default='',
        help='输出视频文件夹'
    )
    parser.add_argument(
        '--extimg',
        action='store_true',
        help='增加渲染额外图像'
    )
    parser.add_argument(
        '--extpcl',
        action='store_true',
        help='增加渲染额外点云图'
    )
    args = parser.parse_args()

    print("Input SMSBag: {}".format(args.sms_bag))
    if not os.path.isdir(args.sms_bag):
        print("SMSBag不存在")
        exit(1)

    smsbag_path = args.sms_bag
    smsbag_racecar_replay(smsbag_path, args.output_dir, args.extimg, args.extpcl)


if __name__ == "__main__":
    main()
