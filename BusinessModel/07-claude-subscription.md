# 07｜Claude Subscription OAuth 服務

## 一句話定位

> 把客戶已有的 Claude Pro/Max 訂閱變成本地 API，所有 agent 呼叫走訂閱 OAuth，**API 帳單歸零**。

---

## 為什麼能賺錢

很多人同時付了兩筆錢：

```
Claude Max 訂閱：$100 USD/月（給自己用）
    +
Anthropic API：$80–200 USD/月（給 agent 用）

→ 總計：$180–300 USD/月
→ 其實 Claude Max 已經包含了足夠的用量，API 費是多付的
```

**真相：用這個服務，API 那筆可以降到 $0–$20。**

---

## 服務內容

```
建置（一次性）：
  ✅ 確認 claude CLI OAuth 登入狀態
  ✅ 安裝 OAuth Server（FastAPI，port 3456）
  ✅ 設定 macOS launchd 開機自動啟動
  ✅ 整合到 LiteLLM Proxy（讓現有路由無縫切換）
  ✅ 更新 soul.md / AGENTS.md，加入訂閱呼叫規則
  ✅ 測試多輪對話、system prompt、模型切換

每月維護：
  ✅ 確認 OAuth 登入狀態未過期
  ✅ 更新 claude CLI 版本
  ✅ 若 Anthropic 改 CLI 介面，同步更新 server
```

---

## 定價

| 方案 | 內容 | 建置費 | 月費 |
|------|------|--------|------|
| 基本版 | OAuth Server 安裝 + launchd | $5,000 TWD | $1,000 TWD |
| 整合版 | 含 LiteLLM 路由整合 + soul.md | $8,000 TWD | $1,500 TWD |
| 完整版 | 含費用審計 + 優化建議 + 每月維護 | $12,000 TWD | $2,500 TWD |

**ROI 話術**：

> 客戶現在每月多付 $80 USD API 費（約 $2,600 TWD）
> 你收月費 $1,500 TWD，客戶每月淨省 $1,100 TWD
> **建置費兩個月回本，之後持續省錢**

---

## 競爭優勢

**這個解法只有懂 claude CLI 的人才知道。**

| 一般客戶的狀況 | 你提供的解法 |
|------------|------------|
| Claude Max + 另付 API 費 | OAuth Server 讓訂閱涵蓋 API 用量 |
| 不知道 claude -p 可以非互動呼叫 | 把 CLI 包成 OpenAI 相容 API |
| 裝好後不知道怎麼維護 | 月費制，你幫他維護 |

---

## 技術架構

```
客戶的 Hermes / OpenClaw
    ↓  POST http://localhost:3456/v1/chat/completions
Claude OAuth Server（本地 FastAPI）
    ↓  subprocess
claude -p "prompt" --model sonnet --output-format json
    ↓  走 Claude CLI OAuth（訂閱）
Claude API
    ↓
回應（OpenAI 格式）→ 回到 Hermes
```

---

## 適合的客戶

| 客戶類型 | 為什麼適合 |
|----------|----------|
| 已有 Claude Pro/Max 的開發者 | 直接省掉 API 費，ROI 立竿見影 |
| 用 Hermes 跑自動化工作流的人 | Agent 大量呼叫，API 費會很高 |
| 想省錢但不想妥協模型品質的人 | 走訂閱還是用 Claude Sonnet/Opus |
| 已裝 cost-control 的人 | 直接加進 LiteLLM 路由，無縫整合 |

---

## 限制（要如實告知客戶）

| 限制 | 說明 |
|------|------|
| 序列執行 | claude CLI 每次只能一個呼叫，不支援並行 |
| 不支援串流 | `stream: true` 無效 |
| 速率限制 | 依訂閱等級（Max 比 Pro 高很多）|
| OAuth 過期 | claude CLI 登入偶爾需要重新授權 |

---

## 與其他服務的組合

```
最強省錢組合：
  cost-control（混合路由）
  + claude-subscription（訂閱路由）
  + local-model（本地路由）

路由優先序：
  隱私任務 → local-model（不出機器）
  一般任務 → claude-subscription（訂閱，$0 API費）
  高頻雜事 → local-model 或 claude-subscription haiku
  超出訂閱限制時 → API fast（Haiku，$0.25/1M，最便宜雲端）
```

---

## 銷售話術

**開場（針對已有 Claude 訂閱的人）：**

> 「你有訂 Claude Max 嗎？你知道你的 agent 每個月還另外付了多少 API 費嗎？很多人都同時付兩筆——訂閱費和 API 費。其實用 claude CLI，可以把你的訂閱包成本地 API，所有 agent 呼叫都走訂閱，API 帳單直接歸零。我幫你裝一次，之後每個月比現在少 $2,000 TWD 以上。要不要試試看？」
