#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn
# @Date  : 2025-08-29


import threading
import time
import cv2
import os
import platform
import argparse
from typing import Union
import numpy as np
from spirems import Publisher, cvimg2sms, def_msg, BaseNode, get_extra_args


class BaseTestCaseNode(threading.Thread, BaseNode):
    def __init__(
        self,
        job_name: str,
        ip: str = '127.0.0.1',
        port: int = 9094,
        param_dict_or_file: Union[dict, str] = None,
        **kwargs
    ):
        threading.Thread.__init__(self)
        BaseNode.__init__(
            self,
            self.__class__.__name__,
            job_name,
            ip=ip,
            port=port,
            param_dict_or_file=param_dict_or_file,
            **kwargs
        )

        self.f_param = self.get_param("f_param", 1.0, "Float parameter.")
        self.i_param = self.get_param("i_param", 2)
        self.b_param = self.get_param("b_param", True)
        self.s_param = self.get_param("s_param", "str")
        self.d_param = self.get_param("d_param", {'num': 12})
        self.l_param = self.get_param("l_param", [1, 2, 3])
        self.t_param = self.get_param("t_param", (4, 5, 6))
        self.n_param = self.get_param("n_param", None, "None Type Demo")
        # self.np_param = self.get_param("np_param", np.array([7, 8, 9]))
        # self.o_param = self.get_param("o_param", self)
        self.params_help()

        self.start()

    def release(self):
        BaseNode.release(self)

    def run(self):
        while self.is_running():
            time.sleep(1)

        self.release()
        print('{} quit!'.format(self.__class__.__name__))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config',
        type=str,
        default='default_params.json',
        help='SpireCV2 Config (.json)')
    parser.add_argument(
        '--job-name',
        type=str,
        default='live',
        help='SpireCV Job Name')
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
    # args = parser.parse_args()
    args, unknown_args = parser.parse_known_args()
    if not os.path.isabs(args.config):
        current_path = os.path.abspath(__file__)
        params_dir = os.path.join(current_path[:current_path.find('spirems-pro') + 11], 'scripts')
        args.config = os.path.join(params_dir, args.config)
    print("--config:", args.config)
    print("--job-name:", args.job_name)
    extra = get_extra_args(unknown_args)

    node = BaseTestCaseNode(args.job_name, param_dict_or_file=args.config, ip=args.ip, port=args.port, **extra)
    node.spin()

