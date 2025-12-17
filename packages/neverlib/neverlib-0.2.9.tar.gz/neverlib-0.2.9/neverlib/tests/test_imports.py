#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: 凌逆战 | Never
Date: 2025-09-07
Description: 测试neverlib导入功能
'''
import sys
import os
import time
from neverlib.utils import get_path_list
from neverlib.data_analyze.dataset_analyzer import AudioFileInfo

# 确保当前目录在Python路径中，以便导入neverlib
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append("../..")
print("开始测试neverlib导入功能...")

from neverlib.audio_aug import limiter
