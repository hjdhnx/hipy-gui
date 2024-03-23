import os
from typing import Any, Dict, List, Optional, Union
from . import constants
from pydantic import BaseSettings, IPvAnyAddress, FilePath
from pydantic.env_settings import env_file_sentinel


class Settings(BaseSettings):
    PROJECT_NAME: str = 'hipy-gui'  # 项目名称 必填
    LOGGING_CONFIG_FILE: FilePath = os.path.join(constants.BASE_DIR, 'configs/logging_config.conf')  # log格式配置文件路径
    WEB_TEMPLATES_DIR: str = os.path.abspath(os.path.join(constants.BASE_DIR, "./templates/"))  # 网页模板路径
    BLOG_URL: str = 'https://blog.csdn.net/qq_32394351'
    ECHO_SQL: bool = False  # 是否打印sql语句
    # 跨域
    BACKEND_CORS_ORIGINS: List[str] = ['*']
    # FastAPI (Only takes effect in run "python main.py". Don't want to take effect when running with "uvicorn/gunicorn main:app")
    HOST: IPvAnyAddress = "0.0.0.0"  # 允许访问程序的ip， 只允许本地访问使用 127.0.0.1， 只在直接允许程序时候生效
    PORT: int = 9898  # 程序端口，只在直接运行程序的时候生效
    RELOAD: bool = True  # 是否自动重启，只在直接运行程序时候生效
    DEBUG: bool = False  # 是否调试模式

    class Config:
        env_file = ".env"


settings = Settings(
    _env_file=constants.DEFAULT_ENV_FILE if os.path.exists(constants.DEFAULT_ENV_FILE) else env_file_sentinel,
    _env_file_encoding='utf-8'
)
