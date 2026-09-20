# 货架调研

美国购物平台商品调研小站：输入品名，从 Amazon、eBay、Walmart 等货架拉回图片、价格和购买链接，并给出一条竞争度启发式判断。

## 本地运行

Python 3.12。本项目用独立虚拟环境，不必绑 `edu_rag`。

```powershell
cd D:\商品查询demo
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

在 `.env` 填入 `SERPAPI_API_KEY`。没有 Key 时，搜索 `wireless earbuds` 仍可走内置演示数据。

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

打开 http://127.0.0.1:8000 。

## 测试

```powershell
pytest
```

SerpAPI 调用在测试里被 mock，不会消耗额度。

## 公网部署（Render）

1. 把本仓库推到 GitHub。
2. 在 [Render](https://render.com/) 用 Blueprint 导入 `render.yaml`，或手动新建 Web Service：
   - Build：`pip install -r requirements.txt`
   - Start：`uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. 在 Environment 写入 `SERPAPI_API_KEY`。
4. 免费档第一次打开可能要等 30–60 秒冷启动。
5. SQLite 缓存在免费磁盘上，实例重启后会清空，只影响额度，不影响功能。

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 选品工作台页面 |
| GET | `/api/health` | 健康检查，含是否已配置 Key |
| POST | `/api/search` | `{"query": "wireless earbuds"}`，返回商品列表与调研摘要 |

同一查询词默认缓存 24 小时，避免重复消耗 SerpAPI 免费额度。
