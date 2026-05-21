# Skill：Second Brain（跨 Session 持久記憶）

> 透過 Cloudflare Workers KV 儲存用戶偏好、背景事實、工作日誌，下次 session 自動載入

## 前置條件

需先部署 Cloudflare Worker：`services/second-brain/DEPLOY_PROMPT.md`

設定環境變數：
```
SECOND_BRAIN_URL=https://second-brain.YOUR_SUBDOMAIN.workers.dev
SECOND_BRAIN_KEY=你的 API Key
```

## 觸發指令

| 指令 | 說明 |
|------|------|
| `/remember [內容]` | 儲存一則記憶（自動分類） |
| `/remember pref [偏好]` | 儲存用戶偏好 |
| `/remember fact [事實]` | 儲存背景事實 |
| `/recall [關鍵字]` | 查詢特定記憶 |
| `/recall all` | 顯示所有記憶 |
| `/forget [key]` | 刪除特定記憶 |
| `/brain status` | 顯示記憶統計 |

## 啟動規則

每次 session 開始時，自動執行：

```
1. GET $SECOND_BRAIN_URL/list?type=pref → 載入所有用戶偏好
2. GET $SECOND_BRAIN_URL/list?type=fact → 載入背景事實
3. GET $SECOND_BRAIN_URL/recall?key=log:latest → 載入上次工作日誌
4. 靜默套用偏好（不打擾用戶）
5. 若有日誌：摘要顯示「上次：XXX」
```

## 三種記憶類型

```
pref: → 用戶偏好（回覆風格、語言、工作時間）
  key 格式：pref:reply_style / pref:language / pref:timezone

fact: → 長期事實（公司名稱、技術棧、客戶資訊）
  key 格式：fact:company / fact:tech_stack / fact:clients

log: → 工作日誌（每日/每週工作記錄）
  key 格式：log:2026-05-21 / log:weekly / log:decisions
```

## 自動記憶時機

```
用戶說「記住...」「以後...」「我偏好...」
  → 自動判斷類型，存入對應 pref 或 fact

Session 結束前
  → 自動寫入 log:[今日日期]（今日完成的事）

用戶明確說「忘記...」「不用記了...」
  → 呼叫 DELETE /forget
```

## API 呼叫格式

```python
import os, httpx

BASE = os.environ["SECOND_BRAIN_URL"]
KEY  = os.environ["SECOND_BRAIN_KEY"]
HDR  = {"X-API-Key": KEY}

# 儲存
httpx.post(f"{BASE}/remember", headers=HDR,
    json={"key": "pref:reply_style", "value": "簡短條列式", "type": "pref"})

# 查詢
r = httpx.get(f"{BASE}/recall", headers=HDR, params={"key": "pref:reply_style"})

# 列出
r = httpx.get(f"{BASE}/list", headers=HDR, params={"type": "pref"})

# 刪除
httpx.delete(f"{BASE}/forget", headers=HDR, params={"key": "pref:reply_style"})
```

## 組合使用

此 skill 常與以下搭配：
- `05-context-manager`：本地 session 記憶 + 雲端跨 session 記憶，雙保險
- `01-kanban-board`：kanban 快照儲存到 Second Brain，跨設備恢復
