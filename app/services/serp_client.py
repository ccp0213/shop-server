"""SerpAPI Google Shopping 客户端与字段映射。"""

import re
from typing import Any

import httpx

from app.config import settings
from app.models import Product

_PRICE_RE = re.compile(r"[\d,]+\.?\d*")
SERPAPI_URL = "https://serpapi.com/search.json"
_TIMEOUT = httpx.Timeout(connect=30.0, read=120.0, write=30.0, pool=30.0)
_ATTEMPTS = 3


class SerpAPIError(RuntimeError):
    """上游搜索失败。"""


def parse_price(raw: str | None) -> float | None:
    """从 `$1,234.50` 这类字符串里抽出美元金额。"""
    if raw is None:
        return None
    match = _PRICE_RE.search(str(raw))
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", ""))
    except ValueError:
        return None


def map_shopping_item(item: dict[str, Any]) -> Product | None:
    """把 SerpAPI shopping_results 的一条记录映射成 Product。"""
    title = (item.get("title") or "").strip()
    url = (item.get("link") or item.get("product_link") or "").strip()
    if not title or not url:
        return None

    extracted = item.get("extracted_price")
    price_usd = float(extracted) if isinstance(extracted, (int, float)) else parse_price(item.get("price"))
    price_str = item.get("price")
    if isinstance(price_str, str) and parse_price(price_str) is not None:
        price_display = price_str
    elif price_usd is not None:
        price_display = f"${price_usd:.2f}"
    else:
        price_display = "暂无报价"

    reviews = item.get("reviews")
    if isinstance(reviews, str) and reviews.isdigit():
        reviews = int(reviews)
    elif not isinstance(reviews, int):
        reviews = None

    rating = item.get("rating")
    if not isinstance(rating, (int, float)):
        rating = None

    return Product(
        title=title,
        price_usd=price_usd,
        price_display=price_display,
        image=item.get("thumbnail"),
        url=url,
        source=(item.get("source") or "Unknown").strip(),
        rating=float(rating) if rating is not None else None,
        reviews=reviews,
    )


def fetch_shopping(query: str) -> dict[str, Any]:
    """请求 SerpAPI Google Shopping。测试可 monkeypatch 本函数。"""
    if not settings.has_api_key:
        raise SerpAPIError("未配置 SERPAPI_API_KEY")
    params = {
        "engine": "google_shopping",
        "q": query,
        "gl": "us",
        "hl": "en",
        "num": settings.serpapi_num,
        "api_key": settings.serpapi_api_key,
    }
    last_error: Exception | None = None
    for _attempt in range(_ATTEMPTS):
        try:
            with httpx.Client(timeout=_TIMEOUT) as client:
                response = client.get(SERPAPI_URL, params=params)
                response.raise_for_status()
                data = response.json()
            break
        except httpx.TimeoutException as exc:
            last_error = exc
            continue
        except httpx.HTTPError as exc:
            raise SerpAPIError(f"SerpAPI 请求失败：{exc}") from exc
    else:
        raise SerpAPIError(f"SerpAPI 请求失败：{last_error}") from last_error
    if data.get("error"):
        raise SerpAPIError(str(data["error"]))
    return data


def search_google_shopping(query: str) -> list[Product]:
    """搜索并映射为内部商品列表。"""
    payload = fetch_shopping(query)
    products: list[Product] = []
    for item in payload.get("shopping_results") or []:
        mapped = map_shopping_item(item)
        if mapped is not None:
            products.append(mapped)
    return products
