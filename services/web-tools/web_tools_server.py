#!/usr/bin/env python3
"""
Web Tools MCP Server
提供兩個工具給 OpenClaw / Hermes Agent：
  1. web_search  — 透過 SearXNG 搜尋（不被封鎖）
  2. browse_url  — 透過 Camoufox 瀏覽網頁（反偵測）

啟動方式：
  python web_tools_server.py

相依套件：
  pip install mcp camoufox[geoip] httpx markdownify
  python -m camoufox fetch
"""

import asyncio
import httpx
from markdownify import markdownify

# ── 設定 ──────────────────────────────────────────────
SEARXNG_URL = "http://localhost:8080"   # SearXNG Docker 位址
MAX_RESULTS = 10                        # 搜尋結果數量上限
MAX_PAGE_CHARS = 8000                   # 網頁內容截斷字數
# ──────────────────────────────────────────────────────

try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("web-tools")
    USE_MCP = True
except ImportError:
    USE_MCP = False
    print("[warn] mcp 套件未安裝，以 standalone 模式執行（僅供測試）")


# ── Tool 1：Web Search ────────────────────────────────

async def _search(query: str, time_range: str = None, language: str = "zh-TW") -> str:
    params = {
        "q": query,
        "format": "json",
        "categories": "general",
        "language": language,
        "pageno": 1,
    }
    if time_range:
        params["time_range"] = time_range

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{SEARXNG_URL}/search", params=params)
        resp.raise_for_status()
        data = resp.json()

    results = data.get("results", [])[:MAX_RESULTS]
    if not results:
        return "沒有找到相關結果。"

    lines = [f"搜尋：{query}\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r.get('title', '(無標題)')}")
        lines.append(f"    {r.get('url', '')}")
        snippet = r.get("content", "").strip()
        if snippet:
            lines.append(f"    {snippet[:200]}")
        lines.append("")

    return "\n".join(lines)


# ── Tool 2：Browse URL ────────────────────────────────

async def _browse(url: str) -> str:
    try:
        from camoufox.async_api import AsyncCamoufox

        async with AsyncCamoufox(
            os="windows",
            humanize=True,
            geoip=True,
            headless=True,
            block_webrtc=True,
        ) as browser:
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            html = await page.content()
            title = await page.title()

    except ImportError:
        # fallback：用 httpx 直接抓（沒有反偵測，但能用）
        async with httpx.AsyncClient(
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            timeout=15,
            follow_redirects=True,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text
            title = url

    # HTML → Markdown（去除雜訊，讓 agent 好讀）
    md = markdownify(html, heading_style="ATX", strip=["script", "style", "nav", "footer"])
    md = "\n".join(line for line in md.splitlines() if line.strip())

    output = f"# {title}\nURL: {url}\n\n{md}"
    return output[:MAX_PAGE_CHARS] + ("\n\n[內容已截斷...]" if len(output) > MAX_PAGE_CHARS else "")


# ── MCP 工具定義 ──────────────────────────────────────

if USE_MCP:

    @mcp.tool()
    async def web_search(
        query: str,
        time_range: str = None,
        language: str = "zh-TW",
    ) -> str:
        """
        透過自架 SearXNG 搜尋網路，不被 rate limit 或 bot 偵測。
        time_range 可選：day / month / year
        language 範例：zh-TW / en-US / ja-JP
        """
        return await _search(query, time_range, language)

    @mcp.tool()
    async def browse_url(url: str) -> str:
        """
        用 Camoufox 反偵測瀏覽器訪問網頁，繞過 Cloudflare / bot 偵測。
        回傳 Markdown 格式的頁面內容。
        """
        return await _browse(url)


# ── Standalone 測試模式 ───────────────────────────────

async def _test():
    print("=== 測試 web_search ===")
    result = await _search("Hermes Agent 2026 use cases")
    print(result)

    print("\n=== 測試 browse_url ===")
    result = await _browse("https://example.com")
    print(result[:500])


if __name__ == "__main__":
    if USE_MCP:
        print("啟動 MCP server（web-tools）...")
        mcp.run(transport="stdio")
    else:
        asyncio.run(_test())
