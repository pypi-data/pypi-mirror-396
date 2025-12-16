#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: renjin@bit.edu.cn
# @Date  : 2025-01-11

"""
【节点名称】：
    YOLO11VIDTrainLoaderNode
【依赖项安装】：
    cd <path-to-yolo11-spire-mod>
    pip install -e .
【订阅类型】：
    无
【发布类型】：
    sensor_msgs::CompressedImage （输出图像）
【备注】：
    无
"""

import threading
import time
import random
import os
import json
import math
from collections import defaultdict
import cv2
from typing import Any, Dict, List, Optional, Tuple, Union
from queue import Queue
from copy import deepcopy
from pathlib import Path
import numpy as np
from spirems import Subscriber, Publisher, cvimg2sms, def_msg, QoS, Logger, BaseNode, get_extra_args, Rate
from ultralytics.utils.instance import Instances
from ultralytics.utils.ops import resample_segments, segment2box, xywh2xyxy, xyxyxyxy2xywhr
from ultralytics.utils import colorstr
from ultralytics.utils.checks import check_version
from ultralytics.utils.metrics import bbox_ioa
import uuid
import torch
from pycocotools import mask as pycoco_mask
import base64
import glob
import argparse
import platform
import sys
from torch.utils.data import Dataset
from PIL import Image, UnidentifiedImageError


def raw_data_imshow(raw_data, norm=True):
    # print(raw_data.keys())
    img = raw_data['img']
    ins = deepcopy(raw_data['instances'])
    ins.convert_bbox(format="xywh")
    cls = raw_data['cls']
    # print(cls.shape)

    targets = def_msg('spirecv_msgs::2DTargets')

    targets["file_name"] = raw_data['im_file']
    h0, w0 = int(raw_data['ori_shape'][0]), int(raw_data['ori_shape'][1])
    h, w = int(raw_data['resized_shape'][0]), int(raw_data['resized_shape'][1])
    targets["height"] = h
    targets["width"] = w
    targets["targets"] = []

    img_cp = img.copy()

    for i in range(len(cls)):
        if norm:
            ann = [
                int(round((ins.bboxes[i, 0] - ins.bboxes[i, 2] / 2) * w, 3)),
                int(round((ins.bboxes[i, 1] - ins.bboxes[i, 3] / 2) * h, 3)),
                int(round(ins.bboxes[i, 2] * w, 3)),
                int(round(ins.bboxes[i, 3] * h, 3))
            ]
        else:
            ann = [
                int(round((ins.bboxes[i, 0] - ins.bboxes[i, 2] / 2), 3)),
                int(round((ins.bboxes[i, 1] - ins.bboxes[i, 3] / 2), 3)),
                int(round(ins.bboxes[i, 2], 3)),
                int(round(ins.bboxes[i, 3], 3))
            ]
        print(ann)
        cv2.rectangle(img_cp, (ann[0], ann[1]), (ann[0]+ann[2], ann[1]+ann[3]), (0, 0, 255), 1)

    cv2.imshow("img_cp", img_cp)
    cv2.waitKey(1000)


def safe_load_image(img_path, flags: int = cv2.IMREAD_COLOR):
    try:
        # 尝试用OpenCV加载
        img = cv2.imread(img_path, flags)
        if img is None:
            # 尝试用PIL加载
            img = Image.open(img_path).convert('RGB')
            img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return img
    except (UnidentifiedImageError, Exception) as e:
        print(f"跳过损坏的图片: {img_path}, 错误: {e}")
        return None


def imread(filename: str, flags: int = cv2.IMREAD_COLOR) -> Optional[np.ndarray]:
    """
    Read an image from a file with multilanguage filename support.

    Args:
        filename (str): Path to the file to read.
        flags (int, optional): Flag that can take values of cv2.IMREAD_*. Controls how the image is read.

    Returns:
        (np.ndarray | None): The read image array, or None if reading fails.

    Examples:
        >>> img = imread("path/to/image.jpg")
        >>> img = imread("path/to/image.jpg", cv2.IMREAD_GRAYSCALE)
    """
    file_bytes = np.fromfile(filename, np.uint8)
    if filename.endswith((".tiff", ".tif")):
        success, frames = cv2.imdecodemulti(file_bytes, cv2.IMREAD_UNCHANGED)
        if success:
            # Handle RGB images in tif/tiff format
            return frames[0] if len(frames) == 1 and frames[0].ndim == 3 else np.stack(frames, axis=2)
        return None
    else:
        im = cv2.imdecode(file_bytes, flags)
        return im[..., None] if im is not None and im.ndim == 2 else im  # Always ensure 3 dimensions


class BaseTransform:
    """
    Base class for image transformations in the Ultralytics library.

    This class serves as a foundation for implementing various image processing operations, designed to be
    compatible with both classification and semantic segmentation tasks.

    Methods:
        apply_image: Apply image transformations to labels.
        apply_instances: Apply transformations to object instances in labels.
        apply_semantic: Apply semantic segmentation to an image.
        __call__: Apply all label transformations to an image, instances, and semantic masks.

    Examples:
        >>> transform = BaseTransform()
        >>> labels = {"image": np.array(...), "instances": [...], "semantic": np.array(...)}
        >>> transformed_labels = transform(labels)
    """

    def __init__(self) -> None:
        """
        Initialize the BaseTransform object.

        This constructor sets up the base transformation object, which can be extended for specific image
        processing tasks. It is designed to be compatible with both classification and semantic segmentation.

        Examples:
            >>> transform = BaseTransform()
        """
        pass

    def apply_image(self, labels):
        """
        Apply image transformations to labels.

        This method is intended to be overridden by subclasses to implement specific image transformation
        logic. In its base form, it returns the input labels unchanged.

        Args:
            labels (Any): The input labels to be transformed. The exact type and structure of labels may
                vary depending on the specific implementation.

        Returns:
            (Any): The transformed labels. In the base implementation, this is identical to the input.

        Examples:
            >>> transform = BaseTransform()
            >>> original_labels = [1, 2, 3]
            >>> transformed_labels = transform.apply_image(original_labels)
            >>> print(transformed_labels)
            [1, 2, 3]
        """
        pass

    def apply_instances(self, labels):
        """
        Apply transformations to object instances in labels.

        This method is responsible for applying various transformations to object instances within the given
        labels. It is designed to be overridden by subclasses to implement specific instance transformation
        logic.

        Args:
            labels (dict): A dictionary containing label information, including object instances.

        Returns:
            (dict): The modified labels dictionary with transformed object instances.

        Examples:
            >>> transform = BaseTransform()
            >>> labels = {"instances": Instances(xyxy=torch.rand(5, 4), cls=torch.randint(0, 80, (5,)))}
            >>> transformed_labels = transform.apply_instances(labels)
        """
        pass

    def apply_semantic(self, labels):
        """
        Apply semantic segmentation transformations to an image.

        This method is intended to be overridden by subclasses to implement specific semantic segmentation
        transformations. In its base form, it does not perform any operations.

        Args:
            labels (Any): The input labels or semantic segmentation mask to be transformed.

        Returns:
            (Any): The transformed semantic segmentation mask or labels.

        Examples:
            >>> transform = BaseTransform()
            >>> semantic_mask = np.zeros((100, 100), dtype=np.uint8)
            >>> transformed_mask = transform.apply_semantic(semantic_mask)
        """
        pass

    def __call__(self, labels):
        """
        Apply all label transformations to an image, instances, and semantic masks.

        This method orchestrates the application of various transformations defined in the BaseTransform class
        to the input labels. It sequentially calls the apply_image and apply_instances methods to process the
        image and object instances, respectively.

        Args:
            labels (dict): A dictionary containing image data and annotations. Expected keys include 'img' for
                the image data, and 'instances' for object instances.

        Returns:
            (dict): The input labels dictionary with transformed image and instances.

        Examples:
            >>> transform = BaseTransform()
            >>> labels = {"img": np.random.rand(640, 640, 3), "instances": []}
            >>> transformed_labels = transform(labels)
        """
        self.apply_image(labels)
        self.apply_instances(labels)
        self.apply_semantic(labels)


class Compose:
    """
    A class for composing multiple image transformations.

    Attributes:
        transforms (List[Callable]): A list of transformation functions to be applied sequentially.

    Methods:
        __call__: Apply a series of transformations to input data.
        append: Append a new transform to the existing list of transforms.
        insert: Insert a new transform at a specified index in the list of transforms.
        __getitem__: Retrieve a specific transform or a set of transforms using indexing.
        __setitem__: Set a specific transform or a set of transforms using indexing.
        tolist: Convert the list of transforms to a standard Python list.

    Examples:
        >>> transforms = [RandomFlip(), RandomPerspective(30)]
        >>> compose = Compose(transforms)
        >>> transformed_data = compose(data)
        >>> compose.append(CenterCrop((224, 224)))
        >>> compose.insert(0, RandomFlip())
    """

    def __init__(self, transforms):
        """
        Initialize the Compose object with a list of transforms.

        Args:
            transforms (List[Callable]): A list of callable transform objects to be applied sequentially.

        Examples:
            >>> from ultralytics.data.augment import Compose, RandomHSV, RandomFlip
            >>> transforms = [RandomHSV(), RandomFlip()]
            >>> compose = Compose(transforms)
        """
        self.transforms = transforms if isinstance(transforms, list) else [transforms]

    def __call__(self, data):
        """
        Apply a series of transformations to input data.

        This method sequentially applies each transformation in the Compose object's transforms to the input data.

        Args:
            data (Any): The input data to be transformed. This can be of any type, depending on the
                transformations in the list.

        Returns:
            (Any): The transformed data after applying all transformations in sequence.

        Examples:
            >>> transforms = [Transform1(), Transform2(), Transform3()]
            >>> compose = Compose(transforms)
            >>> transformed_data = compose(input_data)
        """
        for t in self.transforms:
            # print(type(t))
            data = t(data)
        return data

    def append(self, transform):
        """
        Append a new transform to the existing list of transforms.

        Args:
            transform (BaseTransform): The transformation to be added to the composition.

        Examples:
            >>> compose = Compose([RandomFlip(), RandomPerspective()])
            >>> compose.append(RandomHSV())
        """
        self.transforms.append(transform)

    def insert(self, index, transform):
        """
        Insert a new transform at a specified index in the existing list of transforms.

        Args:
            index (int): The index at which to insert the new transform.
            transform (BaseTransform): The transform object to be inserted.

        Examples:
            >>> compose = Compose([Transform1(), Transform2()])
            >>> compose.insert(1, Transform3())
            >>> len(compose.transforms)
            3
        """
        self.transforms.insert(index, transform)

    def __getitem__(self, index: Union[list, int]) -> "Compose":
        """
        Retrieve a specific transform or a set of transforms using indexing.

        Args:
            index (int | List[int]): Index or list of indices of the transforms to retrieve.

        Returns:
            (Compose): A new Compose object containing the selected transform(s).

        Raises:
            AssertionError: If the index is not of type int or list.

        Examples:
            >>> transforms = [RandomFlip(), RandomPerspective(10), RandomHSV(0.5, 0.5, 0.5)]
            >>> compose = Compose(transforms)
            >>> single_transform = compose[1]  # Returns a Compose object with only RandomPerspective
            >>> multiple_transforms = compose[0:2]  # Returns a Compose object with RandomFlip and RandomPerspective
        """
        assert isinstance(index, (int, list)), f"The indices should be either list or int type but got {type(index)}"
        return Compose([self.transforms[i] for i in index]) if isinstance(index, list) else self.transforms[index]

    def __setitem__(self, index: Union[list, int], value: Union[list, int]) -> None:
        """
        Set one or more transforms in the composition using indexing.

        Args:
            index (int | List[int]): Index or list of indices to set transforms at.
            value (Any | List[Any]): Transform or list of transforms to set at the specified index(es).

        Raises:
            AssertionError: If index type is invalid, value type doesn't match index type, or index is out of range.

        Examples:
            >>> compose = Compose([Transform1(), Transform2(), Transform3()])
            >>> compose[1] = NewTransform()  # Replace second transform
            >>> compose[0:2] = [NewTransform1(), NewTransform2()]  # Replace first two transforms
        """
        assert isinstance(index, (int, list)), f"The indices should be either list or int type but got {type(index)}"
        if isinstance(index, list):
            assert isinstance(value, list), (
                f"The indices should be the same type as values, but got {type(index)} and {type(value)}"
            )
        if isinstance(index, int):
            index, value = [index], [value]
        for i, v in zip(index, value):
            assert i < len(self.transforms), f"list index {i} out of range {len(self.transforms)}."
            self.transforms[i] = v

    def tolist(self):
        """
        Convert the list of transforms to a standard Python list.

        Returns:
            (list): A list containing all the transform objects in the Compose instance.

        Examples:
            >>> transforms = [RandomFlip(), RandomPerspective(10), CenterCrop()]
            >>> compose = Compose(transforms)
            >>> transform_list = compose.tolist()
            >>> print(len(transform_list))
            3
        """
        return self.transforms

    def __repr__(self):
        """
        Return a string representation of the Compose object.

        Returns:
            (str): A string representation of the Compose object, including the list of transforms.

        Examples:
            >>> transforms = [RandomFlip(), RandomPerspective(degrees=10, translate=0.1, scale=0.1)]
            >>> compose = Compose(transforms)
            >>> print(compose)
            Compose([
                RandomFlip(),
                RandomPerspective(degrees=10, translate=0.1, scale=0.1)
            ])
        """
        return f"{self.__class__.__name__}({', '.join([f'{t}' for t in self.transforms])})"


class BaseMixTransform:
    """
    Base class for mix transformations like Cutmix, MixUp and Mosaic.

    This class provides a foundation for implementing mix transformations on datasets. It handles the
    probability-based application of transforms and manages the mixing of multiple images and labels.

    Attributes:
        dataset (Any): The dataset object containing images and labels.
        pre_transform (Callable | None): Optional transform to apply before mixing.
        p (float): Probability of applying the mix transformation.

    Methods:
        __call__: Apply the mix transformation to the input labels.
        _mix_transform: Abstract method to be implemented by subclasses for specific mix operations.
        get_indexes: Abstract method to get indexes of images to be mixed.
        _update_label_text: Update label text for mixed images.

    Examples:
        >>> class CustomMixTransform(BaseMixTransform):
        ...     def _mix_transform(self, labels):
        ...         # Implement custom mix logic here
        ...         return labels
        ...
        ...     def get_indexes(self):
        ...         return [random.randint(0, len(self.dataset) - 1) for _ in range(3)]
        >>> dataset = YourDataset()
        >>> transform = CustomMixTransform(dataset, p=0.5)
        >>> mixed_labels = transform(original_labels)
    """

    def __init__(self, dataset, pre_transform=None, p=0.0) -> None:
        """
        Initialize the BaseMixTransform object for mix transformations like CutMix, MixUp and Mosaic.

        This class serves as a base for implementing mix transformations in image processing pipelines.

        Args:
            dataset (Any): The dataset object containing images and labels for mixing.
            pre_transform (Callable | None): Optional transform to apply before mixing.
            p (float): Probability of applying the mix transformation. Should be in the range [0.0, 1.0].

        Examples:
            >>> dataset = YOLODataset("path/to/data")
            >>> pre_transform = Compose([RandomFlip(), RandomPerspective()])
            >>> mix_transform = BaseMixTransform(dataset, pre_transform, p=0.5)
        """
        self.dataset = dataset
        self.pre_transform = pre_transform
        self.p = p

    def __call__(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply pre-processing transforms and cutmix/mixup/mosaic transforms to labels data.

        This method determines whether to apply the mix transform based on a probability factor. If applied, it
        selects additional images, applies pre-transforms if specified, and then performs the mix transform.

        Args:
            labels (Dict[str, Any]): A dictionary containing label data for an image.

        Returns:
            (Dict[str, Any]): The transformed labels dictionary, which may include mixed data from other images.

        Examples:
            >>> transform = BaseMixTransform(dataset, pre_transform=None, p=0.5)
            >>> result = transform({"image": img, "bboxes": boxes, "cls": classes})
        """
        if random.uniform(0, 1) > self.p:
            return labels

        # print("type(labels):", type(labels))
        # print("type(self.pre_transform):", type(self.pre_transform))

        # Get index of one or three other images
        indexes = self.get_indexes()
        if isinstance(indexes, int):
            indexes = [indexes]

        # Get images information will be used for Mosaic, CutMix or MixUp
        mix_labels = [self.dataset.get_image_and_label(i, forget_i=True) for i in indexes]

        if self.pre_transform is not None:
            for i, data in enumerate(mix_labels):
                mix_labels[i] = self.pre_transform(data)

        for label in labels:
            label["mix_labels"] = mix_labels

        # Update cls and texts
        # 暂未实现
        # labels = self._update_label_text(labels)
        # Mosaic, CutMix or MixUp
        labels = self._mix_transform(labels)
        for label in labels:
            label.pop("mix_labels", None)
        return labels

    def _mix_transform(self, labels: Dict[str, Any]):
        """
        Apply CutMix, MixUp or Mosaic augmentation to the label dictionary.

        This method should be implemented by subclasses to perform specific mix transformations like CutMix, MixUp or
        Mosaic. It modifies the input label dictionary in-place with the augmented data.

        Args:
            labels (Dict[str, Any]): A dictionary containing image and label data. Expected to have a 'mix_labels' key
                with a list of additional image and label data for mixing.

        Returns:
            (Dict[str, Any]): The modified labels dictionary with augmented data after applying the mix transform.

        Examples:
            >>> transform = BaseMixTransform(dataset)
            >>> labels = {"image": img, "bboxes": boxes, "mix_labels": [{"image": img2, "bboxes": boxes2}]}
            >>> augmented_labels = transform._mix_transform(labels)
        """
        raise NotImplementedError

    def get_indexes(self):
        """
        Get a list of shuffled indexes for mosaic augmentation.

        Returns:
            (List[int]): A list of shuffled indexes from the dataset.

        Examples:
            >>> transform = BaseMixTransform(dataset)
            >>> indexes = transform.get_indexes()
            >>> print(indexes)  # [3, 18, 7, 2]
        """
        return random.randint(0, len(self.dataset) - 1)

    @staticmethod
    def _update_label_text(labels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update label text and class IDs for mixed labels in image augmentation.

        This method processes the 'texts' and 'cls' fields of the input labels dictionary and any mixed labels,
        creating a unified set of text labels and updating class IDs accordingly.

        Args:
            labels (Dict[str, Any]): A dictionary containing label information, including 'texts' and 'cls' fields,
                and optionally a 'mix_labels' field with additional label dictionaries.

        Returns:
            (Dict[str, Any]): The updated labels dictionary with unified text labels and updated class IDs.

        Examples:
            >>> labels = {
            ...     "texts": [["cat"], ["dog"]],
            ...     "cls": torch.tensor([[0], [1]]),
            ...     "mix_labels": [{"texts": [["bird"], ["fish"]], "cls": torch.tensor([[0], [1]])}],
            ... }
            >>> updated_labels = self._update_label_text(labels)
            >>> print(updated_labels["texts"])
            [['cat'], ['dog'], ['bird'], ['fish']]
            >>> print(updated_labels["cls"])
            tensor([[0],
                    [1]])
            >>> print(updated_labels["mix_labels"][0]["cls"])
            tensor([[2],
                    [3]])
        """
        if "texts" not in labels:
            return labels

        mix_texts = sum([labels["texts"]] + [x["texts"] for x in labels["mix_labels"]], [])
        mix_texts = list({tuple(x) for x in mix_texts})
        text2id = {text: i for i, text in enumerate(mix_texts)}

        for label in [labels] + labels["mix_labels"]:
            for i, cls in enumerate(label["cls"].squeeze(-1).tolist()):
                text = label["texts"][int(cls)]
                label["cls"][i] = text2id[tuple(text)]
            label["texts"] = mix_texts
        return labels


class Mosaic(BaseMixTransform):
    """
    Mosaic augmentation for image datasets.

    This class performs mosaic augmentation by combining multiple (4 or 9) images into a single mosaic image.
    The augmentation is applied to a dataset with a given probability.

    Attributes:
        dataset: The dataset on which the mosaic augmentation is applied.
        imgsz (int): Image size (height and width) after mosaic pipeline of a single image.
        p (float): Probability of applying the mosaic augmentation. Must be in the range 0-1.
        n (int): The grid size, either 4 (for 2x2) or 9 (for 3x3).
        border (Tuple[int, int]): Border size for width and height.

    Methods:
        get_indexes: Return a list of random indexes from the dataset.
        _mix_transform: Apply mixup transformation to the input image and labels.
        _mosaic3: Create a 1x3 image mosaic.
        _mosaic4: Create a 2x2 image mosaic.
        _mosaic9: Create a 3x3 image mosaic.
        _update_labels: Update labels with padding.
        _cat_labels: Concatenate labels and clips mosaic border instances.

    Examples:
        >>> from ultralytics.data.augment import Mosaic
        >>> dataset = YourDataset(...)  # Your image dataset
        >>> mosaic_aug = Mosaic(dataset, imgsz=640, p=0.5, n=4)
        >>> augmented_labels = mosaic_aug(original_labels)
    """

    def __init__(self, dataset, imgsz: int = 640, p: float = 1.0, n: int = 4):
        """
        Initialize the Mosaic augmentation object.

        This class performs mosaic augmentation by combining multiple (4 or 9) images into a single mosaic image.
        The augmentation is applied to a dataset with a given probability.

        Args:
            dataset (Any): The dataset on which the mosaic augmentation is applied.
            imgsz (int): Image size (height and width) after mosaic pipeline of a single image.
            p (float): Probability of applying the mosaic augmentation. Must be in the range 0-1.
            n (int): The grid size, either 4 (for 2x2) or 9 (for 3x3).

        Examples:
            >>> from ultralytics.data.augment import Mosaic
            >>> dataset = YourDataset(...)
            >>> mosaic_aug = Mosaic(dataset, imgsz=640, p=0.5, n=4)
        """
        assert 0 <= p <= 1.0, f"The probability should be in range [0, 1], but got {p}."
        assert n in {4, 9}, "grid must be equal to 4 or 9."
        super().__init__(dataset=dataset, p=p)
        self.imgsz = imgsz
        self.border = (-imgsz // 2, -imgsz // 2)  # width, height
        self.n = n
        self.buffer_enabled = self.dataset.cache != "ram"

    def get_indexes(self):
        """
        Return a list of random indexes from the dataset for mosaic augmentation.

        This method selects random image indexes either from a buffer or from the entire dataset, depending on
        the 'buffer' parameter. It is used to choose images for creating mosaic augmentations.

        Returns:
            (List[int]): A list of random image indexes. The length of the list is n-1, where n is the number
                of images used in the mosaic (either 3 or 8, depending on whether n is 4 or 9).

        Examples:
            >>> mosaic = Mosaic(dataset, imgsz=640, p=1.0, n=4)
            >>> indexes = mosaic.get_indexes()
            >>> print(len(indexes))  # Output: 3
        """
        if self.buffer_enabled:  # select images from buffer
            return random.choices(list(self.dataset.buffer), k=self.n - 1)
        else:  # select any images
            return [random.randint(0, len(self.dataset) - 1) for _ in range(self.n - 1)]

    def _mix_transform(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply mosaic augmentation to the input image and labels.

        This method combines multiple images (3, 4, or 9) into a single mosaic image based on the 'n' attribute.
        It ensures that rectangular annotations are not present and that there are other images available for
        mosaic augmentation.

        Args:
            labels (Dict[str, Any]): A dictionary containing image data and annotations. Expected keys include:
                - 'rect_shape': Should be None as rect and mosaic are mutually exclusive.
                - 'mix_labels': A list of dictionaries containing data for other images to be used in the mosaic.

        Returns:
            (Dict[str, Any]): A dictionary containing the mosaic-augmented image and updated annotations.

        Raises:
            AssertionError: If 'rect_shape' is not None or if 'mix_labels' is empty.

        Examples:
            >>> mosaic = Mosaic(dataset, imgsz=640, p=1.0, n=4)
            >>> augmented_data = mosaic._mix_transform(labels)
        """
        # print("self.n:", self.n)

        # for label in labels:
            # raw_data_imshow(label)

        for label in labels:
            assert label.get("rect_shape", None) is None, "rect and mosaic are mutually exclusive."
            assert len(label.get("mix_labels", [])), "There are no other images for mosaic augment."
        return (
            self._mosaic3(labels) if self.n == 3 else self._mosaic4(labels) if self.n == 4 else self._mosaic9(labels)
        )  # This code is modified for mosaic3 method.

    def _mosaic3(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a 1x3 image mosaic by combining three images.

        This method arranges three images in a horizontal layout, with the main image in the center and two
        additional images on either side. It's part of the Mosaic augmentation technique used in object detection.

        Args:
            labels (Dict[str, Any]): A dictionary containing image and label information for the main (center) image.
                Must include 'img' key with the image array, and 'mix_labels' key with a list of two
                dictionaries containing information for the side images.

        Returns:
            (Dict[str, Any]): A dictionary with the mosaic image and updated labels. Keys include:
                - 'img' (np.ndarray): The mosaic image array with shape (H, W, C).
                - Other keys from the input labels, updated to reflect the new image dimensions.

        Examples:
            >>> mosaic = Mosaic(dataset, imgsz=640, p=1.0, n=3)
            >>> labels = {
            ...     "img": np.random.rand(480, 640, 3),
            ...     "mix_labels": [{"img": np.random.rand(480, 640, 3)} for _ in range(2)],
            ... }
            >>> result = mosaic._mosaic3(labels)
            >>> print(result["img"].shape)
            (640, 640, 3)
        """
        mosaic_labels = []
        s = self.imgsz
        for i in range(3):
            labels_patch = labels if i == 0 else labels["mix_labels"][i - 1]
            # Load image
            img = labels_patch["img"]
            h, w = labels_patch.pop("resized_shape")

            # Place img in img3
            if i == 0:  # center
                img3 = np.full((s * 3, s * 3, img.shape[2]), 114, dtype=np.uint8)  # base image with 3 tiles
                h0, w0 = h, w
                c = s, s, s + w, s + h  # xmin, ymin, xmax, ymax (base) coordinates
            elif i == 1:  # right
                c = s + w0, s, s + w0 + w, s + h
            elif i == 2:  # left
                c = s - w, s + h0 - h, s, s + h0

            padw, padh = c[:2]
            x1, y1, x2, y2 = (max(x, 0) for x in c)  # allocate coordinates

            img3[y1:y2, x1:x2] = img[y1 - padh :, x1 - padw :]  # img3[ymin:ymax, xmin:xmax]
            # hp, wp = h, w  # height, width previous for next iteration

            # Labels assuming imgsz*2 mosaic size
            labels_patch = self._update_labels(labels_patch, padw + self.border[0], padh + self.border[1])
            mosaic_labels.append(labels_patch)
        final_labels = self._cat_labels(mosaic_labels)

        final_labels["img"] = img3[-self.border[0] : self.border[0], -self.border[1] : self.border[1]]
        return final_labels

    def _mosaic4(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a 2x2 image mosaic from four input images.

        This method combines four images into a single mosaic image by placing them in a 2x2 grid. It also
        updates the corresponding labels for each image in the mosaic.

        Args:
            labels (Dict[str, Any]): A dictionary containing image data and labels for the base image (index 0) and three
                additional images (indices 1-3) in the 'mix_labels' key.

        Returns:
            (Dict[str, Any]): A dictionary containing the mosaic image and updated labels. The 'img' key contains the mosaic
                image as a numpy array, and other keys contain the combined and adjusted labels for all four images.

        Examples:
            >>> mosaic = Mosaic(dataset, imgsz=640, p=1.0, n=4)
            >>> labels = {
            ...     "img": np.random.rand(480, 640, 3),
            ...     "mix_labels": [{"img": np.random.rand(480, 640, 3)} for _ in range(3)],
            ... }
            >>> result = mosaic._mosaic4(labels)
            >>> assert result["img"].shape == (1280, 1280, 3)
        """
        s = self.imgsz
        # print("self.border:", self.border)
        yc, xc = (int(random.uniform(-x, 2 * s + x)) for x in self.border)  # mosaic center x, y
        # print("yc, xc:", yc, xc)

        mfinal_labels = []
        for j, label in enumerate(labels):
            mosaic_labels = []
            for i in range(4):
                labels_patch = label if i == 0 else label["mix_labels"][i - 1][j]
                # Load image
                img = labels_patch["img"]
                h, w = labels_patch.pop("resized_shape")

                # Place img in img4
                if i == 0:  # top left
                    img4 = np.full((s * 2, s * 2, img.shape[2]), 114, dtype=np.uint8)  # base image with 4 tiles
                    x1a, y1a, x2a, y2a = max(xc - w, 0), max(yc - h, 0), xc, yc  # xmin, ymin, xmax, ymax (large image)
                    x1b, y1b, x2b, y2b = w - (x2a - x1a), h - (y2a - y1a), w, h  # xmin, ymin, xmax, ymax (small image)
                elif i == 1:  # top right
                    x1a, y1a, x2a, y2a = xc, max(yc - h, 0), min(xc + w, s * 2), yc
                    x1b, y1b, x2b, y2b = 0, h - (y2a - y1a), min(w, x2a - x1a), h
                elif i == 2:  # bottom left
                    x1a, y1a, x2a, y2a = max(xc - w, 0), yc, xc, min(s * 2, yc + h)
                    x1b, y1b, x2b, y2b = w - (x2a - x1a), 0, w, min(y2a - y1a, h)
                elif i == 3:  # bottom right
                    x1a, y1a, x2a, y2a = xc, yc, min(xc + w, s * 2), min(s * 2, yc + h)
                    x1b, y1b, x2b, y2b = 0, 0, min(w, x2a - x1a), min(y2a - y1a, h)

                img4[y1a:y2a, x1a:x2a] = img[y1b:y2b, x1b:x2b]  # img4[ymin:ymax, xmin:xmax]
                padw = x1a - x1b
                padh = y1a - y1b

                labels_patch = self._update_labels(labels_patch, padw, padh)
                mosaic_labels.append(labels_patch)
            final_labels = self._cat_labels(mosaic_labels)
            final_labels["img"] = img4
            mfinal_labels.append(final_labels)
        
        # for label in mfinal_labels:
            # raw_data_imshow(label, False)

        return mfinal_labels

    def _mosaic9(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a 3x3 image mosaic from the input image and eight additional images.

        This method combines nine images into a single mosaic image. The input image is placed at the center,
        and eight additional images from the dataset are placed around it in a 3x3 grid pattern.

        Args:
            labels (Dict[str, Any]): A dictionary containing the input image and its associated labels. It should have
                the following keys:
                - 'img' (np.ndarray): The input image.
                - 'resized_shape' (Tuple[int, int]): The shape of the resized image (height, width).
                - 'mix_labels' (List[Dict]): A list of dictionaries containing information for the additional
                  eight images, each with the same structure as the input labels.

        Returns:
            (Dict[str, Any]): A dictionary containing the mosaic image and updated labels. It includes the following keys:
                - 'img' (np.ndarray): The final mosaic image.
                - Other keys from the input labels, updated to reflect the new mosaic arrangement.

        Examples:
            >>> mosaic = Mosaic(dataset, imgsz=640, p=1.0, n=9)
            >>> input_labels = dataset[0]
            >>> mosaic_result = mosaic._mosaic9(input_labels)
            >>> mosaic_image = mosaic_result["img"]
        """
        mosaic_labels = []
        s = self.imgsz
        hp, wp = -1, -1  # height, width previous
        for i in range(9):
            labels_patch = labels if i == 0 else labels["mix_labels"][i - 1]
            # Load image
            img = labels_patch["img"]
            h, w = labels_patch.pop("resized_shape")

            # Place img in img9
            if i == 0:  # center
                img9 = np.full((s * 3, s * 3, img.shape[2]), 114, dtype=np.uint8)  # base image with 4 tiles
                h0, w0 = h, w
                c = s, s, s + w, s + h  # xmin, ymin, xmax, ymax (base) coordinates
            elif i == 1:  # top
                c = s, s - h, s + w, s
            elif i == 2:  # top right
                c = s + wp, s - h, s + wp + w, s
            elif i == 3:  # right
                c = s + w0, s, s + w0 + w, s + h
            elif i == 4:  # bottom right
                c = s + w0, s + hp, s + w0 + w, s + hp + h
            elif i == 5:  # bottom
                c = s + w0 - w, s + h0, s + w0, s + h0 + h
            elif i == 6:  # bottom left
                c = s + w0 - wp - w, s + h0, s + w0 - wp, s + h0 + h
            elif i == 7:  # left
                c = s - w, s + h0 - h, s, s + h0
            elif i == 8:  # top left
                c = s - w, s + h0 - hp - h, s, s + h0 - hp

            padw, padh = c[:2]
            x1, y1, x2, y2 = (max(x, 0) for x in c)  # allocate coordinates

            # Image
            img9[y1:y2, x1:x2] = img[y1 - padh :, x1 - padw :]  # img9[ymin:ymax, xmin:xmax]
            hp, wp = h, w  # height, width previous for next iteration

            # Labels assuming imgsz*2 mosaic size
            labels_patch = self._update_labels(labels_patch, padw + self.border[0], padh + self.border[1])
            mosaic_labels.append(labels_patch)
        final_labels = self._cat_labels(mosaic_labels)

        final_labels["img"] = img9[-self.border[0] : self.border[0], -self.border[1] : self.border[1]]
        return final_labels

    @staticmethod
    def _update_labels(labels, padw: int, padh: int) -> Dict[str, Any]:
        """
        Update label coordinates with padding values.

        This method adjusts the bounding box coordinates of object instances in the labels by adding padding
        values. It also denormalizes the coordinates if they were previously normalized.

        Args:
            labels (Dict[str, Any]): A dictionary containing image and instance information.
            padw (int): Padding width to be added to the x-coordinates.
            padh (int): Padding height to be added to the y-coordinates.

        Returns:
            (dict): Updated labels dictionary with adjusted instance coordinates.

        Examples:
            >>> labels = {"img": np.zeros((100, 100, 3)), "instances": Instances(...)}
            >>> padw, padh = 50, 50
            >>> updated_labels = Mosaic._update_labels(labels, padw, padh)
        """
        nh, nw = labels["img"].shape[:2]
        labels["instances"].convert_bbox(format="xyxy")
        labels["instances"].denormalize(nw, nh)
        labels["instances"].add_padding(padw, padh)
        return labels

    def _cat_labels(self, mosaic_labels: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Concatenate and process labels for mosaic augmentation.

        This method combines labels from multiple images used in mosaic augmentation, clips instances to the
        mosaic border, and removes zero-area boxes.

        Args:
            mosaic_labels (List[Dict[str, Any]]): A list of label dictionaries for each image in the mosaic.

        Returns:
            (Dict[str, Any]): A dictionary containing concatenated and processed labels for the mosaic image, including:
                - im_file (str): File path of the first image in the mosaic.
                - ori_shape (Tuple[int, int]): Original shape of the first image.
                - resized_shape (Tuple[int, int]): Shape of the mosaic image (imgsz * 2, imgsz * 2).
                - cls (np.ndarray): Concatenated class labels.
                - instances (Instances): Concatenated instance annotations.
                - mosaic_border (Tuple[int, int]): Mosaic border size.
                - texts (List[str], optional): Text labels if present in the original labels.

        Examples:
            >>> mosaic = Mosaic(dataset, imgsz=640)
            >>> mosaic_labels = [{"cls": np.array([0, 1]), "instances": Instances(...)} for _ in range(4)]
            >>> result = mosaic._cat_labels(mosaic_labels)
            >>> print(result.keys())
            dict_keys(['im_file', 'ori_shape', 'resized_shape', 'cls', 'instances', 'mosaic_border'])
        """
        if len(mosaic_labels) == 0:
            return {}
        cls = []
        instances = []
        imgsz = self.imgsz * 2  # mosaic imgsz
        for labels in mosaic_labels:
            cls.append(labels["cls"])
            instances.append(labels["instances"])
        # Final labels
        final_labels = {
            "im_file": mosaic_labels[0]["im_file"],
            "ori_shape": mosaic_labels[0]["ori_shape"],
            "resized_shape": (imgsz, imgsz),
            "cls": np.concatenate(cls, 0),
            "instances": Instances.concatenate(instances, axis=0),
            "mosaic_border": self.border,
        }
        final_labels["instances"].clip(imgsz, imgsz)
        good = final_labels["instances"].remove_zero_area_boxes()
        final_labels["cls"] = final_labels["cls"][good]
        if "texts" in mosaic_labels[0]:
            final_labels["texts"] = mosaic_labels[0]["texts"]
        return final_labels


class MixUp(BaseMixTransform):
    """
    Apply MixUp augmentation to image datasets.

    This class implements the MixUp augmentation technique as described in the paper [mixup: Beyond Empirical Risk
    Minimization](https://arxiv.org/abs/1710.09412). MixUp combines two images and their labels using a random weight.

    Attributes:
        dataset (Any): The dataset to which MixUp augmentation will be applied.
        pre_transform (Callable | None): Optional transform to apply before MixUp.
        p (float): Probability of applying MixUp augmentation.

    Methods:
        _mix_transform: Apply MixUp augmentation to the input labels.

    Examples:
        >>> from ultralytics.data.augment import MixUp
        >>> dataset = YourDataset(...)  # Your image dataset
        >>> mixup = MixUp(dataset, p=0.5)
        >>> augmented_labels = mixup(original_labels)
    """

    def __init__(self, dataset, pre_transform=None, p: float = 0.0) -> None:
        """
        Initialize the MixUp augmentation object.

        MixUp is an image augmentation technique that combines two images by taking a weighted sum of their pixel
        values and labels. This implementation is designed for use with the Ultralytics YOLO framework.

        Args:
            dataset (Any): The dataset to which MixUp augmentation will be applied.
            pre_transform (Callable | None): Optional transform to apply to images before MixUp.
            p (float): Probability of applying MixUp augmentation to an image. Must be in the range [0, 1].

        Examples:
            >>> from ultralytics.data.dataset import YOLODataset
            >>> dataset = YOLODataset("path/to/data.yaml")
            >>> mixup = MixUp(dataset, pre_transform=None, p=0.5)
        """
        super().__init__(dataset=dataset, pre_transform=pre_transform, p=p)

    def _mix_transform(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply MixUp augmentation to the input labels.

        This method implements the MixUp augmentation technique as described in the paper
        "mixup: Beyond Empirical Risk Minimization" (https://arxiv.org/abs/1710.09412).

        Args:
            labels (Dict[str, Any]): A dictionary containing the original image and label information.

        Returns:
            (Dict[str, Any]): A dictionary containing the mixed-up image and combined label information.

        Examples:
            >>> mixer = MixUp(dataset)
            >>> mixed_labels = mixer._mix_transform(labels)
        """
        r = np.random.beta(32.0, 32.0)  # mixup ratio, alpha=beta=32.0
        labels2 = labels["mix_labels"][0]
        labels["img"] = (labels["img"] * r + labels2["img"] * (1 - r)).astype(np.uint8)
        labels["instances"] = Instances.concatenate([labels["instances"], labels2["instances"]], axis=0)
        labels["cls"] = np.concatenate([labels["cls"], labels2["cls"]], 0)
        return labels


class CutMix(BaseMixTransform):
    """
    Apply CutMix augmentation to image datasets as described in the paper https://arxiv.org/abs/1905.04899.

    CutMix combines two images by replacing a random rectangular region of one image with the corresponding region from another image,
    and adjusts the labels proportionally to the area of the mixed region.

    Attributes:
        dataset (Any): The dataset to which CutMix augmentation will be applied.
        pre_transform (Callable | None): Optional transform to apply before CutMix.
        p (float): Probability of applying CutMix augmentation.
        beta (float): Beta distribution parameter for sampling the mixing ratio.
        num_areas (int): Number of areas to try to cut and mix.

    Methods:
        _mix_transform: Apply CutMix augmentation to the input labels.
        _rand_bbox: Generate random bounding box coordinates for the cut region.

    Examples:
        >>> from ultralytics.data.augment import CutMix
        >>> dataset = YourDataset(...)  # Your image dataset
        >>> cutmix = CutMix(dataset, p=0.5)
        >>> augmented_labels = cutmix(original_labels)
    """

    def __init__(self, dataset, pre_transform=None, p: float = 0.0, beta: float = 1.0, num_areas: int = 3) -> None:
        """
        Initialize the CutMix augmentation object.

        Args:
            dataset (Any): The dataset to which CutMix augmentation will be applied.
            pre_transform (Callable | None): Optional transform to apply before CutMix.
            p (float): Probability of applying CutMix augmentation.
            beta (float): Beta distribution parameter for sampling the mixing ratio.
            num_areas (int): Number of areas to try to cut and mix.
        """
        super().__init__(dataset=dataset, pre_transform=pre_transform, p=p)
        self.beta = beta
        self.num_areas = num_areas

    def _rand_bbox(self, width: int, height: int) -> Tuple[int, int, int, int]:
        """
        Generate random bounding box coordinates for the cut region.

        Args:
            width (int): Width of the image.
            height (int): Height of the image.

        Returns:
            (Tuple[int]): (x1, y1, x2, y2) coordinates of the bounding box.
        """
        # Sample mixing ratio from Beta distribution
        lam = np.random.beta(self.beta, self.beta)

        cut_ratio = np.sqrt(1.0 - lam)
        cut_w = int(width * cut_ratio)
        cut_h = int(height * cut_ratio)

        # Random center
        cx = np.random.randint(width)
        cy = np.random.randint(height)

        # Bounding box coordinates
        x1 = np.clip(cx - cut_w // 2, 0, width)
        y1 = np.clip(cy - cut_h // 2, 0, height)
        x2 = np.clip(cx + cut_w // 2, 0, width)
        y2 = np.clip(cy + cut_h // 2, 0, height)

        return x1, y1, x2, y2

    def _mix_transform(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply CutMix augmentation to the input labels.

        Args:
            labels (Dict[str, Any]): A dictionary containing the original image and label information.

        Returns:
            (Dict[str, Any]): A dictionary containing the mixed image and adjusted labels.

        Examples:
            >>> cutter = CutMix(dataset)
            >>> mixed_labels = cutter._mix_transform(labels)
        """
        # Get a random second image
        h, w = labels["img"].shape[:2]

        cut_areas = np.asarray([self._rand_bbox(w, h) for _ in range(self.num_areas)], dtype=np.float32)
        ioa1 = bbox_ioa(cut_areas, labels["instances"].bboxes)  # (self.num_areas, num_boxes)
        idx = np.nonzero(ioa1.sum(axis=1) <= 0)[0]
        if len(idx) == 0:
            return labels

        labels2 = labels.pop("mix_labels")[0]
        area = cut_areas[np.random.choice(idx)]  # randomly select one
        ioa2 = bbox_ioa(area[None], labels2["instances"].bboxes).squeeze(0)
        indexes2 = np.nonzero(ioa2 >= (0.01 if len(labels["instances"].segments) else 0.1))[0]
        if len(indexes2) == 0:
            return labels

        instances2 = labels2["instances"][indexes2]
        instances2.convert_bbox("xyxy")
        instances2.denormalize(w, h)

        # Apply CutMix
        x1, y1, x2, y2 = area.astype(np.int32)
        labels["img"][y1:y2, x1:x2] = labels2["img"][y1:y2, x1:x2]

        # Restrain instances2 to the random bounding border
        instances2.add_padding(-x1, -y1)
        instances2.clip(x2 - x1, y2 - y1)
        instances2.add_padding(x1, y1)

        labels["cls"] = np.concatenate([labels["cls"], labels2["cls"][indexes2]], axis=0)
        labels["instances"] = Instances.concatenate([labels["instances"], instances2], axis=0)
        return labels


class RandomPerspective:
    """
    Implement random perspective and affine transformations on images and corresponding annotations.

    This class applies random rotations, translations, scaling, shearing, and perspective transformations
    to images and their associated bounding boxes, segments, and keypoints. It can be used as part of an
    augmentation pipeline for object detection and instance segmentation tasks.

    Attributes:
        degrees (float): Maximum absolute degree range for random rotations.
        translate (float): Maximum translation as a fraction of the image size.
        scale (float): Scaling factor range, e.g., scale=0.1 means 0.9-1.1.
        shear (float): Maximum shear angle in degrees.
        perspective (float): Perspective distortion factor.
        border (Tuple[int, int]): Mosaic border size as (x, y).
        pre_transform (Callable | None): Optional transform to apply before the random perspective.

    Methods:
        affine_transform: Apply affine transformations to the input image.
        apply_bboxes: Transform bounding boxes using the affine matrix.
        apply_segments: Transform segments and generate new bounding boxes.
        apply_keypoints: Transform keypoints using the affine matrix.
        __call__: Apply the random perspective transformation to images and annotations.
        box_candidates: Filter transformed bounding boxes based on size and aspect ratio.

    Examples:
        >>> transform = RandomPerspective(degrees=10, translate=0.1, scale=0.1, shear=10)
        >>> image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        >>> labels = {"img": image, "cls": np.array([0, 1]), "instances": Instances(...)}
        >>> result = transform(labels)
        >>> transformed_image = result["img"]
        >>> transformed_instances = result["instances"]
    """

    def __init__(
        self,
        degrees: float = 0.0,
        translate: float = 0.1,
        scale: float = 0.5,
        shear: float = 0.0,
        perspective: float = 0.0,
        border: Tuple[int, int] = (0, 0),
        pre_transform=None,
    ):
        """
        Initialize RandomPerspective object with transformation parameters.

        This class implements random perspective and affine transformations on images and corresponding bounding boxes,
        segments, and keypoints. Transformations include rotation, translation, scaling, and shearing.

        Args:
            degrees (float): Degree range for random rotations.
            translate (float): Fraction of total width and height for random translation.
            scale (float): Scaling factor interval, e.g., a scale factor of 0.5 allows a resize between 50%-150%.
            shear (float): Shear intensity (angle in degrees).
            perspective (float): Perspective distortion factor.
            border (Tuple[int, int]): Tuple specifying mosaic border (top/bottom, left/right).
            pre_transform (Callable | None): Function/transform to apply to the image before starting the random
                transformation.

        Examples:
            >>> transform = RandomPerspective(degrees=10.0, translate=0.1, scale=0.5, shear=5.0)
            >>> result = transform(labels)  # Apply random perspective to labels
        """
        self.degrees = degrees
        self.translate = translate
        self.scale = scale
        self.shear = shear
        self.perspective = perspective
        self.border = border  # mosaic border
        self.pre_transform = pre_transform

    def affine_transform(self, imgs: list[np.ndarray], border: Tuple[int, int]) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Apply a sequence of affine transformations centered around the image center.

        This function performs a series of geometric transformations on the input image, including
        translation, perspective change, rotation, scaling, and shearing. The transformations are
        applied in a specific order to maintain consistency.

        Args:
            img (np.ndarray): Input image to be transformed.
            border (Tuple[int, int]): Border dimensions for the transformed image.

        Returns:
            img (np.ndarray): Transformed image.
            M (np.ndarray): 3x3 transformation matrix.
            s (float): Scale factor applied during the transformation.

        Examples:
            >>> import numpy as np
            >>> img = np.random.rand(100, 100, 3)
            >>> border = (10, 10)
            >>> transformed_img, matrix, scale = affine_transform(img, border)
        """
        # Center
        C = np.eye(3, dtype=np.float32)

        C[0, 2] = -imgs[-1].shape[1] / 2  # x translation (pixels)
        C[1, 2] = -imgs[-1].shape[0] / 2  # y translation (pixels)

        # Perspective
        P = np.eye(3, dtype=np.float32)
        P[2, 0] = random.uniform(-self.perspective, self.perspective)  # x perspective (about y)
        P[2, 1] = random.uniform(-self.perspective, self.perspective)  # y perspective (about x)

        # Rotation and Scale
        R = np.eye(3, dtype=np.float32)
        a = random.uniform(-self.degrees, self.degrees)
        # a += random.choice([-180, -90, 0, 90])  # add 90deg rotations to small rotations
        s = random.uniform(1 - self.scale, 1 + self.scale)
        # s = 2 ** random.uniform(-scale, scale)
        R[:2] = cv2.getRotationMatrix2D(angle=a, center=(0, 0), scale=s)

        # Shear
        S = np.eye(3, dtype=np.float32)
        S[0, 1] = math.tan(random.uniform(-self.shear, self.shear) * math.pi / 180)  # x shear (deg)
        S[1, 0] = math.tan(random.uniform(-self.shear, self.shear) * math.pi / 180)  # y shear (deg)

        # Translation
        T = np.eye(3, dtype=np.float32)
        T[0, 2] = random.uniform(0.5 - self.translate, 0.5 + self.translate) * self.size[0]  # x translation (pixels)
        T[1, 2] = random.uniform(0.5 - self.translate, 0.5 + self.translate) * self.size[1]  # y translation (pixels)

        # Combined rotation matrix
        M = T @ S @ R @ P @ C  # order of operations (right to left) is IMPORTANT
        # Affine image
        for j, img in enumerate(imgs):
            if (border[0] != 0) or (border[1] != 0) or (M != np.eye(3)).any():  # image changed
                if self.perspective:
                    imgs[j] = cv2.warpPerspective(img, M, dsize=self.size, borderValue=(114, 114, 114))
                else:  # affine
                    imgs[j] = cv2.warpAffine(img, M[:2], dsize=self.size, borderValue=(114, 114, 114))
                if imgs[j].ndim == 2:
                    imgs[j] = imgs[j][..., None]
        return imgs, M, s

    def apply_bboxes(self, bboxes: np.ndarray, M: np.ndarray) -> np.ndarray:
        """
        Apply affine transformation to bounding boxes.

        This function applies an affine transformation to a set of bounding boxes using the provided
        transformation matrix.

        Args:
            bboxes (np.ndarray): Bounding boxes in xyxy format with shape (N, 4), where N is the number
                of bounding boxes.
            M (np.ndarray): Affine transformation matrix with shape (3, 3).

        Returns:
            (np.ndarray): Transformed bounding boxes in xyxy format with shape (N, 4).

        Examples:
            >>> bboxes = torch.tensor([[10, 10, 20, 20], [30, 30, 40, 40]])
            >>> M = torch.eye(3)
            >>> transformed_bboxes = apply_bboxes(bboxes, M)
        """
        n = len(bboxes)
        if n == 0:
            return bboxes

        xy = np.ones((n * 4, 3), dtype=bboxes.dtype)
        xy[:, :2] = bboxes[:, [0, 1, 2, 3, 0, 3, 2, 1]].reshape(n * 4, 2)  # x1y1, x2y2, x1y2, x2y1
        xy = xy @ M.T  # transform
        xy = (xy[:, :2] / xy[:, 2:3] if self.perspective else xy[:, :2]).reshape(n, 8)  # perspective rescale or affine

        # Create new boxes
        x = xy[:, [0, 2, 4, 6]]
        y = xy[:, [1, 3, 5, 7]]
        return np.concatenate((x.min(1), y.min(1), x.max(1), y.max(1)), dtype=bboxes.dtype).reshape(4, n).T

    def apply_segments(self, segments: np.ndarray, M: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply affine transformations to segments and generate new bounding boxes.

        This function applies affine transformations to input segments and generates new bounding boxes based on
        the transformed segments. It clips the transformed segments to fit within the new bounding boxes.

        Args:
            segments (np.ndarray): Input segments with shape (N, M, 2), where N is the number of segments and M is the
                number of points in each segment.
            M (np.ndarray): Affine transformation matrix with shape (3, 3).

        Returns:
            bboxes (np.ndarray): New bounding boxes with shape (N, 4) in xyxy format.
            segments (np.ndarray): Transformed and clipped segments with shape (N, M, 2).

        Examples:
            >>> segments = np.random.rand(10, 500, 2)  # 10 segments with 500 points each
            >>> M = np.eye(3)  # Identity transformation matrix
            >>> new_bboxes, new_segments = apply_segments(segments, M)
        """
        n, num = segments.shape[:2]
        if n == 0:
            return [], segments

        xy = np.ones((n * num, 3), dtype=segments.dtype)
        segments = segments.reshape(-1, 2)
        xy[:, :2] = segments
        xy = xy @ M.T  # transform
        xy = xy[:, :2] / xy[:, 2:3]
        segments = xy.reshape(n, -1, 2)
        bboxes = np.stack([segment2box(xy, self.size[0], self.size[1]) for xy in segments], 0)
        segments[..., 0] = segments[..., 0].clip(bboxes[:, 0:1], bboxes[:, 2:3])
        segments[..., 1] = segments[..., 1].clip(bboxes[:, 1:2], bboxes[:, 3:4])
        return bboxes, segments

    def apply_keypoints(self, keypoints: np.ndarray, M: np.ndarray) -> np.ndarray:
        """
        Apply affine transformation to keypoints.

        This method transforms the input keypoints using the provided affine transformation matrix. It handles
        perspective rescaling if necessary and updates the visibility of keypoints that fall outside the image
        boundaries after transformation.

        Args:
            keypoints (np.ndarray): Array of keypoints with shape (N, 17, 3), where N is the number of instances,
                17 is the number of keypoints per instance, and 3 represents (x, y, visibility).
            M (np.ndarray): 3x3 affine transformation matrix.

        Returns:
            (np.ndarray): Transformed keypoints array with the same shape as input (N, 17, 3).

        Examples:
            >>> random_perspective = RandomPerspective()
            >>> keypoints = np.random.rand(5, 17, 3)  # 5 instances, 17 keypoints each
            >>> M = np.eye(3)  # Identity transformation
            >>> transformed_keypoints = random_perspective.apply_keypoints(keypoints, M)
        """
        n, nkpt = keypoints.shape[:2]
        if n == 0:
            return keypoints
        xy = np.ones((n * nkpt, 3), dtype=keypoints.dtype)
        visible = keypoints[..., 2].reshape(n * nkpt, 1)
        xy[:, :2] = keypoints[..., :2].reshape(n * nkpt, 2)
        xy = xy @ M.T  # transform
        xy = xy[:, :2] / xy[:, 2:3]  # perspective rescale or affine
        out_mask = (xy[:, 0] < 0) | (xy[:, 1] < 0) | (xy[:, 0] > self.size[0]) | (xy[:, 1] > self.size[1])
        visible[out_mask] = 0
        return np.concatenate([xy, visible], axis=-1).reshape(n, nkpt, 3)

    def __call__(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply random perspective and affine transformations to an image and its associated labels.

        This method performs a series of transformations including rotation, translation, scaling, shearing,
        and perspective distortion on the input image and adjusts the corresponding bounding boxes, segments,
        and keypoints accordingly.

        Args:
            labels (Dict[str, Any]): A dictionary containing image data and annotations.
                Must include:
                    'img' (np.ndarray): The input image.
                    'cls' (np.ndarray): Class labels.
                    'instances' (Instances): Object instances with bounding boxes, segments, and keypoints.
                May include:
                    'mosaic_border' (Tuple[int, int]): Border size for mosaic augmentation.

        Returns:
            (Dict[str, Any]): Transformed labels dictionary containing:
                - 'img' (np.ndarray): The transformed image.
                - 'cls' (np.ndarray): Updated class labels.
                - 'instances' (Instances): Updated object instances.
                - 'resized_shape' (Tuple[int, int]): New image shape after transformation.

        Examples:
            >>> transform = RandomPerspective()
            >>> image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            >>> labels = {
            ...     "img": image,
            ...     "cls": np.array([0, 1, 2]),
            ...     "instances": Instances(bboxes=np.array([[10, 10, 50, 50], [100, 100, 150, 150]])),
            ... }
            >>> result = transform(labels)
            >>> assert result["img"].shape[:2] == result["resized_shape"]
        """
        # print("type(self.pre_transform):", type(self.pre_transform))
        # for label in labels:
            # raw_data_imshow(label, False)

        if self.pre_transform and "mosaic_border" not in labels[-1]:
            labels = self.pre_transform(labels)
        
        for label in labels:
            label.pop("ratio_pad", None)  # do not need ratio pad

        imgs = []
        clss = []
        minstances = []
        for label in labels:
            img = label["img"]
            cls = label["cls"]
            instances = label.pop("instances")
            # Make sure the coord formats are right
            instances.convert_bbox(format="xyxy")
            instances.denormalize(*img.shape[:2][::-1])

            border = label.pop("mosaic_border", self.border)

            imgs.append(img)
            clss.append(cls)
            minstances.append(instances)

        self.size = imgs[-1].shape[1] + border[1] * 2, imgs[-1].shape[0] + border[0] * 2  # w, h
        # M is affine matrix
        # Scale for func:`box_candidates`
        imgs, M, scale = self.affine_transform(imgs, border)

        for instances, cls, img, label in zip(minstances, clss, imgs, labels):
            bboxes = self.apply_bboxes(instances.bboxes, M)

            segments = instances.segments
            keypoints = instances.keypoints
            # Update bboxes if there are segments.
            if len(segments):
                bboxes, segments = self.apply_segments(segments, M)

            if keypoints is not None:
                keypoints = self.apply_keypoints(keypoints, M)
            new_instances = Instances(bboxes, segments, keypoints, bbox_format="xyxy", normalized=False)
            # Clip
            new_instances.clip(*self.size)

            # Filter instances
            instances.scale(scale_w=scale, scale_h=scale, bbox_only=True)
            # Make the bboxes have the same scale with new_bboxes
            i = self.box_candidates(
                box1=instances.bboxes.T, box2=new_instances.bboxes.T, area_thr=0.01 if len(segments) else 0.10
            )
            label["instances"] = new_instances[i]
            label["cls"] = cls[i]
            label["img"] = img
            label["resized_shape"] = img.shape[:2]
        
        # for label in labels:
            # raw_data_imshow(label, False)
        
        return labels

    @staticmethod
    def box_candidates(
        box1: np.ndarray,
        box2: np.ndarray,
        wh_thr: int = 2,
        ar_thr: int = 100,
        area_thr: float = 0.1,
        eps: float = 1e-16,
    ) -> np.ndarray:
        """
        Compute candidate boxes for further processing based on size and aspect ratio criteria.

        This method compares boxes before and after augmentation to determine if they meet specified
        thresholds for width, height, aspect ratio, and area. It's used to filter out boxes that have
        been overly distorted or reduced by the augmentation process.

        Args:
            box1 (np.ndarray): Original boxes before augmentation, shape (4, N) where n is the
                number of boxes. Format is [x1, y1, x2, y2] in absolute coordinates.
            box2 (np.ndarray): Augmented boxes after transformation, shape (4, N). Format is
                [x1, y1, x2, y2] in absolute coordinates.
            wh_thr (int): Width and height threshold in pixels. Boxes smaller than this in either
                dimension are rejected.
            ar_thr (int): Aspect ratio threshold. Boxes with an aspect ratio greater than this
                value are rejected.
            area_thr (float): Area ratio threshold. Boxes with an area ratio (new/old) less than
                this value are rejected.
            eps (float): Small epsilon value to prevent division by zero.

        Returns:
            (np.ndarray): Boolean array of shape (n) indicating which boxes are candidates.
                True values correspond to boxes that meet all criteria.

        Examples:
            >>> random_perspective = RandomPerspective()
            >>> box1 = np.array([[0, 0, 100, 100], [0, 0, 50, 50]]).T
            >>> box2 = np.array([[10, 10, 90, 90], [5, 5, 45, 45]]).T
            >>> candidates = random_perspective.box_candidates(box1, box2)
            >>> print(candidates)
            [True True]
        """
        w1, h1 = box1[2] - box1[0], box1[3] - box1[1]
        w2, h2 = box2[2] - box2[0], box2[3] - box2[1]
        ar = np.maximum(w2 / (h2 + eps), h2 / (w2 + eps))  # aspect ratio
        return (w2 > wh_thr) & (h2 > wh_thr) & (w2 * h2 / (w1 * h1 + eps) > area_thr) & (ar < ar_thr)  # candidates


class RandomHSV:
    """
    Randomly adjust the Hue, Saturation, and Value (HSV) channels of an image.

    This class applies random HSV augmentation to images within predefined limits set by hgain, sgain, and vgain.

    Attributes:
        hgain (float): Maximum variation for hue. Range is typically [0, 1].
        sgain (float): Maximum variation for saturation. Range is typically [0, 1].
        vgain (float): Maximum variation for value. Range is typically [0, 1].

    Methods:
        __call__: Apply random HSV augmentation to an image.

    Examples:
        >>> import numpy as np
        >>> from ultralytics.data.augment import RandomHSV
        >>> augmenter = RandomHSV(hgain=0.5, sgain=0.5, vgain=0.5)
        >>> image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        >>> labels = {"img": image}
        >>> augmenter(labels)
        >>> augmented_image = augmented_labels["img"]
    """

    def __init__(self, hgain: float = 0.5, sgain: float = 0.5, vgain: float = 0.5) -> None:
        """
        Initialize the RandomHSV object for random HSV (Hue, Saturation, Value) augmentation.

        This class applies random adjustments to the HSV channels of an image within specified limits.

        Args:
            hgain (float): Maximum variation for hue. Should be in the range [0, 1].
            sgain (float): Maximum variation for saturation. Should be in the range [0, 1].
            vgain (float): Maximum variation for value. Should be in the range [0, 1].

        Examples:
            >>> hsv_aug = RandomHSV(hgain=0.5, sgain=0.5, vgain=0.5)
            >>> hsv_aug(image)
        """
        self.hgain = hgain
        self.sgain = sgain
        self.vgain = vgain

    def __call__(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply random HSV augmentation to an image within predefined limits.

        This method modifies the input image by randomly adjusting its Hue, Saturation, and Value (HSV) channels.
        The adjustments are made within the limits set by hgain, sgain, and vgain during initialization.

        Args:
            labels (Dict[str, Any]): A dictionary containing image data and metadata. Must include an 'img' key with
                the image as a numpy array.

        Returns:
            (Dict[str, Any]): A dictionary containing the mixed image and adjusted labels.

        Examples:
            >>> hsv_augmenter = RandomHSV(hgain=0.5, sgain=0.5, vgain=0.5)
            >>> labels = {"img": np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)}
            >>> labels = hsv_augmenter(labels)
            >>> augmented_img = labels["img"]
        """
        img = labels[-1]["img"]
        if img.shape[-1] != 3:  # only apply to RGB images
            return labels
        if self.hgain or self.sgain or self.vgain:
            dtype = img.dtype  # uint8

            r = np.random.uniform(-1, 1, 3) * [self.hgain, self.sgain, self.vgain]  # random gains
            x = np.arange(0, 256, dtype=r.dtype)
            # lut_hue = ((x * (r[0] + 1)) % 180).astype(dtype)   # original hue implementation from ultralytics<=8.3.78
            lut_hue = ((x + r[0] * 180) % 180).astype(dtype)
            lut_sat = np.clip(x * (r[1] + 1), 0, 255).astype(dtype)
            lut_val = np.clip(x * (r[2] + 1), 0, 255).astype(dtype)
            lut_sat[0] = 0  # prevent pure white changing color, introduced in 8.3.79

            for label in labels:
                hue, sat, val = cv2.split(cv2.cvtColor(label["img"], cv2.COLOR_BGR2HSV))
                im_hsv = cv2.merge((cv2.LUT(hue, lut_hue), cv2.LUT(sat, lut_sat), cv2.LUT(val, lut_val)))
                cv2.cvtColor(im_hsv, cv2.COLOR_HSV2BGR, dst=label["img"])  # no return needed
        return labels


class RandomFlip:
    """
    Apply a random horizontal or vertical flip to an image with a given probability.

    This class performs random image flipping and updates corresponding instance annotations such as
    bounding boxes and keypoints.

    Attributes:
        p (float): Probability of applying the flip. Must be between 0 and 1.
        direction (str): Direction of flip, either 'horizontal' or 'vertical'.
        flip_idx (array-like): Index mapping for flipping keypoints, if applicable.

    Methods:
        __call__: Apply the random flip transformation to an image and its annotations.

    Examples:
        >>> transform = RandomFlip(p=0.5, direction="horizontal")
        >>> result = transform({"img": image, "instances": instances})
        >>> flipped_image = result["img"]
        >>> flipped_instances = result["instances"]
    """

    def __init__(self, p: float = 0.5, direction: str = "horizontal", flip_idx: List[int] = None) -> None:
        """
        Initialize the RandomFlip class with probability and direction.

        This class applies a random horizontal or vertical flip to an image with a given probability.
        It also updates any instances (bounding boxes, keypoints, etc.) accordingly.

        Args:
            p (float): The probability of applying the flip. Must be between 0 and 1.
            direction (str): The direction to apply the flip. Must be 'horizontal' or 'vertical'.
            flip_idx (List[int] | None): Index mapping for flipping keypoints, if any.

        Raises:
            AssertionError: If direction is not 'horizontal' or 'vertical', or if p is not between 0 and 1.

        Examples:
            >>> flip = RandomFlip(p=0.5, direction="horizontal")
            >>> flip_with_idx = RandomFlip(p=0.7, direction="vertical", flip_idx=[1, 0, 3, 2, 5, 4])
        """
        assert direction in {"horizontal", "vertical"}, f"Support direction `horizontal` or `vertical`, got {direction}"
        assert 0 <= p <= 1.0, f"The probability should be in range [0, 1], but got {p}."

        self.p = p
        self.direction = direction
        self.flip_idx = flip_idx

    def __call__(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply random flip to an image and update any instances like bounding boxes or keypoints accordingly.

        This method randomly flips the input image either horizontally or vertically based on the initialized
        probability and direction. It also updates the corresponding instances (bounding boxes, keypoints) to
        match the flipped image.

        Args:
            labels (Dict[str, Any]): A dictionary containing the following keys:
                'img' (np.ndarray): The image to be flipped.
                'instances' (ultralytics.utils.instance.Instances): An object containing bounding boxes and
                    optionally keypoints.

        Returns:
            (Dict[str, Any]): The same dictionary with the flipped image and updated instances:
                'img' (np.ndarray): The flipped image.
                'instances' (ultralytics.utils.instance.Instances): Updated instances matching the flipped image.

        Examples:
            >>> labels = {"img": np.random.rand(640, 640, 3), "instances": Instances(...)}
            >>> random_flip = RandomFlip(p=0.5, direction="horizontal")
            >>> flipped_labels = random_flip(labels)
        """
        imgs = []
        minstances = []
        for label in labels:
            img = label["img"]
            instances = label.pop("instances")
            instances.convert_bbox(format="xywh")

            imgs.append(img)
            minstances.append(instances)

        h, w = imgs[-1].shape[:2]
        h = 1 if minstances[-1].normalized else h
        w = 1 if minstances[-1].normalized else w

        # WARNING: two separate if and calls to random.random() intentional for reproducibility with older versions
        if self.direction == "vertical" and random.random() < self.p:
            for j, (img, instances) in enumerate(zip(imgs, minstances)):
                imgs[j] = np.flipud(img)
                minstances[j].flipud(h)
                if self.flip_idx is not None and instances.keypoints is not None:
                    minstances[j].keypoints = np.ascontiguousarray(instances.keypoints[:, self.flip_idx, :])
        if self.direction == "horizontal" and random.random() < self.p:
            for j, (img, instances) in  enumerate(zip(imgs, minstances)):
                imgs[j] = np.fliplr(img)
                minstances[j].fliplr(w)
                if self.flip_idx is not None and instances.keypoints is not None:
                    minstances[j].keypoints = np.ascontiguousarray(instances.keypoints[:, self.flip_idx, :])
        
        for img, instances, label in zip(imgs, minstances, labels):
            label["img"] = np.ascontiguousarray(img)
            label["instances"] = instances
        return labels


class LetterBox:
    """
    Resize image and padding for detection, instance segmentation, pose.

    This class resizes and pads images to a specified shape while preserving aspect ratio. It also updates
    corresponding labels and bounding boxes.

    Attributes:
        new_shape (tuple): Target shape (height, width) for resizing.
        auto (bool): Whether to use minimum rectangle.
        scale_fill (bool): Whether to stretch the image to new_shape.
        scaleup (bool): Whether to allow scaling up. If False, only scale down.
        stride (int): Stride for rounding padding.
        center (bool): Whether to center the image or align to top-left.

    Methods:
        __call__: Resize and pad image, update labels and bounding boxes.

    Examples:
        >>> transform = LetterBox(new_shape=(640, 640))
        >>> result = transform(labels)
        >>> resized_img = result["img"]
        >>> updated_instances = result["instances"]
    """

    def __init__(
        self,
        new_shape: Tuple[int, int] = (640, 640),
        auto: bool = False,
        scale_fill: bool = False,
        scaleup: bool = True,
        center: bool = True,
        stride: int = 32,
        padding_value: int = 114,
        interpolation: int = cv2.INTER_LINEAR,
    ):
        """
        Initialize LetterBox object for resizing and padding images.

        This class is designed to resize and pad images for object detection, instance segmentation, and pose estimation
        tasks. It supports various resizing modes including auto-sizing, scale-fill, and letterboxing.

        Args:
            new_shape (Tuple[int, int]): Target size (height, width) for the resized image.
            auto (bool): If True, use minimum rectangle to resize. If False, use new_shape directly.
            scale_fill (bool): If True, stretch the image to new_shape without padding.
            scaleup (bool): If True, allow scaling up. If False, only scale down.
            center (bool): If True, center the placed image. If False, place image in top-left corner.
            stride (int): Stride of the model (e.g., 32 for YOLOv5).
            padding_value (int): Value for padding the image. Default is 114.
            interpolation (int): Interpolation method for resizing. Default is cv2.INTER_LINEAR.

        Attributes:
            new_shape (Tuple[int, int]): Target size for the resized image.
            auto (bool): Flag for using minimum rectangle resizing.
            scale_fill (bool): Flag for stretching image without padding.
            scaleup (bool): Flag for allowing upscaling.
            stride (int): Stride value for ensuring image size is divisible by stride.
            padding_value (int): Value used for padding the image.
            interpolation (int): Interpolation method used for resizing.

        Examples:
            >>> letterbox = LetterBox(new_shape=(640, 640), auto=False, scale_fill=False, scaleup=True, stride=32)
            >>> resized_img = letterbox(original_img)
        """
        self.new_shape = new_shape
        self.auto = auto
        self.scale_fill = scale_fill
        self.scaleup = scaleup
        self.stride = stride
        self.center = center  # Put the image in the middle or top-left
        self.padding_value = padding_value
        self.interpolation = interpolation

    def __call__(self, labels: Dict[str, Any] = None, image: np.ndarray = None) -> Union[Dict[str, Any], np.ndarray]:
        """
        Resize and pad an image for object detection, instance segmentation, or pose estimation tasks.

        This method applies letterboxing to the input image, which involves resizing the image while maintaining its
        aspect ratio and adding padding to fit the new shape. It also updates any associated labels accordingly.

        Args:
            labels (Dict[str, Any] | None): A dictionary containing image data and associated labels, or empty dict if None.
            image (np.ndarray | None): The input image as a numpy array. If None, the image is taken from 'labels'.

        Returns:
            (Dict[str, Any] | nd.ndarray): If 'labels' is provided, returns an updated dictionary with the resized and padded image,
                updated labels, and additional metadata. If 'labels' is empty, returns the resized
                and padded image.

        Examples:
            >>> letterbox = LetterBox(new_shape=(640, 640))
            >>> result = letterbox(labels={"img": np.zeros((480, 640, 3)), "instances": Instances(...)})
            >>> resized_img = result["img"]
            >>> updated_instances = result["instances"]
        """
        assert labels is not None and image is None
        imgs = [label.get("img") for label in labels]

        

        shape = imgs[-1].shape[:2]  # current shape [height, width]
        # print(shape)

        for label in labels:
            new_shape = label.pop("rect_shape", self.new_shape)
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not self.scaleup:  # only scale down, do not scale up (for better val mAP)
            r = min(r, 1.0)

        # Compute padding
        ratio = r, r  # width, height ratios
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
        if self.auto:  # minimum rectangle
            dw, dh = np.mod(dw, self.stride), np.mod(dh, self.stride)  # wh padding
        elif self.scale_fill:  # stretch
            dw, dh = 0.0, 0.0
            new_unpad = (new_shape[1], new_shape[0])
            ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

        if self.center:
            dw /= 2  # divide padding into 2 sides
            dh /= 2

        if shape[::-1] != new_unpad:  # resize
            for j, img in enumerate(imgs):
                imgs[j] = cv2.resize(img, new_unpad, interpolation=self.interpolation)
                if imgs[j].ndim == 2:
                    imgs[j] = imgs[j][..., None]

        top, bottom = int(round(dh - 0.1)) if self.center else 0, int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)) if self.center else 0, int(round(dw + 0.1))
        h, w, c = imgs[-1].shape
        for j, img in enumerate(imgs):
            if c == 3:
                imgs[j] = cv2.copyMakeBorder(
                    img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(self.padding_value,) * 3
                )
                # print(img.shape)
            else:  # multispectral
                pad_img = np.full((h + top + bottom, w + left + right, c), fill_value=self.padding_value, dtype=img.dtype)
                pad_img[top : top + h, left : left + w] = img
                imgs[j] = pad_img

        for label in labels:
            if label.get("ratio_pad"):
                label["ratio_pad"] = (label["ratio_pad"], (left, top))  # for evaluation

        if len(labels):
            # for label in labels:
                # raw_data_imshow(label)
            
            # print("ratio, left, top:", ratio, left, top)
            labels = [self._update_labels(label, ratio, left, top) for label in labels]
            for img, label in zip(imgs, labels):
                label["img"] = img
                label["resized_shape"] = new_shape
            
            # for label in labels:
                # raw_data_imshow(label, norm=False)
            return labels
        else:
            return img

    @staticmethod
    def _update_labels(labels: Dict[str, Any], ratio: Tuple[float, float], padw: float, padh: float) -> Dict[str, Any]:
        """
        Update labels after applying letterboxing to an image.

        This method modifies the bounding box coordinates of instances in the labels
        to account for resizing and padding applied during letterboxing.

        Args:
            labels (Dict[str, Any]): A dictionary containing image labels and instances.
            ratio (Tuple[float, float]): Scaling ratios (width, height) applied to the image.
            padw (float): Padding width added to the image.
            padh (float): Padding height added to the image.

        Returns:
            (Dict[str, Any]): Updated labels dictionary with modified instance coordinates.

        Examples:
            >>> letterbox = LetterBox(new_shape=(640, 640))
            >>> labels = {"instances": Instances(...)}
            >>> ratio = (0.5, 0.5)
            >>> padw, padh = 10, 20
            >>> updated_labels = letterbox._update_labels(labels, ratio, padw, padh)
        """
        labels["instances"].convert_bbox(format="xyxy")
        # print("labels[img].shape[:2][::-1]:", labels["img"].shape[:2][::-1])
        labels["instances"].denormalize(*labels["img"].shape[:2][::-1])
        labels["instances"].scale(*ratio)
        labels["instances"].add_padding(padw, padh)
        return labels


class CopyPaste(BaseMixTransform):
    """
    CopyPaste class for applying Copy-Paste augmentation to image datasets.

    This class implements the Copy-Paste augmentation technique as described in the paper "Simple Copy-Paste is a Strong
    Data Augmentation Method for Instance Segmentation" (https://arxiv.org/abs/2012.07177). It combines objects from
    different images to create new training samples.

    Attributes:
        dataset (Any): The dataset to which Copy-Paste augmentation will be applied.
        pre_transform (Callable | None): Optional transform to apply before Copy-Paste.
        p (float): Probability of applying Copy-Paste augmentation.

    Methods:
        _mix_transform: Apply Copy-Paste augmentation to the input labels.
        __call__: Apply the Copy-Paste transformation to images and annotations.

    Examples:
        >>> from ultralytics.data.augment import CopyPaste
        >>> dataset = YourDataset(...)  # Your image dataset
        >>> copypaste = CopyPaste(dataset, p=0.5)
        >>> augmented_labels = copypaste(original_labels)
    """

    def __init__(self, dataset=None, pre_transform=None, p: float = 0.5, mode: str = "flip") -> None:
        """Initialize CopyPaste object with dataset, pre_transform, and probability of applying MixUp."""
        super().__init__(dataset=dataset, pre_transform=pre_transform, p=p)
        assert mode in {"flip", "mixup"}, f"Expected `mode` to be `flip` or `mixup`, but got {mode}."
        self.mode = mode

    def _mix_transform(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Copy-Paste augmentation to combine objects from another image into the current image."""
        labels2 = labels["mix_labels"][0]
        return self._transform(labels, labels2)

    def __call__(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Copy-Paste augmentation to an image and its labels."""
        if len(labels[-1]["instances"].segments) == 0 or self.p == 0:
            return labels
        if self.mode == "flip":
            return self._transform(labels)

        # Get index of one or three other images
        indexes = self.get_indexes()
        if isinstance(indexes, int):
            indexes = [indexes]

        # Get images information will be used for Mosaic or MixUp
        mix_labels = [self.dataset.get_image_and_label(i, forget_i=True) for i in indexes]

        if self.pre_transform is not None:
            for i, data in enumerate(mix_labels):
                mix_labels[i] = self.pre_transform(data)
        labels["mix_labels"] = mix_labels

        # Update cls and texts
        labels = self._update_label_text(labels)
        # Mosaic or MixUp
        labels = self._mix_transform(labels)
        labels.pop("mix_labels", None)
        return labels

    def _transform(self, labels1: Dict[str, Any], labels2: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Apply Copy-Paste augmentation to combine objects from another image into the current image."""
        im = labels1["img"]
        if "mosaic_border" not in labels1:
            im = im.copy()  # avoid modifying original non-mosaic image
        cls = labels1["cls"]
        h, w = im.shape[:2]
        instances = labels1.pop("instances")
        instances.convert_bbox(format="xyxy")
        instances.denormalize(w, h)

        im_new = np.zeros(im.shape, np.uint8)
        instances2 = labels2.pop("instances", None)
        if instances2 is None:
            instances2 = deepcopy(instances)
            instances2.fliplr(w)
        ioa = bbox_ioa(instances2.bboxes, instances.bboxes)  # intersection over area, (N, M)
        indexes = np.nonzero((ioa < 0.30).all(1))[0]  # (N, )
        n = len(indexes)
        sorted_idx = np.argsort(ioa.max(1)[indexes])
        indexes = indexes[sorted_idx]
        for j in indexes[: round(self.p * n)]:
            cls = np.concatenate((cls, labels2.get("cls", cls)[[j]]), axis=0)
            instances = Instances.concatenate((instances, instances2[[j]]), axis=0)
            cv2.drawContours(im_new, instances2.segments[[j]].astype(np.int32), -1, (1, 1, 1), cv2.FILLED)

        result = labels2.get("img", cv2.flip(im, 1))  # augment segments
        if result.ndim == 2:  # cv2.flip would eliminate the last dimension for grayscale images
            result = result[..., None]
        i = im_new.astype(bool)
        im[i] = result[i]

        labels1["img"] = im
        labels1["cls"] = cls
        labels1["instances"] = instances
        return labels1


class Albumentations:
    """
    Albumentations transformations for image augmentation.

    This class applies various image transformations using the Albumentations library. It includes operations such as
    Blur, Median Blur, conversion to grayscale, Contrast Limited Adaptive Histogram Equalization (CLAHE), random changes
    in brightness and contrast, RandomGamma, and image quality reduction through compression.

    Attributes:
        p (float): Probability of applying the transformations.
        transform (albumentations.Compose): Composed Albumentations transforms.
        contains_spatial (bool): Indicates if the transforms include spatial operations.

    Methods:
        __call__: Apply the Albumentations transformations to the input labels.

    Examples:
        >>> transform = Albumentations(p=0.5)
        >>> augmented_labels = transform(labels)

    Notes:
        - The Albumentations package must be installed to use this class.
        - If the package is not installed or an error occurs during initialization, the transform will be set to None.
        - Spatial transforms are handled differently and require special processing for bounding boxes.
    """

    def __init__(self, p: float = 1.0) -> None:
        """
        Initialize the Albumentations transform object for YOLO bbox formatted parameters.

        This class applies various image augmentations using the Albumentations library, including Blur, Median Blur,
        conversion to grayscale, Contrast Limited Adaptive Histogram Equalization, random changes of brightness and
        contrast, RandomGamma, and image quality reduction through compression.

        Args:
            p (float): Probability of applying the augmentations. Must be between 0 and 1.

        Attributes:
            p (float): Probability of applying the augmentations.
            transform (albumentations.Compose): Composed Albumentations transforms.
            contains_spatial (bool): Indicates if the transforms include spatial transformations.

        Raises:
            ImportError: If the Albumentations package is not installed.
            Exception: For any other errors during initialization.

        Examples:
            >>> transform = Albumentations(p=0.5)
            >>> augmented = transform(image=image, bboxes=bboxes, class_labels=classes)
            >>> augmented_image = augmented["image"]
            >>> augmented_bboxes = augmented["bboxes"]

        Notes:
            - Requires Albumentations version 1.0.3 or higher.
            - Spatial transforms are handled differently to ensure bbox compatibility.
            - Some transforms are applied with very low probability (0.01) by default.
        """
        self.p = p
        self.transform = None
        prefix = colorstr("albumentations: ")

        try:
            import os

            os.environ["NO_ALBUMENTATIONS_UPDATE"] = "1"  # suppress Albumentations upgrade message
            import albumentations as A

            check_version(A.__version__, "1.0.3", hard=True)  # version requirement

            # List of possible spatial transforms
            spatial_transforms = {
                "Affine",
                "BBoxSafeRandomCrop",
                "CenterCrop",
                "CoarseDropout",
                "Crop",
                "CropAndPad",
                "CropNonEmptyMaskIfExists",
                "D4",
                "ElasticTransform",
                "Flip",
                "GridDistortion",
                "GridDropout",
                "HorizontalFlip",
                "Lambda",
                "LongestMaxSize",
                "MaskDropout",
                "MixUp",
                "Morphological",
                "NoOp",
                "OpticalDistortion",
                "PadIfNeeded",
                "Perspective",
                "PiecewiseAffine",
                "PixelDropout",
                "RandomCrop",
                "RandomCropFromBorders",
                "RandomGridShuffle",
                "RandomResizedCrop",
                "RandomRotate90",
                "RandomScale",
                "RandomSizedBBoxSafeCrop",
                "RandomSizedCrop",
                "Resize",
                "Rotate",
                "SafeRotate",
                "ShiftScaleRotate",
                "SmallestMaxSize",
                "Transpose",
                "VerticalFlip",
                "XYMasking",
            }  # from https://albumentations.ai/docs/getting_started/transforms_and_targets/#spatial-level-transforms

            # Transforms
            T = [
                A.Blur(p=0.01),
                A.MedianBlur(p=0.01),
                A.ToGray(p=0.01),
                A.CLAHE(p=0.01),
                A.RandomBrightnessContrast(p=0.0),
                A.RandomGamma(p=0.0),
                A.ImageCompression(quality_range=(75, 100), p=0.0),
            ]

            # Compose transforms
            self.contains_spatial = any(transform.__class__.__name__ in spatial_transforms for transform in T)
            self.transform = (
                A.Compose(T, bbox_params=A.BboxParams(format="yolo", label_fields=["class_labels"]))
                if self.contains_spatial
                else A.Compose(T)
            )
            if hasattr(self.transform, "set_random_seed"):
                # Required for deterministic transforms in albumentations>=1.4.21
                print("albumentations>=1.4.21")
                self.transform.set_random_seed(torch.initial_seed())
            LOGGER.info(prefix + ", ".join(f"{x}".replace("always_apply=False, ", "") for x in T if x.p))
        except ImportError:  # package not installed, skip
            pass
        except Exception as e:
            LOGGER.info(f"{prefix}{e}")

    def __call__(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply Albumentations transformations to input labels.

        This method applies a series of image augmentations using the Albumentations library. It can perform both
        spatial and non-spatial transformations on the input image and its corresponding labels.

        Args:
            labels (Dict[str, Any]): A dictionary containing image data and annotations. Expected keys are:
                - 'img': np.ndarray representing the image
                - 'cls': np.ndarray of class labels
                - 'instances': object containing bounding boxes and other instance information

        Returns:
            (Dict[str, Any]): The input dictionary with augmented image and updated annotations.

        Examples:
            >>> transform = Albumentations(p=0.5)
            >>> labels = {
            ...     "img": np.random.rand(640, 640, 3),
            ...     "cls": np.array([0, 1]),
            ...     "instances": Instances(bboxes=np.array([[0, 0, 1, 1], [0.5, 0.5, 0.8, 0.8]])),
            ... }
            >>> augmented = transform(labels)
            >>> assert augmented["img"].shape == (640, 640, 3)

        Notes:
            - The method applies transformations with probability self.p.
            - Spatial transforms update bounding boxes, while non-spatial transforms only modify the image.
            - Requires the Albumentations library to be installed.
        """
        if self.transform is None or random.random() > self.p:
            return labels

        im = labels["img"]
        if im.shape[2] != 3:  # Only apply Albumentation on 3-channel images
            return labels

        if self.contains_spatial:
            cls = labels["cls"]
            if len(cls):
                labels["instances"].convert_bbox("xywh")
                labels["instances"].normalize(*im.shape[:2][::-1])
                bboxes = labels["instances"].bboxes
                # TODO: add supports of segments and keypoints
                new = self.transform(image=im, bboxes=bboxes, class_labels=cls)  # transformed
                if len(new["class_labels"]) > 0:  # skip update if no bbox in new im
                    labels["img"] = new["image"]
                    labels["cls"] = np.array(new["class_labels"])
                    bboxes = np.array(new["bboxes"], dtype=np.float32)
                labels["instances"].update(bboxes=bboxes)
        else:
            labels["img"] = self.transform(image=labels["img"])["image"]  # transformed

        return labels


class Format:
    """
    A class for formatting image annotations for object detection, instance segmentation, and pose estimation tasks.

    This class standardizes image and instance annotations to be used by the `collate_fn` in PyTorch DataLoader.

    Attributes:
        bbox_format (str): Format for bounding boxes. Options are 'xywh' or 'xyxy'.
        normalize (bool): Whether to normalize bounding boxes.
        return_mask (bool): Whether to return instance masks for segmentation.
        return_keypoint (bool): Whether to return keypoints for pose estimation.
        return_obb (bool): Whether to return oriented bounding boxes.
        mask_ratio (int): Downsample ratio for masks.
        mask_overlap (bool): Whether to overlap masks.
        batch_idx (bool): Whether to keep batch indexes.
        bgr (float): The probability to return BGR images.

    Methods:
        __call__: Format labels dictionary with image, classes, bounding boxes, and optionally masks and keypoints.
        _format_img: Convert image from Numpy array to PyTorch tensor.
        _format_segments: Convert polygon points to bitmap masks.

    Examples:
        >>> formatter = Format(bbox_format="xywh", normalize=True, return_mask=True)
        >>> formatted_labels = formatter(labels)
        >>> img = formatted_labels["img"]
        >>> bboxes = formatted_labels["bboxes"]
        >>> masks = formatted_labels["masks"]
    """

    def __init__(
        self,
        bbox_format: str = "xywh",
        normalize: bool = True,
        return_mask: bool = False,
        return_keypoint: bool = False,
        return_obb: bool = False,
        mask_ratio: int = 4,
        mask_overlap: bool = True,
        batch_idx: bool = True,
        bgr: float = 0.0,
    ):
        """
        Initialize the Format class with given parameters for image and instance annotation formatting.

        This class standardizes image and instance annotations for object detection, instance segmentation, and pose
        estimation tasks, preparing them for use in PyTorch DataLoader's `collate_fn`.

        Args:
            bbox_format (str): Format for bounding boxes. Options are 'xywh', 'xyxy', etc.
            normalize (bool): Whether to normalize bounding boxes to [0,1].
            return_mask (bool): If True, returns instance masks for segmentation tasks.
            return_keypoint (bool): If True, returns keypoints for pose estimation tasks.
            return_obb (bool): If True, returns oriented bounding boxes.
            mask_ratio (int): Downsample ratio for masks.
            mask_overlap (bool): If True, allows mask overlap.
            batch_idx (bool): If True, keeps batch indexes.
            bgr (float): Probability of returning BGR images instead of RGB.

        Attributes:
            bbox_format (str): Format for bounding boxes.
            normalize (bool): Whether bounding boxes are normalized.
            return_mask (bool): Whether to return instance masks.
            return_keypoint (bool): Whether to return keypoints.
            return_obb (bool): Whether to return oriented bounding boxes.
            mask_ratio (int): Downsample ratio for masks.
            mask_overlap (bool): Whether masks can overlap.
            batch_idx (bool): Whether to keep batch indexes.
            bgr (float): The probability to return BGR images.

        Examples:
            >>> format = Format(bbox_format="xyxy", return_mask=True, return_keypoint=False)
            >>> print(format.bbox_format)
            xyxy
        """
        self.bbox_format = bbox_format
        self.normalize = normalize
        self.return_mask = return_mask  # set False when training detection only
        self.return_keypoint = return_keypoint
        self.return_obb = return_obb
        self.mask_ratio = mask_ratio
        self.mask_overlap = mask_overlap
        self.batch_idx = batch_idx  # keep the batch indexes
        self.bgr = bgr

    def __call__(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format image annotations for object detection, instance segmentation, and pose estimation tasks.

        This method standardizes the image and instance annotations to be used by the `collate_fn` in PyTorch
        DataLoader. It processes the input labels dictionary, converting annotations to the specified format and
        applying normalization if required.

        Args:
            labels (Dict[str, Any]): A dictionary containing image and annotation data with the following keys:
                - 'img': The input image as a numpy array.
                - 'cls': Class labels for instances.
                - 'instances': An Instances object containing bounding boxes, segments, and keypoints.

        Returns:
            (Dict[str, Any]): A dictionary with formatted data, including:
                - 'img': Formatted image tensor.
                - 'cls': Class label's tensor.
                - 'bboxes': Bounding boxes tensor in the specified format.
                - 'masks': Instance masks tensor (if return_mask is True).
                - 'keypoints': Keypoints tensor (if return_keypoint is True).
                - 'batch_idx': Batch index tensor (if batch_idx is True).

        Examples:
            >>> formatter = Format(bbox_format="xywh", normalize=True, return_mask=True)
            >>> labels = {"img": np.random.rand(640, 640, 3), "cls": np.array([0, 1]), "instances": Instances(...)}
            >>> formatted_labels = formatter(labels)
            >>> print(formatted_labels.keys())
        """
        # for label in labels:
        #     raw_data_imshow(label)
        for label in labels:
            img = label.pop("img")
            h, w = img.shape[:2]
            cls = label.pop("cls")
            instances = label.pop("instances")
            instances.convert_bbox(format=self.bbox_format)
            instances.denormalize(w, h)
            nl = len(instances)

            if self.return_mask:
                if nl:
                    masks, instances, cls = self._format_segments(instances, cls, w, h)
                    masks = torch.from_numpy(masks)
                else:
                    masks = torch.zeros(
                        1 if self.mask_overlap else nl, img.shape[0] // self.mask_ratio, img.shape[1] // self.mask_ratio
                    )
                label["masks"] = masks
            label["img"] = self._format_img(img)
            label["cls"] = torch.from_numpy(cls) if nl else torch.zeros(nl)
            label["bboxes"] = torch.from_numpy(instances.bboxes) if nl else torch.zeros((nl, 4))
            if self.return_keypoint:
                label["keypoints"] = (
                    torch.empty(0, 3) if instances.keypoints is None else torch.from_numpy(instances.keypoints)
                )
                if self.normalize:
                    label["keypoints"][..., 0] /= w
                    label["keypoints"][..., 1] /= h
            if self.return_obb:
                label["bboxes"] = (
                    xyxyxyxy2xywhr(torch.from_numpy(instances.segments)) if len(instances.segments) else torch.zeros((0, 5))
                )
            # NOTE: need to normalize obb in xywhr format for width-height consistency
            if self.normalize:
                label["bboxes"][:, [0, 2]] /= w
                label["bboxes"][:, [1, 3]] /= h
            # Then we can use collate_fn
            if self.batch_idx:
                label["batch_idx"] = torch.zeros(nl)
        return labels

    def _format_img(self, img: np.ndarray) -> torch.Tensor:
        """
        Format an image for YOLO from a Numpy array to a PyTorch tensor.

        This function performs the following operations:
        1. Ensures the image has 3 dimensions (adds a channel dimension if needed).
        2. Transposes the image from HWC to CHW format.
        3. Optionally flips the color channels from RGB to BGR.
        4. Converts the image to a contiguous array.
        5. Converts the Numpy array to a PyTorch tensor.

        Args:
            img (np.ndarray): Input image as a Numpy array with shape (H, W, C) or (H, W).

        Returns:
            (torch.Tensor): Formatted image as a PyTorch tensor with shape (C, H, W).

        Examples:
            >>> import numpy as np
            >>> img = np.random.rand(100, 100, 3)
            >>> formatted_img = self._format_img(img)
            >>> print(formatted_img.shape)
            torch.Size([3, 100, 100])
        """
        if len(img.shape) < 3:
            img = np.expand_dims(img, -1)
        img = img.transpose(2, 0, 1)
        img = np.ascontiguousarray(img[::-1] if random.uniform(0, 1) > self.bgr and img.shape[0] == 3 else img)
        img = torch.from_numpy(img)
        return img

    def _format_segments(
        self, instances: Instances, cls: np.ndarray, w: int, h: int
    ) -> Tuple[np.ndarray, Instances, np.ndarray]:
        """
        Convert polygon segments to bitmap masks.

        Args:
            instances (Instances): Object containing segment information.
            cls (np.ndarray): Class labels for each instance.
            w (int): Width of the image.
            h (int): Height of the image.

        Returns:
            masks (np.ndarray): Bitmap masks with shape (N, H, W) or (1, H, W) if mask_overlap is True.
            instances (Instances): Updated instances object with sorted segments if mask_overlap is True.
            cls (np.ndarray): Updated class labels, sorted if mask_overlap is True.

        Notes:
            - If self.mask_overlap is True, masks are overlapped and sorted by area.
            - If self.mask_overlap is False, each mask is represented separately.
            - Masks are downsampled according to self.mask_ratio.
        """
        segments = instances.segments
        if self.mask_overlap:
            masks, sorted_idx = polygons2masks_overlap((h, w), segments, downsample_ratio=self.mask_ratio)
            masks = masks[None]  # (640, 640) -> (1, 640, 640)
            instances = instances[sorted_idx]
            cls = cls[sorted_idx]
        else:
            masks = polygons2masks((h, w), segments, color=1, downsample_ratio=self.mask_ratio)

        return masks, instances, cls


class LoadVisualPrompt:
    """Create visual prompts from bounding boxes or masks for model input."""

    def __init__(self, scale_factor: float = 1 / 8) -> None:
        """
        Initialize the LoadVisualPrompt with a scale factor.

        Args:
            scale_factor (float): Factor to scale the input image dimensions.
        """
        self.scale_factor = scale_factor

    def make_mask(self, boxes: torch.Tensor, h: int, w: int) -> torch.Tensor:
        """
        Create binary masks from bounding boxes.

        Args:
            boxes (torch.Tensor): Bounding boxes in xyxy format, shape: (N, 4).
            h (int): Height of the mask.
            w (int): Width of the mask.

        Returns:
            (torch.Tensor): Binary masks with shape (N, h, w).
        """
        x1, y1, x2, y2 = torch.chunk(boxes[:, :, None], 4, 1)  # x1 shape(n,1,1)
        r = torch.arange(w)[None, None, :]  # rows shape(1,1,w)
        c = torch.arange(h)[None, :, None]  # cols shape(1,h,1)

        return (r >= x1) * (r < x2) * (c >= y1) * (c < y2)

    def __call__(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process labels to create visual prompts.

        Args:
            labels (Dict[str, Any]): Dictionary containing image data and annotations.

        Returns:
            (Dict[str, Any]): Updated labels with visual prompts added.
        """
        imgsz = labels["img"].shape[1:]
        bboxes, masks = None, None
        if "bboxes" in labels:
            bboxes = labels["bboxes"]
            bboxes = xywh2xyxy(bboxes) * torch.tensor(imgsz)[[1, 0, 1, 0]]  # denormalize boxes

        cls = labels["cls"].squeeze(-1).to(torch.int)
        visuals = self.get_visuals(cls, imgsz, bboxes=bboxes, masks=masks)
        labels["visuals"] = visuals
        return labels

    def get_visuals(
        self,
        category: Union[int, np.ndarray, torch.Tensor],
        shape: Tuple[int, int],
        bboxes: Union[np.ndarray, torch.Tensor] = None,
        masks: Union[np.ndarray, torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Generate visual masks based on bounding boxes or masks.

        Args:
            category (int | np.ndarray | torch.Tensor): The category labels for the objects.
            shape (Tuple[int, int]): The shape of the image (height, width).
            bboxes (np.ndarray | torch.Tensor, optional): Bounding boxes for the objects, xyxy format.
            masks (np.ndarray | torch.Tensor, optional): Masks for the objects.

        Returns:
            (torch.Tensor): A tensor containing the visual masks for each category.

        Raises:
            ValueError: If neither bboxes nor masks are provided.
        """
        masksz = (int(shape[0] * self.scale_factor), int(shape[1] * self.scale_factor))
        if bboxes is not None:
            if isinstance(bboxes, np.ndarray):
                bboxes = torch.from_numpy(bboxes)
            bboxes *= self.scale_factor
            masks = self.make_mask(bboxes, *masksz).float()
        elif masks is not None:
            if isinstance(masks, np.ndarray):
                masks = torch.from_numpy(masks)  # (N, H, W)
            masks = F.interpolate(masks.unsqueeze(1), masksz, mode="nearest").squeeze(1).float()
        else:
            raise ValueError("LoadVisualPrompt must have bboxes or masks in the label")
        if not isinstance(category, torch.Tensor):
            category = torch.tensor(category, dtype=torch.int)
        cls_unique, inverse_indices = torch.unique(category, sorted=True, return_inverse=True)
        # NOTE: `cls` indices from RandomLoadText should be continuous.
        # if len(cls_unique):
        #     assert len(cls_unique) == cls_unique[-1] + 1, (
        #         f"Expected a continuous range of class indices, but got {cls_unique}"
        #     )
        visuals = torch.zeros(len(cls_unique), *masksz)
        for idx, mask in zip(inverse_indices, masks):
            visuals[idx] = torch.logical_or(visuals[idx], mask)
        return visuals


class RandomLoadText:
    """
    Randomly sample positive and negative texts and update class indices accordingly.

    This class is responsible for sampling texts from a given set of class texts, including both positive
    (present in the image) and negative (not present in the image) samples. It updates the class indices
    to reflect the sampled texts and can optionally pad the text list to a fixed length.

    Attributes:
        prompt_format (str): Format string for text prompts.
        neg_samples (Tuple[int, int]): Range for randomly sampling negative texts.
        max_samples (int): Maximum number of different text samples in one image.
        padding (bool): Whether to pad texts to max_samples.
        padding_value (str): The text used for padding when padding is True.

    Methods:
        __call__: Process the input labels and return updated classes and texts.

    Examples:
        >>> loader = RandomLoadText(prompt_format="Object: {}", neg_samples=(5, 10), max_samples=20)
        >>> labels = {"cls": [0, 1, 2], "texts": [["cat"], ["dog"], ["bird"]], "instances": [...]}
        >>> updated_labels = loader(labels)
        >>> print(updated_labels["texts"])
        ['Object: cat', 'Object: dog', 'Object: bird', 'Object: elephant', 'Object: car']
    """

    def __init__(
        self,
        prompt_format: str = "{}",
        neg_samples: Tuple[int, int] = (80, 80),
        max_samples: int = 80,
        padding: bool = False,
        padding_value: List[str] = [""],
    ) -> None:
        """
        Initialize the RandomLoadText class for randomly sampling positive and negative texts.

        This class is designed to randomly sample positive texts and negative texts, and update the class
        indices accordingly to the number of samples. It can be used for text-based object detection tasks.

        Args:
            prompt_format (str): Format string for the prompt. The format string should
                contain a single pair of curly braces {} where the text will be inserted.
            neg_samples (Tuple[int, int]): A range to randomly sample negative texts. The first integer
                specifies the minimum number of negative samples, and the second integer specifies the
                maximum.
            max_samples (int): The maximum number of different text samples in one image.
            padding (bool): Whether to pad texts to max_samples. If True, the number of texts will always
                be equal to max_samples.
            padding_value (str): The padding text to use when padding is True.

        Attributes:
            prompt_format (str): The format string for the prompt.
            neg_samples (Tuple[int, int]): The range for sampling negative texts.
            max_samples (int): The maximum number of text samples.
            padding (bool): Whether padding is enabled.
            padding_value (str): The value used for padding.

        Examples:
            >>> random_load_text = RandomLoadText(prompt_format="Object: {}", neg_samples=(50, 100), max_samples=120)
            >>> random_load_text.prompt_format
            'Object: {}'
            >>> random_load_text.neg_samples
            (50, 100)
            >>> random_load_text.max_samples
            120
        """
        self.prompt_format = prompt_format
        self.neg_samples = neg_samples
        self.max_samples = max_samples
        self.padding = padding
        self.padding_value = padding_value

    def __call__(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Randomly sample positive and negative texts and update class indices accordingly.

        This method samples positive texts based on the existing class labels in the image, and randomly
        selects negative texts from the remaining classes. It then updates the class indices to match the
        new sampled text order.

        Args:
            labels (Dict[str, Any]): A dictionary containing image labels and metadata. Must include 'texts' and 'cls' keys.

        Returns:
            (Dict[str, Any]): Updated labels dictionary with new 'cls' and 'texts' entries.

        Examples:
            >>> loader = RandomLoadText(prompt_format="A photo of {}", neg_samples=(5, 10), max_samples=20)
            >>> labels = {"cls": np.array([[0], [1], [2]]), "texts": [["dog"], ["cat"], ["bird"]]}
            >>> updated_labels = loader(labels)
        """
        assert "texts" in labels, "No texts found in labels."
        class_texts = labels["texts"]
        num_classes = len(class_texts)
        cls = np.asarray(labels.pop("cls"), dtype=int)
        pos_labels = np.unique(cls).tolist()

        if len(pos_labels) > self.max_samples:
            pos_labels = random.sample(pos_labels, k=self.max_samples)

        neg_samples = min(min(num_classes, self.max_samples) - len(pos_labels), random.randint(*self.neg_samples))
        neg_labels = [i for i in range(num_classes) if i not in pos_labels]
        neg_labels = random.sample(neg_labels, k=neg_samples)

        sampled_labels = pos_labels + neg_labels
        # Randomness
        # random.shuffle(sampled_labels)

        label2ids = {label: i for i, label in enumerate(sampled_labels)}
        valid_idx = np.zeros(len(labels["instances"]), dtype=bool)
        new_cls = []
        for i, label in enumerate(cls.squeeze(-1).tolist()):
            if label not in label2ids:
                continue
            valid_idx[i] = True
            new_cls.append([label2ids[label]])
        labels["instances"] = labels["instances"][valid_idx]
        labels["cls"] = np.array(new_cls)

        # Randomly select one prompt when there's more than one prompts
        texts = []
        for label in sampled_labels:
            prompts = class_texts[label]
            assert len(prompts) > 0
            prompt = self.prompt_format.format(prompts[random.randrange(len(prompts))])
            texts.append(prompt)

        if self.padding:
            valid_labels = len(pos_labels) + len(neg_labels)
            num_padding = self.max_samples - valid_labels
            if num_padding > 0:
                texts += random.choices(self.padding_value, k=num_padding)

        assert len(texts) == self.max_samples
        labels["texts"] = texts
        return labels


def polygon2mask(imgsz, polygons, color=1, downsample_ratio=1):
    """
    Convert a list of polygons to a binary mask of the specified image size.

    Args:
        imgsz (tuple): The size of the image as (height, width).
        polygons (list[np.ndarray]): A list of polygons. Each polygon is an array with shape [N, M], where
                                     N is the number of polygons, and M is the number of points such that M % 2 = 0.
        color (int, optional): The color value to fill in the polygons on the mask. Defaults to 1.
        downsample_ratio (int, optional): Factor by which to downsample the mask. Defaults to 1.

    Returns:
        (np.ndarray): A binary mask of the specified image size with the polygons filled in.
    """
    mask = np.zeros(imgsz, dtype=np.uint8)
    polygons = np.asarray(polygons, dtype=np.int32)
    polygons = polygons.reshape((polygons.shape[0], -1, 2))
    cv2.fillPoly(mask, polygons, color=color)
    nh, nw = (imgsz[0] // downsample_ratio, imgsz[1] // downsample_ratio)
    # Note: fillPoly first then resize is trying to keep the same loss calculation method when mask-ratio=1
    return cv2.resize(mask, (nw, nh))


def polygons2masks(imgsz, polygons, color, downsample_ratio=1):
    """
    Convert a list of polygons to a set of binary masks of the specified image size.

    Args:
        imgsz (tuple): The size of the image as (height, width).
        polygons (list[np.ndarray]): A list of polygons. Each polygon is an array with shape [N, M], where
                                     N is the number of polygons, and M is the number of points such that M % 2 = 0.
        color (int): The color value to fill in the polygons on the masks.
        downsample_ratio (int, optional): Factor by which to downsample each mask. Defaults to 1.

    Returns:
        (np.ndarray): A set of binary masks of the specified image size with the polygons filled in.
    """
    return np.array([polygon2mask(imgsz, [x.reshape(-1)], color, downsample_ratio) for x in polygons])


def polygons2masks_overlap(imgsz, segments, downsample_ratio=1):
    """Return a (640, 640) overlap mask."""
    masks = np.zeros(
        (imgsz[0] // downsample_ratio, imgsz[1] // downsample_ratio),
        dtype=np.int32 if len(segments) > 255 else np.uint8,
    )
    areas = []
    ms = []
    for si in range(len(segments)):
        mask = polygon2mask(imgsz, [segments[si].reshape(-1)], downsample_ratio=downsample_ratio, color=1)
        ms.append(mask.astype(masks.dtype))
        areas.append(mask.sum())
    areas = np.asarray(areas)
    index = np.argsort(-areas)
    ms = np.array(ms)[index]
    for i in range(len(segments)):
        mask = ms[i] * (i + 1)
        masks = masks + mask
        masks = np.clip(masks, a_min=0, a_max=i + 1)
    return masks, index


class YOLO11VIDTrainLoaderNode(threading.Thread, BaseNode, Dataset):
    def __init__(
        self,
        job_name: str,
        ip: str = '127.0.0.1',
        port: int = 9094,
        param_dict_or_file: Union[dict, str] = None,
        **kwargs
    ):
        Dataset.__init__(self)
        threading.Thread.__init__(self)
        BaseNode.__init__(
            self,
            self.__class__.__name__,
            job_name,
            ip=ip,
            port=port,
            param_dict_or_file=param_dict_or_file,
            sms_shutdown=False,
            sms_logger=True,
            **kwargs
        )
        self.spire_root_dir = self.get_param("spire_root_dir", "/home/amov/spirecv-training-pro/datasets/SV-Box_VID4-ARD-MAV-val_2025-11-24")
        self.spire_json_name = self.get_param("spire_json_name", "")
        self.task = self.get_param("task", "detect")  # detect, segment, pose, obb
        self.mode = self.get_param("mode", "train")
        self.imgsz = self.get_param("imgsz", 1280)
        self.seq_len = self.get_param("seq_len", 3)
        self.rate = self.get_param("rate", 10.0)
        self.epoch = self.get_param("epoch", 1)
        self.flip_idx = self.get_param("flip_idx", [])
        self.kpt_shape = self.get_param("kpt_shape", [8, 3])
        self.names = self.get_param("names", ['Drone'])
        self.augment = self.get_param("augment", True)
        self.prefix = self.get_param("prefix", "")
        self.fraction = self.get_param("fraction", 1.0)
        self.rect = self.get_param("rect", False)
        self.batch_size = self.get_param("batch_size", 16)
        self.stride = self.get_param("stride", 32)
        self.pad = self.get_param("pad", 0.5)
        self.hsv_h = self.get_param("hsv_h", 0.015)  # (float) image HSV-Hue augmentation (fraction)
        self.hsv_s = self.get_param("hsv_s", 0.7)  # (float) image HSV-Saturation augmentation (fraction)
        self.hsv_v = self.get_param("hsv_v", 0.4)  # (float) image HSV-Value augmentation (fraction)
        self.degrees = self.get_param("degrees", 0.0)  # (float) image rotation (+/- deg)
        self.translate = self.get_param("translate", 0.1)  # (float) image translation (+/- fraction)
        self.scale = self.get_param("scale", 0.5)  # (float) image scale (+/- gain)
        self.shear = self.get_param("shear", 0.0)  # (float) image shear (+/- deg)
        self.perspective = self.get_param("perspective", 0.0)  # (float) image perspective (+/- fraction), range 0-0.001
        self.flipud = self.get_param("flipud", 0.0)  # (float) image flip up-down (probability)
        self.fliplr = self.get_param("fliplr", 0.5)  # (float) image flip left-right (probability)
        self.bgr = self.get_param("bgr", 0.0)  # (float) image channel BGR (probability)
        self.mosaic = self.get_param("mosaic", 1.0)  # (float) image mosaic (probability)
        self.mixup = self.get_param("mixup", 0.0)  # (float) image mixup (probability)
        self.cutmix = self.get_param("cutmix", 0.0)  # (float) image cutmix (probability)
        self.copy_paste = self.get_param("copy_paste", 0.0)  # (float) segment copy-paste (probability)
        self.copy_paste_mode = self.get_param("copy_paste_mode", "flip")  # (str) the method to do copy_paste augmentation (flip, mixup)
        self.overlap_mask = self.get_param("overlap_mask", True)  # (bool) merge object masks into a single image mask during training (segment train only)
        self.mask_ratio = self.get_param("mask_ratio", 4)  # (int) mask downsample ratio (segment train only)
        self.channels = self.get_param("channels", 3)
        self.use_shm = self.get_param("use_shm", -1)
        self.params_help()

        self.logger.info("mode={}, batch={}, augment={}, mosaic={}".format(self.mode, self.batch_size, self.augment, self.mosaic))
        self.cv2_flag = cv2.IMREAD_GRAYSCALE if self.channels == 1 else cv2.IMREAD_COLOR

        self.b_use_shm = False
        if self.use_shm == 1 or (self.use_shm == -1 and platform.system() == 'Linux'):
            self.b_use_shm = True

        self._image_writer = Publisher(
            '/' + job_name + '/sensor/image_raw', 'memory_msgs::RawImage' if self.b_use_shm else 'sensor_msgs::CompressedImage',
            ip=ip, port=port, qos=QoS.Reliability
        )

        self.client_id = str(uuid.uuid4()).replace('-', '_')
        self.img_i_queue = Queue()
        self.queue_pool.append(self.img_i_queue)
        self.img_i = 0

        if len(self.spire_json_name) == 0:
            json_files = [os.path.basename(f) for f in glob.glob(os.path.join(self.spire_root_dir, '*')) if f.endswith('.json')]
            assert len(json_files) > 0, "No JSON Files in [{}]".format(self.spire_root_dir)
            sorted_json_files = sorted(json_files, key=os.path.basename, reverse=True)
            self.spire_json_fn = sorted_json_files[0]
            self.logger.info("Use JSON File: {} in [{}]".format(self.spire_json_fn, self.spire_root_dir))
        else:
            self.spire_json_fn = self.spire_json_name


        self.use_segments = self.task == "segment"
        self.use_keypoints = self.task == "pose"
        self.use_obb = self.task == "obb"
        self.data = None
        assert not (self.use_segments and self.use_keypoints), "Can not use both segments and keypoints."

        self._load_dataset()
        self.im_files, self.labels = self.get_img_files_and_labels()
        self.ni = len(self.labels)  # number of images

        if self.rect:
            assert self.batch_size is not None
            self.set_rectangle()

        # Buffer thread for mosaic images
        self.buffer = []  # buffer size = batch size
        self.buffer_lock = threading.Lock()
        self.load_image_lock = threading.Lock()
        self.max_buffer_length = min((self.ni, self.batch_size * 8, 1000)) if self.augment else 0
        # print("self.max_buffer_length:", self.max_buffer_length)
        self.cache = None
        self.ims, self.im_hw0, self.im_hw = [None] * self.ni, [None] * self.ni, [None] * self.ni
        # self.npy_files = [Path(f).with_suffix(".npy") for f in self.im_files]

        # Transforms
        self.transforms = self.build_transforms()

        # self.start()

    def release(self):
        BaseNode.release(self)
        self._image_writer.kill()

    def __len__(self):
        """Returns the length of the labels list for the dataset."""
        return len(self.labels)

    def __getitem__(self, index: int) -> Dict[str, Any]:
        """Returns transformed label information for given index."""
        return self.transforms(self.get_image_and_label(index))

    def close_mosaic(self, hyp: Dict = None) -> None:
        """Sets mosaic, copy_paste and mixup options to 0.0 and builds transformations."""
        self.mosaic = self.set_param("mosaic", 0.0)  # set mosaic ratio=0.0
        self.copy_paste = self.set_param("copy_paste", 0.0)  # keep the same behavior as previous v8 close-mosaic
        self.mixup = self.set_param("mixup", 0.0)  # keep the same behavior as previous v8 close-mosaic
        self.cutmix = self.set_param("cutmix", 0.0)
        self.transforms = self.build_transforms()

    def get_image_and_label(self, index: int, forget_i: bool = False) -> Dict[str, Any]:
        """
        Get and return label information from the dataset.

        Args:
            index (int): Index of the image to retrieve.

        Returns:
            (Dict[str, Any]): Label dictionary with image and metadata.
        """
        label = [deepcopy(l) for l in self.labels[index]]  # requires deepcopy() https://github.com/ultralytics/ultralytics/pull/1948
        for slabel in label:
            slabel.pop("shape", None)  # shape is for rect, remove it
        imgs, ori_shape, resized_shape = self.load_image(index, forget_i=forget_i)
        for slabel, img in zip(label, imgs):
            slabel["img"] = img
            slabel["ori_shape"] = ori_shape
            slabel["resized_shape"] = resized_shape
            slabel["ratio_pad"] = (
                slabel["resized_shape"][0] / slabel["ori_shape"][0],
                slabel["resized_shape"][1] / slabel["ori_shape"][1],
            )  # for evaluation
            # print(slabel.keys())
            # print(slabel["ratio_pad"])

        # assert label["ori_shape"][0] == label["shape"][0] and label["ori_shape"][1] == label["shape"][1]
        if self.rect:
            for slabel in label:
                slabel["rect_shape"] = self.batch_shapes[self.batch[index]]
        return self.update_labels_info(label)

    def update_labels_info(self, label: Dict) -> Dict:
        """
        Update label format for different tasks.

        Args:
            label (dict): Label dictionary containing bboxes, segments, keypoints, etc.

        Returns:
            (dict): Updated label dictionary with instances.

        Note:
            cls is not with bboxes now, classification and semantic segmentation need an independent cls label
            Can also support classification and semantic segmentation by adding or removing dict keys there.
        """
        for slabel in label:
            bboxes = slabel.pop("bboxes")
            segments = slabel.pop("segments", [])
            keypoints = slabel.pop("keypoints", None)
            bbox_format = slabel.pop("bbox_format")
            normalized = slabel.pop("normalized")

            # NOTE: do NOT resample oriented boxes
            segment_resamples = 100 if self.use_obb else 1000
            if len(segments) > 0:
                # make sure segments interpolate correctly if original length is greater than segment_resamples
                max_len = max(len(s) for s in segments)
                segment_resamples = (max_len + 1) if segment_resamples < max_len else segment_resamples
                # list[np.array(segment_resamples, 2)] * num_samples
                segments = np.stack(resample_segments(segments, n=segment_resamples), axis=0)
            else:
                segments = np.zeros((0, segment_resamples, 2), dtype=np.float32)
            slabel["instances"] = Instances(bboxes, segments, keypoints, bbox_format=bbox_format, normalized=normalized)
        return label

    def load_image(self, i: int, rect_mode: bool = True, forget_i: bool = False) -> Tuple[np.ndarray, Tuple[int, int], Tuple[int, int]]:
        """
        Load an image from dataset index 'i'.

        Args:
            i (int): Index of the image to load.
            rect_mode (bool): Whether to use rectangular resizing.

        Returns:
            im (np.ndarray): Loaded image as a NumPy array.
            hw_original (Tuple[int, int]): Original image dimensions in (height, width) format.
            hw_resized (Tuple[int, int]): Resized image dimensions in (height, width) format.

        Raises:
            FileNotFoundError: If the image file is not found.
        """
        im, f = self.ims[i], self.im_files[i]
        if im is None:  # not cached in RAM
            with self.load_image_lock:
                im = [safe_load_image(sf, flags=self.cv2_flag) for sf in f]  # BGR
            if im[-1] is None:
                raise FileNotFoundError(f"Image Not Found {f}")

            h0, w0 = im[-1].shape[:2]  # orig hw
            if rect_mode:  # resize long side to imgsz while maintaining aspect ratio
                r = self.imgsz / max(h0, w0)  # ratio
                if r != 1:  # if sizes are not equal
                    w, h = (min(math.ceil(w0 * r), self.imgsz), min(math.ceil(h0 * r), self.imgsz))
                    for j, sim in enumerate(im):
                        im[j] = cv2.resize(sim, (w, h), interpolation=cv2.INTER_LINEAR)
            elif not (h0 == w0 == self.imgsz):  # resize by stretching image to square imgsz
                for j, sim in enumerate(im):
                    im[j] = cv2.resize(sim, (self.imgsz, self.imgsz), interpolation=cv2.INTER_LINEAR)
            if im[-1].ndim == 2:
                for j, sim in enumerate(im):
                    im[j] = sim[..., None]

            # Add to buffer if training with augmentations
            if self.augment and not forget_i:
                with self.buffer_lock:
                    # print("self.buffer.append(i):", i)
                    self.buffer.append(i)
                    # print("self.buffer:", self.buffer)
                    if 1 < len(self.buffer) >= self.max_buffer_length:  # prevent empty buffer
                        j = self.buffer.pop(0)

            """
            print("(h0, w0)", h0, w0)
            print("im[-1].shape[:2]", im[-1].shape[:2])
            for i, sim in enumerate(im):
                print(sim.shape)
            """
            return im, (h0, w0), im[-1].shape[:2]

        return self.ims[i], self.im_hw0[i], self.im_hw[i]

    def get_img_files_and_labels(self):
        nm, nf, ne, nc, msgs = 0, 0, 0, 0, []  # number missing, found, empty, corrupt, messages
        im_files = []
        labels = []
        for key, val in self.imgs.items():
            img_ids = val["img_ids"]
            mim_files = [os.path.join(self.spire_root_dir, self.imgs[id]["file_name"]) for id in img_ids]
            if len(mim_files) >= self.seq_len:
                mim_files = mim_files[-self.seq_len:]
            else:
                img_0 = mim_files[0]
                while len(mim_files) < self.seq_len:
                    mim_files.insert(0, img_0)

            im_file = os.path.join(self.spire_root_dir, val["file_name"])
            h, w = val["height"], val["width"]

            mlabel = []
            for id in img_ids:
                bboxes = []
                cls_ = []
                segments = []
                keypoints = None
                if id in self.imgToAnns:
                    for ann in self.imgToAnns[id]:
                        bbox = [
                            (ann['bbox'][0] + ann['bbox'][2] / 2.0) / w,
                            (ann['bbox'][1] + ann['bbox'][3] / 2.0) / h,
                            ann['bbox'][2] * 1.0 / w,
                            ann['bbox'][3] * 1.0 / h
                        ]
                        if not (-0.01 < bbox[0] - bbox[2] / 2.0 < 1.01):
                            continue
                        if not (-0.01 < bbox[0] + bbox[2] / 2.0 < 1.01):
                            continue
                        if not (-0.01 < bbox[1] - bbox[3] / 2.0 < 1.01):
                            continue
                        if not (-0.01 < bbox[1] + bbox[3] / 2.0 < 1.01):
                            continue
                        if not (0 <= ann['category_id'] - 1 < len(self.names)):
                            continue

                        bboxes.append(bbox)
                        cls_.append([ann['category_id'] - 1])  # 从0开始
                        if 'segmentation' in ann:
                            segment = ann['segmentation'][0]
                            segment = np.array(segment, dtype=np.float32).reshape(-1, 2)
                            segment[:, 0] /= w
                            segment[:, 1] /= h
                            segments.append(segment)
                        if 'keypoints' in ann:
                            keypoint = np.array(ann['keypoints'], dtype=np.float32).reshape(-1, self.kpt_shape[1])
                            keypoint[:, 0] /= w
                            keypoint[:, 1] /= h
                            if keypoints is None:
                                keypoints = []
                            keypoints.append(keypoint)
                        
                    if keypoints is not None and len(keypoints) > 0:
                        keypoints = np.stack(keypoints, axis=0)

                    if len(bboxes) > 0 and len(cls_) > 0:
                        bboxes = np.array(bboxes).astype(np.float32)
                        cls_ = np.array(cls_).astype(np.float32)
                    else:
                        bboxes = np.zeros((0, 4), dtype=np.float32)
                        cls_ = np.zeros((0, 1), dtype=np.float32)
                else:
                    bboxes = np.zeros((0, 4), dtype=np.float32)
                    cls_ = np.zeros((0, 1), dtype=np.float32)

                if bboxes.shape[0] == 0:
                    ne += 1

                label = {
                    "im_file": os.path.join(self.spire_root_dir, self.imgs[id]["file_name"]),
                    "shape": (h, w),
                    "cls": cls_,
                    "bboxes": bboxes,
                    "segments": segments,
                    "keypoints": keypoints,
                    "normalized": True,
                    "bbox_format": "xywh"
                }
                mlabel.append(label)

            if len(mlabel) >= self.seq_len:
                mlabel = mlabel[-self.seq_len:]
            else:
                label_0 = mlabel[0]
                while len(mlabel) < self.seq_len:
                    mlabel.insert(0, label_0)

            if key < 0:
                print(val)
                print(mlabel)
                print(mim_files)

            labels.append(mlabel)
            # im_files.append(im_file)
            im_files.append(mim_files)

        self.logger.info("{} images, {} backgrounds".format(len(im_files), ne))
        return im_files, labels

    def build_transforms(self) -> Compose:
        """Builds and appends transforms to the list."""
        if self.augment:
            self.mosaic = self.mosaic if self.augment and not self.rect else 0.0
            self.mixup = self.mixup if self.augment and not self.rect else 0.0
            self.cutmix = self.cutmix if self.augment and not self.rect else 0.0
            transforms = self.v8_transforms()
        else:
            transforms = Compose([LetterBox(new_shape=(self.imgsz, self.imgsz), scaleup=False)])
        transforms.append(
            Format(
                bbox_format="xywh",
                normalize=True,
                return_mask=self.use_segments,
                return_keypoint=self.use_keypoints,
                return_obb=self.use_obb,
                batch_idx=True,
                mask_ratio=self.mask_ratio,
                mask_overlap=self.overlap_mask,
                bgr=self.bgr if self.augment else 0.0,  # only affect training.
            )
        )
        return transforms

    def v8_transforms(self, stretch: bool = False):
        """
        Applies a series of image transformations for training.

        This function creates a composition of image augmentation techniques to prepare images for YOLO training.
        It includes operations such as mosaic, copy-paste, random perspective, mixup, and various color adjustments.

        Args:
            stretch (bool): If True, applies stretching to the image. If False, uses LetterBox resizing.

        Returns:
            (Compose): A composition of image transformations to be applied to the dataset.

        Examples:
            >>> from ultralytics.data.dataset import YOLODataset
            >>> from ultralytics.utils import IterableSimpleNamespace
            >>> dataset = YOLODataset(img_path="path/to/images", imgsz=640)
            >>> hyp = IterableSimpleNamespace(mosaic=1.0, copy_paste=0.5, degrees=10.0, translate=0.2, scale=0.9)
            >>> transforms = v8_transforms(dataset, imgsz=640, hyp=hyp)
            >>> augmented_data = transforms(dataset[0])
        """
        # print("self.imgsz:", self.imgsz)
        mosaic = Mosaic(self, imgsz=self.imgsz, p=self.mosaic)
        affine = RandomPerspective(
            degrees=self.degrees,
            translate=self.translate,
            scale=self.scale,
            shear=self.shear,
            perspective=self.perspective,
            pre_transform=None if stretch else LetterBox(new_shape=(self.imgsz, self.imgsz)),
        )

        pre_transform = Compose([mosaic, affine])
        if self.copy_paste_mode == "flip":
            pre_transform.insert(1, CopyPaste(p=self.copy_paste, mode=self.copy_paste_mode))
        else:
            pre_transform.append(
                CopyPaste(
                    self,
                    pre_transform=Compose([Mosaic(self, imgsz=self.imgsz, p=self.mosaic), affine]),
                    p=self.copy_paste,
                    mode=self.copy_paste_mode,
                )
            )

        flip_idx = self.flip_idx  # for keypoints augmentation
        if self.use_keypoints:
            kpt_shape = self.kpt_shape
            if len(flip_idx) == 0 and (self.fliplr > 0.0 or self.flipud > 0.0):
                self.fliplr = self.set_param("fliplr", 0.0)
                self.flipud = self.set_param("flipud", 0.0)
                self.logger.warn("No 'flip_idx' array defined in data.yaml, disabling 'fliplr' and 'flipud' augmentations.")
            elif flip_idx and (len(flip_idx) != kpt_shape[0]):
                raise ValueError(f"data.yaml flip_idx={flip_idx} length must be equal to kpt_shape[0]={kpt_shape[0]}")

        return Compose(
            [
                pre_transform,
                MixUp(self, pre_transform=pre_transform, p=self.mixup),
                CutMix(self, pre_transform=pre_transform, p=self.cutmix),
                Albumentations(p=1.0),
                RandomHSV(hgain=self.hsv_h, sgain=self.hsv_s, vgain=self.hsv_v),
                RandomFlip(direction="vertical", p=self.flipud, flip_idx=flip_idx),
                RandomFlip(direction="horizontal", p=self.fliplr, flip_idx=flip_idx),
            ]
        )  # transforms

    def set_rectangle(self) -> None:
        """Sets the shape of bounding boxes for YOLO detections as rectangles."""
        bi = np.floor(np.arange(self.ni) / self.batch_size).astype(int)  # batch index
        nb = bi[-1] + 1  # number of batches

        s = np.array([x[-1].pop("shape") for x in self.labels])  # hw
        ar = s[:, 0] / s[:, 1]  # aspect ratio
        irect = ar.argsort()
        self.im_files = [self.im_files[i] for i in irect]
        self.labels = [self.labels[i] for i in irect]
        ar = ar[irect]
        # print("ar.shape:", ar.shape)
        # print("bi.shape:", bi.shape)

        # Set training image shapes
        shapes = [[1, 1]] * nb
        for i in range(nb):
            ari = ar[bi == i]
            mini, maxi = ari.min(), ari.max()
            if maxi < 1:
                shapes[i] = [maxi, 1]
            elif mini > 1:
                shapes[i] = [1, 1 / mini]

        self.batch_shapes = np.ceil(np.array(shapes) * self.imgsz / self.stride + self.pad).astype(int) * self.stride
        self.batch = bi  # batch index of image

    def launch_next(self, msg: dict = None):
        if (isinstance(msg, dict) and msg['data']) or msg is None:
            if self.img_i < len(self.img_keys):
                self.img_i_queue.put(self.shuffled_img_ids[self.img_i])
                self.img_i += 1

    def run(self):
        while self.is_running():
            img_i = self.img_i_queue.get(block=True)
            if img_i is None:
                break

            # print("img_i:", img_i)
            mraw_data = self.get_image_and_label(img_i)
            """
            for raw_data in mraw_data:
                raw_data_imshow(raw_data)
                # img, targets = self.raw_data_to_spirecv2(raw_data)
                # print(raw_data.keys())
                # print(raw_data['im_file'])
                # print(raw_data['cls'])
                # print(raw_data['img'].shape)
                # print(raw_data['ori_shape'])
                # print(raw_data['resized_shape'])
                # print(raw_data['ratio_pad'])
                # print(raw_data['instances'])

            continue
            # print(type(self.transforms))
            """
            yolo11_mdata = self.transforms(mraw_data)
            for yolo11_data in yolo11_mdata:
                # print(yolo11_data['ori_shape'])
                # print(yolo11_data['resized_shape'])
                # print(yolo11_data['cls'].numpy())
                # print(yolo11_data['bboxes'].numpy())
                # print(yolo11_data['batch_idx'].numpy())

                img, targets = self.yolo11_data_to_spirecv2(yolo11_data)
                # cv2.imshow("img", img)
                # cv2.waitKey(1000)
                time.sleep(1)

                
                if self.b_use_shm:
                    msg = self._image_writer.cvimg2sms_mem(img)
                else:
                    msg = cvimg2sms(img, 'png')

                msg['img_id'] = img_i
                msg['client_id'] = self.client_id
                msg['spirecv_msgs::2DTargets'] = targets
                self._image_writer.publish(msg)
                

        self.release()
        print('{} quit!'.format(self.__class__.__name__))

    def _load_dataset(self):
        annotation_file = os.path.join(self.spire_root_dir, self.spire_json_fn)
        tic = time.time()
        with open(annotation_file, 'r') as f:
            dataset = json.load(f)
        assert isinstance(dataset, dict), 'annotation file format {} not supported'.format(type(dataset))
        print('Done (t={:0.2f}s)'.format(time.time() - tic))
        self.dataset = dataset
        self._create_index()
        self.img_keys = list(self.imgs.keys())
        self.logger.info("Total Images: {}".format(len(self.img_keys)))
        # self.logger.info("{}".format(self.imgs[2]))

        # 打乱输出图像的顺序
        self.shuffled_img_ids = list(range(len(self.img_keys)))
        # print("self.shuffled_img_ids:", self.shuffled_img_ids)
        random.shuffle(self.shuffled_img_ids)

    def _create_index(self):
        # create index
        print('creating index...')
        anns, cats, imgs = {}, {}, {}
        imgToAnns, catToImgs = defaultdict(list), defaultdict(list)
        if 'annotations' in self.dataset:
            for ann in self.dataset['annotations']:
                imgToAnns[ann['image_id']].append(ann)
                anns[ann['id']] = ann

        if 'images' in self.dataset:
            for img in self.dataset['images']:
                imgs[img['id']] = img

        if 'categories' in self.dataset:
            for cat in self.dataset['categories']:
                cats[cat['id']] = cat

        if 'annotations' in self.dataset and 'categories' in self.dataset:
            for ann in self.dataset['annotations']:
                catToImgs[ann['category_id']].append(ann['image_id'])

        print('index created!')
        # create class members
        self.anns = anns
        self.imgToAnns = imgToAnns
        self.catToImgs = catToImgs
        self.imgs = imgs
        self.cats = cats

    @staticmethod
    def collate_fn(batch: List[Dict]) -> Dict:
        """
        Collate data samples into batches.

        Args:
            batch (List[dict]): List of dictionaries containing sample data.

        Returns:
            (dict): Collated batch with stacked tensors.
        """
        new_batch = [] # {}
        batch_b = []
        for b in batch:
            batch_bb = []
            for bb in b:
                batch_bb.append(dict(sorted(bb.items())))
            batch_b.append(batch_bb)
        batch = batch_b

        # batch = [dict(sorted(b.items())) for b in batch]  # make sure the keys are in the same order
        keys = batch[0][-1].keys()
        values = []
        for j in range(len(batch[0])):
            values_j = list(zip(*[list(b[j].values()) for b in batch]))
            values.append(values_j)

        for j in range(len(batch[0])):
            new_batch_j = {}
            for i, k in enumerate(keys):
                value = values[j][i]
                if k in {"img", "text_feats"}:
                    value = torch.stack(value, 0)
                elif k == "visuals":
                    value = torch.nn.utils.rnn.pad_sequence(value, batch_first=True)
                if k in {"masks", "keypoints", "bboxes", "cls", "segments", "obb"}:
                    value = torch.cat(value, 0)
                new_batch_j[k] = value
            new_batch_j["batch_idx"] = list(new_batch_j["batch_idx"])
            for i in range(len(new_batch_j["batch_idx"])):
                new_batch_j["batch_idx"][i] += i  # add target image index for build_targets()
            new_batch_j["batch_idx"] = torch.cat(new_batch_j["batch_idx"], 0)
            new_batch.append(new_batch_j)
        return new_batch
    
    def raw_data_to_spirecv2(self, raw_data):
        # print(raw_data.keys())
        img = raw_data['img']
        ins = raw_data['instances']
        cls = raw_data['cls']
        # print(cls.shape)

        targets = def_msg('spirecv_msgs::2DTargets')

        targets["file_name"] = raw_data['im_file']
        h0, w0 = int(raw_data['ori_shape'][0]), int(raw_data['ori_shape'][1])
        h, w = int(raw_data['resized_shape'][0]), int(raw_data['resized_shape'][1])
        targets["height"] = h
        targets["width"] = w
        targets["targets"] = []

        for i in range(len(cls)):
            ann = dict()
            if int(cls[i, 0]) < len(self.names):
                c_name = self.names[int(cls[i, 0])].strip().replace(' ', '_').lower()
            else:
                c_name = str(cls[i, 0])
            ann["category_name"] = c_name
            ann["category_id"] = int(cls[i, 0])
            ann["bbox"] = [
                float(round((ins.bboxes[i, 0] - ins.bboxes[i, 2] / 2) * w, 3)),
                float(round((ins.bboxes[i, 1] - ins.bboxes[i, 3] / 2) * h, 3)),
                float(round(ins.bboxes[i, 2] * w, 3)),
                float(round(ins.bboxes[i, 3] * h, 3))
            ]
            targets["targets"].append(ann)
        return img, targets

    def yolo11_data_to_spirecv2(self, yolo11_data):
        # print(yolo11_data)
        img = yolo11_data['img'].numpy()
        img = np.swapaxes(np.swapaxes(img, 0, 1), 1, 2)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        targets = def_msg('spirecv_msgs::2DTargets')

        targets["file_name"] = yolo11_data['im_file']
        h0, w0 = int(yolo11_data['ori_shape'][0]), int(yolo11_data['ori_shape'][1])
        h, w = int(yolo11_data['resized_shape'][0]), int(yolo11_data['resized_shape'][1])
        targets["height"] = h
        targets["width"] = w
        targets["targets"] = []
        cls = yolo11_data['cls'].numpy().astype(np.float64)
        xywh = yolo11_data['bboxes'].numpy().astype(np.float64)
        # print(xywh)
        if 'masks' in yolo11_data:
            masks = yolo11_data['masks'].numpy().squeeze(axis=0)
        if 'keypoints' in yolo11_data:
            keypoints = yolo11_data['keypoints'].numpy()
            keypoints[:, :, 0] *= w
            keypoints[:, :, 1] *= h
            keypoints = np.round(keypoints).astype(np.int32)
        for i in range(len(cls)):
            ann = dict()
            if int(cls[i, 0]) < len(self.names):
                c_name = self.names[int(cls[i, 0])].strip().replace(' ', '_').lower()
            else:
                c_name = str(cls[i, 0])
            ann["category_name"] = c_name
            ann["category_id"] = int(cls[i, 0])
            if self.task == 'obb':
                ann["obb"] = [
                    round(xywh[i, 0] * w, 3),
                    round(xywh[i, 1] * h, 3),
                    round(xywh[i, 2] * w, 3),
                    round(xywh[i, 3] * h, 3),
                    round(xywh[i, 4] * 57.3, 3)
                ]
            else:
                ann["bbox"] = [
                    round((xywh[i, 0] - xywh[i, 2] / 2) * w, 3),
                    round((xywh[i, 1] - xywh[i, 3] / 2) * h, 3),
                    round(xywh[i, 2] * w, 3),
                    round(xywh[i, 3] * h, 3)
                ]
            if 'masks' in yolo11_data:
                mask = np.where(masks == i + 1, 255, 0).astype(np.uint8)
                mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_LINEAR)
                mask = np.where(mask > 127, 1, 0).astype(np.uint8)
                ann["segmentation"] = pycoco_mask.encode(mask.copy('F'))
                ann["segmentation"]["counts"] = base64.b64encode(ann["segmentation"]["counts"]).decode('utf-8')
            if 'keypoints' in yolo11_data and keypoints.shape[1] == self.kpt_shape[0]:
                ann["keypoints"] = keypoints[i].reshape(-1).tolist()
            targets["targets"].append(ann)

        return img, targets


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
        params_dir = os.path.join(current_path[:current_path.find('spirecv-pro') + 11], 'params', 'spirecv2')
        args.config = os.path.join(params_dir, args.config)
    print("--config:", args.config)
    print("--job-name:", args.job_name)
    extra = get_extra_args(unknown_args)

    node = YOLO11VIDTrainLoaderNode(args.job_name, param_dict_or_file=args.config, ip=args.ip, port=args.port, **extra)
    node.start()

    if node.rate > 0:
        rr = Rate(node.rate)
        for j in range(node.epoch):
            for i in range(len(node)):
                node.launch_next()
                rr.sleep()

    print('done!')
