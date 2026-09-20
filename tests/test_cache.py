"""SQLite 查询缓存：规范化 key、TTL 命中与过期。"""

import time

from app.services.cache import SearchCache


def test_cache_hit_and_miss(tmp_path):
    cache = SearchCache(tmp_path / "cache.db", ttl_seconds=3600)
    assert cache.get("Wireless Earbuds") is None
    cache.set("Wireless Earbuds", [{"title": "demo"}])
    assert cache.get("  wireless   earbuds ") == [{"title": "demo"}]


def test_cache_expires(tmp_path):
    cache = SearchCache(tmp_path / "cache.db", ttl_seconds=1)
    cache.set("q", [1])
    time.sleep(1.1)
    assert cache.get("q") is None
