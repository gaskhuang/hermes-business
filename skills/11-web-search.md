# Skill：Web Search（真實網路搜尋）

> 透過 SearXNG + Camoufox 讓 agent 能搜尋網路、瀏覽頁面，繞過 bot 偵測

## 前置條件

需先安裝 web-tools 服務：`services/web-tools/DEPLOY_PROMPT.md`

確認服務運行：
```bash
curl "http://localhost:8080/search?q=test&format=json" | head -20
```

## 觸發指令

| 指令 | 說明 |
|------|------|
| `/search [關鍵字]` | 搜尋網路，返回前 10 筆結果 |
| `/browse [URL]` | 瀏覽特定網頁，返回 markdown 內容 |
| `/search news [主題]` | 搜尋最新新聞（time_range=week）|
| `/search zh [關鍵字]` | 繁體中文搜尋 |

## MCP 工具（agent 直接呼叫）

```python
# 透過 MCP Server 暴露兩個工具：

web_search(query: str, time_range: str = None, language: str = "zh-TW") -> str
  # 呼叫 SearXNG，返回結構化搜尋結果

browse_url(url: str) -> str
  # 用 Camoufox 瀏覽頁面，返回 markdown 格式內容（最多 8000 字）
```

## 技術棧

```
SearXNG（port 8080）  ← 聚合 Google / Bing / DuckDuckGo / Brave
    ↓
MCP Server（stdio）   ← 讓 Hermes 直接呼叫
    ↓
Camoufox              ← 瀏覽頁面（C++ 指紋偽裝，繞過 bot 偵測）
```

## 重要限制

- **必須在家用 IP 運行**（不能 VPS）：Camoufox 偽裝瀏覽器指紋，但需要住宅 IP 才能繞過 Cloudflare/Akamai
- 搜尋結果依 SearXNG 引擎設定，可在 `settings.yml` 調整

## 組合使用

此 skill 常與以下搭配：
- `10-reddit-radar`：搜尋補充爬蟲找不到的資料
- `06-smart-router`：搜尋結果分析可走 fast 模型
- `04-second-brain`：把搜尋到的重要事實存入記憶
