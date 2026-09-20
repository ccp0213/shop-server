"""应用配置：从环境变量读取 SerpAPI Key 与缓存参数。"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """运行时配置。空 Key 时仅允许演示查询。"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    serpapi_api_key: str = ""
    cache_ttl_seconds: int = 86400
    cache_db_path: str = "data/cache.db"
    serpapi_num: int = 20

    @property
    def has_api_key(self) -> bool:
        return bool(self.serpapi_api_key.strip())


settings = Settings()
