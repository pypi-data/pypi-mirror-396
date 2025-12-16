#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
import numpy as np
import cv2
import time
import json
import os
import struct
import argparse
import yaml
import sys
from colorama import init, Fore, Style
from datetime import timedelta
from sensor_msgs.msg import PointCloud2, PointField
from spirems.msg_helper import (encode_msg, decode_msg, get_all_msg_types, def_msg, check_msg,
                                index_msg_header, decode_msg_header, print_table)


def pointcloud2_to_numpy(cloud_msg: PointCloud2) -> np.ndarray:
    """
    将 sensor_msgs/msg/PointCloud2 转换为 NumPy 数组
    
    参数:
        cloud_msg: PointCloud2 消息对象
    返回:
        np.ndarray: 形状为 (N, M) 的数组，N 为点数量，M 为字段数量（如 x,y,z 对应 M=3）
    """
    # 1. 解析元数据
    width = cloud_msg.width
    height = cloud_msg.height
    point_step = cloud_msg.point_step  # 每个点的字节长度
    row_step = cloud_msg.row_step      # 每行的字节长度（通常 = width × point_step）
    data = cloud_msg.data             # 二进制点云数据（bytes 类型）
    fields = cloud_msg.fields         # 字段列表（如 x, y, z, intensity 等）
    
    # 2. 计算总点数
    num_points = width * height
    
    # 3. 解析字段信息（名称、数据类型、偏移量）
    #    PointField 数据类型映射：ROS 类型 → numpy 类型
    dtype_mapping = {
        PointField.FLOAT32: np.float32
    }
    
    # 构建每个字段的 (名称, 数据类型, 偏移量)
    field_info = []
    for field in fields:
        if field.datatype not in dtype_mapping:
            raise TypeError(f"不支持的字段数据类型: {field.datatype}")
        field_info.append(field.name)

    # 4. 将二进制数据转换为 numpy 数组（按字节解析）
    # 转换为 numpy 数组并返回
    data_array = np.frombuffer(data, dtype=np.float32).reshape(-1, len(field_info))
    return data_array, field_info


def get_bag_total_count_from_metadata(bag_dir):
    """
    从ROS 2 bag的metadata.yaml中读取消息总数量
    :param bag_dir: bag文件所在目录（包含metadata.yaml的文件夹路径）
    :return: 消息总数量（int），若文件不存在则返回0
    """
    metadata_path = f"{bag_dir}/metadata.yaml"
    total_count = 0

    try:
        with open(metadata_path, 'r') as f:
            metadata = yaml.safe_load(f)
        total_count = metadata.get("rosbag2_bagfile_information", {}).get("message_count", 0)
    except FileNotFoundError:
        print(f"错误：未在{bag_dir}中找到metadata.yaml文件")
    except Exception as e:
        print(f"解析metadata时出错：{e}")
    return total_count


def progress_bar_with_time(current, total, start_time, bar_length=20):
    """带时间预估的进度条"""
    percent = float(current) / total
    filled_length = int(bar_length * current // total)
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    
    # 计算已用时间和剩余时间
    elapsed_time = time.time() - start_time
    if current > 0:
        remaining_time = elapsed_time / current * (total - current)
    else:
        remaining_time = 0
    
    # 格式化时间（转换为时分秒）
    elapsed_str = str(timedelta(seconds=int(elapsed_time)))
    remaining_str = str(timedelta(seconds=int(remaining_time)))
    
    # 输出进度条
    sys.stdout.write(
        f'\r进度: [{bar}] {percent:.1%} | 已用: {elapsed_str} | 剩余: {remaining_str}' + ' ' * 8
    )
    sys.stdout.flush()
    if current == total:
        print(f'\n完成！总耗时: {elapsed_str}')


def Localization2SMS(msg):
    sms_msg = def_msg('nav_msgs::Localization')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['position'] = {
        "x": msg.position.x,
        "y": msg.position.y,
        "z": msg.position.z
    }
    sms_msg['position_stddev'] = {
        "x": msg.position_stddev.x,
        "y": msg.position_stddev.y,
        "z": msg.position_stddev.z
    }
    sms_msg['orientation_ypr'] = {
        "x": msg.orientation_ypr.x,
        "y": msg.orientation_ypr.y,
        "z": msg.orientation_ypr.z
    }
    sms_msg['orientation_stddev'] = {
        "x": msg.orientation_stddev.x,
        "y": msg.orientation_stddev.y,
        "z": msg.orientation_stddev.z
    }
    return sms_msg

def EgoState2SMS(msg):
    sms_msg = def_msg('vehicle_msgs::EgoState')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['velocity'] = {
        "x": msg.velocity.x,
        "y": msg.velocity.y,
        "z": msg.velocity.z
    }
    sms_msg['velocity_stddev'] = {
        "x": msg.velocity_stddev.x,
        "y": msg.velocity_stddev.y,
        "z": msg.velocity_stddev.z
    }
    sms_msg['angular_rate'] = {
        "x": msg.angular_rate.x,
        "y": msg.angular_rate.y,
        "z": msg.angular_rate.z
    }
    sms_msg['angular_rate_stddev'] = {
        "x": msg.angular_rate_stddev.x,
        "y": msg.angular_rate_stddev.y,
        "z": msg.angular_rate_stddev.z
    }
    sms_msg['acceleration'] = {
        "x": msg.acceleration.x,
        "y": msg.acceleration.y,
        "z": msg.acceleration.z
    }
    sms_msg['acceleration_stddev'] = {
        "x": msg.acceleration_stddev.x,
        "y": msg.acceleration_stddev.y,
        "z": msg.acceleration_stddev.z
    }
    sms_msg['wheels_speed'] = {
        "fl": msg.wheels_speed.fl,
        "fr": msg.wheels_speed.fr,
        "rl": msg.wheels_speed.rl,
        "rr": msg.wheels_speed.rr
    }
    sms_msg['wheels_toe_angle'] = {
        "fl": msg.wheels_toe_angle.fl,
        "fr": msg.wheels_toe_angle.fr,
        "rl": msg.wheels_toe_angle.rl,
        "rr": msg.wheels_toe_angle.rr
    }
    sms_msg['ypr_chassis'] = {
        "x": msg.ypr_chassis.x,
        "y": msg.ypr_chassis.y,
        "z": msg.ypr_chassis.z
    }
    return sms_msg

def Imu2SMS(msg):
    sms_msg = def_msg('sensor_msgs::Imu')
    sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
    sms_msg['frame_id'] = msg.header.frame_id
    sms_msg['orientation'] = {
        "x": msg.orientation.x,
        "y": msg.orientation.y,
        "z": msg.orientation.z,
        "w": msg.orientation.w
    }
    sms_msg['orientation_covariance'] = msg.orientation_covariance.tolist()
    sms_msg['angular_velocity'] = {
        "x": msg.angular_velocity.x,
        "y": msg.angular_velocity.y,
        "z": msg.angular_velocity.z
    }
    sms_msg['angular_velocity_covariance'] = msg.angular_velocity_covariance.tolist()
    sms_msg['linear_acceleration'] = {
        "x": msg.linear_acceleration.x,
        "y": msg.linear_acceleration.y,
        "z": msg.linear_acceleration.z
    }
    sms_msg['linear_acceleration_covariance'] = msg.linear_acceleration_covariance.tolist()
    return sms_msg

def PoseWithCovarianceStamped2SMS(msg):
    sms_msg = def_msg('geometry_msgs::PoseWithCovariance')
    sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
    sms_msg['frame_id'] = msg.header.frame_id
    sms_msg['pose'] = {
        "position": {
            "x": msg.pose.pose.position.x,
            "y": msg.pose.pose.position.y,
            "z": msg.pose.pose.position.z
        },
        "orientation": {
            "x": msg.pose.pose.orientation.x,
            "y": msg.pose.pose.orientation.y,
            "z": msg.pose.pose.orientation.z,
            "w": msg.pose.pose.orientation.w
        }
    }
    sms_msg['covariance'] = msg.pose.covariance.tolist()
    return sms_msg

def TwistWithCovarianceStamped2SMS(msg):
    sms_msg = def_msg('geometry_msgs::TwistWithCovariance')
    sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
    sms_msg['frame_id'] = msg.header.frame_id
    sms_msg['twist'] = {
        "linear": {
            "x": msg.twist.twist.linear.x,
            "y": msg.twist.twist.linear.y,
            "z": msg.twist.twist.linear.z
        },
        "angular": {
            "x": msg.twist.twist.angular.x,
            "y": msg.twist.twist.angular.y,
            "z": msg.twist.twist.angular.z
        }
    }
    sms_msg['covariance'] = msg.twist.covariance.tolist()
    return sms_msg

def PoseStamped2SMS(msg):
    sms_msg = def_msg('geometry_msgs::PoseInFrame')
    sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
    sms_msg['frame_id'] = msg.header.frame_id
    sms_msg['pose'] = {
        "position": {
            "x": msg.pose.position.x,
            "y": msg.pose.position.y,
            "z": msg.pose.position.z
        },
        "orientation": {
            "x": msg.pose.orientation.x,
            "y": msg.pose.orientation.y,
            "z": msg.pose.orientation.z,
            "w": msg.pose.orientation.w
        }
    }
    return sms_msg

def Odometry2SMS(msg):
    sms_msg = def_msg('nav_msgs::Odometry')
    sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
    sms_msg['frame_id'] = msg.header.frame_id
    sms_msg['child_frame_id'] = msg.child_frame_id
    sms_msg['pose'] = {
        "pose": {
            "position": {
                "x": msg.pose.pose.position.x,
                "y": msg.pose.pose.position.y,
                "z": msg.pose.pose.position.z
            },
            "orientation": {
                "x": msg.pose.pose.orientation.x,
                "y": msg.pose.pose.orientation.y,
                "z": msg.pose.pose.orientation.z,
                "w": msg.pose.pose.orientation.w
            }
        },
        "covariance": msg.pose.covariance.tolist()
    }
    sms_msg['twist'] = {
        "twist": {
            "linear": {
                "x": msg.twist.twist.linear.x,
                "y": msg.twist.twist.linear.y,
                "z": msg.twist.twist.linear.z
            },
            "angular": {
                "x": msg.twist.twist.angular.x,
                "y": msg.twist.twist.angular.y,
                "z": msg.twist.twist.angular.z
            }
        },
        "covariance": msg.twist.covariance.tolist()
    }
    return sms_msg

def Bool2SMS(msg, ts):
    sms_msg = def_msg('std_msgs::Boolean')
    sms_msg['timestamp'] = ts / 1e9
    sms_msg['data'] = msg.data
    return sms_msg

def Number2SMS(msg, ts):
    sms_msg = def_msg('std_msgs::Number')
    sms_msg['timestamp'] = ts / 1e9
    sms_msg['data'] = msg.data
    return sms_msg

def NumberMultiArray2SMS(msg, ts):
    sms_msg = def_msg('std_msgs::NumberMultiArray')
    sms_msg['timestamp'] = ts / 1e9
    sms_msg['data'] = msg.data.tolist()
    return sms_msg

def TFMessage2SMS(msg, ts):
    sms_msg = def_msg('geometry_msgs::FrameTransforms')
    sms_msg['timestamp'] = ts / 1e9
    sms_msg['transforms'] = []
    for ts in msg.transforms:
        sms_ts = {
            "timestamp": ts.header.stamp.sec + ts.header.stamp.nanosec / 1e9,
            "parent_frame_id": ts.header.frame_id,
            "child_frame_id": ts.child_frame_id,
            "translation": {
                "x": ts.transform.translation.x,
                "y": ts.transform.translation.y,
                "z": ts.transform.translation.z
            },
            "rotation": {
                "x": ts.transform.rotation.x,
                "y": ts.transform.rotation.y,
                "z": ts.transform.rotation.z,
                "w": ts.transform.rotation.w
            }
        }
        sms_msg['transforms'].append(sms_ts)
    return sms_msg

def Vector3Stamped2SMS(msg):
    sms_msg = def_msg('geometry_msgs::Vector3')
    sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
    sms_msg['frame_id'] = msg.header.frame_id
    sms_msg['x'] = msg.vector.x
    sms_msg['y'] = msg.vector.y
    sms_msg['z'] = msg.vector.z
    return sms_msg

def VectornavCommonGroup2SMS(msg):
    sms_msg = def_msg('nav_msgs::VectornavCommonGroup')
    sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
    sms_msg['frame_id'] = msg.header.frame_id
    sms_msg['group_fields'] = msg.group_fields
    sms_msg['timestartup'] = msg.timestartup
    sms_msg['timegps'] = msg.timegps
    sms_msg['timesyncin'] = msg.timesyncin
    sms_msg['yawpitchroll'] = {
        "x": msg.yawpitchroll.x,
        "y": msg.yawpitchroll.y,
        "z": msg.yawpitchroll.z
    }
    sms_msg['quaternion'] = {
        "x": msg.quaternion.x,
        "y": msg.quaternion.y,
        "z": msg.quaternion.z,
        "w": msg.quaternion.w
    }
    sms_msg['angularrate'] = {
        "x": msg.angularrate.x,
        "y": msg.angularrate.y,
        "z": msg.angularrate.z
    }
    sms_msg['position'] = {
        "x": msg.position.x,
        "y": msg.position.y,
        "z": msg.position.z
    }
    sms_msg['velocity'] = {
        "x": msg.velocity.x,
        "y": msg.velocity.y,
        "z": msg.velocity.z
    }
    sms_msg['accel'] = {
        "x": msg.accel.x,
        "y": msg.accel.y,
        "z": msg.accel.z
    }
    sms_msg['imu_accel'] = {
        "x": msg.imu_accel.x,
        "y": msg.imu_accel.y,
        "z": msg.imu_accel.z
    }
    sms_msg['imu_rate'] = {
        "x": msg.imu_rate.x,
        "y": msg.imu_rate.y,
        "z": msg.imu_rate.z
    }
    sms_msg['magpres_mag'] = {
        "x": msg.magpres_mag.x,
        "y": msg.magpres_mag.y,
        "z": msg.magpres_mag.z
    }
    sms_msg['magpres_temp'] = msg.magpres_temp
    sms_msg['magpres_pres'] = msg.magpres_pres
    sms_msg['deltatheta_dtime'] = msg.deltatheta_dtime
    sms_msg['deltatheta_dtheta'] = {
        "x": msg.deltatheta_dtheta.x,
        "y": msg.deltatheta_dtheta.y,
        "z": msg.deltatheta_dtheta.z
    }
    sms_msg['deltatheta_dvel'] = {
        "x": msg.deltatheta_dvel.x,
        "y": msg.deltatheta_dvel.y,
        "z": msg.deltatheta_dvel.z
    }
    sms_msg['insstatus'] = {
        "mode": msg.insstatus.mode,
        "gps_fix": msg.insstatus.gps_fix,
        "time_error": msg.insstatus.time_error,
        "imu_error": msg.insstatus.imu_error,
        "mag_pres_error": msg.insstatus.mag_pres_error,
        "gps_error": msg.insstatus.gps_error,
        "gps_heading_ins": msg.insstatus.gps_heading_ins,
        "gps_compass": msg.insstatus.gps_compass
    }
    sms_msg['syncincnt'] = msg.syncincnt
    sms_msg['timegpspps'] = msg.timegpspps
    return sms_msg

def VectornavImuGroup2SMS(msg):
    sms_msg = def_msg('nav_msgs::VectornavImuGroup')
    sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
    sms_msg['frame_id'] = msg.header.frame_id
    sms_msg["group_fields"] = msg.group_fields
    sms_msg["imustatus"] = msg.imustatus
    sms_msg["uncompmag"] = {
        "x": msg.uncompmag.x,
        "y": msg.uncompmag.y,
        "z": msg.uncompmag.z
    }
    sms_msg["uncompaccel"] = {
        "x": msg.uncompaccel.x,
        "y": msg.uncompaccel.y,
        "z": msg.uncompaccel.z
    }
    sms_msg["uncompgyro"] = {
        "x": msg.uncompgyro.x,
        "y": msg.uncompgyro.y,
        "z": msg.uncompgyro.z
    }
    sms_msg["temp"] = msg.temp
    sms_msg["pres"] = msg.pres
    sms_msg["deltatheta_time"] = msg.deltatheta_time
    sms_msg["deltatheta_dtheta"] = {
        "x": msg.deltatheta_dtheta.x,
        "y": msg.deltatheta_dtheta.y,
        "z": msg.deltatheta_dtheta.z
    }
    sms_msg["deltavel"] = {
        "x": msg.deltavel.x,
        "y": msg.deltavel.y,
        "z": msg.deltavel.z
    }
    sms_msg["mag"] = {
        "x": msg.mag.x,
        "y": msg.mag.y,
        "z": msg.mag.z
    }
    sms_msg["accel"] = {
        "x": msg.accel.x,
        "y": msg.accel.y,
        "z": msg.accel.z
    }
    sms_msg["angularrate"] = {
        "x": msg.angularrate.x,
        "y": msg.angularrate.y,
        "z": msg.angularrate.z
    }
    sms_msg["sensat"] = msg.sensat
    return sms_msg

def HL_Msg_04_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['hl_latitude'] = msg.hl_latitude
    sms_msg['hl_longitude'] = msg.hl_longitude
    return sms_msg

def HL_Msg_05_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['hl_height'] = msg.hl_height
    sms_msg['hl_vel_east'] = msg.hl_vel_east
    sms_msg['hl_vel_north'] = msg.hl_vel_north
    sms_msg['hl_vel_up'] = msg.hl_vel_up
    return sms_msg

def ControllerStatus2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['safe_stop_mode'] = msg.safe_stop_mode
    sms_msg['reason_for_safestop'] = msg.reason_for_safestop
    sms_msg['connection_loss'] = msg.connection_loss
    sms_msg['input_spd'] = msg.input_spd
    sms_msg['throttle'] = msg.throttle
    sms_msg['steering'] = msg.steering
    sms_msg['front_brake'] = msg.front_brake
    sms_msg['rear_brake'] = msg.rear_brake
    sms_msg['slip_f'] = msg.slip_f
    sms_msg['slip_r'] = msg.slip_r
    sms_msg['gear'] = msg.gear
    return sms_msg

def ControllerDebug2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['lateral_error'] = msg.lateral_error
    sms_msg['yaw_error'] = msg.yaw_error
    sms_msg['speed_error'] = msg.speed_error
    sms_msg['long_ff1'] = msg.long_ff1
    sms_msg['long_ff2'] = msg.long_ff2
    sms_msg['long_fb1p'] = msg.long_fb1p
    sms_msg['long_fb1i'] = msg.long_fb1i
    sms_msg['long_fb1d'] = msg.long_fb1d
    sms_msg['long_fb2'] = msg.long_fb2
    sms_msg['long_ft'] = msg.long_ft
    sms_msg['lat_ff'] = msg.lat_ff
    sms_msg['lat_fb'] = msg.lat_fb
    sms_msg['step_time'] = msg.step_time
    return sms_msg

def ControllerGearStatus2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['predict_downshift_flag'] = msg.predict_downshift_flag
    sms_msg['enable_new_gear_logic'] = msg.enable_new_gear_logic
    sms_msg['gear_status'] = msg.gear_status
    sms_msg['target_gear'] = msg.target_gear
    sms_msg['act_gear'] = msg.act_gear
    return sms_msg

def ControllerBrake2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['front_raw'] = msg.front_raw
    sms_msg['rear_raw'] = msg.rear_raw
    sms_msg['abs_brake_pressure_fl'] = msg.abs_brake_pressure_fl
    sms_msg['abs_brake_pressure_fr'] = msg.abs_brake_pressure_fr
    sms_msg['abs_brake_pressure_rl'] = msg.abs_brake_pressure_rl
    sms_msg['abs_brake_pressure_rr'] = msg.abs_brake_pressure_rr
    sms_msg['warmup_brake_pressure_fl'] = msg.warmup_brake_pressure_fl
    sms_msg['warmup_brake_pressure_fr'] = msg.warmup_brake_pressure_fr
    sms_msg['warmup_brake_pressure_rl'] = msg.warmup_brake_pressure_rl
    sms_msg['warmup_brake_pressure_rr'] = msg.warmup_brake_pressure_rr
    sms_msg['target_brake_pressure_fl'] = msg.target_brake_pressure_fl
    sms_msg['target_brake_pressure_fr'] = msg.target_brake_pressure_fr
    sms_msg['target_brake_pressure_rl'] = msg.target_brake_pressure_rl
    sms_msg['target_brake_pressure_rr'] = msg.target_brake_pressure_rr
    sms_msg['act_brake_pressure_fl'] = msg.act_brake_pressure_fl
    sms_msg['act_brake_pressure_fr'] = msg.act_brake_pressure_fr
    sms_msg['act_brake_pressure_rl'] = msg.act_brake_pressure_rl
    sms_msg['act_brake_pressure_rr'] = msg.act_brake_pressure_rr
    sms_msg['abs_enabled'] = msg.abs_enabled
    sms_msg['brakewarmup_enabled'] = msg.brakewarmup_enabled
    sms_msg['wheel_latched_fl'] = msg.wheel_latched_fl
    sms_msg['wheel_latched_fr'] = msg.wheel_latched_fr
    sms_msg['wheel_latched_rl'] = msg.wheel_latched_rl
    sms_msg['wheel_latched_rr'] = msg.wheel_latched_rr
    return sms_msg

def Wheels_Speed_01_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['wss_speed_fl_rad_s'] = msg.wss_speed_fl_rad_s
    sms_msg['wss_speed_fr_rad_s'] = msg.wss_speed_fr_rad_s
    sms_msg['wss_speed_rl_rad_s'] = msg.wss_speed_rl_rad_s
    sms_msg['wss_speed_rr_rad_s'] = msg.wss_speed_rr_rad_s
    return sms_msg

def PSA_Status_01_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['psa_actual_pos_rad'] = msg.psa_actual_pos_rad
    sms_msg['psa_actual_speed_rad_s'] = msg.psa_actual_speed_rad_s
    sms_msg['psa_actual_torque_m_nm'] = msg.psa_actual_torque_m_nm
    sms_msg['psa_actual_mode_of_operation'] = msg.psa_actual_mode_of_operation
    sms_msg['psa_actual_current_a'] = msg.psa_actual_current_a
    sms_msg['psa_actual_voltage_v'] = msg.psa_actual_voltage_v
    return sms_msg

def PSA_Status_02_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['psa_target_psa_control_ack'] = msg.psa_target_psa_control_ack
    sms_msg['psa_actual_pos'] = msg.psa_actual_pos
    sms_msg['psa_actual_speed'] = msg.psa_actual_speed
    sms_msg['psa_actual_torque'] = msg.psa_actual_torque
    return sms_msg

def VectornavGpsGroup2SMS(msg):
    sms_msg = def_msg('nav_msgs::VectornavGpsGroup')
    sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
    sms_msg['frame_id'] = msg.header.frame_id
    sms_msg["group_fields"] = msg.group_fields
    sms_msg['utc'] = {
        "year": msg.utc.year,
        "month": msg.utc.month,
        "day": msg.utc.day,
        "hour": msg.utc.hour,
        "min": msg.utc.min,
        "sec": msg.utc.sec,
        "ms": msg.utc.ms
    }
    sms_msg["tow"] = msg.tow
    sms_msg["week"] = msg.week
    sms_msg["numsats"] = msg.numsats
    sms_msg["fix"] = msg.fix
    sms_msg["poslla"] = {
        "x": msg.poslla.x,
        "y": msg.poslla.y,
        "z": msg.poslla.z
    }
    sms_msg["posecef"] = {
        "x": msg.posecef.x,
        "y": msg.posecef.y,
        "z": msg.posecef.z
    }
    sms_msg["velned"] = {
        "x": msg.velned.x,
        "y": msg.velned.y,
        "z": msg.velned.z
    }
    sms_msg["velecef"] = {
        "x": msg.velecef.x,
        "y": msg.velecef.y,
        "z": msg.velecef.z
    }
    sms_msg["posu"] = {
        "x": msg.posu.x,
        "y": msg.posu.y,
        "z": msg.posu.z
    }
    sms_msg["velu"] = msg.velu
    sms_msg["timeu"] = msg.timeu
    sms_msg["timeinfo_status"] = msg.timeinfo_status
    sms_msg["timeinfo_leapseconds"] = msg.timeinfo_leapseconds
    sms_msg["dop"] = {
        "g": msg.dop.g,
        "p": msg.dop.p,
        "t": msg.dop.t,
        "v": msg.dop.v,
        "h": msg.dop.h,
        "n": msg.dop.n,
        "e": msg.dop.e
    }
    return sms_msg

def VectornavAttitudeGroup2SMS(msg):
    sms_msg = def_msg('nav_msgs::VectornavAttitudeGroup')
    sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
    sms_msg['frame_id'] = msg.header.frame_id
    sms_msg["group_fields"] = msg.group_fields
    sms_msg["vpestatus"] = {
        "attitude_quality": msg.vpestatus.attitude_quality,
        "gyro_saturation": msg.vpestatus.gyro_saturation,
        "gyro_saturation_recovery": msg.vpestatus.gyro_saturation_recovery,
        "mag_disturbance": msg.vpestatus.mag_disturbance,
        "mag_saturation": msg.vpestatus.mag_saturation,
        "acc_disturbance": msg.vpestatus.acc_disturbance,
        "acc_saturation": msg.vpestatus.acc_saturation,
        "known_mag_disturbance": msg.vpestatus.known_mag_disturbance,
        "known_accel_disturbance": msg.vpestatus.known_accel_disturbance
    }
    sms_msg["yawpitchroll"] = {
        "x": msg.yawpitchroll.x,
        "y": msg.yawpitchroll.y,
        "z": msg.yawpitchroll.z
    }
    sms_msg["quaternion"] = {
        "x": msg.quaternion.x,
        "y": msg.quaternion.y,
        "z": msg.quaternion.z,
        "w": msg.quaternion.w
    }
    sms_msg["dcm"] = msg.dcm.tolist()
    sms_msg["magned"] = {
        "x": msg.magned.x,
        "y": msg.magned.y,
        "z": msg.magned.z
    }
    sms_msg["accelned"] = {
        "x": msg.accelned.x,
        "y": msg.accelned.y,
        "z": msg.accelned.z
    }
    sms_msg["linearaccelbody"] = {
        "x": msg.linearaccelbody.x,
        "y": msg.linearaccelbody.y,
        "z": msg.linearaccelbody.z
    }
    sms_msg["linearaccelned"] = {
        "x": msg.linearaccelned.x,
        "y": msg.linearaccelned.y,
        "z": msg.linearaccelned.z
    }
    sms_msg["ypru"] = {
        "x": msg.ypru.x,
        "y": msg.ypru.y,
        "z": msg.ypru.z
    }
    return sms_msg

def Kistler2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
    sms_msg['frame_id'] = msg.header.frame_id
    sms_msg['velocity'] = {
        "x": msg.velocity.x,
        "y": msg.velocity.y,
        "z": msg.velocity.z
    }
    sms_msg['resultant_velocity'] = {
        "x": msg.resultant_velocity.x,
        "y": msg.resultant_velocity.y,
        "z": msg.resultant_velocity.z
    }
    sms_msg['angle'] = msg.angle
    sms_msg['distance'] = msg.distance
    sms_msg['path_radius'] = msg.path_radius
    sms_msg['velocity_raw'] = {
        "x": msg.velocity_raw.x,
        "y": msg.velocity_raw.y,
        "z": msg.velocity_raw.z
    }
    sms_msg['resultant_velocity_raw'] = {
        "x": msg.resultant_velocity_raw.x,
        "y": msg.resultant_velocity_raw.y,
        "z": msg.resultant_velocity_raw.z
    }
    sms_msg['angle_raw'] = msg.angle_raw
    return sms_msg

def KistlerStatus2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
    sms_msg['frame_id'] = msg.header.frame_id
    sms_msg['sensor_id'] = msg.sensor_id
    sms_msg['temperature'] = msg.temperature
    sms_msg['lamp_current'] = msg.lamp_current
    sms_msg['filter_setting'] = msg.filter_setting
    sms_msg['stst'] = msg.stst
    sms_msg['filter_off_on'] = msg.filter_off_on
    sms_msg['lamp_current_control'] = msg.lamp_current_control
    sms_msg['temperature_ok'] = msg.temperature_ok
    sms_msg['head_status'] = msg.head_status
    sms_msg['angle_switched_off'] = msg.angle_switched_off
    sms_msg['direction'] = msg.direction
    sms_msg['ang_vel_correction'] = msg.ang_vel_correction
    sms_msg['direction_motion'] = msg.direction_motion
    sms_msg['direction_mounting'] = msg.direction_mounting
    sms_msg['direction_head_is_valid'] = msg.direction_head_is_valid
    sms_msg['direction_head'] = msg.direction_head
    return sms_msg

def SensorStatus2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
    sms_msg['frame_id'] = msg.header.frame_id
    sms_msg['gps'] = msg.gps
    sms_msg['gps2'] = msg.gps2
    sms_msg['imu_vec'] = msg.imu_vec
    sms_msg['imu_bo'] = msg.imu_bo
    sms_msg['kistler'] = msg.kistler
    sms_msg['wheel'] = msg.wheel
    sms_msg['ins'] = msg.ins
    sms_msg['lidar_f'] = msg.lidar_f
    sms_msg['lidar_l'] = msg.lidar_l
    sms_msg['lidar_r'] = msg.lidar_r
    sms_msg['radar_f'] = msg.radar_f
    sms_msg['radar_l'] = msg.radar_l
    sms_msg['radar_r'] = msg.radar_r
    sms_msg['radar_rr'] = msg.radar_rr
    sms_msg['cam_fl'] = msg.cam_fl
    sms_msg['cam_fr'] = msg.cam_fr
    sms_msg['cam_lf'] = msg.cam_lf
    sms_msg['cam_lr'] = msg.cam_lr
    sms_msg['cam_rf'] = msg.cam_rf
    sms_msg['cam_rr'] = msg.cam_rr
    sms_msg['cam_rrr'] = msg.cam_rrr
    return sms_msg

def VectornavIns2SMS(msg):
    sms_msg = def_msg('nav_msgs::VectornavIns')
    sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
    sms_msg['frame_id'] = msg.header.frame_id
    sms_msg['group_fields'] = msg.group_fields
    sms_msg['insstatus'] = {
        "mode": msg.insstatus.mode,
        "gps_fix": msg.insstatus.gps_fix,
        "time_error": msg.insstatus.time_error,
        "imu_error": msg.insstatus.imu_error,
        "mag_pres_error": msg.insstatus.mag_pres_error,
        "gps_error": msg.insstatus.gps_error,
        "gps_heading_ins": msg.insstatus.gps_heading_ins,
        "gps_compass": msg.insstatus.gps_compass
    }
    sms_msg['poslla'] = {
        "x": msg.poslla.x,
        "y": msg.poslla.y,
        "z": msg.poslla.z
    }
    sms_msg['posecef'] = {
        "x": msg.posecef.x,
        "y": msg.posecef.y,
        "z": msg.posecef.z
    }
    sms_msg['velbody'] = {
        "x": msg.velbody.x,
        "y": msg.velbody.y,
        "z": msg.velbody.z
    }
    sms_msg['velned'] = {
        "x": msg.velned.x,
        "y": msg.velned.y,
        "z": msg.velned.z
    }
    sms_msg['velecef'] = {
        "x": msg.velecef.x,
        "y": msg.velecef.y,
        "z": msg.velecef.z
    }
    sms_msg['magecef'] = {
        "x": msg.magecef.x,
        "y": msg.magecef.y,
        "z": msg.magecef.z
    }
    sms_msg['accelecef'] = {
        "x": msg.accelecef.x,
        "y": msg.accelecef.y,
        "z": msg.accelecef.z
    }
    sms_msg['linearaccelecef'] = {
        "x": msg.linearaccelecef.x,
        "y": msg.linearaccelecef.y,
        "z": msg.linearaccelecef.z
    }
    sms_msg['posu'] = msg.posu
    sms_msg['velu'] = msg.velu
    return sms_msg

def ICE_Status_01_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['ice_actual_gear'] = msg.ice_actual_gear
    sms_msg['ice_target_gear_ack'] = msg.ice_target_gear_ack
    sms_msg['ice_actual_throttle'] = msg.ice_actual_throttle
    sms_msg['ice_target_throttle_ack'] = msg.ice_target_throttle_ack
    sms_msg['ice_push_to_pass_req'] = msg.ice_push_to_pass_req
    sms_msg['ice_push_to_pass_ack'] = msg.ice_push_to_pass_ack
    sms_msg['ice_water_press_k_pa'] = msg.ice_water_press_k_pa
    sms_msg['ice_available_fuel_l'] = msg.ice_available_fuel_l
    sms_msg['ice_downshift_available'] = msg.ice_downshift_available
    return sms_msg

def ICE_Status_02_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['ice_oil_temp_deg_c'] = msg.ice_oil_temp_deg_c
    sms_msg['ice_engine_speed_rpm'] = msg.ice_engine_speed_rpm
    sms_msg['ice_fuel_press_k_pa'] = msg.ice_fuel_press_k_pa
    sms_msg['ice_water_temp_deg_c'] = msg.ice_water_temp_deg_c
    sms_msg['ice_oil_press_k_pa'] = msg.ice_oil_press_k_pa
    return sms_msg

def Tyre_Surface_Temp_Rear_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['outer_rl'] = msg.outer_rl
    sms_msg['center_rl'] = msg.center_rl
    sms_msg['inner_rl'] = msg.inner_rl
    sms_msg['outer_rr'] = msg.outer_rr
    sms_msg['center_rr'] = msg.center_rr
    sms_msg['inner_rr'] = msg.inner_rr
    return sms_msg

def Tyre_Surface_Temp_Front_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['outer_fl'] = msg.outer_fl
    sms_msg['center_fl'] = msg.center_fl
    sms_msg['inner_fl'] = msg.inner_fl
    sms_msg['outer_fr'] = msg.outer_fr
    sms_msg['center_fr'] = msg.center_fr
    sms_msg['inner_fr'] = msg.inner_fr
    return sms_msg

def Brake_Disk_Temp_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['brake_disk_temp_fl'] = msg.brake_disk_temp_fl
    sms_msg['brake_disk_temp_fr'] = msg.brake_disk_temp_fr
    sms_msg['brake_disk_temp_rr'] = msg.brake_disk_temp_rr
    sms_msg['brake_disk_temp_rl'] = msg.brake_disk_temp_rl
    return sms_msg

def BSU_Status_01_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['bsu_switch_off_req'] = msg.bsu_switch_off_req
    sms_msg['bsu_limp_mode_activated'] = msg.bsu_limp_mode_activated
    sms_msg['bsu_hl_stop_request'] = msg.bsu_hl_stop_request
    sms_msg['bsu_hl_warning'] = msg.bsu_hl_warning
    sms_msg['bsu_em_stop_activated'] = msg.bsu_em_stop_activated
    sms_msg['bsu_ml_stop_activated'] = msg.bsu_ml_stop_activated
    sms_msg['bsu_alive_counter'] = msg.bsu_alive_counter
    sms_msg['bsu_status'] = msg.bsu_status
    sms_msg['abs_external_enable_ack'] = msg.abs_external_enable_ack
    return sms_msg

def EM_Status_01_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['dcdc4812_voltage_v'] = msg.dcdc4812_voltage_v
    sms_msg['em_status'] = msg.em_status
    sms_msg['hl_stop_deceleration_1'] = msg.hl_stop_deceleration_1
    sms_msg['hl_stop_deceleration_2'] = msg.hl_stop_deceleration_2
    sms_msg['hl_stop_time_to_dec_1'] = msg.hl_stop_time_to_dec_1
    sms_msg['hl_stop_time_to_dec_2'] = msg.hl_stop_time_to_dec_2
    return sms_msg

def Bad_Wheel_Load_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['bad_load_wheel_fl'] = msg.bad_load_wheel_fl
    sms_msg['bad_load_wheel_fr'] = msg.bad_load_wheel_fr
    sms_msg['bad_load_wheel_rr'] = msg.bad_load_wheel_rr
    sms_msg['bad_load_wheel_rl'] = msg.bad_load_wheel_rl
    return sms_msg

def Tpms_Rear_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['tpr4_temp_rl'] = msg.tpr4_temp_rl
    sms_msg['tpr4_temp_rr'] = msg.tpr4_temp_rr
    sms_msg['tpr4_abs_press_rl'] = msg.tpr4_abs_press_rl
    sms_msg['tpr4_abs_press_rr'] = msg.tpr4_abs_press_rr
    return sms_msg

def Tpms_Front_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['tpr4_temp_fl'] = msg.tpr4_temp_fl
    sms_msg['tpr4_temp_fr'] = msg.tpr4_temp_fr
    sms_msg['tpr4_abs_press_fl'] = msg.tpr4_abs_press_fl
    sms_msg['tpr4_abs_press_fr'] = msg.tpr4_abs_press_fr
    return sms_msg

def PIT_Packet_0_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['pitot_front_press'] = msg.pitot_front_press
    sms_msg['pitot_yaw_press'] = msg.pitot_yaw_press
    sms_msg['pitot_yaw_angle'] = msg.pitot_yaw_angle
    sms_msg['pitot_absolute_press'] = msg.pitot_absolute_press
    return sms_msg

def PIT_Packet_1_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['pitot_air_temp'] = msg.pitot_air_temp
    sms_msg['pitot_board_temp'] = msg.pitot_board_temp
    return sms_msg

def CBA_Status_FL_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['cba_actual_pressure_fl_pa'] = msg.cba_actual_pressure_fl_pa
    sms_msg['cba_actual_pressure_fl'] = msg.cba_actual_pressure_fl
    sms_msg['cba_target_pressure_fl_ack'] = msg.cba_target_pressure_fl_ack
    sms_msg['cba_actual_current_fl_a'] = msg.cba_actual_current_fl_a
    sms_msg['cba_voltage_fl_v'] = msg.cba_voltage_fl_v
    return sms_msg

def CBA_Status_FR_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['cba_actual_pressure_fr_pa'] = msg.cba_actual_pressure_fr_pa
    sms_msg['cba_actual_pressure_fr'] = msg.cba_actual_pressure_fr
    sms_msg['cba_target_pressure_fr_ack'] = msg.cba_target_pressure_fr_ack
    sms_msg['cba_actual_current_fr_a'] = msg.cba_actual_current_fr_a
    sms_msg['cba_voltage_fr_v'] = msg.cba_voltage_fr_v
    return sms_msg

def CBA_Status_RL_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['cba_actual_pressure_rl_pa'] = msg.cba_actual_pressure_rl_pa
    sms_msg['cba_actual_pressure_rl'] = msg.cba_actual_pressure_rl
    sms_msg['cba_target_pressure_rl_ack'] = msg.cba_target_pressure_rl_ack
    sms_msg['cba_actual_current_rl_a'] = msg.cba_actual_current_rl_a
    sms_msg['cba_voltage_rl_v'] = msg.cba_voltage_rl_v
    return sms_msg

def CBA_Status_RR_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['cba_actual_pressure_rr_pa'] = msg.cba_actual_pressure_rr_pa
    sms_msg['cba_actual_pressure_rr'] = msg.cba_actual_pressure_rr
    sms_msg['cba_target_pressure_rr_ack'] = msg.cba_target_pressure_rr_ack
    sms_msg['cba_actual_current_rr_a'] = msg.cba_actual_current_rr_a
    sms_msg['cba_voltage_rr_v'] = msg.cba_voltage_rr_v
    return sms_msg

def Bad_Ride_Rear_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['bad_ride_height_rear'] = msg.bad_ride_height_rear
    sms_msg['bad_damper_stroke_r3rd'] = msg.bad_damper_stroke_r3rd
    sms_msg['bad_damper_stroke_rl'] = msg.bad_damper_stroke_rl
    sms_msg['bad_damper_stroke_rr'] = msg.bad_damper_stroke_rr
    return sms_msg

def Bad_Ride_Front_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['bad_ride_height_front'] = msg.bad_ride_height_front
    sms_msg['bad_damper_stroke_f3rd'] = msg.bad_damper_stroke_f3rd
    sms_msg['bad_damper_stroke_fl'] = msg.bad_damper_stroke_fl
    sms_msg['bad_damper_stroke_fr'] = msg.bad_damper_stroke_fr
    return sms_msg

def Bad_Misc_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['bad_lap_time'] = msg.bad_lap_time
    sms_msg['bad_lap_distance'] = msg.bad_lap_distance
    sms_msg['bad_lap_number'] = msg.bad_lap_number
    sms_msg['battery_voltage'] = msg.battery_voltage
    return sms_msg

def PDUs_Status_01_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['pdu12_power_supply_voltage_v'] = msg.pdu12_power_supply_voltage_v
    sms_msg['pdu12_total_current_a'] = msg.pdu12_total_current_a
    sms_msg['pdu48_power_supply_voltage_v'] = msg.pdu48_power_supply_voltage_v
    sms_msg['pdu48_total_current_a'] = msg.pdu48_total_current_a
    return sms_msg

def RM_Status_01_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['rm_sector_flag'] = msg.rm_sector_flag
    sms_msg['rm_session_type'] = msg.rm_session_type
    sms_msg['rm_car_flag'] = msg.rm_car_flag
    sms_msg['rm_track_flag'] = msg.rm_track_flag
    return sms_msg

def Bad_Z_Accel_Body_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['bad_gz_body_front'] = msg.bad_gz_body_front
    sms_msg['bad_gz_body_rear'] = msg.bad_gz_body_rear
    return sms_msg

def DiagnosticWord_01_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['bms_starting_faild'] = msg.bms_starting_faild
    sms_msg['bms_timeout_error'] = msg.bms_timeout_error
    sms_msg['cba_fl_counter_error'] = msg.cba_fl_counter_error
    sms_msg['cba_fl_derating'] = msg.cba_fl_derating
    sms_msg['cba_fl_error'] = msg.cba_fl_error
    sms_msg['cba_fl_timeout_error'] = msg.cba_fl_timeout_error
    sms_msg['cba_fr_counter_error'] = msg.cba_fr_counter_error
    sms_msg['cba_fr_derating'] = msg.cba_fr_derating
    sms_msg['cba_fr_error'] = msg.cba_fr_error
    sms_msg['cba_fr_timeout_error'] = msg.cba_fr_timeout_error
    sms_msg['cba_rl_counter_error'] = msg.cba_rl_counter_error
    sms_msg['cba_rl_derating'] = msg.cba_rl_derating
    sms_msg['cba_rl_error'] = msg.cba_rl_error
    sms_msg['cba_rl_timeout_error'] = msg.cba_rl_timeout_error
    sms_msg['cba_rr_counter_error'] = msg.cba_rr_counter_error
    sms_msg['cba_rr_derating'] = msg.cba_rr_derating
    sms_msg['cba_rr_error'] = msg.cba_rr_error
    sms_msg['cba_rr_timeout_error'] = msg.cba_rr_timeout_error
    sms_msg['dcdc_starting_faild'] = msg.dcdc_starting_faild
    sms_msg['dcdc_timeout_error'] = msg.dcdc_timeout_error
    sms_msg['ecu_timeout_em_fault'] = msg.ecu_timeout_em_fault
    sms_msg['dem_cbafl_not_receive'] = msg.dem_cbafl_not_receive
    sms_msg['ice_gear_low_oil_temp_warning'] = msg.ice_gear_low_oil_temp_warning
    sms_msg['ice_engine_off_rejected'] = msg.ice_engine_off_rejected
    sms_msg['dem_pdu12_v_not_receive'] = msg.dem_pdu12_v_not_receive
    sms_msg['ice_starting_fueling_failed'] = msg.ice_starting_fueling_failed
    sms_msg['ice_starting_oil_heater_failed'] = msg.ice_starting_oil_heater_failed
    sms_msg['ice_starting_starting_failed'] = msg.ice_starting_starting_failed
    sms_msg['ice_aps_warning'] = msg.ice_aps_warning
    sms_msg['hl_counter_error'] = msg.hl_counter_error
    sms_msg['hl_timeout_error'] = msg.hl_timeout_error
    sms_msg['ice_counter_error'] = msg.ice_counter_error
    sms_msg['ice_timeout_error'] = msg.ice_timeout_error
    sms_msg['dem_cbafr_not_receive'] = msg.dem_cbafr_not_receive
    sms_msg['ice_oil_temp_under_min_start_limit'] = msg.ice_oil_temp_under_min_start_limit
    sms_msg['pdu12_counter_error'] = msg.pdu12_counter_error
    sms_msg['pdu12_timeout_error'] = msg.pdu12_timeout_error
    sms_msg['pdu48_counter_error'] = msg.pdu48_counter_error
    sms_msg['pdu48_timeout_error'] = msg.pdu48_timeout_error
    sms_msg['dem_cbarl_not_receive'] = msg.dem_cbarl_not_receive
    sms_msg['psa_counter_error'] = msg.psa_counter_error
    sms_msg['psa_derating'] = msg.psa_derating
    sms_msg['psa_error'] = msg.psa_error
    sms_msg['psa_timeout_error'] = msg.psa_timeout_error
    sms_msg['dem_cbarr_not_receive'] = msg.dem_cbarr_not_receive
    sms_msg['em_stop_conditions_active'] = msg.em_stop_conditions_active
    sms_msg['ml_stop_conditions_active'] = msg.ml_stop_conditions_active
    sms_msg['dcdc4812_under_min_start_limit'] = msg.dcdc4812_under_min_start_limit
    sms_msg['ice_override_wrong_config'] = msg.ice_override_wrong_config
    sms_msg['bsu_wrong_init_config'] = msg.bsu_wrong_init_config
    sms_msg['ice_boost_warning'] = msg.ice_boost_warning
    sms_msg['ice_coolant_pressure_warning'] = msg.ice_coolant_pressure_warning
    sms_msg['ice_coolant_temperature_warning'] = msg.ice_coolant_temperature_warning
    sms_msg['ice_fuel_pressure_warning'] = msg.ice_fuel_pressure_warning
    sms_msg['ice_gear_oil_temperature_warning'] = msg.ice_gear_oil_temperature_warning
    sms_msg['ice_oil_pressure_warning'] = msg.ice_oil_pressure_warning
    sms_msg['ice_oil_temperature_warning'] = msg.ice_oil_temperature_warning
    sms_msg['pdu12_active_anti_fire'] = msg.pdu12_active_anti_fire
    sms_msg['ice_sensor_failure_warning'] = msg.ice_sensor_failure_warning
    sms_msg['ice_target_gear_not_reached_warning'] = msg.ice_target_gear_not_reached_warning
    sms_msg['ice_fuel_volume_warning'] = msg.ice_fuel_volume_warning
    sms_msg['rm_counter_error'] = msg.rm_counter_error
    sms_msg['rm_timeout_error'] = msg.rm_timeout_error
    sms_msg['psa_steer_slip_warning'] = msg.psa_steer_slip_warning
    return sms_msg

def DiagnosticWord_02_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['rc_force_race_mode'] = msg.rc_force_race_mode
    sms_msg['rc_beacon_time_out'] = msg.rc_beacon_time_out
    sms_msg['display_timeout_error'] = msg.display_timeout_error
    sms_msg['rm_red_flag'] = msg.rm_red_flag
    sms_msg['rm_safe_stop'] = msg.rm_safe_stop
    sms_msg['display_counter_error'] = msg.display_counter_error
    sms_msg['cba_em_brake_sat_def_val'] = msg.cba_em_brake_sat_def_val
    sms_msg['cba_sat_values_def_val'] = msg.cba_sat_values_def_val
    sms_msg['ice_oil_temp_start_limit_def_val'] = msg.ice_oil_temp_start_limit_def_val
    sms_msg['ml_stop_brake_sat_def_val'] = msg.ml_stop_brake_sat_def_val
    sms_msg['psa_sat_values_def_val'] = msg.psa_sat_values_def_val
    sms_msg['limp_cba_sat_values_def_val'] = msg.limp_cba_sat_values_def_val
    sms_msg['fan_car_speed_max_value_def_val'] = msg.fan_car_speed_max_value_def_val
    sms_msg['fan_car_speed_min_value_def_val'] = msg.fan_car_speed_min_value_def_val
    sms_msg['fan_water_temp_max_value_def_val'] = msg.fan_water_temp_max_value_def_val
    sms_msg['fan_water_temp_min_value_def_val'] = msg.fan_water_temp_min_value_def_val
    sms_msg['heater_oil_temp_max_value_def_val'] = msg.heater_oil_temp_max_value_def_val
    sms_msg['ice_fuel_pres_start_limit_def_val'] = msg.ice_fuel_pres_start_limit_def_val
    sms_msg['ice_oil_temp_by_pass_def_val'] = msg.ice_oil_temp_by_pass_def_val
    sms_msg['psa_sat_rates_def_val'] = msg.psa_sat_rates_def_val
    sms_msg['cba_sat_rates_def_val'] = msg.cba_sat_rates_def_val
    sms_msg['limp_ice_sat_values_def_val'] = msg.limp_ice_sat_values_def_val
    sms_msg['ml_stop_brake_bias_def_val'] = msg.ml_stop_brake_bias_def_val
    sms_msg['rm_em_flag'] = msg.rm_em_flag
    sms_msg['badenia_counter_error'] = msg.badenia_counter_error
    sms_msg['badenia_timeout_error'] = msg.badenia_timeout_error
    sms_msg['bms12_soc_under_level1'] = msg.bms12_soc_under_level1
    sms_msg['bms12_soc_under_level2'] = msg.bms12_soc_under_level2
    sms_msg['bms12_temp_over_level1'] = msg.bms12_temp_over_level1
    sms_msg['bms12_temp_over_level2'] = msg.bms12_temp_over_level2
    sms_msg['bms48_soc_under_level1'] = msg.bms48_soc_under_level1
    sms_msg['bms48_soc_under_level2'] = msg.bms48_soc_under_level2
    sms_msg['bms48_temp_over_level1'] = msg.bms48_temp_over_level1
    sms_msg['bms48_temp_over_level2'] = msg.bms48_temp_over_level2
    sms_msg['hl_m_lsupervisor_request'] = msg.hl_m_lsupervisor_request
    sms_msg['rc_delta_timeout_lim_def_val'] = msg.rc_delta_timeout_lim_def_val
    sms_msg['p2_p_active_duration_def_val'] = msg.p2_p_active_duration_def_val
    sms_msg['p2_p_cooldown_duration_def_val'] = msg.p2_p_cooldown_duration_def_val
    sms_msg['p2_p_max_num_activation_def_val'] = msg.p2_p_max_num_activation_def_val
    return sms_msg

def Flag_Info_Output_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['led_status'] = msg.led_status
    sms_msg['free_running_counter'] = msg.free_running_counter
    sms_msg['spare1_0x7_c'] = msg.spare1_0x7_c
    sms_msg['spare2_0x7_c'] = msg.spare2_0x7_c
    sms_msg['sm_session_type'] = msg.sm_session_type
    sms_msg['sm_track_flag'] = msg.sm_track_flag
    sms_msg['sm_car_flag'] = msg.sm_car_flag
    sms_msg['crc_sm'] = msg.crc_sm
    return sms_msg

def Bad_Alive_2SMS(msg):
    sms_msg = def_msg('std_msgs::Null')
    sms_msg['timestamp'] = msg.timestamp.nanoseconds / 1e9
    sms_msg['bad_alive_badenia'] = msg.bad_alive_badenia
    return sms_msg

def transform_msg(topic, msg_type, timestamp, msg):
    sms_msg = None
    if msg_type == "sensor_msgs/msg/CompressedImage":
        img_data = np.frombuffer(msg.data, dtype=np.uint8)
        img_array = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
        sms_msg = def_msg('memory_msgs::RawImage')
        sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
        sms_msg['frame_id'] = msg.header.frame_id
        sms_msg['width'] = img_array.shape[1]
        sms_msg['height'] = img_array.shape[0]
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            sms_msg['encoding'] = "8UC3"
        elif len(img_array.shape) == 2 or (len(img_array.shape) == 3 and img_array.shape[2] == 1):
            sms_msg['encoding'] = "8UC1"
        else:
            assert False, "CompressedImage Dim Error: {}".format(img_array.shape)
        # print(sms_msg)
        sms_msg['raw'] = img_array
    elif msg_type == "sensor_msgs/msg/PointCloud2" and topic not in ["/offline_map", "/cloud_registered"]:
        pcl_array, field_info = pointcloud2_to_numpy(msg)
        sms_msg = def_msg('memory_msgs::PointCloud')
        sms_msg['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
        sms_msg['width'] = pcl_array.shape[1]
        sms_msg['height'] = pcl_array.shape[0]
        sms_msg['encoding'] = "32FC1"
        sms_msg['fields'] = field_info
        # print(sms_msg)
        sms_msg['raw'] = pcl_array
    elif msg_type == "a2rl_bs_msgs/msg/Localization":
        sms_msg = Localization2SMS(msg)
    elif msg_type == "a2rl_bs_msgs/msg/EgoState":
        sms_msg = EgoState2SMS(msg)
    elif msg_type == "sensor_msgs/msg/Imu":
        sms_msg = Imu2SMS(msg)
    elif msg_type == "geometry_msgs/msg/PoseWithCovarianceStamped":
        sms_msg = PoseWithCovarianceStamped2SMS(msg)
    elif msg_type == "geometry_msgs/msg/TwistWithCovarianceStamped":
        sms_msg = TwistWithCovarianceStamped2SMS(msg)
    elif msg_type == "geometry_msgs/msg/PoseStamped":
        sms_msg = PoseStamped2SMS(msg)
    elif msg_type == "geometry_msgs/msg/Vector3Stamped":
        sms_msg = Vector3Stamped2SMS(msg)
    elif msg_type == "nav_msgs/msg/Odometry":
        sms_msg = Odometry2SMS(msg)
    elif msg_type == "std_msgs/msg/Bool":
        sms_msg = Bool2SMS(msg, timestamp)
    elif msg_type == "std_msgs/msg/Int16":
        sms_msg = Number2SMS(msg, timestamp)
    elif msg_type == "std_msgs/msg/Float32MultiArray":
        sms_msg = NumberMultiArray2SMS(msg, timestamp)
    elif msg_type == "tf2_msgs/msg/TFMessage":
        sms_msg = TFMessage2SMS(msg, timestamp)
    elif msg_type == "vectornav_msgs/msg/CommonGroup":
        sms_msg = VectornavCommonGroup2SMS(msg)
    elif msg_type == "vectornav_msgs/msg/ImuGroup":
        sms_msg = VectornavImuGroup2SMS(msg)
    elif msg_type == "vectornav_msgs/msg/InsGroup":
        sms_msg = VectornavIns2SMS(msg)
    elif msg_type == "vectornav_msgs/msg/TimeGroup":
        pass
    elif msg_type == "vectornav_msgs/msg/GpsGroup":
        sms_msg = VectornavGpsGroup2SMS(msg)
    elif msg_type == "vectornav_msgs/msg/AttitudeGroup":
        sms_msg = VectornavAttitudeGroup2SMS(msg)
    elif msg_type == "a2rl_bs_msgs/msg/ControllerStatus":
        sms_msg = ControllerStatus2SMS(msg)
    elif msg_type == "a2rl_bs_msgs/msg/ControllerBrake":
        sms_msg = ControllerBrake2SMS(msg)
    elif msg_type == "a2rl_bs_msgs/msg/ControllerGearStatus":
        sms_msg = ControllerGearStatus2SMS(msg)
    elif msg_type == "a2rl_bs_msgs/msg/ControllerDebug":
        sms_msg = ControllerDebug2SMS(msg)
    elif msg_type == "a2rl_bs_msgs/msg/ModuleStatusReport":
        pass
    elif msg_type == "a2rl_bs_msgs/msg/ReferencePath":
        pass
    elif msg_type == "a2rl_bs_msgs/msg/SensorStatus":
        sms_msg = SensorStatus2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/Kistler":
        # 地速传感器
        sms_msg = Kistler2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/KistlerStatus":
        # 地速传感器
        sms_msg = KistlerStatus2SMS(msg)
    elif msg_type.startswith("eav25_bsu_msgs/msg/Kistler_"):
        # 地速传感器
        pass
    elif msg_type == "eav25_bsu_msgs/msg/HL_Msg_04":
        # /flyeagle/a2rl/eav25_bsu/hl_msg_04，vectornav反馈数据
        sms_msg = HL_Msg_04_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/HL_Msg_05":
        # /flyeagle/a2rl/eav25_bsu/hl_msg_05，vectornav反馈数据
        sms_msg = HL_Msg_05_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/ICE_Status_01":
        # /flyeagle/a2rl/eav25_bsu/ice_status_01，动力单元信息
        sms_msg = ICE_Status_01_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/ICE_Status_02":
        # /flyeagle/a2rl/eav25_bsu/ice_status_02，动力单元信息
        sms_msg = ICE_Status_02_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/Tyre_Surface_Temp_Rear":
        # /flyeagle/a2rl/eav25_bsu/tyre_surface_temp_rear，胎温监测
        sms_msg = Tyre_Surface_Temp_Rear_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/Tyre_Surface_Temp_Front":
        # /flyeagle/a2rl/eav25_bsu/tyre_surface_temp_front，胎温监测
        sms_msg = Tyre_Surface_Temp_Front_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/Brake_Disk_Temp":
        # /flyeagle/a2rl/eav25_bsu/brake_disk_temp，刹车盘温度监测
        sms_msg = Brake_Disk_Temp_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/PSA_Status_01":
        # /flyeagle/a2rl/eav25_bsu/psa_status_01，转向机构信息
        sms_msg = PSA_Status_01_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/PSA_Status_02":
        # /flyeagle/a2rl/eav25_bsu/psa_status_02，转向机构信息
        sms_msg = PSA_Status_02_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/Wheels_Speed_01":
        # /flyeagle/a2rl/eav25_bsu/wheels_speed_01，轮速
        sms_msg = Wheels_Speed_01_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/BSU_Status_01":
        # /flyeagle/a2rl/eav25_bsu/bsu_status_01，BSU状态
        sms_msg = BSU_Status_01_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/EM_Status_01":
        # /flyeagle/a2rl/eav25_bsu/em_status_01，紧急停车状态
        sms_msg = EM_Status_01_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/Bad_Wheel_Load":
        # /flyeagle/a2rl/eav25_bsu/bad_wheel_load，轮胎载荷
        sms_msg = Bad_Wheel_Load_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/Tpms_Rear":
        # /flyeagle/a2rl/eav25_bsu/tpms_rear，胎压监测
        sms_msg = Tpms_Rear_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/Tpms_Front":
        # /flyeagle/a2rl/eav25_bsu/tpms_front，胎压监测
        sms_msg = Tpms_Front_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/PIT_Packet_0":
        # /flyeagle/a2rl/eav25_bsu/pit_packet_0，皮托管数据
        sms_msg = PIT_Packet_0_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/PIT_Packet_1":
        # /flyeagle/a2rl/eav25_bsu/pit_packet_1，皮托管数据
        sms_msg = PIT_Packet_1_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/CBA_Status_FL":
        # /flyeagle/a2rl/eav25_bsu/cba_status_fl，刹车数据
        sms_msg = CBA_Status_FL_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/CBA_Status_FR":
        # /flyeagle/a2rl/eav25_bsu/cba_status_fr，刹车数据
        sms_msg = CBA_Status_FR_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/CBA_Status_RL":
        # /flyeagle/a2rl/eav25_bsu/cba_status_rl，刹车数据
        sms_msg = CBA_Status_RL_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/CBA_Status_RR":
        # /flyeagle/a2rl/eav25_bsu/cba_status_rr，刹车数据
        sms_msg = CBA_Status_RR_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/Bad_Ride_Rear":
        # /flyeagle/a2rl/eav25_bsu/bad_ride_rear，悬架状态
        sms_msg = Bad_Ride_Rear_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/Bad_Ride_Front":
        # /flyeagle/a2rl/eav25_bsu/bad_ride_front，悬架状态
        sms_msg = Bad_Ride_Front_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/RM_Status_01":
        # /flyeagle/a2rl/eav25_bsu/rm_status_01，旗语
        sms_msg = RM_Status_01_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/Bad_Z_Accel_Body":
        # /flyeagle/a2rl/eav25_bsu/bad_z_accel_body，Z轴G值
        sms_msg = Bad_Z_Accel_Body_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/DiagnosticWord_01":
        # /flyeagle/a2rl/eav25_bsu/diagnostic_word_01，底层诊断信息
        sms_msg = DiagnosticWord_01_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/DiagnosticWord_02":
        # /flyeagle/a2rl/eav25_bsu/diagnostic_word_02，底层诊断信息
        sms_msg = DiagnosticWord_02_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/PDUs_Status_01":
        # /flyeagle/a2rl/eav25_bsu/pd_us_status_01，电源状态
        sms_msg = PDUs_Status_01_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/Bad_Misc":
        # /flyeagle/a2rl/eav25_bsu/bad_misc，Lap信息
        sms_msg = Bad_Misc_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/Flag_Info_Output":
        # /flyeagle/a2rl/eav25_bsu/flag_info_output，车辆状态监控
        sms_msg = Flag_Info_Output_2SMS(msg)
    elif msg_type == "eav25_bsu_msgs/msg/Bad_Alive":
        sms_msg = Bad_Alive_2SMS(msg)
    else:
        # print(msg_type)
        pass
    return sms_msg


def concat_meta_info(meta_info_sub, meta_info):
    for key, val in meta_info_sub.items():
        if key not in meta_info:
            meta_info[key] = val
        else:
            if key == 'message_count':
                meta_info['message_count'] += val
            elif key == 'duration':
                meta_info['duration'] += val
            elif key == 'topics_with_message_count':
                for skey, sval in val.items():
                    if skey not in meta_info['topics_with_message_count']:
                        meta_info['topics_with_message_count'][skey] = sval
                    else:
                        meta_info['topics_with_message_count'][skey]['message_count'] += sval['message_count']
    return meta_info


def ros2bag_to_smsbag(ros2bag_path, smsbag_dir):
    total_count = get_bag_total_count_from_metadata(ros2bag_path)
    print("Message Count:", total_count)
    # 创建读取器
    reader = rosbag2_py.SequentialReader()
    
    # 配置读取器（指定bag路径和存储格式）
    storage_options = rosbag2_py.StorageOptions(uri=ros2bag_path, storage_id='sqlite3')
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format='cdr',
        output_serialization_format='cdr'
    )
    reader.open(storage_options, converter_options)
    
    # 获取bag中的所有话题信息
    topic_types = reader.get_all_topics_and_types()
    # 创建话题到消息类型的映射（用于反序列化）
    type_map = {topic.name: topic.type for topic in topic_types}
    """
    for k, v in type_map.items():
        print(k, v)
    """
    # return 0

    last_timestamp = 0
    sub_name = ''
    sub_dir = ''
    jsonl_fp = None
    fp_dict = {}
    save_name = None
    version = 2
    meta_info_sub = {}
    meta_info = {}
    ts = 0.0
    # 遍历所有消息
    msg_count = 0
    start_time = time.time()
    attr_errors = []
    while reader.has_next():
        topic, data, timestamp = reader.read_next()
        msg_count += 1
        try:
            # 获取消息类型
            msg_type = get_message(type_map[topic])
        except Exception as e:
            e = str(e)
            if e not in attr_errors:
                attr_errors.append(e)
                print(Fore.YELLOW + "\n[WARN]: " + e + Style.RESET_ALL)
            continue

        # 反序列化消息
        msg = deserialize_message(data, msg_type)

        assert timestamp >= last_timestamp
        last_timestamp = timestamp
        ts = timestamp / 1e9
        local_time = time.localtime(ts)
        # 格式化结构化时间为指定字符串格式
        if save_name is None:
            save_name = os.path.join(smsbag_dir, "smsbag_" + time.strftime("%Y-%m-%d_%H-%M-%S", local_time))
            print('SmsBag: ' + save_name)
        time_min = time.strftime("%Y-%m-%d_%H-%M", local_time)

        # 打印消息信息（根据需要处理）
        if total_count > 0:
            progress_bar_with_time(msg_count, total_count, start_time)
        # print(f"Topic: {topic}, Timestamp: {timestamp}, Message: {msg}")
        # print(f"Topic: {topic}, Type: {msg_type}, Timestamp: {timestamp}")
        sms_msg = transform_msg(topic, type_map[topic], timestamp, msg)
        if sms_msg is not None:
            sms_msg['url'] = topic
            sms_msg['timerec'] = ts

            if sub_name != time_min:
                if jsonl_fp is not None:
                    jsonl_fp.close()

                if len(meta_info_sub) > 0:
                    meta_info_sub['duration'] = int(ts * 1000) - meta_info_sub['starting_time']
                    with open(os.path.join(sub_dir, "metadata.json"), "w", encoding="utf-8") as f:
                        json.dump(
                            meta_info_sub, 
                            f,
                            indent=4,           # 缩进空格数，使JSON更易读
                            ensure_ascii=False, # 保留非ASCII字符（如中文）
                            sort_keys=True      # 按键名排序
                        )
                    meta_info = concat_meta_info(meta_info_sub, meta_info)

                sub_name = time_min
                sub_dir = os.path.join(save_name, sub_name)
                if not os.path.exists(sub_dir):
                    os.makedirs(sub_dir)
                jsonl_fn = os.path.join(sub_dir, time_min + '.jsonl')
                jsonl_fp = open(jsonl_fn, "w", encoding="utf-8")
                for val in fp_dict.values():
                    val.close()

                meta_info_sub = {}
                meta_info_sub['intro'] = 'smsbag_bagfile_information'
                meta_info_sub['version'] = version
                meta_info_sub['starting_time'] = int(ts * 1000)
                meta_info_sub['topics_with_message_count'] = {}
                meta_info_sub['message_count'] = 0

            if sms_msg['url'] not in meta_info_sub['topics_with_message_count']:
                meta_info_sub['topics_with_message_count'][sms_msg['url']] = {
                    "type": sms_msg['type'],
                    "message_count": 1
                }
            else:
                meta_info_sub['topics_with_message_count'][sms_msg['url']]['message_count'] += 1
            meta_info_sub['message_count'] += 1

            if sms_msg['type'] == 'memory_msgs::RawImage':
                img = sms_msg['raw']
                bin_fn = os.path.join(sub_dir, sms_msg['url'].replace('/', '-') + '.bin')
                if not os.path.isfile(bin_fn):
                    fp_dict[sms_msg['url']] = open(bin_fn, 'wb')
                sms_msg['bin_n'] = sms_msg['url'].replace('/', '-') + '.bin'
                success, img_encoded = cv2.imencode('.jpg', img)
                img_encoded = img_encoded.tobytes()
                data_prefix = struct.pack('<IQ', int(len(img_encoded) + 12), int(sms_msg['timestamp'] * 1000))
                data = data_prefix + img_encoded
                fp_dict[sms_msg['url']].write(data)
                fp_dict[sms_msg['url']].flush()
                del sms_msg['raw']
            elif sms_msg['type'] == 'memory_msgs::PointCloud':
                pcl = sms_msg['raw']
                bin_fn = os.path.join(sub_dir, sms_msg['url'].replace('/', '-') + '.bin')
                if not os.path.isfile(bin_fn):
                    fp_dict[sms_msg['url']] = open(bin_fn, 'wb')
                sms_msg['bin_n'] = sms_msg['url'].replace('/', '-') + '.bin'
                pcl = pcl.tobytes()
                data_prefix = struct.pack('<IQ', int(len(pcl) + 12), int(sms_msg['timestamp'] * 1000))
                data = data_prefix + pcl
                fp_dict[sms_msg['url']].write(data)
                fp_dict[sms_msg['url']].flush()
                del sms_msg['raw']

            # print(sms_msg)
            jsonl_fp.write(json.dumps(sms_msg) + '\n')
            jsonl_fp.flush()

    if jsonl_fp is not None:
        jsonl_fp.close()

    if len(meta_info_sub) > 0 and ts > 0:
        meta_info_sub['duration'] = int(ts * 1000) - meta_info_sub['starting_time']
        with open(os.path.join(sub_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(
                meta_info_sub, 
                f,
                indent=4,           # 缩进空格数，使JSON更易读
                ensure_ascii=False, # 保留非ASCII字符（如中文）
                sort_keys=True      # 按键名排序
            )
        meta_info = concat_meta_info(meta_info_sub, meta_info)

    if save_name is not None:
        with open(os.path.join(save_name, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(
                meta_info, 
                f,
                indent=4,           # 缩进空格数，使JSON更易读
                ensure_ascii=False, # 保留非ASCII字符（如中文）
                sort_keys=True      # 按键名排序
            )


def main():
    parser = argparse.ArgumentParser(description="ROS2Bag -> SMSBag 转换程序")
    parser.add_argument(
        '-r', '--ros2-bag',
        type=str,
        default='',
        help='待转换的ros2bag路径'
    )
    parser.add_argument(
        '-s', '--sms-bag',
        type=str,
        default='',
        help='输出smsbag的父路径'
    )
    args = parser.parse_args()

    print("Input ROS2Bag_Path: {}".format(args.ros2_bag))
    print("Output SMSBag_Dir : {}".format(args.sms_bag))

    if not os.path.isdir(args.ros2_bag):
        print("ROS2Bag不存在")
        exit(1)

    if len(args.sms_bag) > 0 and not os.path.isdir(args.sms_bag):
        print("SMSBag_Dir不存在")
        exit(1)

    ros2bag_path = args.ros2_bag
    smsbag_dir = args.sms_bag
    ros2bag_to_smsbag(ros2bag_path, smsbag_dir)


if __name__ == "__main__":
    main()
