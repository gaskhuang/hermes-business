請幫我安裝「Web Tools Service」，這會讓你能夠搜尋網路和瀏覽網頁，而且不會被網站的機器人偵測系統封鎖。請依序執行以下所有步驟：

---

## 步驟 1：確認環境

```bash
docker --version
python3 --version
```

如果 Docker 沒安裝，告訴我，我會先處理。

---

## 步驟 2：建立服務目錄並下載檔案

```bash
mkdir -p ~/web-tools-service/searxng/config
cd ~/web-tools-service
```

---

## 步驟 3：建立 docker-compose.yml

```bash
cat > ~/web-tools-service/docker-compose.yml << 'EOF'
name: web-tools

services:
  searxng:
    container_name: searxng
    image: docker.io/searxng/searxng:latest
    restart: always
    ports:
      - "8080:8080"
    volumes:
      - ./searxng/config/:/etc/searxng/:Z
      - searxng-data:/var/cache/searxng/
    environment:
      - SEARXNG_BASE_URL=http://localhost:8080/
    depends_on:
      - valkey

  valkey:
    container_name: searxng-valkey
    image: docker.io/valkey/valkey:9-alpine
    command: valkey-server --save 30 1 --loglevel warning
    restart: always
    volumes:
      - valkey-data:/data/

volumes:
  searxng-data:
  valkey-data:
EOF
```

---

## 步驟 4：建立 SearXNG 設定檔

```bash
SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")

cat > ~/web-tools-service/searxng/config/settings.yml << EOF
use_default_settings: true

server:
  secret_key: "${SECRET}"
  limiter: false
  port: 8080
  bind_address: "0.0.0.0"

search:
  safe_search: 0
  default_lang: "zh-TW"
  formats:
    - html
    - json
    - csv
    - rss
EOF
```

---

## 步驟 5：啟動 SearXNG

```bash
cd ~/web-tools-service
docker compose up -d

# 等待啟動（約 10 秒）
sleep 12

# 確認正常
curl -s "http://localhost:8080/search?q=test&format=json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'✓ SearXNG 正常，找到 {len(d[\"results\"])} 筆結果')"
```

---

## 步驟 6：安裝 Python 套件

```bash
pip install -U "camoufox[geoip]" mcp httpx markdownify
python3 -m camoufox fetch
```

---

## 步驟 7：建立 MCP Server

```bash
cat > ~/web-tools-service/web_tools_server.py << 'PYEOF'
#!/usr/bin/env python3
import asyncio
import httpx
from markdownify import markdownify

SEARXNG_URL = "http://localhost:8080"
MAX_RESULTS = 10
MAX_PAGE_CHARS = 8000

try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("web-tools")
    USE_MCP = True
except ImportError:
    USE_MCP = False

async def _search(query, time_range=None, language="zh-TW"):
    params = {"q": query, "format": "json", "language": language, "pageno": 1}
    if time_range:
        params["time_range"] = time_range
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{SEARXNG_URL}/search", params=params)
        data = resp.json()
    results = data.get("results", [])[:MAX_RESULTS]
    if not results:
        return "沒有找到相關結果。"
    lines = [f"搜尋：{query}\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r.get('title','')}")
        lines.append(f"    {r.get('url','')}")
        if r.get("content"):
            lines.append(f"    {r['content'][:200]}")
        lines.append("")
    return "\n".join(lines)

async def _browse(url):
    try:
        from camoufox.async_api import AsyncCamoufox
        async with AsyncCamoufox(os="windows", humanize=True, geoip=True, headless=True, block_webrtc=True) as browser:
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            html = await page.content()
            title = await page.title()
    except ImportError:
        async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}, timeout=15, follow_redirects=True) as client:
            resp = await client.get(url)
            html = resp.text
            title = url
    md = markdownify(html, heading_style="ATX", strip=["script","style","nav","footer"])
    md = "\n".join(l for l in md.splitlines() if l.strip())
    output = f"# {title}\nURL: {url}\n\n{md}"
    return output[:MAX_PAGE_CHARS] + ("\n\n[截斷...]" if len(output) > MAX_PAGE_CHARS else "")

if USE_MCP:
    @mcp.tool()
    async def web_search(query: str, time_range: str = None, language: str = "zh-TW") -> str:
        """透過自架 SearXNG 搜尋網路。time_range: day/month/year"""
        return await _search(query, time_range, language)

    @mcp.tool()
    async def browse_url(url: str) -> str:
        """用 Camoufox 反偵測瀏覽器訪問網頁，繞過 Cloudflare 等封鎖。"""
        return await _browse(url)

if __name__ == "__main__":
    if USE_MCP:
        mcp.run(transport="stdio")
    else:
        asyncio.run(_search("test"))
PYEOF
```

---

## 步驟 8：設定 OpenClaw MCP

在 OpenClaw 的 `mcp_settings.json` 或 `.openclaw/config.yml` 中加入：

```json
{
  "mcpServers": {
    "web-tools": {
      "command": "python3",
      "args": ["/Users/YOUR_USERNAME/web-tools-service/web_tools_server.py"]
    }
  }
}
```

**或 Hermes 用戶（加入 soul.md 或 config.yml）：**

```yaml
tools:
  - type: mcp
    name: web-tools
    command: python3
    args:
      - /Users/YOUR_USERNAME/web-tools-service/web_tools_server.py
```

---

## 步驟 9：驗證測試

重啟 OpenClaw/Hermes 後，輸入以下指令測試：

```
請用 web_search 搜尋「2026 AI agent trends」並告訴我前 3 個結果
```

然後：

```
請用 browse_url 訪問 https://example.com 並摘要內容
```

---

## 安裝完成後你可以做什麼

✅ 搜尋網路，不被 rate limit（SearXNG 同時查多個搜尋引擎）
✅ 瀏覽任何網站，繞過 Cloudflare bot 偵測（Camoufox）
✅ 抓取需要登入的頁面（搭配 cookies）
✅ 在居家 IP 下執行，不怕 datacenter IP 被封鎖

## 注意事項

- **一定要在家裡的電腦跑**，不要在 VPS/雲端跑（居家 IP 才是關鍵）
- SearXNG 只監聽 localhost，外部無法存取（安全）
- Camoufox 每次會模擬不同的瀏覽器指紋
