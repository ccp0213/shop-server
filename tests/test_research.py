"""调研分析：价格带、平台分布、竞争度启发式。"""

from app.models import Product
from app.services.research import summarize


def _product(title: str, price: float | None, source: str) -> Product:
    return Product(
        title=title,
        price_usd=price,
        price_display=f"${price:.2f}" if price is not None else "暂无报价",
        image=None,
        url="https://example.com",
        source=source,
    )


def test_empty_products_marked_insufficient():
    summary = summarize([])
    assert summary.sample_size == 0
    assert summary.min_price is None
    assert summary.competition_level == "insufficient"
    assert "仅供参考" in summary.conclusion


def test_price_band_ignores_missing_prices():
    products = [
        _product("A", 10.0, "Amazon"),
        _product("B", None, "eBay"),
        _product("C", 30.0, "Walmart"),
        _product("D", 20.0, "Amazon"),
    ]
    summary = summarize(products)
    assert summary.sample_size == 4
    assert summary.min_price == 10.0
    assert summary.max_price == 30.0
    assert summary.median_price == 20.0
    assert summary.avg_price == 20.0


def test_platform_counts_group_sources():
    products = [
        _product("A", 10.0, "Amazon"),
        _product("B", 12.0, "Amazon"),
        _product("C", 9.0, "eBay"),
    ]
    summary = summarize(products)
    counts = {item.source: item.count for item in summary.platform_counts}
    assert counts["Amazon"] == 2
    assert counts["eBay"] == 1


def test_many_products_narrow_price_band_is_red_ocean():
    products = [_product(f"item-{i}", 19.0 + (i % 3) * 0.4, "Amazon") for i in range(14)]
    summary = summarize(products)
    assert summary.competition_level == "red_ocean"
    assert "红海" in summary.conclusion
    assert "仅供参考" in summary.conclusion


def test_few_products_high_price_is_opportunity():
    products = [
        _product("Pro A", 189.0, "Amazon"),
        _product("Pro B", 210.0, "eBay"),
        _product("Pro C", 175.0, "Walmart"),
    ]
    summary = summarize(products)
    assert summary.competition_level == "opportunity"
    assert "机会" in summary.conclusion
