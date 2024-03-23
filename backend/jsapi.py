#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : jsapi.py
# Author: DaShenHan&道长-----先苦后甜，任凭晚风拂柳颜------
# Author's Blog: https://blog.csdn.net/qq_32394351
# Date  : 2024/3/23
# https://pywebview.flowrl.com/guide/api.html

import webview
import os
from pathlib import Path


class JsApi:
    def __init__(self) -> None:
        self._window = None

    def set_window(self, window):
        self._window = window

    def quit(self):
        self._window.destroy()

    def show_notification(self):
        # self.w.set_title('hello world')
        self._window.create_confirmation_dialog("Hello", "This is a desktop notification!")

    def select_file(self):
        file_types = ('Image Files (*.bmp;*.jpg;*.gif;*.js;*.json;*.py;*.txt;*.md)', 'All files (*.*)')
        file_path = self._window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=True, file_types=file_types)
        if file_path:
            fpath = Path(os.path.abspath(file_path[0])).as_posix()
            fname = Path(os.path.basename(file_path[0])).as_posix()
            print('fpath:', fpath, 'fname:', fname)
            # self._window.evaluate_js(f'updateFilePath("{fpath}")')
            return {'fpath': fpath, 'fname': fname}

    def save_file_dialog(self):
        file_path = self._window.create_file_dialog(
            webview.SAVE_DIALOG, directory='/', save_filename='test.file'
        )
        print(file_path)
        with open(file_path, mode='w+', encoding='utf-8') as f:
            f.write('hello world')
        self._window.evaluate_js('alert("保存成功")')


jsapi = JsApi()
