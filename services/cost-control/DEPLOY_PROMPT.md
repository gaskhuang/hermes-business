# Cost Control Pro — 一鍵部署指令

> 把以下全文貼入你的 Hermes / OpenClaw，agent 會自動完成安裝。

---

```
請幫我安裝「Cost Control Pro — AI 費用控制路由層」，依以下步驟逐一執行，每一步完成後告訴我結果。

## 步驟 1：環境檢查

執行以下指令，告訴我結果：

```bash
python3 --version
pip3 show litellm 2>/dev/null | head -1 || echo "litellm 未安裝"
which ollama && ollama --version || echo "ollama 未安裝"
echo "ANTHROPIC_API_KEY: $([ -n "$ANTHROPIC_API_KEY" ] && echo '已設定' || echo '未設定')"
echo "OPENAI_API_KEY: $([ -n "$OPENAI_API_KEY" ] && echo '已設定' || echo '未設定')"
```

## 步驟 2：安裝 LiteLLM

```bash
pip3 install "litellm[proxy]" --quiet
pip3 show litellm | grep Version
```

## 步驟 3：建立專案目錄

```bash
mkdir -p ~/cost-control-proxy
cd ~/cost-control-proxy
```

## 步驟 4：建立路由設定檔

在 ~/cost-control-proxy/litellm_config.yaml 建立以下內容（根據剛才的環境檢查結果，只加入已有 API key 的模型）：

---
model_list:
  - model_name: "fast"
    litellm_params:
      model: "claude-haiku-3-5"
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: "standard"
    litellm_params:
      model: "claude-sonnet-4-5"
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: "powerful"
    litellm_params:
      model: "claude-opus-4"
      api_key: os.environ/ANTHROPIC_API_KEY

  # 如果有安裝 Ollama，加入以下（否則跳過）
  - model_name: "local-fast"
    litellm_params:
      model: "ollama/phi4:14b"
      api_base: "http://localhost:11434"

  - model_name: "local-coder"
    litellm_params:
      model: "ollama/qwen2.5-coder:32b"
      api_base: "http://localhost:11434"

  - model_name: "local-general"
    litellm_params:
      model: "ollama/qwen2.5:32b"
      api_base: "http://localhost:11434"

router_settings:
  routing_strategy: "cost-based"
  allowed_fails: 2
  fallbacks:
    - fast:
        - standard
    - local-fast:
        - fast

general_settings:
  max_budget: 50
  budget_duration: "1mo"
---

## 步驟 5：建立智慧路由器（router.py）

在 ~/cost-control-proxy/router.py 建立以下內容：

---
"""
Cost Control Pro — 智慧路由器
讓 Hermes / OpenClaw 自動選擇最省錢的模型

使用方式：
    from router import smart_call
    result = smart_call("幫我分類這封 Email", task_hint="classify")
"""
import os
from openai import OpenAI

PROXY_BASE = os.getenv("LITELLM_PROXY_URL", "http://localhost:4000")
client = OpenAI(base_url=PROXY_BASE, api_key="anything")

TASK_MODEL_MAP = {
    "classify":  "fast",
    "summarize": "fast",
    "format":    "fast",
    "extract":   "fast",
    "translate": "fast",
    "draft":     "standard",
    "analyze":   "standard",
    "plan":      "standard",
    "review":    "standard",
    "reason":    "powerful",
    "strategy":  "powerful",
    "architect": "powerful",
    "code":      "local-coder",
    "private":   "local-general",
}

KEYWORD_RULES = [
    (["分類","classify","是否","判斷"],           "classify"),
    (["摘要","summary","重點","總結"],             "summarize"),
    (["翻譯","translate","英文","中文轉"],         "translate"),
    (["幫我寫","草稿","draft","回覆","回信"],      "draft"),
    (["分析","analyze","為什麼","原因","深入"],    "analyze"),
    (["架構","設計","系統","規劃","architect"],    "architect"),
    (["程式","code","function","class","bug"],    "code"),
    (["密碼","token","secret","機密","客戶資料"], "private"),
]

def detect_task(prompt: str) -> str:
    p = prompt.lower()
    for keywords, task in KEYWORD_RULES:
        if any(k in p for k in keywords):
            return task
    return "analyze"

def smart_call(prompt: str, task_hint: str = None, system: str = None,
               temperature: float = 0.7, max_tokens: int = 2000) -> str:
    task = task_hint or detect_task(prompt)
    model = TASK_MODEL_MAP.get(task, "standard")
    print(f"🔀 路由：{task} → {model}")
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    try:
        r = client.chat.completions.create(
            model=model, messages=msgs,
            temperature=temperature, max_tokens=max_tokens)
        return r.choices[0].message.content
    except Exception as e:
        print(f"❌ {model} 失敗，fallback 到 standard：{e}")
        r = client.chat.completions.create(
            model="standard", messages=msgs,
            temperature=temperature, max_tokens=max_tokens)
        return r.choices[0].message.content
---

## 步驟 6：建立啟動腳本

在 ~/cost-control-proxy/start.sh 建立：

---
#!/bin/bash
# Cost Control Pro — 啟動 LiteLLM Proxy
cd ~/cost-control-proxy
litellm --config litellm_config.yaml --port 4000 >> proxy.log 2>&1
---

執行：
```bash
chmod +x ~/cost-control-proxy/start.sh
```

## 步驟 7：設定 macOS 開機自動啟動（launchd）

建立 ~/Library/LaunchAgents/com.cost-control.proxy.plist：

---
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.cost-control.proxy</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>/Users/USERNAME/cost-control-proxy/start.sh</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/Users/USERNAME/cost-control-proxy/proxy.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/USERNAME/cost-control-proxy/proxy.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>ANTHROPIC_API_KEY</key>
    <string>PLACEHOLDER_ANTHROPIC</string>
    <key>OPENAI_API_KEY</key>
    <string>PLACEHOLDER_OPENAI</string>
  </dict>
</dict>
</plist>
---

注意：把 USERNAME 換成實際用戶名（用 `whoami` 查），把 PLACEHOLDER_* 換成實際 API key。

執行：
```bash
launchctl load ~/Library/LaunchAgents/com.cost-control.proxy.plist
launchctl start com.cost-control.proxy
sleep 3
curl -s http://localhost:4000/health | python3 -m json.tool
```

## 步驟 8：測試三層路由

```bash
# 測試 fast（Haiku）
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"fast","messages":[{"role":"user","content":"用一句話說你是什麼模型"}]}'

# 測試 standard（Sonnet）
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"standard","messages":[{"role":"user","content":"用一句話說你是什麼模型"}]}'

# 若有 Ollama，測試 local-fast
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"local-fast","messages":[{"role":"user","content":"用一句話說你是什麼模型"}]}'
```

每個都應該回應不同的模型名稱。

## 步驟 9：更新 soul.md / AGENTS.md

在你的 soul.md 或 AGENTS.md 頂部加入以下內容：

---
# 模型路由規則（Cost Control Pro）

你的 API 呼叫透過本地 LiteLLM Proxy（http://localhost:4000）路由。
根據任務類型選擇對應模型，節省費用：

| 任務類型 | 使用模型 | 適用場景 |
|----------|---------|---------|
| fast | Claude Haiku | 分類、摘要、格式化、翻譯、確認 |
| standard | Claude Sonnet | 分析、草稿、研究、規劃（預設） |
| powerful | Claude Opus | 複雜推理、架構設計、策略規劃 |
| local-coder | 本地 Qwen | 所有程式碼任務（免費） |
| local-general | 本地 Llama | 隱私資料、不能上雲的任務 |

## 使用方式

在呼叫 LLM 時，根據任務類型指定 model 參數：
- ANTHROPIC_API_KEY 不變，但 base_url 改為 http://localhost:4000
- model 名稱用上表的路由名稱（fast/standard/powerful/local-*）
- 不確定時用 standard（安全預設值）
---

## 步驟 10：驗證安裝完成

執行以下確認清單：
```bash
echo "=== Cost Control Pro 安裝狀態 ==="
curl -s http://localhost:4000/health > /dev/null && echo "✅ Proxy 運行中" || echo "❌ Proxy 未啟動"
ls ~/cost-control-proxy/litellm_config.yaml > /dev/null && echo "✅ 設定檔存在" || echo "❌ 設定檔缺失"
ls ~/cost-control-proxy/router.py > /dev/null && echo "✅ 路由器存在" || echo "❌ 路由器缺失"
launchctl list | grep cost-control > /dev/null && echo "✅ 開機自啟已設定" || echo "⚠️  開機自啟未設定"
which ollama > /dev/null && echo "✅ Ollama 可用" || echo "ℹ️  Ollama 未安裝（本地模型不可用）"
echo "=== 完成 ==="
```

全部 ✅ 後，說「安裝完成」並告訴我每月預計可以節省多少費用（根據你目前的使用量估算）。
```
