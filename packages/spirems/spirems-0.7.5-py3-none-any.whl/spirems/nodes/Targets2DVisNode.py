#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn
# @Date  : 2025-01-20


import threading
import time
import cv2
import os
import json
import argparse
import numpy as np
from typing import Union
from queue import Queue
from spirems import Publisher, Subscriber, cvimg2sms, sms2cvimg, sms2pcl, sms2tensor
from spirems.nodes.BaseNode import BaseNode, get_extra_args
import base64
import uuid
import sys
import copy
try:
    from pycocotools import mask as pycoco_mask
except:
    pass


class Colors:
    def __init__(self):
        hexs = ('FF3838', 'FF9D97', 'FF701F', 'FFB21D', 'CFD231', '48F90A',
                '92CC17', '3DDB86', '1A9334', '00D4BB', '2C99A8', '00C2FF',
                '344593', '6473FF', '0018EC', '8438FF', '520085', 'CB38FF',
                'FF95C8', 'FF37C7')
        self.palette = [self.hex2rgb(f'#{c}') for c in hexs]
        self.n = len(self.palette)

    def __call__(self, i, bgr=False):
        c = self.palette[int(i) % self.n]
        return (c[2], c[1], c[0]) if bgr else c

    @staticmethod
    def hex2rgb(h):  # rgb order (PIL)
        return tuple(int(h[1 + i:1 + i + 2], 16) for i in (0, 2, 4))


def draw_rotated_box(img, center, size, angle, color=(0, 255, 0), thickness=2):
    """
    在图像上绘制旋转框
    :param img: 输入图像
    :param center: 旋转框中心点 (cx, cy)
    :param size: 旋转框的宽度和高度 (w, h)
    :param angle: 旋转角度（以度为单位，顺时针为正）
    :param color: 框的颜色 (B, G, R)
    :param thickness: 框的线宽
    :return: 绘制了旋转框的图像
    """
    # 获取旋转框的宽度和高度
    width, height = size

    # 计算旋转框的四个角点
    rect = ((center[0], center[1]), (width, height), angle)
    box = cv2.boxPoints(rect)  # 获取旋转框的四个角点
    box = np.int32(box)  # 将角点转换为整数

    # 在图像上绘制旋转框
    cv2.drawContours(img, [box], 0, color, thickness)

    return img


class Targets2DVisNode(threading.Thread, BaseNode):
    def __init__(
        self,
        job_name: str,
        ip: str = '127.0.0.1',
        port: int = 9094,
        image_topic="",
        **kwargs
    ):
        threading.Thread.__init__(self)
        BaseNode.__init__(
            self,
            self.__class__.__name__,
            job_name,
            ip=ip,
            port=port,
            param_dict_or_file=None,
            sms_shutdown=False,
            **kwargs
        )
        self.imshow = self.get_param("imshow", True)
        self.image_topic = self.get_param("image_topic", image_topic)
        self.score_threshold = self.get_param("score_threshold", 0.3)
        self.resize = self.get_param("resize", [-1, -1])
        self.show_crossx = self.get_param("show_crossx", False)
        self.show_labels = self.get_param("show_labels", True)
        self.show_axes = self.get_param("show_axes", False)
        self.show_corners = self.get_param("show_corners", True)
        self.params_help()

        # print("\033[32mimage_topic:    \033[0m", self.image_topic)
        # print("\033[32mscore_threshold:\033[0m", self.score_threshold)
        # print("\033[32mresize:         \033[0m", self.resize)
        # print("\033[32mshow_crossx:    \033[0m", self.show_crossx)
        # print("\033[32mshow_labels:    \033[0m", self.show_labels)
        # print("\033[32mshow_axes:      \033[0m", self.show_axes)
        # print("\033[32mshow_corners:   \033[0m", self.show_corners)
        self.received_shape = []

        input_topic = self.image_topic if len(self.image_topic) > 0 else '/' + job_name + '/sensor/image_raw'

        self._image_reader = Subscriber(
            input_topic, 'std_msgs::Null', self.image_callback,
            ip=ip, port=port
        )
        """
        self._image_writer = Publisher(
            '/' + job_name + '/detection_vis', 'sensor_msgs::CompressedImage',
            ip=ip, port=port
        )
        """
        self.colors_obj = Colors()

        self.image_queue = Queue()
        self.queue_pool.append(self.image_queue)
        self.start()

    def release(self):
        BaseNode.release(self)
        self._image_reader.kill()
        # self._image_writer.kill()

    def image_callback(self, msg):
        if not self.image_queue.empty():
            return
        if msg['type'] in ['memory_msgs::RawImage', 'sensor_msgs::CompressedImage']:
            img = sms2cvimg(msg)
            self.image_queue.put({'img': img, 'msg': msg})
            if self.received_shape != list(img.shape):
                self.received_shape = list(img.shape)
                print("  \033[32mRecevied Tensor Shape: \033[0m{}".format(self.received_shape))
        elif msg['type'] in ['memory_msgs::PointCloud', 'sensor_msgs::PointCloud']:
            pcl = sms2pcl(msg)
            if self.received_shape != list(pcl.shape):
                self.received_shape = list(pcl.shape)
                print("  \033[32mRecevied Tensor Shape: \033[0m{}".format(self.received_shape))
        elif msg['type'] in ['memory_msgs::Tensor']:
            tensor = sms2tensor(msg)
            if (msg['dtype'] == 'uint8' or msg['dtype'] == 'float32') and (len(msg['shape']) == 2 or len(msg['shape']) == 3):
                if msg['shape'][0] <= 8192 and msg['shape'][1] <= 8192:
                    if len(msg['shape']) == 3 and msg['shape'][2] in [1, 3, 4]:
                        self.image_queue.put({'img': tensor, 'msg': msg})
                    else:
                        self.image_queue.put({'img': tensor, 'msg': msg})
            if self.received_shape != list(tensor.shape):
                self.received_shape = list(tensor.shape)
                print("  \033[32mRecevied Tensor Shape: \033[0m{}".format(self.received_shape))
        else:
            print("Unsupported message type: {}".format(msg['type']))
            self.image_queue.put(None)

    def run(self):
        while self.is_running():
            img_msg = self.image_queue.get(block=True)
            if img_msg is None:
                break

            img, msg = img_msg['img'], img_msg['msg']
            camera_matrix = None
            distortion = None
            if self.show_labels and 'spirecv_msgs::2DTargets' in msg:
                if 'camera_matrix' in msg['spirecv_msgs::2DTargets']:
                    camera_matrix = np.array(msg['spirecv_msgs::2DTargets']['camera_matrix']).reshape(3, 3)
                if 'distortion' in msg['spirecv_msgs::2DTargets']:
                    distortion = np.array(msg['spirecv_msgs::2DTargets']['distortion'])
                min_siz = min(msg['spirecv_msgs::2DTargets']['height'], msg['spirecv_msgs::2DTargets']['width'])
                if min_siz <= 720:
                    thickness = 1
                elif 720 < min_siz <= 1200:
                    thickness = 2
                else:
                    thickness = 3

                if 'rois' in msg['spirecv_msgs::2DTargets'] and len(msg['spirecv_msgs::2DTargets']['rois']) > 0:
                    roi = msg['spirecv_msgs::2DTargets']['rois'][0]
                    img_roi = img[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2], :].copy()
                    img = cv2.addWeighted(img, 0.5, np.zeros_like(img, dtype=np.uint8), 0.5, 0)
                    img[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2], :] = img_roi
                
                masks = []
                result_classid = []
                for obj in msg['spirecv_msgs::2DTargets']['targets']:
                    if 'score' not in obj or obj['score'] >= self.score_threshold:
                        if "segmentation" in obj:
                            obj_seg = copy.deepcopy(obj['segmentation'])
                            obj_seg_counts = base64.b64decode(obj['segmentation']['counts'])
                            obj_seg["counts"] = obj_seg_counts
                            mask = pycoco_mask.decode(obj_seg)
                            masks.append(mask)
                            result_classid.append(obj['category_id'])

                if len(masks) > 0:
                    alpha = 0.5
                    colors_ = [self.colors_obj(x, True) for x in result_classid]
                    masks = np.asarray(masks, dtype=np.uint8)
                    masks = np.ascontiguousarray(masks.transpose(1, 2, 0))
                    masks = np.asarray(masks, dtype=np.float32)
                    colors_ = np.asarray(colors_, dtype=np.float32)
                    s = masks.sum(2, keepdims=True).clip(0, 1)
                    masks = (masks @ colors_).clip(0, 255)
                    img[:] = masks * alpha + img * (1 - s * alpha)

                for obj in msg['spirecv_msgs::2DTargets']['targets']:
                    if self.show_corners and 'corners' in obj:
                        pts = np.array(obj['corners'], np.int32).reshape((-1, 1, 2))
                        cv2.polylines(img, [pts], isClosed=True, color=(0, 255, 255), thickness=1, lineType=cv2.LINE_AA)
                    if self.show_axes and 'rvec' in obj and 'tvec' in obj and camera_matrix is not None and distortion is not None:
                        cv2.drawFrameAxes(img, camera_matrix, distortion, np.array([obj['rvec']]), np.array([obj['tvec']]), length=0.01)

                    if 'score' not in obj or obj['score'] >= self.score_threshold:
                        if 'obb' in obj:
                            img = draw_rotated_box(
                                img, 
                                (int(round(obj['obb'][0])), int(round(obj['obb'][1]))),
                                (int(round(obj['obb'][2])), int(round(obj['obb'][3]))),
                                obj['obb'][4]
                            )
                        cv2.rectangle(
                            img,
                            (int(obj['bbox'][0]), int(obj['bbox'][1])),
                            (int(obj['bbox'][0] + obj['bbox'][2]), int(obj['bbox'][1] + obj['bbox'][3])),
                            (0, 0, 255),
                            thickness,
                            cv2.LINE_AA
                        )
                        if 'tracked_id' in obj:
                            cate_text = str(obj['tracked_id']) + "-" + obj['category_name']
                        else:
                            cate_text = obj['category_name']
                        if 'score' in obj and obj['score'] >= self.score_threshold:
                            cate_text += "-" + "{:.2f}".format(obj['score'])
                        if 'keypoints' in obj:
                            kpts = obj['keypoints']
                            if 'kpt_links' in msg['spirecv_msgs::2DTargets']:
                                for kl in msg['spirecv_msgs::2DTargets']['kpt_links']:
                                    if kpts[kl[0]][0] > 0 and kpts[kl[0]][1] > 0 and kpts[kl[1]][0] > 0 and kpts[kl[1]][1] > 0:
                                        cv2.line(img, (int(kpts[kl[0]][0]), int(kpts[kl[0]][1])), (int(kpts[kl[1]][0]), int(kpts[kl[1]][1])), (0, 255, 255), 2)
                            for kp in obj['keypoints']:
                                if kp[0] > 0 and kp[1] > 0:
                                    cv2.circle(img, (int(kp[0]), int(kp[1])), 4, (180, 105, 255), -1)
                        (text_w, text_h), baseline= cv2.getTextSize(cate_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                        if obj['bbox'][3] < 50:  # pixel
                            cv2.rectangle(
                                img,
                                (int(obj['bbox'][0]), int(obj['bbox'][1])),
                                (int(obj['bbox'][0] + text_w + 2), int(obj['bbox'][1] - 17)),
                                (0, 0, 0),
                                -1,
                                cv2.LINE_AA
                            )
                            cv2.putText(
                                img,
                                cate_text,
                                (int(obj['bbox'][0]) + 2, int(obj['bbox'][1]) - 5),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (255, 255, 255),
                                1
                            )
                        else:
                            cv2.rectangle(
                                img,
                                (int(obj['bbox'][0]), int(obj['bbox'][1])),
                                (int(obj['bbox'][0] + text_w + 2), int(obj['bbox'][1] + 17)),
                                (0, 0, 0),
                                -1,
                                cv2.LINE_AA
                            )
                            cv2.putText(
                                img,
                                cate_text,
                                (int(obj['bbox'][0]) + 2, int(obj['bbox'][1]) + 13),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (255, 255, 255),
                                1
                            )

                if "fei_cxcy" in msg['spirecv_msgs::2DTargets']:
                    cx = int(msg['spirecv_msgs::2DTargets']['fei_cxcy'][0])
                    cy = int(msg['spirecv_msgs::2DTargets']['fei_cxcy'][1])
                    cv2.circle(img, (cx, cy), 8, (154, 250, 0), 2)

            if self.imshow:
                if self.resize is not None and len(self.resize) == 2 and self.resize[0] > 0 and self.resize[1] > 0:
                    img_show = cv2.resize(img, self.resize)
                else:
                    img_show = img
                if self.show_crossx:
                    cx, cy = int(img_show.shape[1] / 2), int(img_show.shape[0] / 2)
                    cv2.line(img_show, (cx-40, cy), (cx+40, cy), (0,0,255), 1, cv2.LINE_AA)
                    cv2.line(img_show, (cx, cy-40), (cx, cy+40), (0,0,255), 1, cv2.LINE_AA)
                    cv2.circle(img_show, (cx, cy), 40, (0,0,255), 1, cv2.LINE_AA)
                cv2.imshow('img', img_show)
                cv2.waitKey(5)

        self.release()
        print('{} quit!'.format(self.__class__.__name__))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_topic',
        help='SpireCV2 Image Topic.')
    parser.add_argument(
        '-j', '--job-name',
        type=str,
        default='',
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
    args, unknown_args = parser.parse_known_args()
    # print("--config:", args.config)
    # print("--job-name:", args.job_name)
    extra = get_extra_args(unknown_args)
    if len(args.job_name) == 0:
        args.job_name = str(uuid.uuid4().hex)

    node = Targets2DVisNode(args.job_name, image_topic=args.input_topic, ip=args.ip, port=args.port, **extra)
    node.spin()


if __name__ == '__main__':
    main()
