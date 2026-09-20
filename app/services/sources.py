"""把 Google Shopping 的店铺名收成常见平台。"""

_RULES = (
    ("amazon", "Amazon"),
    ("ebay", "eBay"),
    ("walmart", "Walmart"),
    ("target", "Target"),
    ("best buy", "Best Buy"),
    ("bestbuy", "Best Buy"),
)


def canonical_source(source: str) -> str:
    """Amazon.com、Walmart - Store 等统一成平台名，其余归为其他。"""
    text = (source or "").strip().lower()
    for needle, name in _RULES:
        if needle in text:
            return name
    return "其他"
