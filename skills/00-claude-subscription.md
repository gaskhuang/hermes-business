# Skill：Claude Subscription OAuth（訂閱路由）

> 透過本地 OAuth Server，讓所有 LLM 呼叫走你的 Claude 訂閱，不消耗 API 額度

## 前置條件

1. 已安裝並登入 claude CLI（執行過 `claude`）
2. 已啟動 OAuth Server：`~/claude-oauth-server/start.sh`
3. 確認運行：`curl http://localhost:3456/health`

## 觸發指令

| 指令 | 說明 |
|------|------|
| `/sub [prompt]` | 用訂閱模型（Sonnet）回答 |
| `/sub opus [prompt]` | 用訂閱 Opus 回答（最強）|
| `/sub status` | 確認 OAuth Server 是否運行 |

## 使用方式

### 直接呼叫（不透過 LiteLLM）

```python
import httpx

def ask_via_subscription(prompt: str, model: str = "sonnet") -> str:
    r = httpx.post(
        "http://localhost:3456/v1/chat/completions",
        json={
            "model": f"claude-oauth-{model}",
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=120
    )
    return r.json()["choices"][0]["message"]["content"]
```

### 透過 LiteLLM（已整合，model 名稱用 "subscription"）

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:4000", api_key="anything")

response = client.chat.completions.create(
    model="subscription",       # 走訂閱 OAuth
    messages=[{"role": "user", "content": "你好"}]
)
```

## 原理

```
你的 prompt
    ↓
OAuth Server（localhost:3456）
    ↓  subprocess
claude -p "prompt" --model sonnet --output-format json
    ↓
Claude API（走你的 OAuth，計入訂閱用量，不額外計費）
    ↓
回應（OpenAI 格式）
```

## 費用說明

- **Claude Pro（$20 USD/月）**：使用限制較低，適合輕度用戶
- **Claude Max（$100 USD/月）**：高用量上限，重度使用者最划算
- **API 直接呼叫（Sonnet）**：$3 USD / 1M tokens，用量大時比 Max 貴

> Max 訂閱每月 API 等值用量通常超過 $200 USD，比付 API 划算。

## 限制

- **序列執行**：claude CLI 每次只能跑一個呼叫，不支援並行
- **不支援串流**：`stream: true` 無效，統一轉成同步回應
- **速率限制**：取決於你的訂閱等級（Max 比 Pro 高很多）

## 與其他 Skill 組合

```
subscription + smart-router：
  → 把 "standard" 和 "powerful" 的路由改成 "subscription"
  → 日常任務全走訂閱，只有隱私任務走本地

subscription + kanban-board：
  → Agent 自主處理 kanban 任務，全程用訂閱模型，不產生 API 費用
```
