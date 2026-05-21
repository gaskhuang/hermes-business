# Skill：Smart Router（智慧模型路由）

> 根據任務類型自動選擇最省錢的模型，不用每次手動切換

## 前置條件

需先安裝 LiteLLM Proxy：`services/cost-control/DEPLOY_PROMPT.md`

確認 Proxy 運行中：
```bash
curl -s http://localhost:4000/health
```

## 觸發指令

| 指令 | 說明 |
|------|------|
| `/route [任務描述]` | 顯示這個任務會路由到哪個模型 |
| `/route status` | 顯示所有可用模型和當月費用 |
| `/route fast [prompt]` | 強制使用快速模型（Haiku）|
| `/route local [prompt]` | 強制使用本地模型（Ollama）|
| `/route powerful [prompt]` | 強制使用強力模型（Opus）|

## 路由規則（自動偵測）

| 任務關鍵字 | 路由到 | 模型 | 費用 |
|-----------|--------|------|------|
| 分類、摘要、格式化、翻譯、確認 | `fast` | Claude Haiku | $0.25/1M |
| 分析、草稿、研究、規劃（預設）| `standard` | Claude Sonnet | $3/1M |
| 推理、架構、策略、複雜 | `powerful` | Claude Opus | $15/1M |
| 程式碼、code、function | `local-coder` | Qwen2.5-Coder | $0 |
| 隱私、機密、客戶資料 | `local-general` | Llama 3.3 | $0 |

## 行為規則

```
接收任務時：
  1. 掃描關鍵字，判斷任務類型
  2. 選擇對應模型
  3. 若不確定：預設 standard

隱私原則：
  → 只要 prompt 中出現客戶名稱、合約內容、密碼 → 強制走 local-general

費用超限：
  → 若當月費用超過設定上限 → 降級到 fast 或 local
```

## API 端點

```
Base URL：http://localhost:4000
格式：OpenAI 相容（直接把 api_base 改成這個 URL）
```

## 在 soul.md 加入此 skill 後的效果

```
用戶說：「幫我分類這 50 封 Email」
  → 偵測到「分類」→ 路由到 fast（Haiku）→ 省 92%

用戶說：「這份客戶合約的重點是什麼」
  → 偵測到「客戶」→ 路由到 local-general→ 資料不出機器

用戶說：「設計一個支援百萬用戶的 API 架構」
  → 偵測到「架構」→ 路由到 powerful（Opus）→ 用對刀
```

## 組合使用

此 skill 常與以下搭配：
- `07-local-llm`：確保本地模型已啟動才路由過去
- `08-cost-watcher`：即時追蹤路由決策帶來的費用變化
