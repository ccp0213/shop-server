"""FastAPI 入口：页面、静态资源与搜索 API。"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.routers.search import router as search_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="货架调研", description="美国购物平台商品调研工具")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.include_router(search_router)


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"serpapi_configured": settings.has_api_key},
    )
