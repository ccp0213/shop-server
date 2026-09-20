"""SQLite 查询缓存：按规范化 query 存 JSON，带 TTL。"""

import json
import sqlite3
import time
from pathlib import Path


def normalize_query(query: str) -> str:
    """大小写不敏感，连续空白压成单空格。"""
    return " ".join(query.lower().split())


class SearchCache:
    """单文件 SQLite 缓存，适合 Mini Project 单实例部署。"""

    def __init__(self, db_path: str | Path, ttl_seconds: int) -> None:
        self.db_path = Path(db_path)
        self.ttl_seconds = ttl_seconds
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS search_cache (
                    query_key TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get(self, query: str):
        key = normalize_query(query)
        now = time.time()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload, created_at FROM search_cache WHERE query_key = ?",
                (key,),
            ).fetchone()
            if row is None:
                return None
            if now - row["created_at"] > self.ttl_seconds:
                conn.execute("DELETE FROM search_cache WHERE query_key = ?", (key,))
                return None
            return json.loads(row["payload"])

    def set(self, query: str, payload) -> None:
        key = normalize_query(query)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO search_cache (query_key, payload, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(query_key) DO UPDATE SET
                    payload = excluded.payload,
                    created_at = excluded.created_at
                """,
                (key, json.dumps(payload, ensure_ascii=False), time.time()),
            )
