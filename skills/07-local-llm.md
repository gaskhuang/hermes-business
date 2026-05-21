# Skill：Local LLM（本地模型管理）

> 管理 Ollama 本地模型，確保隱私任務不出機器、高頻任務零成本

## 前置條件

需先安裝 Ollama：`services/local-model/DEPLOY_PROMPT.md`

## 觸發指令

| 指令 | 說明 |
|------|------|
| `/local [prompt]` | 用本地模型回答（自動選最適合的）|
| `/local code [prompt]` | 強制用 Qwen2.5-Coder（程式碼）|
| `/local fast [prompt]` | 強制用 Phi-4（快速任務）|
| `/local status` | 顯示 Ollama 狀態和可用模型 |
| `/local models` | 列出所有已下載模型 |

## 啟動規則

每次 session 開始時，靜默確認：

```bash
curl -s http://localhost:11434/api/tags > /dev/null
# 成功：Ollama 可用，記錄在 session 狀態
# 失敗：記錄「本地模型不可用」，相關路由 fallback 到雲端
```

## 模型選擇邏輯

```
/local [prompt] 時，自動選擇：

含「程式」「code」「function」「bug」
  → ollama/qwen2.5-coder:32b

含「分類」「摘要」「翻譯」「確認」
  → ollama/phi4:14b

其他（通用、繁中、分析）
  → ollama/qwen2.5:32b（或 llama3.3:70b，若有安裝）
```

## 隱私守門員

當任務中出現以下關鍵字時，**強制走本地模型**（即使沒有用 `/local` 指令）：

```
客戶資料 / 合約 / 密碼 / API Key / token / 機密 / 保密
財務資料 / 身分證 / 護照
```

> 若本地模型不可用，**暫停任務並警告用戶**，不自動 fallback 到雲端

## 模型健康檢查

```bash
# /local status 輸出格式：
=== 本地模型狀態 ===
Ollama 服務：✅ 運行中
API 端點：http://localhost:11434 ✅

已安裝模型：
  phi4:14b          9.0GB  ✅ 可用
  qwen2.5-coder:32b 20.1GB ✅ 可用
  qwen2.5:32b       20.3GB ✅ 可用
  
推薦用途：
  快速雜事 → phi4:14b
  程式碼   → qwen2.5-coder:32b
  繁中分析 → qwen2.5:32b
```

## 組合使用

此 skill 常與以下搭配：
- `06-smart-router`：自動路由時，本地模型作為隱私/費用選項
- `08-cost-watcher`：追蹤本地 vs 雲端的費用節省比例
