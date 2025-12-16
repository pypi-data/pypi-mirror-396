#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import numpy as np
import os
import time
import cv2
from PIL import ImageFont, ImageDraw, Image


font_path = dict()
font_path['source_code_pro'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../res/source_code_pro.ttf')
font_path['source_code_pro_bold'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../res/source_code_pro_bold.ttf')
font_path['jetbrains_mono'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../res/jetbrains_mono.ttf')
font_path['jetbrains_mono_bold'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../res/jetbrains_mono_bold.ttf')
font_path['fradmcn'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../res/fradmcn.ttf')
font_path['msyh_boot'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../res/msyh_boot.ttf')
font_dict = dict()
font_dict['source_code_pro'] = dict()
font_dict['source_code_pro_bold'] = dict()
font_dict['jetbrains_mono'] = dict()
font_dict['jetbrains_mono_bold'] = dict()
font_dict['fradmcn'] = dict()
font_dict['msyh_boot'] = dict()


def _get_font(
    font: str = 'jetbrains_mono_bold',
    font_size: float = 30
):
    if font_size in font_dict[font]:
        print('Font Exist!')
    else:
        font_dict[font][font_size] = ImageFont.truetype(font_path[font], font_size)
    return font_dict[font][font_size]

def cvbgr2pilrgb(cv_bgr: np.ndarray) -> Image.Image:
    pil_rgb = Image.fromarray(cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2RGB))
    return pil_rgb

def pilrgb2cvbgr(pil_rgb: Image.Image) -> np.ndarray:
    cv_bgr = cv2.cvtColor(np.array(pil_rgb), cv2.COLOR_RGB2BGR)
    return cv_bgr

def put_text(
    pil_img: Image.Image,
    text: str,
    xy: tuple[float, float],
    font: str = 'jetbrains_mono_bold',
    font_size: float = 30,
    color: any = (255, 255, 255)
) -> Image.Image:
    draw = ImageDraw.Draw(pil_img)
    img_font = _get_font(font, font_size)
    draw.text(xy, text, font=img_font, fill=color)
    return pil_img

def put_texts(
    pil_img: Image.Image,
    texts: list,
    xys: list,
    font: str = 'jetbrains_mono_bold',
    font_size: float = 30,
    color: any = (255, 255, 255)
) -> Image.Image:
    draw = ImageDraw.Draw(pil_img)
    img_font = _get_font(font, font_size)
    for xy, text in zip(xys, texts):
        draw.text(xy, text, font=img_font, fill=color)
    return pil_img

def put_texts_v(
    pil_img: Image.Image,
    texts: list,
    xy: tuple[float, float],
    font: str = 'jetbrains_mono_bold',
    font_size: float = 30,
    color: any = (255, 255, 255),
    background: any = (0, 0, 0),
    border: int = 15
) -> Image.Image:
    w, h = pil_img.size
    roi_w, roi_h = max([len(t) for t in texts]) * font_size * 0.6, len(texts) * font_size * 1.2
    roi_x1, roi_y1 = xy[0] - border, xy[1] - border
    roi_x2, roi_y2 = xy[0] + roi_w + border, xy[1] + roi_h + border
    if roi_x1 < 0:
        roi_x1 = 0
    if roi_y1 < 0:
        roi_y1 = 0
    if roi_x2 > w:
        roi_x2 = w
    if roi_y2 > h:
        roi_y2 = h
    roi_img = pil_img.crop((roi_x1, roi_y1, roi_x2, roi_y2))
    bgr_img = Image.new("RGB", roi_img.size, background)
    combined_image = Image.blend(bgr_img, roi_img, 0.5)
    pil_img.paste(combined_image, (roi_x1, roi_y1))

    draw = ImageDraw.Draw(pil_img)
    # draw.rectangle((roi_x1, roi_y1, roi_x2, roi_y2), outline="red")
    img_font = _get_font(font, font_size)
    for j, text in enumerate(texts):
        draw.text((xy[0], xy[1] + j * font_size * 1.2), text, font=img_font, fill=color)

    return pil_img

def put_texts_stat(
    pil_img: Image.Image,
    texts: list,
    values: list,
    units: list,
    xy: tuple[float, float],
    font: str = 'jetbrains_mono_bold',
    font_size: float = 30,
    color: any = (255, 255, 255),
    background_rect: any = (0, 0, 500, 300)
) -> Image.Image:
    roi_img = pil_img.crop(background_rect)
    bgr_img = Image.new("RGB", roi_img.size, (0, 0, 0))
    combined_image = Image.blend(bgr_img, roi_img, 0.5)
    pil_img.paste(combined_image, (background_rect[0], background_rect[1]))

    t_len = max([len(t) for t in texts])
    val_len = max([len(v) for v in values])
    values = [v.rjust(val_len + 2) for v in values]
    draw = ImageDraw.Draw(pil_img)
    # draw.rectangle((roi_x1, roi_y1, roi_x2, roi_y2), outline="red")
    img_font = _get_font(font, font_size)
    unit_font = _get_font(font, font_size * 0.7)
    for j, (text, value, unit) in enumerate(zip(texts, values, units)):
        draw.text((xy[0], xy[1] + j * font_size * 1.2), text, font=img_font, fill=color)
        draw.text((xy[0] + t_len * font_size * 0.6, xy[1] + j * font_size * 1.2), value,
                  font=img_font, fill=(255, 250, 0))
        draw.text((xy[0] + (t_len + val_len + 3) * font_size * 0.6, xy[1] + j * font_size * 1.2 + font_size * 0.1), unit,
                  font=unit_font, fill=(255, 250, 0))

    return pil_img


if __name__ == '__main__':
    img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../res/racecar.jpg')
    img = Image.open(img_path)
    _get_font()

    t1 = time.time()
    # img = put_text(img, 'Hello World', (10, 10))
    t2 = time.time()
    print('dt1', t2 - t1)
    img = put_texts_stat(
        img,
        ['CPU Clock', 'CPU Power', 'CPU Temp', 'CPU Usage', 'GPU Usage'],
        ['5677', '204.0', '69', '52', '94'],
        ['MHz', 'W', 'Deg', '%', '%'],
        (15, 10),
        font_size=40,
        background_rect = (0, 0, 495, 270),
        font='source_code_pro_bold'
    )
    print('dt2', time.time() - t2)
    img.show()
    print('done!')
