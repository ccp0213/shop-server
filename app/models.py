"""对外 API 与内部服务共用的数据模型。"""

from pydantic import BaseModel, Field, field_validator


class Product(BaseModel):
    """一条美国购物平台上的竞品。"""

    title: str
    price_usd: float | None
    price_display: str
    image: str | None
    url: str
    source: str
    rating: float | None = None
    reviews: int | None = None


class PlatformCount(BaseModel):
    """某一来源平台的商品数量。"""

    source: str
    count: int


class ResearchSummary(BaseModel):
    """基于当前结果集的简易调研摘要。"""

    sample_size: int
    min_price: float | None
    median_price: float | None
    max_price: float | None
    avg_price: float | None
    platform_counts: list[PlatformCount]
    competition_level: str
    conclusion: str


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)

    @field_validator("query")
    @classmethod
    def strip_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("查询词不能为空")
        return stripped


class SearchResponse(BaseModel):
    query: str
    cached: bool
    demo: bool = False
    products: list[Product]
    summary: ResearchSummary
