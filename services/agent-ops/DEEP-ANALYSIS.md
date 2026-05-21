# Agent 長跑架構深度分析

> 拆解社群最熱議的兩個問題：Hermes 卡住不回應 + Cron Job 失效

---

## 一、核心問題：為什麼 Agent 跑不久？

大多數人用 Hermes / OpenClaw 的方式是這樣的：

```
用戶說「幫我做 X」
    → Agent 開始跑
    → 跑 10 分鐘後卡住
    → 用戶推一下「繼續」
    → 再跑 10 分鐘又卡
    → 用戶放棄
```

**根本原因有三個：**

1. **單線程思維**：Agent 把所有事情都塞在同一個對話，context 越來越長，思考越來越慢
2. **無狀態記憶**：每次 session 開始，Agent 不知道上次做到哪裡，只能從頭想
3. **阻塞式架構**：主 Agent 同時做「接收請求」和「執行任務」，兩個互相拖慢

解法是借鑑軟體工程的概念：**Kanban Board + 多代理委派**。

---

## 二、問題一：Hermes 一直 think 不回應

### 什麼情況會發生

```
症狀：
  - 輸入指令後，Hermes 顯示「思考中...」很久
  - 偶爾出現截斷、忘記前面說過的話
  - 複雜任務到一半就卡住，不繼續也不報錯

根本原因：
  - 主 Agent context window 塞滿了
  - 同時處理「管理邏輯」和「執行邏輯」，互相干擾
  - native compaction 觸發，壓縮後「忘記」自己在做什麼
```

### 解法：Multi-Profile + Gateway 分離

**概念：就像餐廳分工**

```
❌ 錯誤方式（一個人全包）：
   老闆 → 接電話訂位 + 炒菜 + 記帳 + 應付客訴 → 全部卡死

✅ 正確方式（分工）：
   Gateway Agent（前台）→ 只接請求，寫到 kanban，立刻回應「已收到」
   Worker Agent（廚房）→ 讀 kanban，執行任務，寫結果
   Specialist Agent（外燴）→ 被 Worker 呼叫，處理特定領域（研究/寫作/程式）
```

### 實作方式

**Step 1：設定 Gateway Profile（soul.md 核心指令）**

```markdown
# Gateway 角色設定

你是 Hermes 的前台接待。你的唯一工作是：
1. 接收用戶請求
2. 把請求寫入 kanban.md（格式見下方）
3. 立刻回應「已收到，Worker 會處理」
4. 絕對不執行任何實際任務

kanban.md 格式：
| ID | 任務 | 狀態 | 建立時間 | 完成時間 | 備注 |
|----|------|------|----------|----------|------|
| 001 | 分析競爭對手 | TODO | 14:00 | — | 需要網頁搜尋 |
```

**Step 2：設定 Worker Profile（soul.md 核心指令）**

```markdown
# Worker 角色設定

你是 Hermes 的執行層。每次啟動時：
1. 讀取 kanban.md
2. 找第一個狀態為 TODO 的任務
3. 把它改為 IN_PROGRESS
4. 全力執行（可以呼叫子 Agent）
5. 完成後寫入結果，狀態改為 DONE
6. 繼續找下一個 TODO

若沒有 TODO 任務，回報「所有任務完成」並等待。
```

**Step 3：Gateway 永遠不被阻塞**

```
用戶請求 → Gateway（< 3 秒）→ 寫入 kanban → 回覆「已排程」
                                    ↓
                             Worker 非同步執行（可跑 2 小時）
                                    ↓
                            完成後通知用戶（Telegram）
```

---

## 三、問題二：Cron Job 效果不好

### 什麼情況會發生

```
症狀：
  - 設定 launchd 每小時跑一次，但 Agent 每次都從頭開始
  - 重複做已經做過的事
  - 不知道上一次跑成功還是失敗
  - 目標漂移：一開始設定的目標跑幾次後被忘記

根本原因：
  - Cron 只是「定時觸發」，不包含「記憶與狀態」
  - Agent 沒有辦法知道：我的目標是什麼？上次做到哪？
```

### 解法：/goal + Kanban Board + Heartbeat.md

**三個文件搭配使用：**

```
goal.md         ← 不變的目標（Agent 每次啟動都先讀這個）
kanban.md       ← 任務狀態追蹤（哪些做完、哪些待辦）
heartbeat.md    ← 每次 cron 執行的健康記錄
```

### goal.md 格式

```markdown
# Agent 長期目標

## 核心使命
每 12 小時監控 r/hermesagent 和 r/openclaw，產出雷達報告並發送 Telegram。

## 永遠要做的事
- [ ] 確認上次報告是否成功發送
- [ ] 爬取過去 12 小時的新文章與留言
- [ ] 產出 reports/latest.md
- [ ] 發送摘要到 Telegram

## 絕對不要做的事
- 不要爬超過 12 小時前的文章（重複）
- 不要在失敗時靜默退出，要寫入 heartbeat.md
```

### kanban.md 格式（跨 session 持久化）

```markdown
# Agent Kanban Board

更新時間：2026-05-21 14:00

## TODO
| ID | 任務 | 優先度 | 備注 |
|----|------|--------|------|

## IN_PROGRESS
| ID | 任務 | 開始時間 | 負責子 Agent |
|----|------|----------|-------------|
| 042 | 爬取 r/openclaw | 14:00 | scraper-agent |

## DONE（最近 10 筆）
| ID | 任務 | 完成時間 | 結果摘要 |
|----|------|----------|---------|
| 041 | 發送 Telegram 報告 | 02:03 | 成功，12 篇文章 |

## BLOCKED
| ID | 任務 | 原因 | 需要協助 |
|----|------|------|---------|
```

### heartbeat.md 格式（診斷用）

```markdown
# Agent Heartbeat Log

## 最近一次執行
- 時間：2026-05-21 14:00:05
- 狀態：✅ 成功
- 執行時間：47 秒
- 產出：reports/radar_20260521_1400.md
- 發送：Telegram ✅

## 執行歷史（最近 10 次）
| 時間 | 狀態 | 執行秒數 | 備注 |
|------|------|---------|------|
| 14:00 | ✅ | 47 | 正常 |
| 02:00 | ✅ | 52 | 正常 |
| 14:00(昨) | ❌ | 12 | rdt 連線超時 |

## 系統狀態
- rdt-cli：可用
- Telegram Bot：可用
- reports/目錄：可寫入
```

### Cron Agent 啟動流程（每次固定這樣跑）

```
1. 讀取 goal.md → 確認本次目標
2. 讀取 kanban.md → 檢查是否有未完成任務（IN_PROGRESS = 上次崩潰）
   → 若有 IN_PROGRESS：優先從這裡恢復，不重新開始
3. 讀取 heartbeat.md → 確認上次是否成功
   → 若失敗：先處理失敗原因，再繼續
4. 執行任務，更新 kanban
5. 完成後更新 heartbeat.md
```

---

## 四、Kanban Board + 子代理委派（完整架構）

### 整體流程圖

```
用戶（或 Cron）
    ↓
Gateway Agent
  → 接收請求
  → 拆分成子任務
  → 寫入 kanban.md
    ↓
Orchestrator Agent（協調者）
  → 讀 kanban，分派任務給對應 Worker
  → 監控進度
  → 整合結果
    ↓
  ┌─────────────────────────────┐
  │  Worker Agents（並行）       │
  │  ├── Research Agent         │
  │  │   └── 搜尋、爬蟲、分析    │
  │  ├── Writer Agent           │
  │  │   └── 撰寫報告、草稿      │
  │  └── Coder Agent            │
  │      └── 寫程式、測試        │
  └─────────────────────────────┘
    ↓
  kanban.md（所有 Worker 寫回結果）
    ↓
Orchestrator 整合 → 通知用戶（Telegram）
```

### 為什麼這樣就能跑數小時不需要推

```
✅ Gateway 永遠快速回應（不卡）
✅ Worker 有 kanban 作為「工作記憶」，重啟不失狀態
✅ 子代理各自有小 context，不會填滿
✅ heartbeat.md 提供健康檢查，出錯自動恢復
✅ goal.md 確保目標不漂移
```

---

## 五、適合什麼客戶

| 客戶類型 | 痛點 | 適合的解法 |
|----------|------|-----------|
| 用 Hermes 跑複雜任務的開發者 | Agent 常卡住，要一直推 | Multi-profile + kanban |
| 想設定自動化工作流程的創業者 | Cron 跑起來但 Agent 不聰明 | goal + kanban + heartbeat |
| 已有多個 Agent 但難以協調的團隊 | 各自為政，沒有整合 | Orchestrator 架構 |
