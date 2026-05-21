# Claude Subscription OAuth Server — 一鍵部署

> 把以下全文貼入你的 Hermes / OpenClaw，agent 會自動完成安裝。
> 前提：已登入 claude CLI（執行過 `claude` 並完成 OAuth 授權）

---

```
請幫我安裝「Claude Subscription OAuth Server」，依以下步驟執行，每步完成後告訴我結果。

## 步驟 1：確認 claude CLI 已登入

```bash
which claude
claude -p "說你好" --output-format json 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('✅ claude CLI 正常，等值費用:', d.get('total_cost_usd'), 'USD（不實際扣款）')
" || echo "❌ claude CLI 未安裝或未登入"
```

若顯示 ❌，請先安裝 Claude Code 並登入：
1. 下載 Claude Code
2. 執行 `claude`，完成 OAuth 登入

## 步驟 2：建立服務目錄並安裝依賴

```bash
mkdir -p ~/claude-oauth-server
cd ~/claude-oauth-server
uv venv --quiet
source .venv/bin/activate
uv pip install fastapi uvicorn --quiet
python3 -c "import fastapi, uvicorn; print('✅ 依賴安裝完成')"
```

## 步驟 3：建立伺服器程式

在 ~/claude-oauth-server/server.py 建立以下內容：

---
import json, subprocess, shutil, time, uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

CLAUDE_BIN = shutil.which("claude") or "/Users/YOURUSERNAME/.local/bin/claude"
PORT = 3456
app = FastAPI()

MODEL_ALIASES = {
    "claude-oauth": "sonnet", "claude-oauth-sonnet": "sonnet",
    "claude-oauth-opus": "opus", "claude-oauth-haiku": "haiku",
    "subscription": "sonnet", "subscription-opus": "opus",
    "sonnet": "sonnet", "opus": "opus", "haiku": "haiku",
}

def messages_to_prompt(messages):
    system_parts, conv = [], []
    for m in messages:
        role, content = m.get("role",""), m.get("content","")
        if isinstance(content, list):
            content = " ".join(c.get("text","") for c in content if isinstance(c,dict))
        if role == "system": system_parts.append(content)
        elif role == "user": conv.append(f"User: {content}")
        elif role == "assistant": conv.append(f"Assistant: {content}")
    sys_prompt = "\n\n".join(system_parts) if system_parts else None
    if len(conv) > 1:
        hist = "\n".join(conv[:-1])
        sys_prompt = (f"{sys_prompt}\n\n對話歷史：\n{hist}" if sys_prompt
                      else f"對話歷史：\n{hist}")
    last_user = conv[-1].replace("User: ","",1) if conv else ""
    return last_user, sys_prompt

def call_claude(prompt, model="sonnet", system_prompt=None):
    cmd = [CLAUDE_BIN, "--print", "--output-format", "json", "--model", model, prompt]
    if system_prompt: cmd.extend(["--system-prompt", system_prompt])
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0: raise RuntimeError(r.stderr[:300])
    d = json.loads(r.stdout)
    if d.get("is_error"): raise RuntimeError(str(d))
    return {"text": d.get("result",""), "elapsed": time.time()-t0,
            "usage": d.get("usage",{}), "cost": d.get("total_cost_usd",0)}

@app.post("/v1/chat/completions")
async def chat(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    model = MODEL_ALIASES.get(body.get("model",""), "sonnet")
    if not messages: raise HTTPException(400, "messages required")
    prompt, sys_p = messages_to_prompt(messages)
    result = call_claude(prompt, model, sys_p)
    return JSONResponse({
        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": f"claude-oauth-{model}",
        "choices": [{"index":0,"message":{"role":"assistant","content":result["text"]},"finish_reason":"stop"}],
        "usage": {"prompt_tokens": result["usage"].get("input_tokens",0),
                  "completion_tokens": result["usage"].get("output_tokens",0),
                  "total_tokens": result["usage"].get("input_tokens",0)+result["usage"].get("output_tokens",0)},
        "x_subscription_cost_usd": result["cost"],
        "x_elapsed_seconds": round(result["elapsed"],2),
        "x_note": "走 Claude 訂閱 OAuth，不消耗 API 額度",
    })

@app.get("/health")
async def health():
    return {"status":"ok","claude_bin":CLAUDE_BIN,"port":PORT}

if __name__ == "__main__":
    print(f"Claude OAuth Server 啟動中：http://localhost:{PORT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
---

注意：把 YOURUSERNAME 換成你的實際用戶名（用 `whoami` 查）

## 步驟 4：建立啟動腳本

```bash
cat > ~/claude-oauth-server/start.sh << 'EOF'
#!/bin/bash
cd ~/claude-oauth-server
source .venv/bin/activate
python3 server.py >> server.log 2>&1
EOF
chmod +x ~/claude-oauth-server/start.sh
```

## 步驟 5：設定 macOS 開機自動啟動

```bash
USERNAME=$(whoami)
cat > ~/Library/LaunchAgents/com.claude-oauth.server.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.claude-oauth.server</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>/Users/$USERNAME/claude-oauth-server/start.sh</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key>
  <string>/Users/$USERNAME/claude-oauth-server/server.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/$USERNAME/claude-oauth-server/server.log</string>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.claude-oauth.server.plist
launchctl start com.claude-oauth.server
sleep 4
curl -s http://localhost:3456/health
```

## 步驟 6：測試 API

```bash
curl -s http://localhost:3456/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"subscription","messages":[{"role":"user","content":"用一句話介紹你自己"}]}' \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('回答:', d['choices'][0]['message']['content'])
print('耗時:', d['x_elapsed_seconds'], '秒')
print('等值費用:', d['x_subscription_cost_usd'], 'USD（不實際扣款）')
"
```

## 步驟 7：整合到 LiteLLM（若已安裝 cost-control）

在 ~/cost-control-proxy/litellm_config.yaml 的 model_list 最前面加入：

```yaml
  - model_name: "subscription"
    litellm_params:
      model: "openai/claude-oauth-sonnet"
      api_base: "http://localhost:3456"
      api_key: "not-needed"

  - model_name: "subscription-opus"
    litellm_params:
      model: "openai/claude-oauth-opus"
      api_base: "http://localhost:3456"
      api_key: "not-needed"
```

重啟 LiteLLM 後，所有路由到 `subscription` 的呼叫都走訂閱 OAuth，不扣 API 費用。

## 步驟 8：驗證完成

```bash
echo "=== Claude Subscription OAuth Server 狀態 ==="
curl -s http://localhost:3456/health > /dev/null && echo "✅ Server 運行中（port 3456）" || echo "❌ Server 未啟動"
launchctl list | grep claude-oauth > /dev/null && echo "✅ 開機自啟已設定" || echo "⚠️  開機自啟未設定"
echo "=== 完成 ==="
```

全部 ✅ 後，告訴我伺服器已啟動，並測試呼叫一次確認回應正常。
```
