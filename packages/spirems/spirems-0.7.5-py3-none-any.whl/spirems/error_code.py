#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn
# @Date  : 2024-07-08

from spirems.msg_helper import get_all_msg_types, def_msg
from colorama import Fore


ERROR_CODE_BOOK = {
    101: "Topic parsing error.",
    201: "topic_url wrong, at least 2 chars.",
    202: "topic_url wrong, need started with '/'.",
    203: "topic_url wrong, only to use 'a-z', '0-9', '_' or '/'.",
    204: "topic_url wrong, as the same as the existing.",
    205: "The topic_type you specified does not exist, please check the spelling or add the type to the msgs.",
    206: "Publisher/Subscriber does not include the topic_type and url fields.",
    207: "Uploaded unregistered topic.",
    208: "The topic type uploaded does not match the registered topic type.",
    209: "Cannot register as both a publisher and a subscriber.",
    210: "node_name wrong, at least 2 chars.",
    211: "node_name wrong, only to use 'a-z', '0-9' or '_'.",
    212: "Parameter does not include the node_name field.",
    213: "Cannot register Parameter with a publisher or a subscriber.",
    214: "node_name wrong, already exists.",
    215: "The current parameter node is not registered.",
    216: "node_name wrong, cannot start with '_'.",
    217: "param_key wrong, at least 2 chars.",
    218: "param_key wrong, only to use 'a-z', '0-9' or '_', except for the first '/'.",
    219: "param_key wrong, cannot start with '_'.",
    220: "global_param_key wrong, at least 6 chars.",
    221: "global_param_key wrong, only to use 'a-z', '0-9', '_' or '/'.",
    222: "global_param_key wrong, should start with '/'.",
    223: "_global param node cannot create new parameters, only update parameters.",
    224: "Service/Client does not include request_type, response_type and url fields.",
    225: "Cannot register as both a service and a client.",
    226: "service_url wrong, as the same as the existing.",
    227: "The request_type/response_type you specified does not exist, please check the spelling or add the type to the msgs.",
    228: "Request/Response by unregistered client.",
    229: "The request/response type does not match the registered request/response type.",
    230: "Cannot publish a topic with the same registered url but a different type.",
    231: "Cannot subscribe a topic with the same registered url but a different type.",
    232: "Cannot request a topic with the same registered url but a different type.",
    240: "Please check the topic_type returned in your callback, as it does not match the definition.",
    300: "The send queue is full, data loss occurred, please check the sending frequency.",
    501: "When the topic type != memory_msgs::, calling cvimg2sms_mem will return a null value."
}


def ec2msg(ec: int) -> dict:
    msg = def_msg('_sys_msgs::Result')
    msg['error_code'] = ec
    msg['data'] = ERROR_CODE_BOOK[ec]
    return msg


def ec2str(ec: int) -> str:
    return ERROR_CODE_BOOK[ec]


def sms_info(msg: str):
    print(Fore.GREEN + "[INFO] {}".format(msg) + Fore.RESET)


def sms_warn(msg: str):
    print(Fore.YELLOW + "[WARN] {}".format(msg) + Fore.RESET)


def sms_error(msg: str):
    print(Fore.RED + "[ERROR] {}".format(msg) + Fore.RESET)


def sms_debug(msg: str):
    print(Fore.WHITE + "[DEBUG] {}".format(msg) + Fore.RESET)
