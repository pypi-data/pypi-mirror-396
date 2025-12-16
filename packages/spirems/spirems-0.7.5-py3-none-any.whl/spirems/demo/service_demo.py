#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn


from spirems.client import Client
from spirems.msg_helper import get_all_msg_types, get_all_msg_schemas, get_all_foxglove_schemas, load_msg_types, def_msg
import argparse
import getpass
from colorama import init, Fore, Back, Style

# 初始化 colorama
# autoreset=True 表示每次打印后自动重置颜色，避免后续输出继承颜色
init(autoreset=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'cmd',
        type=str,
        default='',
        help='Command')
    parser.add_argument(
        '--ip',
        type=str,
        default='59.110.144.11',
        help='SpireMS Core IP')
    parser.add_argument(
        '--port',
        type=int,
        default=9094,
        help='SpireMS Core Port')
    args, unknown_args = parser.parse_known_args()

    print(Fore.GREEN + "Your Device_ID is: " + Fore.YELLOW + "{}".format(args.cmd))
    passwd = getpass.getpass(prompt=Fore.GREEN + "Enter Your Password:")

    cc = Client("/service_serial", "std_msgs::String", "std_msgs::String", ip=args.ip, port=args.port)
    req = def_msg("std_msgs::String")
    req["data"] = "{}:{}".format(passwd, args.cmd)
    response = cc.request(req)

    if response is not None and "data" in response and response["data"] != "Hello!":
        print(Fore.GREEN + "Your License:")
        print(response["data"])
    else:
        print(Fore.RED + "ERROR!")
    cc.kill()


if __name__ == '__main__':
    main()
