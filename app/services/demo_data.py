"""无 API Key 时可用的内置演示数据，保证站点能被打开评审。"""

from app.models import Product
from app.services.cache import normalize_query

DEMO_QUERY = "wireless earbuds"

DEMO_PRODUCTS = [
    Product(
        title="TOZO T6 True Wireless Earbuds",
        price_usd=29.99,
        price_display="$29.99",
        image="https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=400&h=400&q=80",
        url="https://www.amazon.com/s?k=TOZO+T6+True+Wireless+Earbuds",
        source="Amazon",
        rating=4.4,
        reviews=187632,
    ),
    Product(
        title="JBL Tune 230NC TWS",
        price_usd=49.95,
        price_display="$49.95",
        image="https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?auto=format&fit=crop&w=400&h=400&q=80",
        url="https://www.amazon.com/s?k=JBL+Tune+230NC",
        source="Amazon",
        rating=4.3,
        reviews=21450,
    ),
    Product(
        title="Apple AirPods 4",
        price_usd=129.00,
        price_display="$129.00",
        image="https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?auto=format&fit=crop&w=400&h=400&q=80",
        url="https://www.walmart.com/search?q=Apple+AirPods+4",
        source="Walmart",
        rating=4.6,
        reviews=8433,
    ),
    Product(
        title="Sony WF-C700N Noise Canceling Earbuds",
        price_usd=98.00,
        price_display="$98.00",
        image="https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?auto=format&fit=crop&w=400&h=400&q=80",
        url="https://www.ebay.com/sch/i.html?_nkw=Sony+WF-C700N",
        source="eBay",
        rating=4.5,
        reviews=2104,
    ),
    Product(
        title="Beats Studio Buds",
        price_usd=79.95,
        price_display="$79.95",
        image="https://images.unsplash.com/photo-1598331668826-20cecc596b86?auto=format&fit=crop&w=400&h=400&q=80",
        url="https://www.target.com/s?searchTerm=Beats+Studio+Buds",
        source="Target",
        rating=4.4,
        reviews=5621,
    ),
    Product(
        title="Anker Soundcore Life P3",
        price_usd=59.99,
        price_display="$59.99",
        image="https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=400&h=400&q=80",
        url="https://www.bestbuy.com/site/searchpage.jsp?st=Anker+Soundcore+Life+P3",
        source="Best Buy",
        rating=4.5,
        reviews=9801,
    ),
]


def is_demo_query(query: str) -> bool:
    return normalize_query(query) == DEMO_QUERY
