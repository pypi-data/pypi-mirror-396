#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn
# @Date  : 2025-06-16

import os
import json
import struct
import json
import time
import re
import shutil
import math
from enum import Enum
import pathlib
import requests
from tqdm import tqdm
from spirems.log import get_logger


def download_model_rw(node_name: str, model_name: str):
    if model_name.startswith("sms::"):
        model_name = model_name[5:]
    url = "http://59.110.144.11/download/spirecv/" + node_name + "/" + model_name
    local_dir = os.path.join(pathlib.Path.home(), ".sms", node_name)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    local_fn = os.path.join(local_dir, model_name)
    local_fn_tmp = local_fn + ".downloading"

    err = 0
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        content_type = response.headers.get('Content-Type', '')
        if content_type not in ["application/octet-stream", "video/mp4"]:
            raise Exception("[DownloadServer]: Model does not exist")
        response = requests.get(url, stream=True, timeout=10)
        total_size = int(response.headers.get('Content-Length', 0))
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc="downloading")
        with open(local_fn_tmp, 'wb') as f:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                progress_bar.update(len(data))
    except requests.exceptions.HTTPError as e:
        print("HTTP Error")
        err= 1
    except requests.exceptions.ConnectionError:
        print("URL Connect Failed")
        err = 2
    except requests.exceptions.Timeout:
        print("Timeout")
        err = 3
    except requests.exceptions.RequestException as e:
        print("Request Error")
        err = 4
    except Exception as e:
        print(e)
        err = 5

    if 0 == err:
        os.rename(local_fn_tmp, local_fn)
        return local_fn
    else:
        return None


def download_model(node_name: str, model_name: str):
    assert len(node_name) > 0 and len(model_name) > 0
    if model_name.startswith("sms::"):
        model_name = model_name[5:]
    url = "http://59.110.144.11/download/spirecv/" + node_name + "/" + model_name
    local_dir = os.path.join(pathlib.Path.home(), ".sms", node_name)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    local_fn = os.path.join(local_dir, model_name)
    if not os.path.exists(local_fn):
        return download_model_rw(node_name, model_name)
    return local_fn


if __name__ == '__main__':
    fn = download_model("YOLOv11DetNode_Rknn", "a2a-c3_yolo11n_i512.pt")
    print(fn)
