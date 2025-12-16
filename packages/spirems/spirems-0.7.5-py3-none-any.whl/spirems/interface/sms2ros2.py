#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn
# @Date  : 2025-03-26

import socket
import time
import threading
from spirems.msg_helper import (encode_msg, decode_msg, get_all_msg_types, def_msg, check_msg,
                                index_msg_header, decode_msg_header, print_table)
import sys
import os
import argparse
import json
from queue import Queue
from spirems.subscriber import Subscriber
from spirems.publisher import Publisher
from spirems.client import Client
from spirems import sms2cvimg, sms2pcl, cvimg2sms
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


topics_to_trans = [
    'memory_msgs::RawImage',
    'memory_msgs::PointCloud',
    'sensor_msgs::CompressedImage',
    'std_msgs::String'
]


class ROS2ImgPub(Node):
    def __init__(self, node_name, url):
        super().__init__(node_name)
        self.publisher_ = self.create_publisher(Image, url, 10)
        self.bridge = CvBridge()

    def pub(self, img):
        msg = self.bridge.cv2_to_imgmsg(img, "bgr8")
        current_time = self.get_clock().now()
        msg.header.stamp = current_time.to_msg()
        self.publisher_.publish(msg)


class SMS2ROS(threading.Thread):
    def __init__(
        self,
        ip: str = '127.0.0.1',
        port: int = 9094
    ):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.client = Client(
            '/system/service',
            'std_msgs::String',
            'std_msgs::StringMultiArray',
            ip=self.ip,
            port=self.port,
            request_once=False
        )

        record_urls, record_types = self.topic_list()
        self.queue = Queue()
        self.readers = []
        self.urls = []
        print("Subscribe:")
        for url_, type_ in zip(record_urls, record_types):
            reader_ = Subscriber(
                url_, 'std_msgs::Null', lambda msg, url=url_: self.queue.put({'msg': msg, 'url': url, 'raw': sms2cvimg(msg) if msg['type'] == 'memory_msgs::RawImage' else sms2pcl(msg)}) if msg['type'] in ['memory_msgs::RawImage', 'memory_msgs::PointCloud'] else self.queue.put({'msg': msg, 'url': url}),
                ip=self.ip, port=self.port
            )
            print('  ' + url_)
            self.readers.append(reader_)
            self.urls.append(url_)

        self.is_running = True
        self.ros2_node_idx = 0
        self.ros2_urls = []
        self.ros2_nodes = []
        self.topic_thread = threading.Thread(target=self.topic_update_run)
        self.topic_thread.start()
        self.start()

    def topic_update_run(self):
        while self.is_running:
            # print('topic_update_run')
            time.sleep(2)
            # t1 = time.time()
            record_urls, record_types = self.topic_list()
            # print('topic_update_run', time.time() - t1)
            for url_, type_ in zip(record_urls, record_types):
                if url_ not in self.urls:
                    reader_ = Subscriber(
                        url_, 'std_msgs::Null', lambda msg, url=url_: self.queue.put({'msg': msg, 'url': url, 'raw': sms2cvimg(msg) if msg['type'] == 'memory_msgs::RawImage' else sms2pcl(msg)}) if msg['type'] in ['memory_msgs::RawImage', 'memory_msgs::PointCloud'] else self.queue.put({'msg': msg, 'url': url}),
                        ip=self.ip, port=self.port
                    )
                    print('  ' + url_)
                    self.readers.append(reader_)
                    self.urls.append(url_)

    def release(self):
        self.is_running = False
        self.queue.put(None)
        for reader_ in self.readers:
            reader_.kill()
        for node_ in self.ros2_nodes:
            node_.destroy_node()

    def run(self):
        while self.is_running:
            try:
                msg = self.queue.get(block=True)
                if msg is None:
                    break

                msg['msg']['url'] = msg['url']
                if msg['msg']['type'] == 'memory_msgs::RawImage':
                    img = msg['raw']
                    if msg['msg']['url'] not in self.ros2_urls:
                        node = ROS2ImgPub('ImgPub_{}'.format(self.ros2_node_idx), msg['msg']['url'])
                        self.ros2_nodes.append(node)
                        self.ros2_urls.append(msg['msg']['url'])
                        self.ros2_node_idx += 1
                    idx = self.ros2_urls.index(msg['msg']['url'])
                    node = self.ros2_nodes[idx]
                    node.pub(img)
                    
                elif msg['msg']['type'] == 'memory_msgs::PointCloud':
                    pcl = msg['raw']

                elif msg['msg']['type'] == 'sensor_msgs::CompressedImage':
                    img = sms2cvimg(msg['msg'])
                    if msg['msg']['url'] not in self.ros2_urls:
                        node = ROS2ImgPub('ImgPub_{}'.format(self.ros2_node_idx), msg['msg']['url'])
                        self.ros2_nodes.append(node)
                        self.ros2_urls.append(msg['msg']['url'])
                        self.ros2_node_idx += 1
                    idx = self.ros2_urls.index(msg['msg']['url'])
                    node = self.ros2_nodes[idx]
                    node.pub(img)

                elif msg['msg']['type'] == 'std_msgs::String':
                    print(msg['msg'])
                    
            except Exception as e:
                print(e)
                self.is_running = False

        self.release()

    def topic_list(self):
        req = def_msg('std_msgs::String')
        req['data'] = 'topic list'
        results = self.client.request(req)
        record_urls, record_types = [], []
        if 'data' in results:
            if len(results['data']) > 1:
                available_topics = results['data'][1:]
                # print(available_topics)
                for t in available_topics:
                    if t[1] in topics_to_trans:
                        record_urls.append(t[0])
                        record_types.append(t[1])
            else:
                print("There are no topics available to subscribe to.")
        return record_urls, record_types


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--ip',
        type=str,
        default='127.0.0.1',
        help='SpireMS Core IP.')
    parser.add_argument(
        '--port',
        type=int,
        default=9094,
        help='SpireMS Core Port.')
    args = parser.parse_args()
    rclpy.init(args=None)
    node = SMS2ROS(args.ip, args.port)
    node.join()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
