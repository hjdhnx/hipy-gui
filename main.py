import random
import socket

import uvicorn
import webview
import threading
from backend.app import app
from backend.jsapi import jsapi

import sys

# 将根目录添加到系统路径
sys.path.append('./backend/')


def get_unused_port():
    """获取未被使用的端口"""
    port = 5707
    # port = 9978
    ok = True
    while ok:
        # port = random.randint(1024, 65535)  # 端口范围一般为1024-65535
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("127.0.0.1", port))
            sock.close()
            ok = False
            return port
        except OSError:
            port += 1


port = get_unused_port()

# 启动FastAPI服务
t = threading.Thread(target=uvicorn.run, args=(app,), kwargs={"host": "0.0.0.0", "port": port})
t.daemon = True
t.start()

chinese = {
    'global.quitConfirmation': u'确定关闭?',
}
# 在PyWebview应用程序中加载FastAPI应用程序的URL
# webview.create_window('Hipy GUI', f'http://127.0.0.1:{port}/index.html', js_api=api)
window = webview.create_window('Hipy GUI', f'http://127.0.0.1:{port}/index.html',
                               fullscreen=False,  # 以全屏模式启动
                               # width=800,	# 自定义窗口大小
                               # height=600,
                               # resizable=False,  # 固定窗口大小
                               text_select=False,  # 禁止选择文字内容
                               confirm_close=True,  # 关闭时提示
                               js_api=jsapi)
jsapi.set_window(window)
webview.start(localization=chinese)
