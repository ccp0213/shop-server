"""搜索 API：演示查询、缺 Key、缓存命中。"""

from fastapi.testclient import TestClient

from app.main import app
from app.models import Product


client = TestClient(app)


def test_empty_query_rejected():
    response = client.post("/api/search", json={"query": "   "})
    assert response.status_code == 422


def test_demo_query_works_without_api_key(monkeypatch):
    monkeypatch.setattr("app.routers.search.settings.serpapi_api_key", "")
    response = client.post("/api/search", json={"query": "wireless earbuds"})
    assert response.status_code == 200
    body = response.json()
    assert body["demo"] is True
    assert body["cached"] is False
    assert len(body["products"]) >= 3
    assert body["summary"]["sample_size"] == len(body["products"])
    assert "仅供参考" in body["summary"]["conclusion"]
    assert all(item["image"] or item["title"] for item in body["products"])
    assert all(item["url"] for item in body["products"])


def test_non_demo_query_without_key_returns_503(monkeypatch):
    monkeypatch.setattr("app.routers.search.settings.serpapi_api_key", "")
    response = client.post("/api/search", json={"query": "standing desk"})
    assert response.status_code == 503
    assert "SERPAPI" in response.json()["detail"] or "演示" in response.json()["detail"]


def test_search_uses_cache(monkeypatch, tmp_path):
    from app.routers import search as search_module
    from app.services.cache import SearchCache

    cache = SearchCache(tmp_path / "cache.db", ttl_seconds=3600)
    monkeypatch.setattr(search_module, "cache", cache)
    monkeypatch.setattr(search_module.settings, "serpapi_api_key", "test-key")

    products = [
        Product(
            title="Desk",
            price_usd=199.0,
            price_display="$199.00",
            image=None,
            url="https://www.amazon.com/desk",
            source="Amazon",
        )
    ]
    called = {"n": 0}

    def fake_search(query: str):
        called["n"] += 1
        return products

    monkeypatch.setattr(search_module, "search_google_shopping", fake_search)
    first = client.post("/api/search", json={"query": "standing desk"})
    second = client.post("/api/search", json={"query": "Standing Desk"})
    assert first.status_code == 200
    assert second.status_code == 200
    assert called["n"] == 1
    assert second.json()["cached"] is True
    assert first.json()["cached"] is False
