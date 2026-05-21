# Web Tools Service

> 讓 Hermes / OpenClaw 的 agent 真正能「上網」，而且不被封鎖。

## 包含什麼

| 元件 | 說明 |
|------|------|
| **SearXNG** | 自架搜尋引擎，聚合 Google/Bing/DDG，無 rate limit |
| **Camoufox** | Firefox 反偵測瀏覽器，繞過 Cloudflare、bot 偵測 |
| **MCP Server** | 把上面兩個包成 `web_search` / `browse_url` 工具 |

## 快速安裝

```bash
chmod +x install.sh
./install.sh
```

## 手動安裝

```bash
# 1. 啟動 SearXNG
docker compose up -d

# 2. 安裝 Camoufox
pip install -U "camoufox[geoip]"
python3 -m camoufox fetch

# 3. 安裝 MCP 套件
pip install mcp httpx markdownify

# 4. 啟動 MCP Server
python3 web_tools_server.py
```

## 部署給客戶

把 `DEPLOY_PROMPT.md` 全文貼進客戶的 agent，自動完成安裝。

## 在 OpenClaw 設定 MCP

```json
{
  "mcpServers": {
    "web-tools": {
      "command": "python3",
      "args": ["/path/to/web_tools_server.py"]
    }
  }
}
```

## 在 Hermes 設定 MCP

```yaml
tools:
  - type: mcp
    name: web-tools
    command: python3
    args: ["/path/to/web_tools_server.py"]
```

## 注意事項

- **必須在家用 IP 的機器上跑**，VPS datacenter IP 無效
- SearXNG 預設只監聽 localhost，外部無法存取
- Camoufox 每次模擬不同的瀏覽器指紋
