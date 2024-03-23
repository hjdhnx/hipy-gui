#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : views.py
# Author: DaShenHan&道长-----先苦后甜，任凭晚风拂柳颜------
# Author's Blog: https://blog.csdn.net/qq_32394351
# Date  : 2023/12/3

from fastapi.responses import JSONResponse

from time import time
import ujson

from fastapi import APIRouter, Depends, Query, WebSocket, Request as Req, HTTPException
from starlette.responses import HTMLResponse, RedirectResponse, Response
import os
from ..common.resp import respSuccessJson, respErrorJson, respParseJson, respVodJson, abort
from ..common import error_code
from ..core.config import settings
from ..core.logger import logger
from ..utils.web import htmler, render_template_string, remove_comments, parseJson
from ..utils.vod_tool import base64ToImage, get_interval
from ..utils.quickjs_ctx import initContext
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
    # groups = {}
    # group_dict = curd_dict_data.getByType(db, _type='vod_rule_group')
    # group_details = group_dict.get('details')
    # for li in group_details:
    #     groups[li['label']] = li['value']
    # order_bys = [asc(curd_vod_rules.model.order_num)]
    # hipy_rules = curd_vod_rules.search(db=db, status=1, group=groups['hipy'], file_type='.py', page=1, page_size=9999,
    #                                    order_bys=order_bys)
    # drpy_rules = curd_vod_rules.search(db=db, status=1, group=groups['drpy_js'], page=1, page_size=9999,
    #                                    order_bys=order_bys)
    hipy_rules = []
    drpy_rules = []
    # print(hipy_rules.get('results')[0])
    hipy_rules = [{
        'name': rec['name'],
        'file_type': rec['file_type'],
        'ext': rec['ext'] or '',
        'searchable': rec['searchable'],
        'quickSearch': rec['quickSearch'],
        'filterable': rec['filterable'],
        'order_num': rec['order_num'],
    } for rec in hipy_rules.get('results') or [] if rec['active'] and rec['is_exist']]

    drpy_rules = [{
        'name': rec['name'],
        'file_type': rec['file_type'],
        'ext': rec['ext'] or '',
        'searchable': rec['searchable'],
        'quickSearch': rec['quickSearch'],
        'filterable': rec['filterable'],
        'order_num': rec['order_num'],
    } for rec in drpy_rules.get('results') or [] if rec['active'] and rec['is_exist']]

    # print(hipy_rules)
    # print(drpy_rules)
    cf_value_type = 'file'
    if cf_value_type == 'file':
        def get_content(_d):
            """
            内部函数.获取配置参数对应文件的文本内容
            @param _d: 参数dict
            @return:
            """
            _d_value = _d['value']
            _d_group = _d_value.split('/')[0]
            _d_file_name = '/'.join(_d_value.split('/')[1:])
            _resp = get_file_path(_d_group, _d_file_name)
            if isinstance(_resp, list):
                _file_path = _resp[0]
                # print(jx_file_path)
                with open(_file_path, encoding='utf-8') as f:
                    _content = f.read()
                _content = remove_comments(_content)
            else:
                _content = ''
            return _content

        data = []
        # print(data)
        config = {}
        jxs = []
        custom_content = ''
        custom_dict = {}
        hipy_env = {}
        for d in data:
            if d['value_type'] == 'file':
                config[d['key']] = f"{host}/files/{d['value']}"
            elif d['value_type'] == 'json':
                try:
                    d['value'] = ujson.loads(d['value'])
                except Exception as e:
                    logger.info(f"错误{e}.参数{d['key']}的值不是正确的json文本。转字典失败。赋值为空字典")
                    d['value'] = {}
                config[d['key']] = d['value']
            else:
                config[d['key']] = d['value']

            if d['key'] == 'vod_vip_parse' and d['value_type'] == 'file':
                jx_content = get_content(d)
                jx_content = render_template_string(jx_content, host=host)
                for jx in jx_content.split('\n'):
                    jx = jx.strip()
                    jx_arr = jx.split(',')
                    if len(jx_arr) > 1:
                        jx_name = jx_arr[0]
                        jx_url = jx_arr[1]
                        jx_type = jx_arr[2] if len(jx_arr) > 2 else 0
                        jx_ua = jx_arr[3] if len(jx_arr) > 3 else ''
                        jx_flag = jx_arr[4] if len(jx_arr) > 4 else ''
                        jxs.append({
                            'name': jx_name,
                            'url': jx_url,
                            'type': jx_type,
                            'ua': jx_ua,
                            'flag': jx_flag,
                        })
            elif d['key'] == 'vod_config_custom' and d['value_type'] == 'file':
                custom_content = get_content(d)
            elif d['key'] == 'vod_hipy_env' and d['value_type'] == 'json':
                hipy_env = d['value']
        cf_value = ''
        group = cf_value.split('/')[0]
        file_name = '/'.join(cf_value.split('/')[1:])
        resp = get_file_path(group, file_name)
        if isinstance(resp, int):
            return abort(404, f'invalid value:{cf_value},file not found')
        file_path = resp[0]

        rules = hipy_rules + drpy_rules
        # 按order_num排序
        rules.sort(key=lambda x: x['order_num'])

        rules = ujson.dumps(rules, ensure_ascii=False)
        # rules里支持{{host}}渲染
        rules = render_template_string(rules, **{'host': host})
        rules = ujson.loads(rules)
        # print(rules)
        # 自定义额外sites,从用户附加里面去获取
        sites = []

        context = {'config': config, 'rules': rules, 'env': hipy_env,
                   'host': host, 'mode': mode, 'sites': sites,
                   'jxs': jxs, 'alists': [],
                   }
        if custom_content:
            try:
                render_custom_content = render_template_string(custom_content, **context)
                custom_dict = parseJson(render_custom_content)
            except Exception as e:
                logger.info(f'获取custom_dict发生错误:{e}')

        # print(custom_dict)
        # print(config)
        # print(context)
        try:
            with open(file_path, encoding='utf-8') as f:
                file_content = f.read()
            render_text = render_template_string(file_content, **context)
            # 单引号替换双引号
            render_text = render_text.replace("'", '"')
            render_dict = ujson.loads(render_text)
            if custom_content and custom_dict:
                merge_config(render_dict, custom_dict)
                render_dict['cost_time'] = get_interval(t1)
                render_text = ujson.dumps(render_dict, ensure_ascii=False, indent=4)
            else:
                render_dict['cost_time'] = get_interval(t1)
            # print(render_dict)
            # return HTMLResponse(render_text)
            # rules经过{{host}}渲染后这里不需要二次渲染
            # render_text = render_template_string(render_text, **context)
            # return Response(status_code=200, media_type='text/plain', content=render_text)
            return respVodJson(render_dict)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{e}")
            # raise HTTPException(status_code=500)
    else:
        return abort(404, f'invalid value_type:{cf_value_type},only file allowed')


def get_file_path(group, filename):
    """
    获取本地文件路径和类型
    @param db: 数据库游标
    @param group: 文件组label
    @param filename: 文件名称带后缀
    @return: 404 [file_path,media_type] [file_path]
    """
    error_msg = f'group:{group},filename:{filename}'
    project_dir = os.getcwd()
    groups = {}
    group_dict = {}
    group_details = group_dict.get('details')
    for li in group_details:
        groups[li['label']] = li['value']
    # 判断分组在系统字典里才进行上传操作
    if group in groups.keys():
        folder_path = groups[group]
        folder_path = os.path.join(project_dir, folder_path)
        file_path = os.path.join(folder_path, filename)
        file_path = Path(file_path).as_posix()
        if not os.path.exists(file_path):
            logger.info(f'{error_msg},file_path:{file_path}')
            return 404
        else:
            if filename.endswith('.js'):
                return [file_path, 'text/javascript; charset=utf-8']

            return [file_path]

    else:
        logger.info(f'{error_msg},groups:{groups}')
        return 404


def get_file_content(file_name: str):
    try:
        with open(get_file_path('drpy_libs', file_name)[0], encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        logger.info(f'获取文件{file_name}发生错误:{e}')
        return ''


@router.get("/files/{group}/{filename:path}", summary="T4静态文件")
async def t4_files(*,
                   request: Req,
                   group: str = Query(..., title="hipy源分组"),
                   filename: str = Query(..., title="hipy源文件名")):
    """
    返回静态文件链接
    @param db:
    @param request: Request请求
    @param group: hipy文件分组
    @param filename: 文件名
    @return:
    """

    def getParams(key=None, value=''):
        return request.query_params.get(key) or value

    host = str(request.base_url)
    # logger.info(f'host:{host}')
    resp = get_file_path(group, filename)
    if isinstance(resp, int):
        raise HTTPException(status_code=resp)

    file_path = resp[0]
    media_type = resp[1] if len(resp) > 1 else None
    if file_path.endswith('.js') and getParams('render'):
        try:
            key = 'vod_hipy_env'
            vod_configs_obj = {}
            env = vod_configs_obj.get('value')
            env = ujson.loads(env)
        except Exception as e:
            logger.info(f'获取环境变量发生错误:{e}')
            env = {}
        with open(file_path, encoding='utf-8') as f:
            js_code = f.read()

        for k in env.keys():
            if f'${k}' in js_code:
                js_code = js_code.replace(f'${k}', f'{env[k]}')
        return Response(js_code, media_type=media_type)
    else:
        return FileResponse(file_path, media_type=media_type)


@router.get('/parse/api/{filename:path}', summary="执行js后台解析")
def get_js_vip_parse(*,
                     request: Req,
                     filename: str = Query(..., title="解析js文件名")):
    t1 = time()

    def getParams(_key=None, _value=''):
        if _key:
            return request.query_params.get(_key) or _value
        else:
            return request.query_params.__dict__['_dict']

    def getCryptoJS():
        return get_file_content('crypto-hiker.js')

    resp = get_file_path('js_parse_api', filename)
    if isinstance(resp, int):
        raise HTTPException(status_code=resp)
    url = getParams('url')
    if not url or not url.startswith('http'):
        return respErrorJson(error=error_code.ERROR_INTERNAL.set_msg(f'url必填!{url},且必须是http开头'))
    file_path = resp[0]
    if not file_path.endswith('.js'):
        return respErrorJson(
            error=error_code.ERROR_INTERNAL.set_msg(f'暂不支持非js文件解析api:{file_path.split("/")[-1]}'))
    if not Context:
        return respErrorJson(error=error_code.ERROR_INTERNAL.set_msg(f'缺少必要的依赖库quickjs，无法执行js解析'))

    # ==================== 初始化js引擎开始 ======================
    ctx = Context()
    with open(file_path, encoding='utf-8') as f:
        js_code = f.read()
    prefix_code = get_file_content('qjs_env.js')
    try:
        vod_configs_obj = {}
        env = vod_configs_obj.get('value')
        env = ujson.loads(env)
    except Exception as e:
        logger.info(f'获取环境变量发生错误:{e}')
        env = {}
    initContext(ctx, url, prefix_code, env, getParams, getCryptoJS)
    # ==================== 初始化js引擎结束 ======================
    try:
        ctx.eval(js_code.strip().replace('js:', '', 1))
        realUrl = str(ctx.eval('lazy()'))
        # print(realUrl)
        if not realUrl:
            return respParseJson(msg=f'解析失败:{realUrl}', code=404)
        if realUrl == url:
            return respParseJson(msg=f'解析失败:{realUrl}', code=404, extra={'from': realUrl})
        if str(realUrl).startswith('redirect://'):
            return RedirectResponse(realUrl.split('redirect://')[1])
        elif str(realUrl).startswith('toast://'):
            return respParseJson(msg=str(realUrl).split('toast://')[1], code=404)
        elif str(realUrl).startswith('image://'):
            img_data = base64ToImage(str(realUrl).split('image://')[1])
            return Response(img_data, media_type='image/jpeg')

        return respParseJson(msg=f'{filename}解析成功', url=realUrl,
                             extra={'time': f'{get_interval(t1)}毫秒', 'from': url})
    except Exception as e:
        msg = f'{filename}解析出错:{e}'
        logger.info(msg)
        return respErrorJson(error=error_code.ERROR_INTERNAL.set_msg(msg))
