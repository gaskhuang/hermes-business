# Local Model Setup

> Mac M 系列 + Ollama：一次設定，之後 inference 成本為零

## 為什麼要跑本地模型

| 情境 | 雲端 | 本地 |
|------|------|------|
| 隱私資料（合約、客戶資訊） | 資料上傳到 Anthropic/OpenAI | 資料不出你的機器 |
| 高頻雜事（分類、摘要） | 每次付費 | 免費 |
| 程式碼生成 | $3–15/1M tokens | $0 |
| 離線使用 | 需要網路 | 完全離線 |

## 推薦模型（32GB Mac）

| 模型 | 大小 | 用途 |
|------|------|------|
| qwen2.5-coder:32b | 20GB | 程式碼，媲美 GPT-4o |
| qwen2.5:32b | 20GB | 繁中通用分析 |
| phi4:14b | 9GB | 快速雜事分類 |

## 安裝

把 `DEPLOY_PROMPT.md` 貼入 Hermes，自動完成：
1. 安裝 Ollama
2. 下載推薦模型（依你的記憶體自動選擇）
3. 整合到 LiteLLM Proxy（與 cost-control 服務搭配）
4. 設定開機自動啟動

## 檔案說明

| 檔案 | 用途 |
|------|------|
| `DEPLOY_PROMPT.md` | 一鍵部署指令 |
| `SETUP.md` | 完整手動安裝教學與說明 |
