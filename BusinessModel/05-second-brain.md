# 05｜Second Brain 記憶層服務（Cloudflare）

## 一句話定位

> 讓你的 AI Agent 不再每次都像第一次見面——用 Cloudflare 免費建一個跨設備、跨 session 的持久記憶層。

---

## 為什麼能賺錢

Agent 的最大缺陷之一：

```
用戶：「我跟你說過我喜歡簡短的回覆。」
Agent：「抱歉，我不記得上次的對話。」
用戶：[再說一遍]
用戶：[下次又要再說一遍]
```

每次重新解釋 = 用戶體驗的摩擦 = 用戶最終放棄

**更嚴重的問題：企業場景**

```
CTO 告訴 Agent 公司的技術棧、偏好、禁止事項
→ 第二天 Agent 全忘了
→ CTO 要一直在系統 prompt 裡塞這些資訊
→ 浪費大量 token，且難以維護
```

### Cloudflare Workers KV 的優勢

| 特性 | 說明 |
|------|------|
| 完全免費 | 100k 讀/天、1k 寫/天，個人使用綽綽有餘 |
| 全球分佈 | 讀取延遲 < 50ms，全球任何地方都快 |
| 無需伺服器 | Cloudflare 託管，不用管機器 |
| 跨設備同步 | 電腦/手機/任何設備共用同一套記憶 |

---

## 商業模式

### 服務內容

```
建置（一次性）：
  ✅ 部署 Cloudflare Worker（memory API）
  ✅ 設定 KV namespace（記憶倉庫）
  ✅ 設定 API Key 驗證
  ✅ 整合到客戶的 Hermes / OpenClaw soul.md
  ✅ 建立記憶分類架構（偏好/事實/工作日誌）
  ✅ 測試跨 session 記憶恢復

每月維護：
  ✅ 監控使用量（確保在免費額度內）
  ✅ 定期清理過期記憶
  ✅ 根據新需求新增記憶類型
```

### 定價

| 方案 | 內容 | 建置費 | 月費 |
|------|------|--------|------|
| 個人版 | 單人記憶層，3 種記憶類型 | $6,000 TWD | $1,500 TWD |
| 團隊版 | 多人共用，角色隔離，管理後台 | $15,000 TWD | $3,000 TWD |
| 企業版 | 多客戶隔離，自訂 domain，SLA | $30,000 TWD | $6,000 TWD |

---

## 三種記憶類型

### 1. 用戶偏好（pref:）

```
Agent 行為設定，啟動時自動載入：

pref:reply_style → 「簡短、條列式、不要廢話」
pref:language    → 「繁體中文，偶爾夾英文術語」
pref:timezone    → 「Asia/Taipei (UTC+8)」
pref:work_hours  → 「週一到五 9:00-18:00」
```

### 2. 長期事實（fact:）

```
固定背景資訊，不需用戶重複說明：

fact:company     → 「Hermes Business，做 AI agent 服務」
fact:tech_stack  → 「Python, Cloudflare, Hermes Agent」
fact:clients     → 「目前有 5 個付費客戶，最大客戶是 XX」
fact:goals_2026  → 「月收入達到 $50,000 TWD，拓展 3 個垂直產業」
```

### 3. 工作日誌（log:）

```
跨 session 的工作連續性：

log:2026-05-21 → 「完成：Reddit 雷達、商業模式文件、GitHub push」
log:weekly     → 「本週重點：Agent Ops 服務打包，5 個潛在客戶聯繫」
log:decisions  → 「決定：先做 EA-as-a-Service，延後 IT 自動化」
```

---

## 運作示意

```
早上 Session 開始：
  Agent → GET /list?type=pref → 載入偏好（簡短、中文...）
  Agent → GET /list?type=fact → 載入背景（公司名稱、目標...）
  Agent → GET /recall?key=log:2026-05-21 → 知道昨天做了什麼
  → 無需用戶重新說明，直接進入狀態

對話中用戶說「記住，我的 API key 是 xxx」：
  Agent → POST /remember { key: "fact:api_key", value: "xxx" }
  → 下次 session 自動載入

Session 結束前：
  Agent → POST /remember { key: "log:2026-05-21", value: "今天完成了..." }
  → 下次 session 知道昨天做了什麼
```

---

## 競爭優勢

| 其他解法 | 問題 | 你的解法 |
|----------|------|---------|
| 塞進系統 prompt | 佔 token、難維護 | KV 動態載入，只載入需要的 |
| Notion 記憶層 | 需要 OAuth，設定複雜 | HTTP API，5 分鐘整合 |
| 向量資料庫（Pinecone） | 貴、需要管理 | Cloudflare 完全免費 |
| 本地 .md 文件 | 換設備就沒了 | 全球同步，任何設備都能讀 |

---

## 技術亮點

**可組合性**：Second Brain 可以和 Agent Ops（Kanban 架構）組合：

```
Agent Ops（任務管理） + Second Brain（持久記憶）
= 真正的「無狀態重啟、有記憶恢復」自動化 Agent
```

**多設備場景**：

```
辦公室電腦的 Hermes 存了一個決策記憶
→ 同一個 Cloudflare KV
→ 手機的 Telegram Bot 也能讀到
→ 隨時隨地，記憶不斷線
```

---

## 銷售話術

**開場（針對已有 Agent 的用戶）：**

> 「你有沒有每次跟 Agent 說話都要重新介紹自己是誰、公司在做什麼？這是因為 Agent 沒有跨 session 的記憶。我幫人建一個 Cloudflare 記憶層，用戶偏好、公司背景、工作紀錄全部持久化，下次開 session 自動載入。成本是零（Cloudflare 免費方案），設定費收一次。有沒有興趣試看看？」
