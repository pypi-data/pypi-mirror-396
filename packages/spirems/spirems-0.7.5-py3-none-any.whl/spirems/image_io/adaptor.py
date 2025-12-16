#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn
# @Date  : 2024-07-08

import time
import sys
current_os = sys.platform
if current_os.startswith('linux') or current_os.startswith('darwin'):
    try:
        from spirems.exts import csms_shm
    except Exception as e:
        pass

try:
    import cv2
except Exception as e:
    print('Cannot import cv2 (pip install opencv-python)')

try:
    import av
except Exception as e:
    pass

import numpy as np
import base64
from spirems.msg_helper import get_all_msg_types, def_msg
from spirems.publisher import Publisher

nvjpeg_on = False
configs = def_msg('_config_msgs::Default')
if configs['use_nvjpeg']:
    try:
        from nvjpeg import NvJpeg
        nj = NvJpeg()
        nvjpeg_on = True
        print("NVJPEG ON")
    except Exception as e:
        # pip install pynvjpeg
        # print("NVJPEG OFF")
        pass


def tensor2sms(tensor: np.ndarray, memory_url: str, frame_id: str = '', timestamp: float = 0.0) -> dict:
    sms_timestamp = timestamp if timestamp > 0 else time.time()
    sms_mem = {}
    tensor = np.ascontiguousarray(tensor)
    if tensor.dtype == 'int8':
        sms_mem = csms_shm.tensor2sms_int8(tensor, memory_url)
    elif tensor.dtype == 'int16':
        sms_mem = csms_shm.tensor2sms_int16(tensor, memory_url)
    elif tensor.dtype == 'int32':
        sms_mem = csms_shm.tensor2sms_int32(tensor, memory_url)
    elif tensor.dtype == 'int64':
        sms_mem = csms_shm.tensor2sms_int64(tensor, memory_url)
    elif tensor.dtype == 'uint8':
        sms_mem = csms_shm.tensor2sms_uint8(tensor, memory_url)
    elif tensor.dtype == 'uint16':
        sms_mem = csms_shm.tensor2sms_uint16(tensor, memory_url)
    elif tensor.dtype == 'uint32':
        sms_mem = csms_shm.tensor2sms_uint32(tensor, memory_url)
    elif tensor.dtype == 'uint64':
        sms_mem = csms_shm.tensor2sms_uint64(tensor, memory_url)
    elif tensor.dtype == 'float32':
        sms_mem = csms_shm.tensor2sms_float32(tensor, memory_url)
    elif tensor.dtype == 'float64':
        sms_mem = csms_shm.tensor2sms_float64(tensor, memory_url)
    else:
        assert False, "Unsupported sms::dtype ({})!".format(tensor.dtype)
    sms_mem["timestamp"] = sms_timestamp
    sms_mem["frame_id"] = frame_id
    return sms_mem


def sms2tensor(sms: dict) -> np.ndarray:
    assert sms['type'] == 'memory_msgs::Tensor'
    assert current_os.startswith('linux') or current_os.startswith('darwin'), "Memory sharing must be utilized within the Linux/MacOS operating system."
    if sms['dtype'] == 'int8':
        tensor = csms_shm.sms2tensor_int8(sms)
    elif sms['dtype'] == 'int16':
        tensor = csms_shm.sms2tensor_int16(sms)
    elif sms['dtype'] == 'int32':
        tensor = csms_shm.sms2tensor_int32(sms)
    elif sms['dtype'] == 'int64':
        tensor = csms_shm.sms2tensor_int64(sms)
    elif sms['dtype'] == 'uint8':
        tensor = csms_shm.sms2tensor_uint8(sms)
    elif sms['dtype'] == 'uint16':
        tensor = csms_shm.sms2tensor_uint16(sms)
    elif sms['dtype'] == 'uint32':
        tensor = csms_shm.sms2tensor_uint32(sms)
    elif sms['dtype'] == 'uint64':
        tensor = csms_shm.sms2tensor_uint64(sms)
    elif sms['dtype'] == 'float32':
        tensor = csms_shm.sms2tensor_float32(sms)
    elif sms['dtype'] == 'float64':
        tensor = csms_shm.sms2tensor_float64(sms)
    else:
        assert False, "Unsupported sms::dtype ({})!".format(sms['dtype'])
    return tensor


def cvimg2sms(img: np.ndarray, format: str = 'jpeg', frame_id: str = 'camera', timestamp: float = 0.0) -> dict:
    assert img.dtype == np.uint8, "CHECK img.dtype == np.uint8!"
    color_img = True
    if len(img.shape) == 3:
        assert img.shape[0] > 0 and img.shape[1] > 0, "CHECK img.H and W > 0!"
        assert img.shape[2] == 1 or img.shape[2] == 3, "CHECK img.shape[2] == 3 or 1!"
        if img.shape[2] == 1:
            color_img = False
            img = np.squeeze(img, axis=2)
        else:
            color_img = True
    elif len(img.shape) == 2:
        assert img.shape[0] > 0 and img.shape[1] > 0, "CHECK img.H and W > 0!"
        color_img = False
    else:
        assert False, "CHECK img.ndim == 3 or 2"

    if format in ['jpeg', 'jpg', 'png', 'webp']:
        sms = def_msg('sensor_msgs::CompressedImage')
    elif format in ['h264']:
        sms = def_msg('sensor_msgs::CompressedImage')
    else:
        assert False, "Format ({}) is not supported".format(format)

    if timestamp > 0:
        sms['timestamp'] = timestamp
    else:
        sms['timestamp'] = time.time()
    sms['frame_id'] = frame_id
    sms['format'] = format
    sms['is_color'] = 1 if color_img else 0

    # t1 = time.time()
    if sms['format'] in ['jpeg', 'jpg']:
        if nvjpeg_on and color_img:
            img_encoded = nj.encode(img)
        else:
            success, img_encoded = cv2.imencode('.jpg', img)
    elif sms['format'] == 'png':
        success, img_encoded = cv2.imencode('.png', img)
    elif sms['format'] == 'webp':
        success, img_encoded = cv2.imencode('.webp', img, [cv2.IMWRITE_WEBP_QUALITY, 50])
    elif sms['format'] == 'h264':
        av_img = av.VideoFrame.from_ndarray(img, format="rgb24")
        codec = av.CodecContext.create('h264', 'w')
        codec.pix_fmt = "yuv420p"
        codec.width = img.shape[1]
        codec.height = img.shape[0]
        packet = codec.encode(av_img)
        while not len(packet):
            packet = codec.encode()
        img_encoded = bytes(packet[0])
    else:
        assert False, "Format ({}) is not supported".format(format)
    # print("-- imencode: {}".format(time.time() - t1))
    """
    elif sms['format'] == 'uint8':
        img_encoded = img.tobytes()
    """

    # t1 = time.time()
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')
    # print("-- b64encode: {}".format(time.time() - t1))
    sms['data'] = img_base64

    return sms


def sms2cvimg(sms: dict) -> np.ndarray:
    assert sms['type'] == 'sensor_msgs::CompressedImage' or sms['type'] == 'memory_msgs::RawImage'

    if sms['type'] == 'sensor_msgs::CompressedImage':
        assert sms['format'] in ['jpeg', 'jpg', 'png', 'webp', 'h264']
        img_base64 = base64.b64decode(sms['data'])
        if sms['format'] in ['jpeg', 'jpg', 'png', 'webp']:
            img_encoded = np.frombuffer(img_base64, dtype='uint8')
            if nvjpeg_on and sms['format'] in ['jpeg', 'jpg'] and sms['is_color'] == 1:
                img = nj.decode(img_encoded)
            elif sms['is_color'] == 1:
                img = cv2.imdecode(img_encoded, cv2.IMREAD_COLOR)
            else:
                img = cv2.imdecode(img_encoded, cv2.IMREAD_GRAYSCALE)
        elif sms['format'] in ['h264']:
            packet = av.packet.Packet(img_base64)
            codec = av.CodecContext.create(sms['format'], "r")
            imgs = codec.decode(packet)
            while not len(imgs):
                imgs = codec.decode()
            img = imgs[0].to_ndarray(format='rgb24')
            codec.close()
        else:
            assert False, "Format ({}) is not supported".format(sms['format'])
        """
        elif sms['format'] == 'uint8':
            img = np.frombuffer(img_base64, dtype='uint8')
            img = img.reshape(sms['height'], sms['width'], sms['channel'])
        """
    else:
        assert current_os.startswith('linux') or current_os.startswith('darwin'), "Memory sharing must be utilized within the Linux/MacOS operating system."
        if sms['encoding'] in ['8UC1', '8UC2', '8UC3', '8UC4']:
            img = csms_shm.sms2cvimg_uint8(sms)
        elif sms['encoding'] in ['16UC1', '16UC2', '16UC3', '16UC4']:
            img = csms_shm.sms2cvimg_uint16(sms)
        elif sms['encoding'] in ['32FC1', '32FC2', '32FC3', '32FC4']:
            img = csms_shm.sms2cvimg_float(sms)
        else:
            assert False, "Unsupported sms::encoding type!"
        if sms['encoding'] in ['8UC1', '16UC1', '32FC1']:
            img = np.squeeze(img, axis=2)
    return img


def pcl2sms(
    pcl: np.ndarray, 
    fields: list = ['x', 'y', 'z'],
    position: list = [0, 0, 0],
    orientation: list = [0, 0, 0, 0],
    frame_id: str = 'lidar', 
    timestamp: float = 0.0
):    
    assert len(fields) == pcl.shape[1]
    assert pcl.dtype == np.float32 and pcl.ndim == 2
    if position is not None:
        assert len(position) == 3
    if orientation is not None:
        assert len(orientation) == 4

    sms = def_msg('sensor_msgs::PointCloud')
    sms['frame_id'] = frame_id
    if timestamp > 0:
        sms['timestamp'] = timestamp
    else:
        sms['timestamp'] = time.time()

    if position is not None:
        sms['pose']['position']['x'] = position[0]
        sms['pose']['position']['y'] = position[1]
        sms['pose']['position']['z'] = position[2]
    if orientation is not None:
        sms['pose']['orientation']['x'] = orientation[0]
        sms['pose']['orientation']['y'] = orientation[1]
        sms['pose']['orientation']['z'] = orientation[2]
        sms['pose']['orientation']['w'] = orientation[3]    
    if position is None and orientation is None:
        del sms['pose']

    sms['fields'] = []
    offset = 0
    for field in fields:
        sms['fields'].append({
            "name": field,
            "offset": offset,
            "type": 7
        })
        offset += 4
    
    sms['point_stride'] = offset
    pcl_base64 = base64.b64encode(pcl.tobytes()).decode('utf-8')
    # print("-- b64encode: {}".format(time.time() - t1))
    sms['data'] = pcl_base64
    return sms


def sms2pcl(sms: dict) -> np.ndarray:
    assert sms['type'] == 'memory_msgs::PointCloud' or sms['type'] == 'sensor_msgs::PointCloud'

    if sms['type'] == 'memory_msgs::PointCloud':
        assert current_os.startswith('linux') or current_os.startswith('darwin'), "Memory sharing must be utilized within the Linux/MacOS operating system."
        pcl = csms_shm.sms2pcl_float(sms)
    else:
        pcl_base64 = base64.b64decode(sms['data'])
        pcl = np.frombuffer(pcl_base64, dtype=np.float32)
        column = int(sms['point_stride'] / 4)
        pcl = pcl.reshape(-1, column)
    return pcl


class SMSCodec:
    def __init__(self, img_width: int, img_height: int, codec: str = 'h264', frame_id: str = 'camera'):
        self.enc_codec = av.CodecContext.create(codec, "w")
        self.enc_codec.pix_fmt = "yuv420p"
        self.enc_codec.width = img_width
        self.enc_codec.height = img_height
        self.enc_codec.flags |= self.enc_codec.flags.LOW_DELAY
        self.dec_codec = av.CodecContext.create(codec, "r")
        self.dec_codec.pix_fmt = "yuv420p"
        self.dec_codec.width = img_width
        self.dec_codec.height = img_height
        self.dec_codec.flags |= self.dec_codec.flags.LOW_DELAY
        self.img_width = img_width
        self.img_height = img_height
        self.frame_id = frame_id
        self.codec = codec

    def encode(self, img: np.ndarray) -> dict:
        assert len(img.shape) == 3 and img.shape[0] > 0 and img.shape[1] > 0 and img.shape[2] == 3 \
               and img.dtype == np.uint8, "CHECK img.ndim == 3 and img.dtype == np.uint8!"

        sms_msg = def_msg('sensor_msgs::CompressedImage')
        sms_msg['timestamp'] = time.time()
        sms_msg['frame_id'] = self.frame_id
        sms_msg['format'] = self.codec

        if img.shape[0] != self.img_height or img.shape[1] != self.img_width:
            img = cv2.resize(img, (self.img_width, self.img_height))
        av_img = av.VideoFrame.from_ndarray(img, format="rgb24")
        packet = self.enc_codec.encode(av_img)

        if len(packet):
            img_encoded = bytes(packet[-1])
            img_base64 = base64.b64encode(img_encoded).decode('utf-8')
            sms_msg['data'] = img_base64
        else:
            sms_msg['data'] = ''
        return sms_msg

    def decode(self, msg: dict) -> np.ndarray:
        assert msg['format'] in ['h264']
        assert msg['type'] == 'sensor_msgs::CompressedImage'

        img = None
        if len(msg['data']):
            try:
                img_base64 = base64.b64decode(msg['data'])
                for packet in self.dec_codec.parse(img_base64):
                    frames = self.dec_codec.decode(packet)
                    if len(frames):
                        img = frames[-1].to_ndarray(format='rgb24')
            except:
                pass
        return img


if __name__ == '__main__':
    cap = cv2.VideoCapture(r'G:\Movie\001.mkv')
    # img1 = cv2.imread(r'C:\Users\jario\Pictures\2023-04-09-114628.png')
    pub = Publisher('/sensors/camera/image_raw', 'sensor_msgs::CompressedImage')
    cc = SMSCodec(1920, 800)
    while True:
        try:
            ret, img1 = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            # img1 = cv2.resize(img1, (1920, 800))
            sms = cc.encode(img1)
            # sms = cvimg2sms(img1, format='h264')
            pub.publish(sms)
            cv2.imshow("img", img1)
            cv2.waitKey(5)
        except KeyboardInterrupt:
            print('stopped by keyboard')
            pub.kill()
            pub.join()
