# Skill：Cost Watcher（API 費用監控）

> 追蹤每日/每月 AI API 費用，發現浪費點，自動告警

## 前置條件

需先安裝 LiteLLM Proxy：`services/cost-control/DEPLOY_PROMPT.md`

## 觸發指令

| 指令 | 說明 |
|------|------|
| `/cost` | 顯示今日費用摘要 |
| `/cost month` | 顯示本月費用和預測 |
| `/cost top` | 顯示最貴的前 10 次呼叫 |
| `/cost breakdown` | 依模型分類的費用明細 |
| `/cost alert [金額]` | 設定月費上限告警（USD）|
| `/cost report` | 產出完整費用優化建議報告 |

## 啟動規則

每週一次（或用戶問到費用時）：

```
1. 從 LiteLLM Proxy 取得費用數據
2. 若預測本月超出預算 → 主動提醒
3. 若某個模型佔比超過 70% → 提示可能有優化空間
```

## 費用報告格式

```
📊 AI 費用報告 — 2026-05-21

今日：$0.43 USD
  fast（Haiku）  ：$0.02  — 80 次呼叫
  standard（Sonnet）：$0.38 — 12 次呼叫
  local（Ollama）：$0.00  — 45 次呼叫

本月累計：$8.20 USD
預測月底：$12.50 USD（預算 $30 USD，剩餘空間充足）

🔍 優化建議：
  - 「分類 Email」共呼叫 standard 8 次 → 可改 fast，省 $0.24
  - 本地模型使用率 48%，持續良好

🔔 告警設定：$30 USD/月
```

## 自動偵測浪費點

```
若發現以下模式，主動提示：

1. 相同任務反覆用貴模型
   「過去 7 天，你用 Sonnet 做了 30 次摘要，改用 Haiku 可省 $2.10」

2. 短 prompt 用強力模型
   「偵測到 10 次 <50 字的 prompt 走了 Opus，建議改 standard」

3. 高頻低難度任務
   「確認指令（好的/已收到）用了 Sonnet 15 次，完全不需要」
```

## 費用數據來源

```python
# LiteLLM Proxy API
import httpx

def get_spend():
    r = httpx.get("http://localhost:4000/spend/logs",
                  headers={"Authorization": f"Bearer {API_KEY}"})
    return r.json()

def get_monthly():
    r = httpx.get("http://localhost:4000/spend/calculate",
                  params={"start_date": "2026-05-01"})
    return r.json()
```

## 組合使用

此 skill 常與以下搭配：
- `06-smart-router`：路由決策 + 費用追蹤形成完整閉環
- `07-local-llm`：追蹤本地模型節省了多少費用
- `09-telegram-notify`：每週費用報告自動發送到 Telegram
