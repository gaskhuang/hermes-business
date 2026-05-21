# 本地模型設定指南

> Mac M 系列 + Ollama + LiteLLM 整合完整教學

---

## 一、確認你的 Mac 能跑什麼

```bash
# 查看記憶體大小
system_profiler SPHardwareDataType | grep Memory

# 對應能跑的最大模型
# 16GB → 7B–13B（入門）
# 32GB → 32B（主流，強烈推薦）  
# 48GB → 70B 量化版（很好）
# 64GB → 70B 完整版（極佳）
# 96GB → 70B 多個並行（頂配）
```

---

## 二、安裝 Ollama

```bash
# 安裝
brew install ollama

# 設定為背景服務（開機自動啟動）
brew services start ollama

# 確認運行
curl http://localhost:11434/api/tags
```

---

## 三、下載推薦模型

### 依照你的記憶體選擇

```bash
# ── 16GB Mac ─────────────────────────────────────
ollama pull phi4:14b               # 快速推理，微軟出品，超值
ollama pull qwen2.5:14b            # 中文能力強

# ── 32GB Mac（最推薦組合）────────────────────────
ollama pull qwen2.5-coder:32b      # 程式碼，媲美 GPT-4o
ollama pull qwen2.5:32b            # 通用，中文最強
ollama pull phi4:14b               # 快速分類摘要用

# ── 48GB+ Mac ────────────────────────────────────
ollama pull llama3.3:70b           # 最強開源通用模型
ollama pull qwen2.5-coder:32b      # 程式碼
ollama pull nomic-embed-text       # Embedding（向量搜尋）

# 查看已下載模型
ollama list
```

### 各模型任務對照

| 模型 | 大小 | 最適合 | 速度 |
|------|------|--------|------|
| phi4:14b | 9GB | 快速分類、摘要、確認 | 極快 |
| qwen2.5:32b | 20GB | 繁體中文、分析、草稿 | 快 |
| qwen2.5-coder:32b | 20GB | 程式碼生成與審查 | 快 |
| llama3.3:70b | 43GB | 複雜推理、策略規劃 | 中等 |
| nomic-embed-text | 0.3GB | 文件向量化（RAG） | 極快 |

---

## 四、用 MLX 加速（Apple Silicon 專屬）

```bash
# MLX 是 Apple 優化的推理框架，比 Ollama 快 2–3 倍
pip install mlx-lm

# 跑模型（格式不同，但效果更好）
mlx_lm.generate \
  --model mlx-community/Qwen2.5-32B-Instruct-4bit \
  --prompt "你好"

# 常用 MLX 量化模型（從 HuggingFace 下載）
# mlx-community/Qwen2.5-32B-Instruct-4bit  （推薦）
# mlx-community/Llama-3.3-70B-Instruct-4bit
# mlx-community/phi-4-4bit
```

---

## 五、整合到 LiteLLM（讓 Hermes 自動切換）

```bash
# 安裝 LiteLLM
pip install "litellm[proxy]"

# 啟動 Proxy（用我們準備好的設定檔）
litellm --config litellm_config.yaml --port 4000

# 確認本地模型可以透過 proxy 呼叫
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local-coder",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

---

## 六、讓 Hermes 使用本地模型

### 在 soul.md / AGENTS.md 加入

```markdown
# 模型使用規則

你可以透過設定 model 參數選擇使用不同的模型：

- `fast`：分類、摘要、格式化等雜事
- `standard`：日常分析、草稿撰寫
- `powerful`：複雜推理、架構設計
- `local-coder`：所有程式碼任務（本地，免費）
- `local-general`：涉及客戶資料或隱私的任務（本地，不出機器）

API endpoint：http://localhost:4000（LiteLLM Proxy）
```

---

## 七、費用監控

```bash
# 開啟 LiteLLM Dashboard
open http://localhost:4000/ui

# 可以看到：
# - 每個模型的呼叫次數
# - 估算費用（本地模型顯示 $0）
# - 回應速度對比
# - 錯誤率

# 設定月費用上限（超過自動降級到本地）
# 在 litellm_config.yaml 設定：
# max_budget: 30   # USD
```

---

## 八、常見問題

**Q：Ollama 跑起來很慢？**
```bash
# 確認有用到 GPU
ollama run qwen2.5:32b
# 看 Activity Monitor → GPU 有沒有在動

# 如果沒有，重新安裝 Ollama
brew reinstall ollama
```

**Q：模型輸出繁體中文有問題？**
```bash
# 在 system prompt 加入
"請使用繁體中文回覆。輸出格式：條列式，簡短精確。"

# Qwen 系列對繁體中文最友善
ollama pull qwen2.5:32b
```

**Q：想同時跑多個模型？**
```bash
# Ollama 支援並行（記憶體夠的話）
OLLAMA_NUM_PARALLEL=2 ollama serve
```
