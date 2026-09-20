"""SerpAPI 字段映射与价格解析。"""

import httpx

from app.services.serp_client import map_shopping_item, parse_price, search_google_shopping


def test_parse_price_from_plain_number_string():
    assert parse_price("$12.99") == 12.99
    assert parse_price("$1,234.50") == 1234.50
    assert parse_price(None) is None
    assert parse_price("N/A") is None


def test_map_prefers_extracted_price_and_merchant_link():
    item = {
        "title": "Sony WH-1000XM5",
        "extracted_price": 348.0,
        "price": "$348.00",
        "thumbnail": "https://img.example/xm5.jpg",
        "link": "https://www.amazon.com/dp/B0B",
        "product_link": "https://www.google.com/shopping/product/1",
        "source": "Amazon.com",
        "rating": 4.6,
        "reviews": 12000,
    }
    product = map_shopping_item(item)
    assert product is not None
    assert product.title == "Sony WH-1000XM5"
    assert product.price_usd == 348.0
    assert product.price_display == "$348.00"
    assert product.url == "https://www.amazon.com/dp/B0B"
    assert product.source == "Amazon.com"
    assert product.image == "https://img.example/xm5.jpg"
    assert product.rating == 4.6
    assert product.reviews == 12000


def test_map_falls_back_to_price_string_and_product_link():
    item = {
        "title": "Yoga Mat",
        "price": "$24.99",
        "product_link": "https://www.google.com/shopping/product/2",
        "source": "Walmart",
    }
    product = map_shopping_item(item)
    assert product is not None
    assert product.price_usd == 24.99
    assert product.url == "https://www.google.com/shopping/product/2"
    assert product.price_display == "$24.99"


def test_map_skips_item_without_title_or_link():
    assert map_shopping_item({"price": "$1.00"}) is None
    assert map_shopping_item({"title": "Only title"}) is None


def test_search_maps_shopping_results(monkeypatch):
    def fake_fetch(query: str):
        assert query == "yoga mat"
        return {
            "shopping_results": [
                {
                    "title": "Yoga Mat",
                    "extracted_price": 19.99,
                    "price": "$19.99",
                    "link": "https://www.ebay.com/itm/1",
                    "source": "eBay",
                }
            ]
        }

    monkeypatch.setattr("app.services.serp_client.fetch_shopping", fake_fetch)
    products = search_google_shopping("yoga mat")
    assert len(products) == 1
    assert products[0].source == "eBay"


def test_fetch_retries_after_connect_timeout(monkeypatch):
    from app.services import serp_client

    calls = {"n": 0}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"shopping_results": []}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            return None

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def get(self, *args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                raise httpx.ConnectTimeout("timed out")
            return FakeResponse()

    monkeypatch.setattr(serp_client.settings, "serpapi_api_key", "test-key")
    monkeypatch.setattr(serp_client.httpx, "Client", FakeClient)
    payload = serp_client.fetch_shopping("yoga mat")
    assert calls["n"] == 2
    assert payload["shopping_results"] == []
