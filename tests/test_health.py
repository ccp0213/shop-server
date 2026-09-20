"""健康检查与首页可访问。"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert "serpapi_configured" in body


def test_home_page_renders():
    response = client.get("/")
    assert response.status_code == 200
    assert "货架调研" in response.text
