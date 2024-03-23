from fastapi.routing import APIRouter
from .vod import vod_api
from .web import web_api

api_router = APIRouter()
web_router = APIRouter()

api_router.include_router(vod_api, prefix="/vod", tags=["爬虫源生成"])
web_router.include_router(web_api, prefix="", tags=["网页"])

__all__ = ['api_router', 'web_router']
