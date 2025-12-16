#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn
# @Date  : 2024-08-06

from spirems.subscriber import Subscriber
from spirems.publisher import Publisher
from spirems.parameter import Parameter
from spirems.msg_helper import def_msg
from spirems.log2sms import Logger
from spirems.error_code import sms_error, sms_warn
import os
import sys
import json
import time
from typing import Union


def bar_character_processing(s: str) -> str:
    if len(s) > 2 and s.startswith("--"):
        s = s.replace("-", "_")
        s = s[2:]
    elif len(s) > 1 and s.startswith("-"):
        s = s[1:]
    return s


def get_extra_args(unknown_args: list):
    extra = {}
    to_del = set()
    for i, arg in enumerate(unknown_args):
        equal_arg = arg.split('=')
        if len(equal_arg) == 2 and len(equal_arg[0]) > 0 and len(equal_arg[1]) > 0:
            key = bar_character_processing(equal_arg[0])
            extra[key] = equal_arg[1]
            to_del.add(i)
    for i in sorted(to_del, reverse=True):
        del unknown_args[i]

    if len(unknown_args) % 2 == 0:
        for i in range(0, len(unknown_args), 2):
            key = unknown_args[i]
            key = bar_character_processing(key)
            value = unknown_args[i + 1]
            extra[key] = value
    elif len(unknown_args) == 1 and unknown_args[0] in ['-p', 'show-params', '--show-params']:
        extra['show_params'] = True
    return extra


def update_parameter_dict(json_params: dict, node_name: str, job_name: str, **kwargs):
    n_name = '/' + node_name + '/'
    r_name = '/' + node_name + '_' + job_name + '/'
    g_name = '/_global/'
    dict_params = dict()
    for param_key, param_val in json_params.items():
        if param_key.startswith(n_name):
            param_key = param_key[len(n_name):]
            if param_key not in kwargs:
                dict_params.update({param_key: param_val})
        if param_key.startswith(r_name):
            param_key = param_key[len(r_name):]
            if param_key not in kwargs:
                dict_params.update({param_key: param_val})
        if param_key.startswith(g_name):
            param_key = '/' + param_key[len(g_name):]
            dict_params.update({param_key: param_val})
    return dict_params


def load_parameter_file(parameter_file: str, node_name: str, job_name: str, **kwargs):
    assert os.path.isfile(parameter_file) and parameter_file.endswith('.json'), \
        "The input parameter_file must be a JSON file."
    with open(parameter_file, 'r') as f:
        json_params = json.load(f)
    dict_params = update_parameter_dict(json_params, node_name, job_name, **kwargs)
    return dict_params


def parse_json_str(s: str):
    try:
        r = json.loads(s)
        return r
    except json.decoder.JSONDecodeError as e:
        sms_error("Cannot parse JSON str: \"{}\"".format(s))
        raise e
    return None


def param_type_convert(param_name: str, default: any, comein: any):
    default_tp = type(default)
    if isinstance(default, list) or isinstance(default, dict):
        if isinstance(comein, str):
            comein = parse_json_str(comein)
    elif isinstance(default, tuple):
        if isinstance(comein, str):
            comein = parse_json_str(comein)
            if type(comein) == list:
                comein = tuple(comein)
            else:
                sms_error("Cannot convert {}='{}' to <class 'tuple'>".format(param_name, comein))
                raise ValueError
    elif isinstance(default, bool):
        if comein in [True, 'True', 'true', '1']:
            comein = True
        elif comein in [False, 'False', 'false', '0']:
            comein = False
    elif isinstance(default, int):
        if isinstance(comein, str):
            try:
                comein = default_tp(comein)
            except ValueError as e:
                try:
                    comein = float(comein)
                    default_tp = type(comein)
                    sms_warn("Convert {}={} <int> to {}={} <float>".format(param_name, default, param_name, comein))
                except ValueError as e:
                    sms_error("Cannot convert {}='{}' to <class 'int'> or <class 'float'>".format(param_name, comein))
                    raise e
        elif isinstance(comein, float):
            default_tp = type(comein)
            sms_warn("Convert {}={} <int> to {}={} <float>".format(param_name, default, param_name, comein))
    elif isinstance(default, float):
        if isinstance(comein, str):
            try:
                comein = default_tp(comein)
            except ValueError as e:
                sms_error("Cannot convert {}='{}' to {}".format(param_name, comein, default_tp))
                raise e
        if isinstance(comein, int):
            comein = default_tp(comein)
    elif default is None:
        if comein == 'None':
            comein = None
        elif type(comein) in [list, dict, tuple, int, float, bool, str]:
            default_tp = type(comein)

    if type(comein) != default_tp:
        sms_error("{}={}, but your input is {}".format(param_name, default_tp, type(comein)))
        raise TypeError
    return comein


class BaseNode:
    def __init__(
        self,
        node_name: str,
        job_name: str,
        ip: str = '127.0.0.1',
        port: int = 9094,
        param_dict_or_file: Union[dict, str] = None,
        multi_instance_node: bool = True,
        sms_shutdown: bool = False,
        sms_logger: bool = False,
        **kwargs
    ):
        self._shutdown = False
        self.node_name = node_name
        self.job_name = job_name
        self._ip = ip
        self._port = port
        self._kwargs = kwargs
        # print(self._kwargs)
        self.queue_pool = []
        if multi_instance_node:
            self._param_server = Parameter(
                node_name + "_" + job_name,
                self.params_changed,
                ip=ip,
                port=port
            )
        else:
            self._param_server = Parameter(
                node_name,
                self.params_changed,
                ip=ip,
                port=port
            )
        self.sms_shutdown  = sms_shutdown
        if self.sms_shutdown and len(self.job_name):
            self._shutdown_reader = Subscriber(
                '/' + self.job_name + '/shutdown',
                'std_msgs::Boolean',
                self._shutdown_callback,
                ip=ip,
                port=port
            )
        if param_dict_or_file:
            if isinstance(param_dict_or_file, str):
                dict_params = load_parameter_file(param_dict_or_file, self.node_name, self.job_name, **kwargs)
                if len(dict_params):
                    self._param_server.set_params(dict_params)
            elif isinstance(param_dict_or_file, dict):
                dict_params = update_parameter_dict(param_dict_or_file, self.node_name, self.job_name, **kwargs)
                if len(dict_params):
                    self._param_server.set_params(dict_params)
        self.param_notes = {}
        self.sms_logger = sms_logger
        if self.sms_logger:
            self.logger = Logger(node_name + "_" + job_name)

    def params_help(self, info: bool = True):
        if 'show_params' in self._kwargs and self._kwargs['show_params']:
            for key, val in self._param_server.sync_params.items():
                if not key.startswith('/'):
                    print("  \033[32m{}\033[0m = {}, \033[33m{}\033[0m".format(key, val, self.param_notes[key] if key in self.param_notes else ""))
            print("quitting ...")
            self._param_server.kill()
            if self.sms_shutdown and len(self.job_name):
                self._shutdown_reader.kill()
            if self.sms_logger:
                self.logger.quit()
            sys.exit()
        elif info:
            for key, val in self._param_server.sync_params.items():
                if not key.startswith('/'):
                    print("  \033[32m{}\033[0m = {}".format(key, val))
            print("starting ...")
    
    def set_param(self, param_name: str, param_val: any):
        self._param_server.set_param(param_name, param_val)
        setattr(self, param_name, param_val)
        return param_val

    def get_param(self, param_name: str, default: any, note: str = "") -> any:
        self.param_notes[param_name] = note
        if param_name in self._param_server.sync_params:
            if param_name in self._kwargs:
                param_val = self._kwargs[param_name]
                param_val = param_type_convert(param_name, default, param_val)
                self._param_server.set_param(param_name, param_val)
                return param_val
            else:
                return self._param_server.sync_params[param_name]
        else:
            if param_name in self._kwargs:
                param_val = self._kwargs[param_name]
                param_val = param_type_convert(param_name, default, param_val)
                self._param_server.set_param(param_name, param_val)
                return param_val
            else:
                self._param_server.set_param(param_name, default)
                return default

    def release(self):
        if self.sms_shutdown:
            self._shutdown_reader.kill()
        if self.sms_logger:
            self.logger.quit()
        self._param_server.kill()

    def shutdown(self):
        self._shutdown = True
        for q in self.queue_pool:
            q.put(None)

    def emit_shutdown(self):
        if len(self.job_name):
            shutdown_writer = Publisher(
                '/' + self.job_name + '/shutdown', 'std_msgs::Boolean',
                ip=self._ip, port=self._port
            )
            msg = def_msg('std_msgs::Boolean')
            msg['data'] = True
            shutdown_writer.publish(msg)
            shutdown_writer.kill()

    def is_running(self) -> bool:
        return not self._shutdown

    def _shutdown_callback(self, msg):
        if msg['data']:
            self.shutdown()

    def params_changed(self, params):
        member_variables = dir(self)
        for param_key, param_val in params.items():
            if param_key in member_variables:
                setattr(self, param_key, param_val)
            global_key = param_key.replace('/', 'g_')
            if global_key in member_variables:
                setattr(self, global_key, param_val)

    def spin(self):
        try:
            while self.is_running():
                time.sleep(1)
        except KeyboardInterrupt:
            # 捕获 Ctrl+C 后的处理逻辑
            print("\nCtrl+C detected, exiting program")
            self.shutdown()


if __name__ == '__main__':
    bn = BaseNode(
        'COCODatasetLoaderNode',
        'EvalJob',
        param_dict_or_file=r'C:\deep\SpireCV\params\spirecv2\default_params.json'
    )
