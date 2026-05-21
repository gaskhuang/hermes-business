# 這段貼進客戶的 AGENTS.md 或 soul.md

---

## Context 管理規則（三層保護）

你必須主動管理自己的 context，不要依賴系統壓縮來保存記憶。

### 每 10–15 輪執行一次：
在當前工作目錄建立或更新 `.task_state.md`，格式如下：

```
# Task State
更新時間：[現在時間]
輪次：[目前輪次]

## 🎯 當前目標
[使用者目前要做什麼]

## ✅ 已完成
- [條列已完成的步驟]

## ⏭️ 下一步
- [條列接下來要做的事]

## 🚧 障礙 / 決策記錄
- [遇到的問題、做了什麼決定、為什麼]

## 📁 關鍵檔案與路徑
- [本次任務用到的重要檔案]

## 💬 最後 3 輪摘要
[用 2–3 句話描述最近的對話重點]
```

### Session 開始時：
1. 先用 `ls -a` 或 `find . -name ".task_state.md"` 確認是否有舊的 task state
2. 有的話讀取並告訴使用者：「找到上次任務記錄，目標是 [XXX]，下一步是 [XXX]，是否繼續？」
3. 沒有的話正常開始

### Context 接近上限時：
1. 立即更新 `.task_state.md`
2. 告知使用者「即將 compaction，已儲存狀態」
3. compaction 後重新讀取 `.task_state.md` 找回方向

### 使用者指令：
- 「存狀態」/ "save state" → 立即更新 `.task_state.md`
- 「從哪裡停的」/ "where were we" → 讀取並摘要 `.task_state.md`
- 「清除狀態」/ "fresh start" → 刪除 `.task_state.md`

---
