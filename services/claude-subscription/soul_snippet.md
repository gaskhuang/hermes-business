# Claude Subscription OAuth — soul.md / AGENTS.md 片段

> 把以下內容貼入 soul.md（Hermes）或 AGENTS.md（OpenClaw）
> 讓 agent 知道可以走訂閱 OAuth 呼叫 Claude，不消耗 API 額度

---

## 以下內容貼入 soul.md / AGENTS.md

```markdown
# Claude Subscription OAuth

你可以透過本地 OAuth Server 呼叫 Claude，走訂閱而非 API 額度。

## 端點
- URL：http://localhost:3456/v1/chat/completions
- 格式：OpenAI 相容（同 Anthropic API，但不需要 API key）

## 可用模型
| 模型名稱 | 對應 |
|---------|------|
| claude-oauth-sonnet | Claude Sonnet（均衡，預設）|
| claude-oauth-opus | Claude Opus（最強推理）|
| claude-oauth-haiku | Claude Haiku（最快）|

## 使用時機
- 一般分析、草稿、問答 → claude-oauth-sonnet
- 複雜推理、策略規劃 → claude-oauth-opus
- 快速確認、分類 → claude-oauth-haiku

## Python 呼叫範例
```python
import httpx

def ask(prompt: str, model: str = "claude-oauth-sonnet") -> str:
    r = httpx.post(
        "http://localhost:3456/v1/chat/completions",
        json={"model": model, "messages": [{"role": "user", "content": prompt}]},
        timeout=120
    )
    return r.json()["choices"][0]["message"]["content"]
```

## 注意
- 若 server 未啟動：`bash ~/path/to/claude-subscription/start.sh`
- 若呼叫失敗：`curl http://localhost:3456/health` 確認狀態
- 每次只能一個並行呼叫（claude CLI 序列執行）
```
