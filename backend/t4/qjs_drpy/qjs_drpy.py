#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : qjs_drpy.py
# Author: DaShenHan&道长-----先苦后甜，任凭晚风拂柳颜------
# Date  : 2024/3/20

import os
import threading
import ujson
from quickjs import Context
from backend.utils.quickjs_ctx import initContext
from backend.utils.tools import get_md5
from backend.t4.test.ad_remove import fixAdM3u8
from concurrent.futures import ThreadPoolExecutor, wait


class Drpy:
    def __init__(self, api='drpy', t4_js_api='', debug=0):
        """
        初始化一个drpy类
        @param api: 可以传api如996影视.js
        @param t4_js_api: 本地代理url
        @param debug: 开启调试模式|默认关闭，开启后可以显示源里打印的日志
        """
        key = '_' + get_md5(api)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self._lock = threading.Lock()
        self._api = api
        self.key = key
        self.t4_js_api = t4_js_api
        self.debug = debug
        self.ctx = self.submit(self.initCtx)

    def initCtx(self) -> Context:
        base_path = os.path.dirname(__file__)

        def _(p):
            return os.path.join(base_path, p)

        with open(_('qjs_module_muban.js'), encoding='utf-8') as f:
            _qjs_module_muban = f.read()
        with open(_('qjs_module_cheerio.js'), encoding='utf-8') as f:
            _qjs_module_cheerio = f.read()
        with open(_('qjs_module_gbk.js'), encoding='utf-8') as f:
            _qjs_module_gbk = f.read()
        with open(_('qjs_module_crypto.js'), encoding='utf-8') as f:
            _qjs_module_crypto = f.read()
        with open(_('qjs_module_drpy2.js'), encoding='utf-8') as f:
            _qjs_module_drpy2 = f.read() + f'\nglobalThis.{self.key} = ' + '{ init, home, homeVod, category, detail, ' \
                                                                           'play, search, proxy, sniffer, isVideo};'

        ctx = initContext(Context(), url='', prefix_code='true', env={'debug': self.debug}, getParams=lambda: {},
                          getCryptoJS=lambda: 'true')
        ctx.module(_qjs_module_muban)
        ctx.module(_qjs_module_cheerio)
        ctx.module(_qjs_module_gbk)
        ctx.module(_qjs_module_crypto)
        ctx.module(_qjs_module_drpy2)
        return ctx

    def submit(self, function, *args):
        with self._lock:
            future = self.executor.submit(function, *args)
            wait([future])
            return future.result()

    def setDebug(self, debug):
        return self.submit(self.ctx.set, '_debug', debug)

    def getName(self):
        return self._api.split('/')[-1]

    def toJsObJect(self, any):
        if isinstance(any, dict) or isinstance(any, list):
            return self.submit(self.ctx.parse_json, ujson.dumps(any, ensure_ascii=False))
        return any

    @staticmethod
    def toDict(_object):
        return ujson.loads(_object.json())

    @staticmethod
    def setDict(_str):
        return ujson.loads(_str)

    def call(self, func: str, *args):
        return self.submit(self._call, func, *args)

    def _call(self, func: str, *args, run_gc=True):
        def convert_arg(arg):
            if isinstance(arg, (type(None), str, bool, float, int)):
                return arg
            else:
                # More complex objects are passed through JSON.
                return self.ctx.parse_json(ujson.dumps(arg, ensure_ascii=False))

        try:
            return self.ctx.eval(f'globalThis.{self.key}.{func}')(*[convert_arg(a) for a in args])
        finally:
            if run_gc:
                self.ctx.gc()

    def init(self, extend=""):
        self.call('init', extend)

    def homeContent(self, filter=None):
        return self.setDict(self.call('home', filter))

    def homeVideoContent(self):
        return self.setDict(self.call('homeVod'))

    def categoryContent(self, tid, pg, filter, extend):
        return self.setDict(self.call('category', tid, pg, filter, extend))

    def detailContent(self, ids):
        if isinstance(ids, list):
            ids = ids[0]
        return self.setDict(self.call('detail', ids))

    def searchContent(self, key, quick, pg=1):
        return self.setDict(self.call('search', key, quick, pg))

    def playerContent(self, flag, id, vipFlags=None):
        return self.setDict(self.call('play', flag, id, vipFlags))

    def isVideo(self):
        """
        返回是否为视频的匹配字符串
        @return: None空 reg:正则表达式  js:input js代码
        """
        # return 'js:input.includes(".m3u8)?true:false'

    @staticmethod
    def adRemove():
        """
        m3u8广告移除函数。将自动执行返回的字符串的本地代理功能
        @return: None空 reg:正则表达式  js:input js代码
        """
        # return 'reg:/video/adjump.*?ts'

    def getProxyUrl(self):
        """
        获取本地代理地址
        @return:
        """
        return self.t4_js_api

    @staticmethod
    def fixAdM3u8(*args):
        return fixAdM3u8(*args)

    def localProxy(self, params):
        return self.toDict(self.call('proxy', params))


if __name__ == '__main__':
    drpy = Drpy(debug=1)
    # drpy.init('https://ghproxy.liuzhicong.com/https://github.com/hjdhnx/dr_py/raw/main/js/荐片.js')
    # drpy.init('https://ghproxy.liuzhicong.com/https://github.com/hjdhnx/dr_py/raw/main/js/555影视[飞].js')
    # drpy.init('https://ghproxy.liuzhicong.com/https://github.com/hjdhnx/dr_py/raw/main/js/农民影视.js')
    drpy.init('https://ghproxy.liuzhicong.com/https://github.com/hjdhnx/dr_py/raw/main/js/996影视.js')
    # drpy.init('https://ghproxy.liuzhicong.com/https://github.com/hjdhnx/dr_py/raw/main/js/奇珍异兽.js')
    drpy.setDebug(1)
    print(drpy.homeContent())
    # f = quickjs.Function(
    #     "adder", """
    #             function adder(x, y) {
    #                 return x + y;
    #             }
    #             """)

    print(drpy.categoryContent('3', 1, False, {}))
    # print(drpy.detailContent("3$/detail/790.html"))
    # print(drpy.playerContent("索尼", "https://www.cs1369.com/play/790-1-1.html", []))
    # print(drpy.searchContent("斗罗大陆", False, 1))
