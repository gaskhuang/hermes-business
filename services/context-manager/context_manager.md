# Skill: Context Manager Pro
# 三層 Context 保護系統

> 版本：1.0 | 適用：OpenClaw / Hermes Agent
> 作者：Gask

---

## 這個 Skill 在做什麼

你的 agent 會在長 session 中自動管理 context，避免「失憶」：

- **每 10–15 輪**自動把當前任務狀態寫進 `.task_state.md`
- **Session 開始時**自動讀取上次的任務狀態，從中斷點繼續
- **Native compaction 前**先觸發一次 task state 儲存，確保不遺失

你不需要手動做任何事，背景自動執行。

---

## 三層架構說明

### 第一層：最後 5 輪保持 Raw（不壓縮）
最近的對話絕對不壓縮，保持思路連貫。
agent 永遠知道「剛才在做什麼」。

### 第二層：Task State 外部化（核心）
每 10–15 輪，把以下內容寫進 `.task_state.md`：
- 當前目標是什麼
- 已完成哪些步驟
- 下一步要做什麼
- 遇到的障礙與決策

session 被中斷、compaction 發生、電腦重開——只要讀這個檔案，就能立刻恢復狀態。

### 第三層：Native Compaction 當安全網
compaction 只是備用，不依賴它做主要記憶。
壓縮前先確保 task state 已更新。

---

## 行為規則（Agent 請讀這裡）

### 規則 1：Session 開始時
```
1. 檢查當前目錄是否有 .task_state.md
2. 如果有 → 讀取並報告：「找到上次的任務狀態，是否繼續？」
3. 如果沒有 → 正常開始，準備建立新的 task state
```

### 規則 2：每 10–15 輪自動存檔
```
每完成 10–15 輪對話，或在以下時機主動觸發：
- 完成一個子任務
- 遇到需要等待的操作
- 使用者說「先停一下」、「等等繼續」
- 即將進行大量 token 消耗的操作

執行：更新 .task_state.md
```

### 規則 3：Compaction 發生前
```
偵測到 context 接近上限（約 80% 滿）：
1. 先更新 .task_state.md
2. 告知使用者：「即將進行 context 壓縮，已儲存任務狀態」
3. 壓縮後主動讀取 .task_state.md 重新定向
```

### 規則 4：使用者可以手動觸發
```
使用者說「存一下狀態」、「save state」→ 立即更新 .task_state.md
使用者說「從哪裡停的」、「繼續」→ 讀取並摘要 .task_state.md
使用者說「清除狀態」、「fresh start」→ 刪除 .task_state.md，重新開始
```

---

## .task_state.md 格式

每次更新時，用以下格式覆寫 `.task_state.md`：

```markdown
# Task State
更新時間：{{timestamp}}
輪次：{{turn_count}}

## 🎯 當前目標
{{main_goal}}

## ✅ 已完成
{{completed_steps_as_bullet_list}}

## ⏭️ 下一步
{{next_steps_as_bullet_list}}

## 🚧 障礙 / 決策記錄
{{blockers_and_decisions}}

## 📁 關鍵檔案與路徑
{{important_files_referenced}}

## 💬 最後幾輪摘要（原始）
{{last_3_turns_raw_summary}}
```

---

## 安裝方式

### OpenClaw
把本檔案放入 skills 目錄，並在 `AGENTS.md` 加入以下一行：

```
@context_manager.md
```

### Hermes Agent
把本檔案放入 `~/.hermes/skills/` 目錄，重啟 Hermes 後輸入：

```
/load context_manager
```

或加入 skill bundle（見下方）。

---

## Skill Bundle 整合（Hermes）

建立 `~/.hermes/bundles/context_aware.yaml`：

```yaml
name: context_aware
description: 帶 context 保護的工作 session
skills:
  - context_manager
triggers:
  on_session_start: true
  on_compaction: true
```

之後輸入 `/context_aware` 啟動帶保護的工作模式。
