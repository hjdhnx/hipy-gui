import random
import socket
import uvicorn
import webview
import threading
import os
from backend.app import app


# https://pywebview.flowrl.com/guide/api.html

class Api:
    def __init__(self):
        self.w = webview.Window

    def show_notification(self):
        # self.w.set_title('hello world')
        self.w.create_confirmation_dialog("Hello", "This is a desktop notification!")

    def select_file(self):
        file_path = self.w.create_file_dialog(webview.OPEN_DIALOG)
        if file_path:
            self.w.evaluate_js(f'updateFilePath("{os.path.basename(file_path)}")')


def get_unused_port():
    """获取未被使用的端口"""
    while True:
        port = random.randint(1024, 65535)  # 端口范围一般为1024-65535
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("127.0.0.1", port))
            sock.close()
            return port
        except OSError:
            pass


port = get_unused_port()

# 启动FastAPI服务
t = threading.Thread(target=uvicorn.run, args=(app,), kwargs={"host": "0.0.0.0", "port": port})
t.daemon = True
t.start()

api = Api()
# 在PyWebview应用程序中加载FastAPI应用程序的URL
# webview.create_window('Hipy GUI', f'http://127.0.0.1:{port}/index.html', js_api=api)
webview.create_window('Hipy GUI', f'http://127.0.0.1:{port}/index.html', width=800, height=600, js_api=api)
webview.start()
