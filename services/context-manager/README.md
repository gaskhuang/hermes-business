# Context Manager Pro

> 三層 context 保護，讓 agent 長 session 不失憶。

## 問題

OpenClaw / Hermes 在長時間工作時，native compaction 會壓縮對話，導致 agent「忘記」自己在做什麼。

## 解法：三層架構

| 層 | 機制 | 作用 |
|----|------|------|
| 第一層 | 最後 5 輪保持 raw | 永遠知道「剛才在做什麼」 |
| 第二層 | 每 10–15 輪寫入 `.task_state.md` | session 中斷後能從檔案恢復 |
| 第三層 | native compaction 當安全網 | 不依賴它，壓縮前先存檔 |

## 安裝方式

### OpenClaw
1. 把 `context_manager.md` 放進 skills 目錄
2. 把 `AGENTS_md_snippet.md` 的內容貼進 `AGENTS.md`

### Hermes
1. 把 `context_manager.md` 放進 `~/.hermes/skills/`
2. 把 `AGENTS_md_snippet.md` 的內容貼進 `soul.md`

### 一鍵部署（給客戶）
把 `DEPLOY_PROMPT.md` 全文貼進 agent，自動完成安裝。

## 使用指令

| 你說 | Agent 做什麼 |
|------|-------------|
| 「存狀態」| 立即更新 `.task_state.md` |
| 「從哪裡停的」| 讀取並摘要任務狀態 |
| 「清除狀態」| 刪除 `.task_state.md`，重新開始 |
