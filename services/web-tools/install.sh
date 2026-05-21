#!/bin/bash
# Web Tools Service — 一鍵安裝腳本
# 支援：macOS / Ubuntu / Debian
# 安裝：SearXNG (Docker) + Camoufox + MCP Server

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; exit 1; }

echo ""
echo "======================================"
echo "  Web Tools Service — 安裝程序"
echo "  SearXNG + Camoufox + MCP Server"
echo "======================================"
echo ""

# ── 1. 檢查 Docker ────────────────────────────────────
log "檢查 Docker..."
if ! command -v docker &>/dev/null; then
    warn "Docker 未安裝。請先安裝 Docker Desktop："
    echo "  macOS: https://docs.docker.com/desktop/install/mac-install/"
    echo "  Linux: https://docs.docker.com/engine/install/"
    err "請安裝 Docker 後重新執行此腳本"
fi
log "Docker 版本：$(docker --version)"

# ── 2. 檢查 Python ────────────────────────────────────
log "檢查 Python..."
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
    err "找不到 Python 3，請先安裝"
fi
PYVER=$($PYTHON --version 2>&1)
log "Python 版本：$PYVER"

# ── 3. 設定 SearXNG secret key ──────────────────────
log "設定 SearXNG..."
SECRET=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
SETTINGS="$SCRIPT_DIR/searxng/config/settings.yml"

if [ -f "$SETTINGS" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/CHANGE_THIS_TO_A_RANDOM_STRING/$SECRET/" "$SETTINGS"
    else
        sed -i "s/CHANGE_THIS_TO_A_RANDOM_STRING/$SECRET/" "$SETTINGS"
    fi
    log "已設定 secret key"
fi

# ── 4. 啟動 SearXNG ──────────────────────────────────
log "啟動 SearXNG Docker..."
cd "$SCRIPT_DIR"
docker compose up -d

# 等待 SearXNG 就緒
echo "  等待 SearXNG 啟動..."
for i in {1..15}; do
    if curl -sf "http://localhost:8080/search?q=test&format=json" > /dev/null 2>&1; then
        log "SearXNG 啟動成功！http://localhost:8080"
        break
    fi
    sleep 2
    if [ $i -eq 15 ]; then
        warn "SearXNG 啟動超時，請手動確認：docker logs searxng"
    fi
done

# ── 5. 安裝 Python 套件 ──────────────────────────────
log "安裝 Python 套件..."
$PYTHON -m pip install -q --upgrade \
    "camoufox[geoip]" \
    "mcp" \
    "httpx" \
    "markdownify"
log "套件安裝完成"

# ── 6. 下載 Camoufox 瀏覽器 ──────────────────────────
log "下載 Camoufox 瀏覽器（約 100MB，需要一點時間）..."
$PYTHON -m camoufox fetch
log "Camoufox 下載完成"

# ── 7. 快速測試 ───────────────────────────────────────
log "執行快速測試..."
cd "$SCRIPT_DIR"
TEST_RESULT=$($PYTHON -c "
import asyncio, httpx
async def test():
    async with httpx.AsyncClient() as c:
        r = await c.get('http://localhost:8080/search?q=test&format=json')
        data = r.json()
        count = len(data.get('results', []))
        print(f'SearXNG 正常，找到 {count} 筆結果')
asyncio.run(test())
" 2>&1)
log "$TEST_RESULT"

# ── 8. 輸出 MCP 設定 ─────────────────────────────────
echo ""
echo "======================================"
echo "  安裝完成！"
echo "======================================"
echo ""
echo "MCP Server 路徑："
echo "  $SCRIPT_DIR/web_tools_server.py"
echo ""
echo "加入 OpenClaw MCP 設定（貼進 openclaw 設定檔）："
echo '  {
    "mcpServers": {
      "web-tools": {
        "command": "python3",
        "args": ["'"$SCRIPT_DIR/web_tools_server.py"'"]
      }
    }
  }'
echo ""
echo "加入 Hermes MCP 設定："
echo '  tools:'
echo '    - type: mcp'
echo '      command: python3'
echo "      args: [\"$SCRIPT_DIR/web_tools_server.py\"]"
echo ""
echo "手動測試："
echo "  python3 $SCRIPT_DIR/web_tools_server.py"
echo ""
