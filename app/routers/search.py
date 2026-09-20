"""商品搜索接口：缓存 → SerpAPI → 调研摘要。"""

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models import Product, SearchRequest, SearchResponse
from app.services.cache import SearchCache
from app.services.demo_data import DEMO_PRODUCTS, is_demo_query
from app.services.research import summarize
from app.services.serp_client import SerpAPIError, search_google_shopping
from app.services.sources import canonical_source

router = APIRouter(prefix="/api")
cache = SearchCache(settings.cache_db_path, settings.cache_ttl_seconds)


def _with_platform(products: list[Product]) -> list[Product]:
    return [item.model_copy(update={"source": canonical_source(item.source)}) for item in products]


@router.get("/health")
def health() -> dict:
    return {"ok": True, "serpapi_configured": settings.has_api_key}


@router.post("/search", response_model=SearchResponse)
def search(payload: SearchRequest) -> SearchResponse:
    query = payload.query

    if is_demo_query(query) and not settings.has_api_key:
        return SearchResponse(
            query=query,
            cached=False,
            demo=True,
            products=_with_platform(DEMO_PRODUCTS),
            summary=summarize(_with_platform(DEMO_PRODUCTS)),
        )

    cached_payload = cache.get(query)
    if cached_payload is not None:
        products = _with_platform([Product.model_validate(item) for item in cached_payload])
        return SearchResponse(
            query=query,
            cached=True,
            demo=False,
            products=products,
            summary=summarize(products),
        )

    if not settings.has_api_key:
        raise HTTPException(
            status_code=503,
            detail="未配置 SERPAPI_API_KEY。可先搜索演示词「wireless earbuds」。",
        )

    try:
        products = _with_platform(search_google_shopping(query))
    except SerpAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    cache.set(query, [item.model_dump() for item in products])
    return SearchResponse(
        query=query,
        cached=False,
        demo=False,
        products=products,
        summary=summarize(products),
    )
