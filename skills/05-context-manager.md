# Skill：Context Manager（三層 Session 記憶保護）

> 防止 agent 在長 session 中「忘記自己在做什麼」——三層保護機制

## 觸發指令

| 指令 | 說明 |
|------|------|
| `/save` | 立即將當前任務狀態寫入 .task_state.md |
| `/load` | 讀取並摘要 .task_state.md |
| `/state` | 顯示當前任務狀態 |
| `/clear-state` | 清除狀態，重新開始 |

## 三層保護架構

```
第一層：保持最後 5 輪對話為 raw（不壓縮）
  → 永遠知道「剛才在做什麼」

第二層：每 10–15 輪對話寫入 .task_state.md
  → Session 中斷後能從文件恢復

第三層：native compaction 作為安全網
  → 不依賴它，壓縮前先執行第二層
```

## .task_state.md 格式

```markdown
# Task State
儲存時間：[時間]

## 當前目標
[這個 session 要完成什麼]

## 已完成
- [具體完成的事項]

## 下一步
- [接下來要做什麼]

## 阻塞點
- [目前卡在哪裡，需要什麼才能繼續]

## 重要文件
- [這個任務涉及的文件路徑列表]

## 摘要
[給下一次 session 看的簡短摘要，200 字以內]
```

## 自動觸發時機

```
每 10–15 輪對話：自動寫入 .task_state.md
Session 開始：讀取 .task_state.md（若存在），詢問是否恢復
Compaction 前：立刻寫入（不等 15 輪）
用戶說「存狀態」：立刻寫入
```

## 啟動規則

```
1. 嘗試讀取 .task_state.md
2. 若存在且不超過 24 小時：
   → 顯示摘要，詢問「要繼續上次的任務嗎？」
3. 若超過 24 小時或不存在：
   → 靜默繼續
```

## 組合使用

此 skill 常與以下搭配：
- `04-second-brain`：本地短期記憶 + 雲端長期記憶，互補
- `01-kanban-board`：任務狀態和 kanban 同步，雙重保險
