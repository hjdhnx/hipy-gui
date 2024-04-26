#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : views.py
# Author: DaShenHan&道长-----先苦后甜，任凭晚风拂柳颜------
# Author's Blog: https://blog.csdn.net/qq_32394351
# Date  : 2023/12/3
import ast
from fastapi.responses import JSONResponse

from time import time
import ujson

from fastapi import APIRouter, Depends, Query, WebSocket, Request as Req, HTTPException
from starlette.responses import HTMLResponse, RedirectResponse, Response
import os
from ..common.resp import respSuccessJson, respErrorJson, respParseJson, respVodJson, abort
from ..core.config import settings
from ..core.logger import logger
from ..utils.web import htmler, render_template_string, remove_comments, parseJson
from ..utils.vod_tool import base64ToImage, get_interval
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from pathlib import Path

try:
    from quickjs import Function, Context
except ImportError:
    Function = None
    Context = None

router = APIRouter()
htmler2 = Jinja2Templates(directory=settings.WEB_TEMPLATES_DIR)


@router.get("/doc", response_class=HTMLResponse, summary="文档首页")
async def read_root(request: Req):
    return htmler2.TemplateResponse("index.html", {"request": request})


@router.get("/", summary="网站首页")
async def web_home():
    html = htmler.renderTemplate('index')
    return HTMLResponse(html)


@router.get("/index")
def index():
    return JSONResponse({"status": 200, "msg": "ok"})


@router.get('/blog', summary="博客首页")
async def blog():
    return RedirectResponse(settings.BLOG_URL)


def merge_config(base_conf: dict, custom_conf: dict):
    """
    配置字典合并策略
    @param base_conf:
    @param custom_conf:
    @return:
    """
    if not custom_conf or len(custom_conf.keys()) < 1:
        return base_conf
    for key, value in custom_conf.items():
        # 合并列表
        if base_conf.get(key) and isinstance(base_conf[key], list) and isinstance(value, list):
            for v in value:
                if 'order_num' not in v:
                    v['order_num'] = 9999
            base_conf[key].extend(value)
            if key == 'sites':
                base_conf[key].sort(key=lambda x: x['order_num'])
        # 合并字典
        elif base_conf.get(key) and isinstance(base_conf[key], dict) and isinstance(value, dict):
            base_conf[key].update(value)
        # 覆盖其他类型
        elif base_conf.get(key) and type(base_conf[key]) == type(value):
            base_conf[key] = value
        # 新增原来不存在的
        elif not base_conf.get(key):
            base_conf[key] = value
    logger.info(f'合并配置共有解析数量:{len(base_conf.get("parses"))}')
    return base_conf


@router.get("/config/{mode}", summary="自动生成tvbox-hipy配置")
async def hipy_configs(*,
                       request: Req,
                       mode: int = Query(..., title="模式 0:t4 1:t3"),
                       ):
    t1 = time()
    host = str(request.base_url).rstrip('/')
    work_path = Path(os.getcwd()).as_posix()
    py_path = os.path.join(work_path, 'py')
    js_path = os.path.join(work_path, 'js')
    lib_path = os.path.join(work_path, 'libs')
    config_path = os.path.join(work_path, 'config')
    config_json_file = os.path.join(work_path, 'config/config.json')
    config_txt_file = os.path.join(work_path, 'config/config.txt')
    custom_file = os.path.join(work_path, 'config/custom.conf')
    for path in [py_path, js_path, lib_path, config_path]:
        os.makedirs(path, exist_ok=True)

    hipy_rules = os.listdir(py_path)
    drpy_rules = os.listdir(js_path)
    hipy_rules = [{
        'name': rec.replace('.py', ''),
        'file_type': '.py',
        'api': f'{host}/files/py/{rec}',
        'searchable': 1,
        'quickSearch': 1,
        'filterable': 1,
    } for rec in hipy_rules]

    drpy_rules = [{
        'name': rec.replace('.js', ''),
        'file_type': '.js',
        'api': f'{host}/files/libs/drpy2.min.js',
        'ext': f'{host}/files/js/{rec}',
        'searchable': 1,
        'quickSearch': 1,
        'filterable': 1,
    } for rec in drpy_rules]

    try:
        with open(config_json_file, encoding='utf-8') as f:
            config = ujson.loads(f.read())
    except Exception as e:
        config = {}

    rules = hipy_rules + drpy_rules
    rules = ujson.dumps(rules, ensure_ascii=False)
    rules = render_template_string(rules, **{'host': host})
    rules = ujson.loads(rules)
    context = {'config': config, 'rules': rules, 'env': {},
               'host': host, 'mode': mode, 'sites': [],
               'jxs': [], 'alists': [],
               }
    try:
        with open(config_txt_file, encoding='utf-8') as f:
            file_content = f.read()
        render_text = render_template_string(file_content, **context)
        render_dict = ast.literal_eval(render_text)
        render_dict['cost_time'] = get_interval(t1)
        return respVodJson(render_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")


@router.get("/files/{filename:path}", summary="T4静态文件")
async def t4_files(*,
                   request: Req,
                   filename: str = Query(..., title="hipy源文件名")):
    work_path = Path(os.getcwd()).as_posix()
    file_path = os.path.join(work_path, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        media_type = 'text/javascript; charset=utf-8' if filename.endswith('.js') else None
        return FileResponse(file_path, media_type=media_type)
    else:
        raise HTTPException(status_code=404)
