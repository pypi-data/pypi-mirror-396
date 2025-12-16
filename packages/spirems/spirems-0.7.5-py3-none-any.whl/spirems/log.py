#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import logging
import os
from datetime import datetime
from colorama import Fore, Back, Style, init


log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
LOGER_NAMES = dict()


class ColoredFormatter(logging.Formatter):
    """自定义日志格式化器，根据级别设置颜色"""
    
    # 定义不同日志级别的颜色
    LOG_LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,       # 调试信息：青色
        logging.INFO: Fore.GREEN,       # 信息：绿色
        logging.WARNING: Fore.YELLOW,   # 警告：黄色
        logging.ERROR: Fore.RED,        # 错误：红色
        logging.CRITICAL: Fore.RED + Back.WHITE  # 严重错误：红底白字
    }
    
    def format(self, record):
        # 为日志级别添加颜色
        level_color = self.LOG_LEVEL_COLORS.get(record.levelno, Fore.WHITE)
        record.levelname = f"{level_color}{record.levelname}{Style.RESET_ALL}"
        
        # 为日志消息添加颜色（可选）
        # record.msg = f"{level_color}{record.msg}{Style.RESET_ALL}"
        
        # 调用父类的format方法
        return super().format(record)


def get_logger(name: str = "default"):
    if name not in LOGER_NAMES:
        logger = logging.getLogger(name)
        """
        formatter = logging.Formatter('[%(levelname)s] [%(name)s] %(asctime)s - %(message)s')
        current_time = datetime.now()
        formatted_time = current_time.strftime("log_%Y_%m_%d.txt")
        f_handler = logging.FileHandler(os.path.join(log_dir, formatted_time))
        f_handler.encoding = 'utf-8'
        f_handler.setFormatter(formatter)
        """
        # formatter = logging.Formatter('[%(levelname)s] [%(name)s] %(asctime)s - %(message)s')
        formatter = ColoredFormatter(
            "[%(levelname)s] [%(name)s] %(asctime)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        s_handler = logging.StreamHandler()
        s_handler.encoding = 'utf-8'
        s_handler.setFormatter(formatter)
        logger.setLevel(level=logging.DEBUG)
        logger.addHandler(s_handler)
        # logger.addHandler(f_handler)
        LOGER_NAMES[name] = logger
    return LOGER_NAMES[name]
