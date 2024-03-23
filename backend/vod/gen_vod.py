#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : gen_vod.py
# Author: DaShenHan&道长-----先苦后甜，任凭晚风拂柳颜------
# Author's Blog: https://blog.csdn.net/qq_32394351
# Date  : 2024/1/7

import importlib
import sys
import os
sys.path.append('../../backend/')
sys.path.append('../t4/')
print(sys.path)


class Vod:
    def __init__(self, api, query_params, t4_api=None):
        self.api = api
        # self.module_url = "t4.spiders." + api
        try:
            # self.module_url = "backend.t4.spiders." + api
            self.module_url = "backend.t4.spiders." + api
            self.module = self.import_module(self.module_url).Spider(query_params=query_params, t4_api=t4_api)
        except Exception as e:
            current_directory = os.path.dirname(os.path.realpath(sys.argv[0]))
            raise ValueError(f'{current_directory}---{os.path.abspath(__file__)} {e} {self.module_url}') from e

    def import_module(self, module_url):
        return importlib.import_module(module_url)
