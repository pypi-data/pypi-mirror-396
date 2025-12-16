#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn
# @Date  : 2024-07-08

import socket
import time

from spirems.msg_helper import (encode_msg, decode_msg, get_all_msg_types, def_msg, check_msg,
                                index_msg_header, decode_msg_header, print_table)
import sys
import argparse
import json
from spirems.subscriber import Subscriber
from spirems.client import Client


def version():
    import spirems
    print(spirems.__version__)


def _echo(topic, ip, port):
    def _parse_msg(msg):
        formatted_str = json.dumps(msg, indent=4)
        print(formatted_str)

    sub = Subscriber(topic, 'std_msgs::Null', _parse_msg, ip=ip, port=port)
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print('stopped by keyboard')
        sub.kill()
        # sub.join()


t1 = 0
t2 = 0
t3 = 0
min_dt = 1e6
max_dt = 0
cnt = 0


def _hz(topic, ip, port):
    def _parse_msg(msg):
        global t1, t2, t3, min_dt, max_dt, cnt
        cnt += 1
        if t1 == 0:
            t1 = time.time()
            t2 = t1
            t3 = t1
            cnt = 0
        else:
            dt = time.time() - t1
            if dt < min_dt:
                min_dt = dt
            if dt > max_dt:
                max_dt = dt
            t1 = time.time()
            if t1 - t2 > 2:
                t2 = t1
                print("Average Rate: {:.2f}, Max Time Interval: {:.1f} ms, Min Time Interval: {:.1f} ms".format(
                    cnt / (t1 - t3), max_dt * 1000, min_dt * 1000
                ))

    sub = Subscriber(topic, 'std_msgs::Null', _parse_msg, ip=ip, port=port)
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print('stopped by keyboard')
        sub.kill()
        # sub.join()


def _list_v2(ip, port, url=None):
    client = Client(
        '/system/service',
        'std_msgs::String',
        'std_msgs::StringMultiArray',
        ip=ip,
        port=port,
        request_once=True
    )
    req = def_msg('std_msgs::String')
    req['data'] = 'topic list'
    results = client.request_once(req)
    if 'data' in results:
        if url is None:
            print_table(results['data'])
        else:
            columns = results['data'][0]
            for r in results['data'][1:]:
                if r[0] == url:
                    for i, c in enumerate(r):
                        print("\033[32m{}\033[0m:".format(columns[i]))
                        print("  {}".format(c))


def _list(ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(5)
    client_socket.connect((ip, port))

    client_socket.send(encode_msg(def_msg('_sys_msgs::SmsTopicList')))
    columns = ['Topics', 'Type', 'Subscribed-by']

    def _parse_msg(res):
        success, decode_data = decode_msg(res)
        topics = []
        if decode_data['type'] == '_sys_msgs::Result':
            data = decode_data['data'].split(';')
            for t in data:
                url_type = t.split(',')
                topics.append(url_type)
            if len(topics) > 0 and len(topics[0]) == 3:
                max_widths1 = [max(len(str(d[i])) for d in topics) for i in range(len(columns))]
                max_widths2 = [len(d) for d in columns]
                max_widths = [max(w1, w2) for w1, w2 in zip(max_widths1, max_widths2)]
            else:
                max_widths = [len(d) for d in columns]
                topics = []
            for i, column in enumerate(columns):
                print(f'| {column:>{max_widths[i]}} ', end='')
            print('|')
            for row in topics:
                for i, value in enumerate(row):
                    print(f'| {value:>{max_widths[i]}} ', end='')
                print('|')
            return True
        return False

    last_data = b''
    big_msg = 0
    while True:
        try:
            data = client_socket.recv(4096)
            recv_msgs = []
            checked_msgs, parted_msgs, parted_lens = check_msg(data)

            if len(parted_msgs) > 0:
                for parted_msg, parted_len in zip(parted_msgs, parted_lens):
                    if parted_len > 0:
                        last_data = parted_msg
                        big_msg = parted_len
                    else:
                        last_data += parted_msg
                        if 0 < big_msg <= len(last_data):
                            recv_msgs.append(last_data[:big_msg])
                            big_msg = 0
                            last_data = b''

            recv_msgs.extend(checked_msgs)
            if len(recv_msgs) > 0:
                _quit = False
                for msg in recv_msgs:
                    if _parse_msg(msg):
                        _quit = True
                        break
                if _quit:
                    break

        except Exception as e:
            print(e)
            break


def _check(ip, port):
    from spirems.msg_helper import QoS, Rate
    from spirems.publisher import Publisher
    from spirems.image_io.adaptor import cvimg2sms, sms2cvimg
    import platform
    import numpy as np
    b_use_shm = False
    if platform.system() in ['Linux', 'Darwin']:
        b_use_shm = True
    image_writer = Publisher(
        '/check/sensor/image_raw', 'memory_msgs::RawImage' if b_use_shm else 'sensor_msgs::CompressedImage',
        ip=ip, port=port
    )

    r = Rate(30)
    while True:
        try:
            height, width = 480, 640
            # 生成均值 128，标准差 50 的正态分布数组
            mean = 128
            std = 50
            noise_gaussian = np.random.normal(mean, std, (height, width)).astype(np.int16)
            # 截断到 [0, 255] 并转换为 uint8
            noise_gaussian = np.clip(noise_gaussian, 0, 255).astype(np.uint8)
            if b_use_shm:
                msg = image_writer.cvimg2sms_mem(noise_gaussian)
            else:
                msg = cvimg2sms(noise_gaussian)
            image_writer.publish(msg)
            r.sleep()
        except KeyboardInterrupt:
            print("Ctrl+C detected, exiting program ...")
            image_writer.kill()
            break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'cmd',
        nargs='+',
        help='Your Command (list, ls, hz, echo, check)')
    parser.add_argument(
        '--ip',
        type=str,
        default='127.0.0.1',
        help='SpireMS Core IP')
    parser.add_argument(
        '--port',
        type=int,
        default=9094,
        help='SpireMS Core Port')
    args = parser.parse_args()
    # print(args.ip)
    # print(args.port)
    # print(args.cmd)
    if args.cmd[0] in ['ls', 'list', 'hz', 'echo', 'check']:
        if 'list' == args.cmd[0] or 'ls' == args.cmd[0]:
            _list_v2(args.ip, args.port, url=args.cmd[1] if len(args.cmd) > 1 and len(args.cmd[1]) > 0 else None)
        elif 'echo' == args.cmd[0]:
            assert len(args.cmd) > 1, "Usage: sms echo [topic_url]"
            _echo(args.cmd[1], args.ip, args.port)
        elif 'hz' == args.cmd[0]:
            assert len(args.cmd) > 1, "Usage: sms hz [topic_url]"
            _hz(args.cmd[1], args.ip, args.port)
        elif 'check' == args.cmd[0]:
            _check(args.ip, args.port)
    else:
        print('[ERROR] Supported command: list, ls, hz, echo, check')


if __name__ == '__main__':
    main()
