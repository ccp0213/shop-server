"""价格带、平台分布与竞争度启发式分析。"""

from statistics import mean, median

from app.models import PlatformCount, Product, ResearchSummary

_DISCLAIMER = "启发式，仅供参考。"


def summarize(products: list[Product]) -> ResearchSummary:
    """对当前商品列表做本地统计，不调用任何外部服务。"""
    prices = sorted(item.price_usd for item in products if item.price_usd is not None)
    counts: dict[str, int] = {}
    for item in products:
        counts[item.source] = counts.get(item.source, 0) + 1
    platform_counts = [
        PlatformCount(source=source, count=count)
        for source, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    if not prices:
        return ResearchSummary(
            sample_size=len(products),
            min_price=None,
            median_price=None,
            max_price=None,
            avg_price=None,
            platform_counts=platform_counts,
            competition_level="insufficient",
            conclusion=f"有效报价不足，还看不清价格带。{_DISCLAIMER}",
        )

    min_price = prices[0]
    max_price = prices[-1]
    avg_price = round(mean(prices), 2)
    median_price = round(float(median(prices)), 2)
    spread_ratio = (max_price - min_price) / avg_price if avg_price else 0
    sample_size = len(products)
    level, conclusion = _competition(sample_size, avg_price, spread_ratio)
    return ResearchSummary(
        sample_size=sample_size,
        min_price=min_price,
        median_price=median_price,
        max_price=max_price,
        avg_price=avg_price,
        platform_counts=platform_counts,
        competition_level=level,
        conclusion=conclusion,
    )


def _competition(sample_size: int, avg_price: float, spread_ratio: float) -> tuple[str, str]:
    """样本少且均价高偏机会；样本多且价格带窄偏红海。"""
    if sample_size >= 12 and spread_ratio < 0.3:
        return (
            "red_ocean",
            f"同类商品多、报价挤在很窄的区间，偏红海。{_DISCLAIMER}",
        )
    if sample_size <= 5 and avg_price >= 80:
        return (
            "opportunity",
            f"公开货架上的相近商品不多，且均价偏高，有一定切入机会。{_DISCLAIMER}",
        )
    if sample_size <= 4:
        return (
            "insufficient",
            f"样本偏少，只能当线索，还不宜下开发结论。{_DISCLAIMER}",
        )
    return (
        "mixed",
        f"已有一批可比商品，价格带有宽度，适合再拆规格和评价后判断。{_DISCLAIMER}",
    )
