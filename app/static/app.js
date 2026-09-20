const form = document.getElementById("search-form");
const input = document.getElementById("query");
const button = document.getElementById("search-btn");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const emptyEl = document.getElementById("empty");
const shelfEl = document.getElementById("shelf");
const filtersEl = document.getElementById("filters");
const railEl = document.getElementById("price-rail");
const conclusionEl = document.getElementById("conclusion");
const summaryMetaEl = document.getElementById("summary-meta");
const platformsEl = document.getElementById("platforms");

let activeSource = "全部";

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    input.value = chip.dataset.query;
    form.requestSubmit();
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = input.value.trim();
  if (!query) {
    showStatus("先输入一个商品名称。");
    return;
  }
  await runSearch(query);
});

async function runSearch(query) {
  button.disabled = true;
  showStatus("正在搜索，首次可能需要几十秒…");
  try {
    const response = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const body = await response.json();
    if (!response.ok) {
      showStatus(body.detail || "搜索失败。");
      hideResult();
      return;
    }
    activeSource = "全部";
    renderResult(body);
    statusEl.hidden = true;
  } catch (error) {
    showStatus("网络异常，稍后重试。");
    hideResult();
  } finally {
    button.disabled = false;
  }
}

function renderResult(payload) {
  emptyEl.hidden = true;
  resultEl.hidden = false;
  const summary = payload.summary;
  const cacheNote = payload.cached ? "缓存" : "新查询";
  const demoNote = payload.demo ? '<span class="demo-flag">演示</span>' : "";
  summaryMetaEl.innerHTML = `${summary.sample_size} 件 · ${cacheNote}${demoNote}`;
  conclusionEl.textContent = summary.conclusion;
  platformsEl.innerHTML = summary.platform_counts
    .map((item) => `<li>${item.source} ${item.count}</li>`)
    .join("");
  renderRail(payload.products, summary);
  renderFilters(payload.products);
  renderShelf(payload.products);
}

function renderRail(products, summary) {
  const priced = products.filter((item) => typeof item.price_usd === "number");
  if (!priced.length || summary.min_price == null || summary.max_price == null) {
    railEl.innerHTML = '<p class="rail__empty">没有可用报价，画不出价格带。</p>';
    return;
  }
  const min = summary.min_price;
  const max = summary.max_price;
  const span = Math.max(max - min, 0.01);
  const mid =
    summary.median_price != null ? `中位 $${Number(summary.median_price).toFixed(0)}` : "";
  railEl.innerHTML = `
    <div class="rail__scale">
      <span>$${min.toFixed(0)}</span>
      <span>${mid}</span>
      <span>$${max.toFixed(0)}</span>
    </div>
    <div class="rail__track"></div>
  `;
  const track = railEl.querySelector(".rail__track");
  priced.slice(0, 12).forEach((item) => {
    const left = ((item.price_usd - min) / span) * 100;
    const mark = document.createElement("i");
    mark.className = "rail__dot";
    mark.style.left = `${left}%`;
    mark.title = `${item.title} · ${item.price_display}`;
    track.appendChild(mark);
  });
}

function renderFilters(products) {
  const order = ["Amazon", "eBay", "Walmart", "Target", "Best Buy", "其他"];
  const unique = [...new Set(products.map((item) => item.source))];
  const sources = [
    "全部",
    ...order.filter((name) => unique.includes(name)),
    ...unique.filter((name) => !order.includes(name)),
  ];
  filtersEl.innerHTML = "";
  sources.forEach((source) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = `filter${source === activeSource ? " is-on" : ""}`;
    chip.textContent = source;
    chip.addEventListener("click", () => {
      activeSource = source;
      renderFilters(products);
      renderShelf(products);
    });
    filtersEl.appendChild(chip);
  });
}

function renderShelf(products) {
  const visible =
    activeSource === "全部"
      ? products
      : products.filter((item) => item.source === activeSource);
  shelfEl.innerHTML = "";
  if (!visible.length) {
    shelfEl.innerHTML = "<p class='status'>这个平台没有匹配商品。</p>";
    return;
  }
  visible.forEach((item) => {
    const card = document.createElement("article");
    card.className = "card";
    const image = item.image
      ? `<img src="${escapeAttr(item.image)}" alt="" referrerpolicy="no-referrer">`
      : `<div class="card__fallback">无图</div>`;
    const rating =
      item.rating != null
        ? `${item.rating} 分${item.reviews != null ? ` · ${formatCount(item.reviews)} 评价` : ""}`
        : "暂无评分";
    card.innerHTML = `
      ${image}
      <div class="card__body">
        <div class="card__meta">
          <span class="source">${escapeHtml(item.source)}</span>
          <span class="price">${escapeHtml(item.price_display)}</span>
        </div>
        <h3>${escapeHtml(item.title)}</h3>
        <p class="rating">${escapeHtml(rating)}</p>
        <a class="buy" href="${escapeAttr(item.url)}" target="_blank" rel="noopener noreferrer">打开购买页</a>
      </div>
    `;
    const img = card.querySelector("img");
    if (img) {
      img.addEventListener("error", () => {
        const fallback = document.createElement("div");
        fallback.className = "card__fallback";
        fallback.textContent = "无图";
        img.replaceWith(fallback);
      });
    }
    shelfEl.appendChild(card);
  });
}

function formatCount(value) {
  return new Intl.NumberFormat("en-US").format(value);
}

function showStatus(message) {
  statusEl.hidden = false;
  statusEl.textContent = message;
}

function hideResult() {
  resultEl.hidden = true;
  emptyEl.hidden = false;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function escapeAttr(value) {
  return escapeHtml(value).replaceAll("'", "&#39;");
}
