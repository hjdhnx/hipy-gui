#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : constants.py
# Author: DaShenHan&道长-----先苦后甜，任凭晚风拂柳颜------
# Author's Blog: https://blog.csdn.net/qq_32394351
# Date  : 2024/3/23
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
DEFAULT_ENV_FILE = os.path.abspath(os.path.join(BASE_DIR,
                                                "./configs/.env"))  # default env file path: './configs/.env' when run "python main.py", you can change in this if you want
