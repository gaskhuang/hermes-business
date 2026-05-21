# Claude Subscription OAuth Server

> 把你的 Claude Pro/Max 訂閱包成本地 OpenAI 相容 API
> 讓 Hermes / LiteLLM 直接路由進來，**不消耗 API 額度**

---

## 原理

```
Hermes / LiteLLM
    ↓  POST http://localhost:3456/v1/chat/completions
Claude Subscription OAuth Server（這個）
    ↓  claude -p "..." --model sonnet --output-format json
claude CLI（走你的 OAuth 登入，使用訂閱額度）
    ↓
回應（OpenAI 格式）
```

**關鍵**：`claude` CLI 用的是 OAuth 登入（`claude auth login`），
呼叫時走你的 Claude Pro/Max 訂閱，**不需要 ANTHROPIC_API_KEY**，
也**不會產生 API 帳單**。

---

## 快速啟動

```bash
cd services/claude-subscription
uv venv && uv pip install fastapi uvicorn
source .venv/bin/activate
python3 claude_oauth_server.py
```

確認運行：
```bash
curl http://localhost:3456/health
```

---

## 支援的模型名稱

| 呼叫名稱 | 對應 claude CLI |
|---------|----------------|
| `claude-oauth-sonnet` | `--model sonnet` |
| `claude-oauth-opus` | `--model opus` |
| `claude-oauth-haiku` | `--model haiku` |
| `subscription` | `--model sonnet`（LiteLLM 別名）|

---

## 整合到 LiteLLM（已內建於 cost-control 設定）

`services/cost-control/litellm_config.yaml` 已加入：

```yaml
- model_name: "subscription"
  litellm_params:
    model: "openai/claude-oauth-sonnet"
    api_base: "http://localhost:3456"
    api_key: "not-needed"
```

啟動後，Hermes 就可以用 `model: "subscription"` 走訂閱 OAuth。

---

## 使用限制

| 項目 | 說明 |
|------|------|
| 速率限制 | 依你的訂閱方案（Pro: 較低，Max: 很高） |
| 並行呼叫 | 每次只能一個（claude CLI 是序列執行）|
| 串流 | 目前不支援（`stream: true` 會被轉成同步）|
| 多模態 | 目前只支援文字 |

---

## 成本對比

| 方案 | 每百萬 tokens | 月費模式 |
|------|-------------|---------|
| Anthropic API（Sonnet） | $3 USD | 按量計費 |
| Claude Pro 訂閱 + 此服務 | $0（含在月費）| $20 USD/月 |
| Claude Max 訂閱 + 此服務 | $0（含在月費）| $100 USD/月 |

**Max 訂閱重度使用的話，此方案回本極快。**
