#!/bin/bash
# Claude Subscription OAuth Server — 安裝腳本
# 用途：把 claude CLI OAuth 包成本地 OpenAI 相容 API（port 3456）

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USERNAME=$(whoami)
PORT=3456
PLIST_NAME="com.claude-oauth.server"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  Claude Subscription OAuth Server — 安裝     ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Step 1：確認 claude CLI ─────────────────────────────────
echo "▶ 確認 claude CLI..."
CLAUDE_BIN=$(which claude 2>/dev/null || echo "")
if [ -z "$CLAUDE_BIN" ]; then
  echo "❌ 找不到 claude CLI"
  echo "   請先安裝 Claude Code 並登入：https://claude.ai/download"
  exit 1
fi

# 快速測試 OAuth 是否正常
TEST=$(claude -p "ok" --output-format json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print('ok' if not d.get('is_error') else 'fail')" 2>/dev/null || echo "fail")
if [ "$TEST" != "ok" ]; then
  echo "❌ claude CLI 未登入或無法使用"
  echo "   請執行 claude 完成 OAuth 授權"
  exit 1
fi
echo "   ✅ claude CLI 可用：$CLAUDE_BIN"

# ── Step 2：安裝 Python 依賴 ────────────────────────────────
echo "▶ 安裝 Python 依賴..."
cd "$DIR"
if command -v uv &>/dev/null; then
  uv venv --quiet 2>/dev/null || true
  source .venv/bin/activate
  uv pip install -r requirements.txt --quiet
else
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt --quiet
fi
echo "   ✅ 依賴安裝完成"

# ── Step 3：建立啟動腳本 ─────────────────────────────────────
echo "▶ 建立啟動腳本..."
cat > "$DIR/start.sh" << EOF
#!/bin/bash
cd "$DIR"
source .venv/bin/activate
exec python3 claude_oauth_server.py
EOF
chmod +x "$DIR/start.sh"
echo "   ✅ start.sh 已建立"

# ── Step 4：更新 claude_oauth_server.py 的 CLAUDE_BIN 路徑 ──
echo "▶ 更新 server 設定..."
sed -i '' "s|shutil.which(\"claude\") or \"/Users/gask/.local/bin/claude\"|shutil.which(\"claude\") or \"$CLAUDE_BIN\"|g" \
    "$DIR/claude_oauth_server.py" 2>/dev/null || true
echo "   ✅ CLAUDE_BIN 已設定為 $CLAUDE_BIN"

# ── Step 5：launchd plist ────────────────────────────────────
echo "▶ 設定 macOS launchd..."

# 找 venv Python
VENV_PYTHON="$DIR/.venv/bin/python3"

# 若已存在，先卸載
if launchctl list "$PLIST_NAME" &>/dev/null 2>&1; then
  launchctl unload "$PLIST_PATH" 2>/dev/null || true
fi

# 直接用 venv python 執行，不經過 shell script（繞過 launchd 沙盒限制）
cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_NAME}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${VENV_PYTHON}</string>
    <string>${DIR}/claude_oauth_server.py</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${DIR}</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${DIR}/server.log</string>
  <key>StandardErrorPath</key>
  <string>${DIR}/server.log</string>
  <key>ThrottleInterval</key>
  <integer>10</integer>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/usr/bin:/bin:/Users/${USERNAME}/.local/bin</string>
  </dict>
</dict>
</plist>
EOF

launchctl load "$PLIST_PATH"
echo "   ✅ launchd 已設定，開機自動啟動"

# ── Step 6：啟動並測試 ───────────────────────────────────────
echo "▶ 啟動服務..."
launchctl start "$PLIST_NAME"
echo "   等待啟動（5 秒）..."
sleep 5

# 健康檢查
HEALTH=$(curl -s "http://localhost:${PORT}/health" 2>/dev/null || echo "fail")
if echo "$HEALTH" | grep -q '"status":"ok"'; then
  echo "   ✅ Server 運行中：http://localhost:${PORT}"
else
  echo "   ⚠️  Server 啟動中，請稍後再確認："
  echo "   curl http://localhost:${PORT}/health"
  echo "   tail -f ${DIR}/server.log"
fi

# ── 完成 ─────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  安裝完成！                                   ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  端點：http://localhost:${PORT}/v1/chat/completions ║"
echo "║  模型：claude-oauth-sonnet/opus/haiku        ║"
echo "║  費用：走訂閱 OAuth，不消耗 API 額度          ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "測試指令："
echo "  curl -s http://localhost:${PORT}/v1/chat/completions \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"model\":\"claude-oauth-sonnet\",\"messages\":[{\"role\":\"user\",\"content\":\"你好\"}]}' \\"
echo "    | python3 -c \"import json,sys; d=json.load(sys.stdin); print(d['choices'][0]['message']['content'])\""
echo ""
