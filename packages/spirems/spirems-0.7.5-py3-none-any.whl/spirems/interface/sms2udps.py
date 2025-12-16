#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
import threading
import socket
import json
import argparse
import sys
from queue import Queue
from spirems import Subscriber
from spirems.msg_helper import check_topic_url
from spirems.error_code import ec2str


class SMS2UDPServerNode(threading.Thread):
    def __init__(
        self,
        specified_input_topic: str,
        udp_ip: str = "0.0.0.0",
        udp_port: int = 9870,
        ip: str = '127.0.0.1',
        port: int = 9094
    ):
        threading.Thread.__init__(self)
        self.specified_input_topic = specified_input_topic
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.queue = Queue()
        self._reader = Subscriber(
            specified_input_topic, 'std_msgs::Null', self.callback,
            ip=ip, port=port
        )
        self.is_running = True
        self.start()
    
    def release(self):
        self.is_running = False
        self.queue.put(None)
        self._reader.kill()

    def callback(self, msg):
        self.queue.put(msg)

    def send(self, json_str: str):
        try:
            json_data = json.dumps(json_str).encode('utf-8')
            self.sock.sendto(json_data, (self.udp_ip, self.udp_port))
        except:
            self.sock.close()
    
    def run(self):
        while self.is_running:
            msg = self.queue.get(block=True)
            if msg is None:
                break

            self.send(msg)
        self.release()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_topic',
        help='SpireMS Topic URL.')
    parser.add_argument(
        '-i', '--udp-ip',
        type=str,
        default="0.0.0.0",
        help='UDP Server port.')
    parser.add_argument(
        '-p', '--udp-port',
        type=int,
        default=9870,
        help='UDP Server port.')
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

    print("input-topic:", args.input_topic)
    error_code = check_topic_url(args.input_topic)
    if error_code != 0:
        sys.exit(ec2str(error_code))

    print("udp-ip:", args.udp_ip)
    print("udp-port:", args.udp_port)
    print("sms-ip:", args.ip)
    print("sms-port:", args.port)

    node = SMS2UDPServerNode(
        args.input_topic,
        args.udp_ip,
        args.udp_port,
        args.ip,
        args.port
    )


if __name__ == '__main__':
    main()
