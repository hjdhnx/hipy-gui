import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .core.constants import BASE_DIR
from .core.config import settings
from .core.middleware import middleware
from . import api_router, web_router

app = FastAPI(title=settings.PROJECT_NAME, middleware=middleware)
app.include_router(api_router, prefix="/api/v1")
app.include_router(web_router, prefix="")
ROOT_PATH = os.path.join(os.path.dirname(__file__), "..")
public_file_abspath = os.path.join(ROOT_PATH, "public")
temp_file_abspath = os.path.join(BASE_DIR, "templates")
public_file_abspath = Path(public_file_abspath).as_posix()
os.makedirs(public_file_abspath, exist_ok=True)

app.mount("/web", StaticFiles(directory=temp_file_abspath), name="templates")  # 模板静态文件
app.mount("/", StaticFiles(directory=public_file_abspath), name="public")
