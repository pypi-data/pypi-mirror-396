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
from spirems import sms2cvimg, sms2pcl, cvimg2sms, sms2tensor, tensor2sms
import cv2
import numpy as np
import struct
from pathlib import Path
nvjpeg_on = False
try:
    from nvjpeg import NvJpeg
    nj = NvJpeg()
    nvjpeg_on = True
    # print("NVJPEG ON")
except Exception as e:
    # pip install pynvjpeg
    # print("NVJPEG OFF")
    pass


def read_pcd(pcd_path):
    header = {}
    with open(pcd_path, 'rb') as f:
        for line in f:
            line = line.decode('utf-8').strip()
            if line.startswith("DATA"):
                header["DATA"] = line.split()[1]
                break
            if line:
                key, val = line.split(' ', 1)
                header[key] = val

        width = int(header["WIDTH"])
        height = int(header["HEIGHT"])
        fields = header["FIELDS"].split()
        size = list(map(int, header["SIZE"].split()))
        count = list(map(int, header["COUNT"].split()))
        dtype = header["TYPE"].split()
        point_size = sum(s * c for s, c in zip(size, count))
        num_points = width * height

        data = f.read()
        if header["DATA"] == "binary":
            dt = np.dtype([(f, np.float32) for f in fields])
            arr = np.frombuffer(data, dtype=dt, count=num_points)
            return arr.view(np.float32).reshape(num_points, -1)
        else:
            raise NotImplementedError("only support binary")


def save_pcd_binary(filename, points, fields=['x', 'y', 'z']):
    """
    将NumPy数组保存为二进制格式的PCD文件
    :param filename: 文件名（如：'cloud.pcd'）
    :param points: NumPy数组，形状为(N, 3)，数据类型建议为float32
    """
    # print(fields)
    # print(points.shape)
    header = [
        "# .PCD v0.7 - Point Cloud Data file format",
        "VERSION 0.7",
        f"FIELDS {' '.join(fields)}",
        f"SIZE {' '.join('4' for f in fields)}",
        f"TYPE {' '.join('F' for f in fields)}",
        f"COUNT {' '.join('1' for f in fields)}",
        f"WIDTH {len(points)}",
        "HEIGHT 1",
        "VIEWPOINT 0 0 0 1 0 0 0",
        f"POINTS {len(points)}",
        f"DATA binary\n"
    ]
    header = '\n'.join(header)
    # print(header)
    with open(filename, 'wb') as f:
        f.write(header.encode('ascii'))
        assert points.dtype == np.float32
        f.write(np.ascontiguousarray(points, dtype=np.float32).tobytes())
        # np.savetxt(f, points, fmt='%.6f %.6f %.6f')


class SMSBagRecorder(threading.Thread):
    def __init__(
        self,
        record_urls: list,
        record_types: list,
        save_path: str = '',
        ip: str = '127.0.0.1',
        port: int = 9094,
        multi_file_for_nparr: bool = False,
        version: int = 2,
        nvjpeg: bool = False,
        use_png: bool = False
    ):
        threading.Thread.__init__(self)
        self.record_urls = record_urls
        self.record_types = record_types
        self.save_path = save_path
        self.ip = ip
        self.port = port
        self.multi_file_for_nparr = multi_file_for_nparr
        # self.version = 1 if multi_file_for_nparr else 2
        self.version = version
        self.nvjpeg = nvjpeg
        self.use_png = use_png
        self.nvjpeg_err = False
        self.meta_info_sub = {}
        self.meta_info = {}
        self.get_ctrl_c = False

        self.queue = Queue()
        self.readers = []
        print("Subscribe:")
        for url_, type_ in zip(record_urls, record_types):
            reader_ = Subscriber(
                url_, 'std_msgs::Null', lambda msg, url=url_: self.queue.put({'msg': msg, 'url': url, 'rec': time.time(), 'raw': sms2cvimg(msg) if msg['type'] == 'memory_msgs::RawImage' else (sms2pcl(msg) if msg['type'] == 'memory_msgs::PointCloud' else sms2tensor(msg))}) if msg['type'] in ['memory_msgs::RawImage', 'memory_msgs::PointCloud', 'memory_msgs::Tensor'] else self.queue.put({'msg': msg, 'url': url, 'rec': time.time()}),
                ip=ip, port=port
            )
            print('  ' + url_)
            self.readers.append(reader_)

        self.is_running = True
        self.start()

    def release(self):
        if self.is_running:
            self.is_running = False
            self.queue.put(None)
            for reader_ in self.readers:
                reader_.kill()
    
    def ctrl_c(self):
        self.get_ctrl_c = True

    def concat_meta_info(self):
        for key, val in self.meta_info_sub.items():
            if key not in self.meta_info:
                self.meta_info[key] = val
            else:
                if key == 'message_count':
                    self.meta_info['message_count'] += val
                elif key == 'duration':
                    self.meta_info['duration'] += val
                elif key == 'topics_with_message_count':
                    for skey, sval in val.items():
                        if skey not in self.meta_info['topics_with_message_count']:
                            self.meta_info['topics_with_message_count'][skey] = sval
                        else:
                            self.meta_info['topics_with_message_count'][skey]['message_count'] += sval['message_count']

    def run(self):
        save_name = os.path.join(self.save_path, "smsbag_" + time.strftime("%Y-%m-%d_%H-%M-%S"))
        print('SmsBag: ' + save_name)
        sub_name = ''
        sub_dir = ''
        jsonl_fp = None
        fp_dict = {}
        while self.is_running:
            try:
                msg = self.queue.get(block=True)
                if msg is None:
                    break

                msg['msg']['url'] = msg['url']
                msg['msg']['timerec'] = msg['rec']

                time_min = time.strftime("%Y-%m-%d_%H-%M")
                if sub_name != time_min:
                    print("Storage pressure:", self.queue.qsize())
                    if jsonl_fp is not None:
                        jsonl_fp.close()

                    if len(self.meta_info_sub) > 0:
                        self.meta_info_sub['duration'] = int(time.time() * 1000) - self.meta_info_sub['starting_time']
                        with open(os.path.join(sub_dir, "metadata.json"), "w", encoding="utf-8") as f:
                            json.dump(
                                self.meta_info_sub, 
                                f,
                                indent=4,           # 缩进空格数，使JSON更易读
                                ensure_ascii=False, # 保留非ASCII字符（如中文）
                                sort_keys=True      # 按键名排序
                            )
                        self.concat_meta_info()

                    sub_name = time_min
                    sub_dir = os.path.join(save_name, sub_name)
                    os.makedirs(sub_dir)
                    jsonl_fn = os.path.join(sub_dir, time_min + '.jsonl')
                    jsonl_fp = open(jsonl_fn, "w", encoding="utf-8")
                    for val in fp_dict.values():
                        val.close()

                    self.meta_info_sub = {}
                    self.meta_info_sub['intro'] = 'smsbag_bagfile_information'
                    self.meta_info_sub['version'] = self.version
                    self.meta_info_sub['starting_time'] = int(time.time() * 1000)
                    self.meta_info_sub['topics_with_message_count'] = {}
                    self.meta_info_sub['message_count'] = 0

                if msg['url'] not in self.meta_info_sub['topics_with_message_count']:
                    self.meta_info_sub['topics_with_message_count'][msg['url']] = {
                        "type": msg['msg']['type'],
                        "message_count": 1
                    }
                else:
                    self.meta_info_sub['topics_with_message_count'][msg['url']]['message_count'] += 1
                self.meta_info_sub['message_count'] += 1

                if msg['msg']['type'] == 'memory_msgs::RawImage':
                    img = msg['raw']
                    if self.multi_file_for_nparr:
                        img_fn = os.path.join(sub_dir, msg['url'].replace('/', '-'))
                        # print(img_fn)
                        if not os.path.exists(img_fn):
                            os.makedirs(img_fn)
                        img_n = str(int(msg['msg']['timestamp'] * 1000)) + '.jpg'
                        msg['msg']['img_n'] = img_n
                        cv2.imwrite(os.path.join(img_fn, img_n), img)
                    else:
                        bin_fn = os.path.join(sub_dir, msg['url'].replace('/', '-') + '.bin')
                        if not os.path.isfile(bin_fn):
                            fp_dict[msg['url']] = open(bin_fn, 'wb')
                        msg['msg']['bin_n'] = msg['url'].replace('/', '-') + '.bin'
                        if self.nvjpeg:
                            if nvjpeg_on:
                                img_encoded = nj.encode(img)
                            else:
                                if not self.nvjpeg_err:
                                    self.nvjpeg_err = True
                                    print("NvJpeg is unavailable.")
                                success, img_encoded = cv2.imencode('.jpg', img)
                                img_encoded = img_encoded.tobytes()
                        else:
                            success, img_encoded = cv2.imencode('.png' if self.use_png else '.jpg', img)
                            img_encoded = img_encoded.tobytes()
                        data_prefix = struct.pack('<IQ', int(len(img_encoded) + 12), int(msg['msg']['timestamp'] * 1000))
                        data = data_prefix + img_encoded
                        fp_dict[msg['url']].write(data)
                        fp_dict[msg['url']].flush()
                elif msg['msg']['type'] == 'memory_msgs::PointCloud':
                    pcl = msg['raw']
                    if self.multi_file_for_nparr:
                        pcl_fn = os.path.join(sub_dir, msg['url'].replace('/', '-'))
                        # print(pcl_fn)
                        if not os.path.exists(pcl_fn):
                            os.makedirs(pcl_fn)
                        pcd_n = str(int(msg['msg']['timestamp'] * 1000)) + '.pcd'
                        msg['msg']['pcd_n'] = pcd_n
                        save_pcd_binary(os.path.join(pcl_fn, pcd_n), pcl, fields=msg['msg']['fields'])
                        # save_pcd_binary(os.path.join(pcl_fn, pcd_n), pcl[:, [1,2,3]], fields=['x', 'y', 'z'])
                    else:
                        bin_fn = os.path.join(sub_dir, msg['url'].replace('/', '-') + '.bin')
                        if not os.path.isfile(bin_fn):
                            fp_dict[msg['url']] = open(bin_fn, 'wb')
                        msg['msg']['bin_n'] = msg['url'].replace('/', '-') + '.bin'
                        pcl = pcl.tobytes()
                        data_prefix = struct.pack('<IQ', int(len(pcl) + 12), int(msg['msg']['timestamp'] * 1000))
                        data = data_prefix + pcl
                        fp_dict[msg['url']].write(data)
                        fp_dict[msg['url']].flush()
                elif msg['msg']['type'] == 'memory_msgs::Tensor':
                    tensor = msg['raw']
                    if self.multi_file_for_nparr:
                        tensor_fn = os.path.join(sub_dir, msg['url'].replace('/', '-'))
                        if not os.path.exists(tensor_fn):
                            os.makedirs(tensor_fn)
                        npy_n = str(int(msg['msg']['timestamp'] * 1000)) + '.npy'
                        msg['msg']['npy_n'] = npy_n
                        np.save(os.path.join(tensor_fn, npy_n), tensor)
                    else:
                        bin_fn = os.path.join(sub_dir, msg['url'].replace('/', '-') + '.bin')
                        if not os.path.isfile(bin_fn):
                            fp_dict[msg['url']] = open(bin_fn, 'wb')
                        msg['msg']['bin_n'] = msg['url'].replace('/', '-') + '.bin'
                        tensor = tensor.tobytes()
                        data_prefix = struct.pack('<IQ', int(len(tensor) + 12), int(msg['msg']['timestamp'] * 1000))
                        data = data_prefix + tensor
                        fp_dict[msg['url']].write(data)
                        fp_dict[msg['url']].flush()

                jsonl_fp.write(json.dumps(msg['msg']) + '\n')
                jsonl_fp.flush()

                if self.get_ctrl_c:
                    raise KeyboardInterrupt("Ctrl+C")
            except KeyboardInterrupt as e:
                print(e)
                if jsonl_fp is not None:
                    jsonl_fp.close()

                if len(self.meta_info_sub) > 0:
                    self.meta_info_sub['duration'] = int(time.time() * 1000) - self.meta_info_sub['starting_time']
                    with open(os.path.join(sub_dir, "metadata.json"), "w", encoding="utf-8") as f:
                        json.dump(
                            self.meta_info_sub, 
                            f,
                            indent=4,           # 缩进空格数，使JSON更易读
                            ensure_ascii=False, # 保留非ASCII字符（如中文）
                            sort_keys=True      # 按键名排序
                        )
                    self.concat_meta_info()

                with open(os.path.join(save_name, "metadata.json"), "w", encoding="utf-8") as f:
                    json.dump(
                        self.meta_info, 
                        f,
                        indent=4,           # 缩进空格数，使JSON更易读
                        ensure_ascii=False, # 保留非ASCII字符（如中文）
                        sort_keys=True      # 按键名排序
                    )
                self.release()
                break

        self.release()


def _record(
        topics, ip, port, 
        save_path='',
        version=2,
        nvjpeg=False,
        use_png=False
    ):
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
        if len(results['data']) > 1:
            available_topics = results['data'][1:]
            record_urls, record_types = [], []
            if topics is None:
                record_urls = [t[0] for t in available_topics]
                record_types = [t[1] for t in available_topics]
            else:
                for t1 in topics:
                    for t in available_topics:
                        if t1 == t[0]:
                            record_urls.append(t[0])
                            record_types.append(t[1])
            if len(record_urls) > 0:
                recorder = SMSBagRecorder(
                    record_urls, 
                    record_types, 
                    ip=ip, 
                    port=port, 
                    save_path=save_path,
                    multi_file_for_nparr=True if version == 1 else False,
                    version=version,
                    nvjpeg=nvjpeg,
                    use_png=use_png
                )
                try:
                    # recorder.join()
                    while recorder.is_running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("quitting ...")
                    recorder.ctrl_c()
            else:
                print("The topic you subscribed to does not exist.")
        else:
            print("There are no topics available to subscribe to.")


class SMSBagPlayer(threading.Thread):
    def __init__(
        self,
        smsbag_dir: str,
        ip: str = '127.0.0.1',
        port: int = 9094,
        loop: bool = False,
        to_publish: bool = False,
        queue_size: int = 2000
    ):
        threading.Thread.__init__(self)

        smsbag_dir = smsbag_dir.strip().rstrip('/')
        smsbag_name = os.path.basename(smsbag_dir)
        print("Now Playing:", smsbag_name)
        assert smsbag_name.startswith("smsbag_"), 'smsbag must be a folder and start with "smsbag_" (smsbag需要以"smsbag_"开头且是一个文件夹).'
        subdirs = sorted(
            [entry.name for entry in os.scandir(smsbag_dir) if entry.is_dir()],
            key=lambda x: x.lower()
        )
        assert len(subdirs) > 0, 'The number of subfolders in "smsbag" cannot be 0 (smsbag的子文件夹数量不能为0).'
        self.n_subdirs = len(subdirs)
        self.i_subdirs = 0

        smsbag_jsonls = []
        self.smsbag_dir = smsbag_dir
        self.smsbag_subdirs = subdirs
        self.bin_data_buff = {}
        self.bin_buff_size = 100
        self.del_buff = {}
        self.del_buff_size = 1000
        self.bin_lock = threading.Lock()

        for subdir in subdirs:
            jsonl_path = os.path.join(smsbag_dir, subdir, subdir + '.jsonl')
            if os.path.exists(jsonl_path) and os.path.isfile(jsonl_path):
                smsbag_jsonls.append(jsonl_path)

        self.smsbag_jsonls = smsbag_jsonls
        self.ip = ip
        self.port = port
        self.loop = loop
        self.first_msg = True
        self.version = 1
        self.get_ctrl_c = False

        self._publishers = dict()
        self.queue = Queue(maxsize=queue_size)
        self.is_loading = True
        self.is_bin_loading = True
        self.loop_once = False

        self.bin_loading_thread = threading.Thread(target=self.bin_loading)
        self.bin_loading_thread.start()
        time.sleep(1)

        self.loading_thread = threading.Thread(target=self.loading)
        self.loading_thread.start()
        self.is_running = True
        if to_publish:
            self.start()

    def load_svbin(self, bin_fns, bin_name):
        for bin_fn in bin_fns:
            if self.get_ctrl_c:
                break
            with open(bin_fn, 'rb') as f:
                bin_head = f.read(12)
                while len(bin_head) == 12:
                    bin_size, bin_stamp = struct.unpack('<IQ', bin_head)
                    bin_data = f.read(bin_size - 12)
                    if len(bin_data) == bin_size - 12:
                        try:
                            with self.bin_lock:
                                if bin_name not in self.bin_data_buff:
                                    self.bin_data_buff[bin_name] = {}
                                    self.del_buff[bin_name] = []
                            while self.is_bin_loading and len(self.bin_data_buff[bin_name]) > self.bin_buff_size:
                                time.sleep(0.001)
                            if self.is_bin_loading:
                                with self.bin_lock:
                                    self.bin_data_buff[bin_name][bin_stamp] = bin_data
                        except:
                            print("bin file corrupted, last data lost.")
                            break
                    else:
                        break
                    bin_head = f.read(12)

    def bin_loading(self):
        while self.is_loading and self.is_bin_loading:
            bin_name_fns = {}
            for subdir in self.smsbag_subdirs:
                folder = Path(os.path.join(self.smsbag_dir, subdir))
                for file in folder.rglob('*.bin'):
                    if file.is_file():
                        bin_name = str(os.path.basename(file))
                        if bin_name not in bin_name_fns:
                            bin_name_fns[bin_name] = []
                        bin_name_fns[bin_name].append(file)

            s_threads = []
            for bin_name in bin_name_fns.keys():
                s_thread = threading.Thread(target=self.load_svbin, args=(bin_name_fns[bin_name], bin_name))
                s_thread.start()
                s_threads.append(s_thread)

            for t in s_threads:
                t.join()

            if self.get_ctrl_c:
                break
            if not self.loop:
                self.is_bin_loading = False
            else:
                while not self.loop_once:
                    time.sleep(0.001)
                while not self.is_bin_loading:
                    time.sleep(0.001)
                    with self.bin_lock:
                        for k in self.bin_data_buff.keys():
                            self.bin_data_buff[k].clear()

        # print("bin_loading self.release()", self.queue.qsize())
    
    def get_progress(self):
        return self.i_subdirs / self.n_subdirs

    def loading(self):
        while self.is_loading:
            self.loop_once = False
            # remaining_data = []
            for i, smsbag_jsonl in enumerate(self.smsbag_jsonls):
                # parsed_data = []
                # print("i", i)
                self.i_subdirs = i

                with open(smsbag_jsonl, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            if 'timerec' in data:
                                self.version = 2
                            if data['type'].startswith('memory_msgs::'):
                                data['base_dir'] = str(os.path.dirname(smsbag_jsonl))
                            # parsed_data.append(data)

                            dict_put = {'msg': data}
                            data_exist = True
                            if data['type'] == 'memory_msgs::RawImage':
                                if 'img_n' in data:
                                    img_fn = os.path.join(data['base_dir'], data['url'].replace('/', '-'), data['img_n'])
                                    if os.path.exists(img_fn):
                                        img_raw = cv2.imread(img_fn, cv2.IMREAD_UNCHANGED)
                                        dict_put['raw'] = img_raw
                                    else:
                                        data_exist = False
                                elif 'bin_n' in data:
                                    bin_fn = os.path.join(data['base_dir'], data['bin_n'])
                                    time_ms = int(data['timestamp'] * 1000)
                                    if time_ms in self.del_buff[data['bin_n']]:
                                        continue
                                    while time_ms not in self.bin_data_buff[data['bin_n']] and not self.get_ctrl_c:
                                        time.sleep(0.001)
                                    if self.get_ctrl_c:
                                        break
                                    with self.bin_lock:
                                        raw_bytes = self.bin_data_buff[data['bin_n']][time_ms]
                                        del self.bin_data_buff[data['bin_n']][time_ms]
                                    self.del_buff[data['bin_n']].append(time_ms)
                                    if len(self.del_buff[data['bin_n']]) > self.del_buff_size:
                                        self.del_buff[data['bin_n']].pop(0)
                                    try:
                                        bin_data_np = np.frombuffer(raw_bytes, dtype='uint8')
                                        img_raw = cv2.imdecode(bin_data_np, cv2.IMREAD_UNCHANGED)
                                        dict_put['raw'] = img_raw
                                    except:
                                        print("[WARN]: Image Decode Error.")
                                        data_exist = False
                            elif data['type'] == 'memory_msgs::PointCloud':
                                if 'pcd_n' in data:
                                    pcd_fn = os.path.join(data['base_dir'], data['url'].replace('/', '-'), data['pcd_n'])
                                    if os.path.exists(pcd_fn):
                                        points_np = read_pcd(pcd_fn)
                                        dict_put['raw'] = points_np
                                    else:
                                        data_exist = False
                                elif 'bin_n' in data:
                                    time_ms = int(data['timestamp'] * 1000)
                                    if time_ms in self.del_buff[data['bin_n']]:
                                        continue
                                    while time_ms not in self.bin_data_buff[data['bin_n']] and not self.get_ctrl_c:
                                        time.sleep(0.001)
                                    if self.get_ctrl_c:
                                        break
                                    with self.bin_lock:
                                        raw_bytes = self.bin_data_buff[data['bin_n']][time_ms]
                                        del self.bin_data_buff[data['bin_n']][time_ms]
                                    self.del_buff[data['bin_n']].append(time_ms)
                                    if len(self.del_buff[data['bin_n']]) > self.del_buff_size:
                                        self.del_buff[data['bin_n']].pop(0)
                                    bin_data_np = np.frombuffer(raw_bytes, dtype='float32')
                                    bin_data_np = bin_data_np.reshape(data['height'], data['width'])
                                    dict_put['raw'] = bin_data_np
                            elif data['type'] == 'memory_msgs::Tensor':
                                if 'npy_n' in data:
                                    tensor_fn = os.path.join(data['base_dir'], data['url'].replace('/', '-'), data['npy_n'])
                                    if os.path.exists(tensor_fn):
                                        tensor_np = np.load(tensor_fn)
                                        dict_put['raw'] = tensor_np
                                    else:
                                        data_exist = False
                                elif 'bin_n' in data:
                                    time_ms = int(data['timestamp'] * 1000)
                                    if time_ms in self.del_buff[data['bin_n']]:
                                        continue
                                    while time_ms not in self.bin_data_buff[data['bin_n']] and not self.get_ctrl_c:
                                        time.sleep(0.001)
                                    if self.get_ctrl_c:
                                        break
                                    with self.bin_lock:
                                        raw_bytes = self.bin_data_buff[data['bin_n']][time_ms]
                                        del self.bin_data_buff[data['bin_n']][time_ms]
                                    self.del_buff[data['bin_n']].append(time_ms)
                                    if len(self.del_buff[data['bin_n']]) > self.del_buff_size:
                                        self.del_buff[data['bin_n']].pop(0)
                                    bin_data_np = np.frombuffer(raw_bytes, dtype=data['dtype'])
                                    bin_data_np = bin_data_np.reshape(*data['shape'])
                                    dict_put['raw'] = bin_data_np

                            if data_exist:
                                while self.queue.full() and not self.get_ctrl_c:
                                    time.sleep(0.01)
                                if self.get_ctrl_c:
                                    break
                                self.queue.put(dict_put, block=True, timeout=None)
                                # print("self.queue.qsize()", self.queue.qsize())
                        except json.JSONDecodeError:
                            print("File: {}, Line: {}, Parsing failed.")
                        if line_num % 100 == 0:
                            time.sleep(0.001)

                """
                parsed_data.extend(remaining_data)
                # print("version =", self.version)
                if self.version > 1:
                    parsed_data.sort(key=lambda x: x["timerec"])
                else:
                    parsed_data.sort(key=lambda x: x["timestamp"])

                if i != len(self.smsbag_jsonls) - 1:
                    rnum = int(len(parsed_data) / 2)
                    remaining_data = parsed_data[-rnum:]
                    parsed_data = parsed_data[:-rnum]
                else:
                    remaining_data = []
                """
                # for data in parsed_data:

            # print("self.loop", self.loop)
            if self.get_ctrl_c:
                break
            if not self.loop:
                self.is_loading = False
                self.is_bin_loading = False
                # print("self.is_loading", self.is_loading)
            else:
                while not self.queue.empty():
                    time.sleep(0.001)
                self.first_msg = True
                self.is_bin_loading = False
                self.loop_once = True
                n_bins = np.sum(np.array([len(v) for v in self.bin_data_buff.values()]))
                while n_bins > 0:
                    n_bins = np.sum(np.array([len(v) for v in self.bin_data_buff.values()]))
                    time.sleep(0.001)
                self.is_bin_loading = True
                time.sleep(1)

        # print("self.queue.size", self.queue.qsize())
        while not self.queue.empty() and not self.get_ctrl_c:
            time.sleep(1)

        # print("loading self.release()", self.queue.qsize())
        self.release()

    def release(self):
        if self.is_running:
            self.is_running = False
            self.is_loading = False
            self.is_bin_loading = False
            while not self.queue.empty():
                self.queue.get()
            self.queue.put(None)
            for url, pub in self._publishers.items():
                pub.kill()
            with self.bin_lock:
                for key in self.bin_data_buff.keys():
                    self.bin_data_buff[key].clear()

    def next(self):
        msg = self.queue.get(block=True)
        return msg
    
    def ctrl_c(self):
        self.get_ctrl_c = True

    def run(self):
        timestamp_base = 0.0
        self.first_msg = True
        while self.is_running:
            # print(self.queue.qsize())
            msg = self.queue.get(block=True)
            if msg is None:
                break

            if self.first_msg:
                self.first_msg = False
                timestamp_base = msg['msg']['timerec'] if self.version > 1 else msg['msg']['timestamp']
                timestamp_now = time.time()

            dt_now = time.time() - timestamp_now
            dt_base = msg['msg']['timerec'] - timestamp_base if self.version > 1 else msg['msg']['timestamp'] - timestamp_base
            while dt_now <= dt_base:
                time.sleep(0.001)
                dt_now = time.time() - timestamp_now
                dt_base = msg['msg']['timerec'] - timestamp_base if self.version > 1 else msg['msg']['timestamp'] - timestamp_base

            url = msg['msg']['url']
            if url not in self._publishers:
                self._publishers[url] = Publisher(url, msg['msg']['type'], self.ip, self.port)

            if msg['msg']['type'] == 'memory_msgs::RawImage':
                raw_msg = self._publishers[url].cvimg2sms_mem(msg['raw'], msg['msg']['frame_id'], msg['msg']['timestamp'])
                self._publishers[url].publish(raw_msg)
            elif msg['msg']['type'] == 'memory_msgs::PointCloud':
                raw_msg = self._publishers[url].pcl2sms_mem(msg['raw'], msg['msg']['fields'], msg['msg']['frame_id'], msg['msg']['timestamp'])
                self._publishers[url].publish(raw_msg)
            elif msg['msg']['type'] == 'memory_msgs::Tensor':
                raw_msg = tensor2sms(msg['raw'], url.replace('/', '_') + "_bagtensor", msg['msg']['frame_id'], msg['msg']['timestamp'])
                self._publishers[url].publish(raw_msg)
            else:
                self._publishers[url].publish(msg['msg'])
            
            # print("self.is_running", self.is_running, self.queue.qsize())
            if self.get_ctrl_c:
                break

        # print("run self.release()", self.queue.qsize())
        self.release()


def _play(
        smsbag_dir, ip, port, loop
    ):
    if not os.path.isdir(smsbag_dir):
        sys.exit("The SmsBag path ({}) does not exist.".format(smsbag_dir))

    player = SMSBagPlayer(smsbag_dir, ip, port, loop=loop, to_publish=True)
    try:
        # player.join()
        while player.is_loading:
            time.sleep(1)
    except KeyboardInterrupt:
        print("quitting ...")
        player.ctrl_c()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'cmd',
        nargs='+',
        help="Your Command (record, play, tomcap). "
             "1.record后面可以跟多个需要记录的话题且以空格隔开;"
             "2.play后面必须跟待播放的smsbag的地址;"
             "3.tomcap是一个mcap格式的GUI转换工具")
    parser.add_argument(
        '-s', '--save-path',
        type=str,
        default='',
        help='SmsBag saving path.')
    parser.add_argument(
        '-v', '--version',
        type=int,
        default=2,
        help='SmsBag version.')
    parser.add_argument(
        '-l', '--loop',
        action='store_true',
        help='Enables loop playback when playing a bagfile.')
    parser.add_argument(
        '--nvjpeg',
        action='store_true',
        help='Enables nvjpeg encoding when recording a bagfile.')
    parser.add_argument(
        '--png',
        action='store_true',
        help='Enables png encoding when recording a bagfile.')
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
    # print(args.ip)
    # print(args.port)
    # print(args.cmd)
    if len(args.save_path) > 0:
        if os.path.exists(args.save_path) and os.path.isdir(args.save_path):
            print("Save to {}.".format(args.save_path))
        else:
            sys.exit("The folder ({}) does not exist.".format(args.save_path))

    if args.cmd[0] in ['record', 'play', 'tomcap']:
        if 'play' == args.cmd[0]:
            assert len(args.cmd) > 1, "Usage: smsbag play [smsbag_dir]"
            _play(args.cmd[1], args.ip, args.port, loop=args.loop)
        elif 'record' == args.cmd[0]:
            topics = None
            if len(args.cmd) > 1:
                topics = args.cmd[1:]
            _record(topics, args.ip, args.port, save_path=args.save_path, version=args.version, nvjpeg=args.nvjpeg, use_png=args.png)
        elif 'tomcap' == args.cmd[0]:
            from spirems.interface.smsbag2mcap import AddressTransferApp
            import tkinter as tk
            root = tk.Tk()
            app = AddressTransferApp(root)
            root.mainloop()
    else:
        print('[ERROR] Supported command, use record, play, tomcap.')


if __name__ == '__main__':
    main()
