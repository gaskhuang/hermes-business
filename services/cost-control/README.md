# Cost Control Pro

> 混合路由 + 本地模型，把 AI API 月費壓低 60–95%

## 問題

大多數人用最貴的模型跑所有事情：
- 分類 Email → Claude Sonnet（$3/1M tokens）
- 確認「好的，已收到」→ Claude Sonnet
- 真正需要推理的任務 → 還是 Sonnet（反而不夠強）

**結果：60% 的 API 費用是浪費，10% 的任務反而模型不夠強。**

## 解法：三層路由 + 本地模型

```
雜事（分類/摘要/格式化）→ Haiku / 本地 Phi-4    省 92%
日常（分析/草稿/研究）  → Sonnet（維持品質）
複雜（推理/架構/策略）  → Opus（升級反而省錢）
隱私（客戶資料/合約）   → 本地 Ollama（零成本）
```

## 安裝

把 `DEPLOY_PROMPT.md` 全文貼入 Hermes 或 OpenClaw，agent 會自動：

1. 安裝 LiteLLM Proxy
2. 建立路由設定（三層模型）
3. 偵測並整合本地 Ollama（如果有安裝）
4. 設定 macOS launchd 開機自動啟動
5. 更新 soul.md / AGENTS.md，加入路由使用規則
6. 執行測試，確認三層路由都能正常呼叫

## 費用試算

| 月呼叫量 | 優化前 | 混合路由 | 加本地模型 |
|----------|--------|---------|----------|
| 500 次   | $30 USD | $9 USD | $3 USD |
| 2,000 次 | $120 USD | $36 USD | $10 USD |
| 10,000 次 | $600 USD | $180 USD | $50 USD |

## 檔案說明

| 檔案 | 用途 |
|------|------|
| `DEPLOY_PROMPT.md` | 一鍵部署指令，貼給 agent 執行 |
| `litellm_config.yaml` | LiteLLM Proxy 路由設定 |
| `router.py` | Python 智慧路由器（可直接 import） |
| `DEEP-ANALYSIS.md` | 完整技術分析與社群調研 |
