#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
xxxxxx.py
描述这个模块的功能
作者: CAOZUZHEN
创建日期: 2025/12/12 23:22
"""
import time
import  stringutil


def getTime():
    return time.ctime()

def formatStrUtil():
    print(stringutil.FormatString.formatStr())

formatStrUtil()