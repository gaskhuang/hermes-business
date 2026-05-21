# AI 費用控制深度分析

> 社群最核心焦慮的解法：混合路由 + 本地模型

---

## 一、問題有多嚴重

社群常見的費用崩潰路徑：

```
用戶開始用 Claude Sonnet 跑 agent
  → 每次 session 幾百個 token
  → 一天 20 個 session
  → 第一個月帳單 $150 USD
  → 「我只是想要幫我整理一下 Email」
```

**關鍵洞察：大多數人用 $20/月 的任務，在付 $150/月 的帳單**

原因是預設用最強模型跑所有事情，包括：
- 格式化輸出（根本不需要推理）
- 分類任務（簡單 if/else 邏輯）
- 摘要長文件（填空，非推理）
- 確認指令（「好的，已收到」）

這些任務用 Haiku / GPT-4o-mini / 本地模型，品質完全一樣，成本差 20–50 倍。

---

## 二、社群最推薦的兩條路線

### 路線 A：混合路由（Mixed Routing）

**核心概念**：同一個 agent，根據任務複雜度自動切換模型

```
任務進來
    ↓
Router 評估複雜度
    ├── 簡單（格式化/分類/摘要）→ Haiku / GPT-4o-mini（$0.25/1M tokens）
    ├── 中等（分析/規劃/草稿）→ Claude Sonnet / GPT-4o（$3/1M tokens）
    └── 複雜（深度推理/創意）→ Claude Opus / o1（$15+/1M tokens）
```

**節省比例（社群實測數字）**：
- 純 Opus/GPT-4 → 混合路由：省 60–80%
- 加上本地模型：省 85–95%

---

### 路線 B：本地模型（Local Models）

**核心概念**：一次性硬體投資，之後 inference 成本為零

```
雲端模型（每月付費）vs 本地模型（一次買硬體）

雲端：$100/月 × 12 = $1,200/年，永遠付費
本地：MacBook M4 $60,000 + Ollama，跑到壞為止
      → 大量使用下，6 個月回本
```

---

## 三、混合路由：最推薦工具是 LiteLLM

### 為什麼 LiteLLM？

社群推薦理由：
- **統一 API**：呼叫 100+ 模型，都用 OpenAI 格式，零改 code
- **費用追蹤**：每次呼叫自動記錄 cost，月底看報表
- **路由規則**：可設定 fallback、負載均衡、cost-based routing
- **本地模型整合**：Ollama 直接接進來，混合使用

### LiteLLM Proxy 架構

```
Hermes Agent
    ↓  OpenAI API 格式（不需要改 agent 的 code）
LiteLLM Proxy（本地或 Docker）
    ├── 規則：task_type == "summary" → Haiku
    ├── 規則：task_type == "reasoning" → Sonnet
    ├── 規則：budget_exceeded → Ollama (本地)
    └── fallback：若 Anthropic 掛了 → OpenAI
    ↓
實際 API 呼叫（你設定的模型）
```

### 路由規則設計（最常被社群採用）

```yaml
# litellm_config.yaml

model_list:
  # 便宜模型（雜事）
  - model_name: "fast"
    litellm_params:
      model: "claude-haiku-3-5"
      api_key: os.environ/ANTHROPIC_API_KEY

  # 標準模型（日常）
  - model_name: "standard"
    litellm_params:
      model: "claude-sonnet-4-5"
      api_key: os.environ/ANTHROPIC_API_KEY

  # 強力模型（複雜推理）
  - model_name: "powerful"
    litellm_params:
      model: "claude-opus-4"
      api_key: os.environ/ANTHROPIC_API_KEY

  # 本地模型（隱私/省錢）
  - model_name: "local"
    litellm_params:
      model: "ollama/qwen2.5-coder:32b"
      api_base: "http://localhost:11434"

router_settings:
  routing_strategy: "cost-based"    # 依成本自動路由
  allowed_fails: 2                   # 失敗 2 次才 fallback

general_settings:
  max_budget: 50                     # 月上限 $50 USD，超了自動降級
  budget_duration: "1mo"
```

### 在 Agent 裡如何觸發不同路由

```python
# 方法一：在 system prompt 裡標記任務類型
def call_llm(task_type: str, prompt: str):
    model_map = {
        "classify": "fast",      # 分類 → Haiku
        "summarize": "fast",     # 摘要 → Haiku
        "draft": "standard",     # 草稿 → Sonnet
        "analyze": "standard",   # 分析 → Sonnet
        "reason": "powerful",    # 深度推理 → Opus
        "private": "local",      # 隱私資料 → 本地
    }
    model = model_map.get(task_type, "standard")
    
    return litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        api_base="http://localhost:4000"  # LiteLLM proxy
    )

# 方法二：自動偵測（用 Haiku 判斷任務複雜度，成本幾乎為零）
def smart_route(prompt: str) -> str:
    classifier_response = litellm.completion(
        model="fast",
        messages=[{
            "role": "user",
            "content": f"判斷以下任務的複雜度，只回答 fast/standard/powerful：\n{prompt[:200]}"
        }]
    )
    return classifier_response.choices[0].message.content.strip()
```

---

## 四、本地模型：社群最推薦硬體與軟體

### 硬體推薦排行（2026 社群共識）

| 方案 | 硬體 | 能跑的最大模型 | 每月成本 | 適合誰 |
|------|------|-------------|---------|--------|
| ⭐⭐⭐ 最推薦 | Mac M4 Pro 48GB | 70B 量化版 | 電費約 $100 TWD | 開發者、顧問 |
| ⭐⭐⭐ 最推薦 | Mac M3 Max 96GB | 70B 全精度 | 電費約 $150 TWD | 重度使用者 |
| ⭐⭐ 次選 | RTX 4090 24GB | 34B 量化版 | 電費約 $500 TWD | 已有 Windows 機 |
| ⭐ 入門 | Mac M2 16GB | 7B–13B | 電費約 $50 TWD | 測試用 |

**為什麼 Mac M 系列最受推薦：**
1. Unified Memory（CPU/GPU 共用記憶體）→ 能跑比 VRAM 更大的模型
2. 用電效率極高（RTX 4090 功耗 450W，M4 Pro 只有 30W）
3. MLX framework（Apple 優化），速度比 llama.cpp 快 2–3 倍
4. 靜音，可以放辦公室

### 軟體棧推薦

**Ollama（最多人用，最簡單）**

```bash
# 安裝
brew install ollama

# 下載模型
ollama pull qwen2.5-coder:32b      # 程式碼任務（媲美 GPT-4o）
ollama pull llama3.3:70b           # 通用推理（最強開源）
ollama pull phi4:14b               # 快速推理（微軟，超值）
ollama pull nomic-embed-text       # embedding（本地向量搜尋）

# 啟動（OpenAI 相容 API）
ollama serve
# → http://localhost:11434
```

**哪個模型做什麼（社群實測共識）**

| 任務 | 推薦本地模型 | 對標雲端模型 |
|------|------------|------------|
| 程式碼生成/審查 | Qwen2.5-Coder 32B | GPT-4o |
| 通用推理/分析 | Llama 3.3 70B | Claude Sonnet |
| 快速分類/摘要 | Phi-4 14B | Claude Haiku |
| 文件 Embedding | nomic-embed-text | OpenAI text-embedding |
| 繁體中文任務 | Qwen2.5 72B | Claude Sonnet |

---

## 五、混合策略：雲端 + 本地最佳組合

```
任務類型分流圖：

所有 Agent 任務
    │
    ├── 隱私敏感（客戶資料、密碼、合約）
    │       └── → 本地 Ollama（絕對不出機器）
    │
    ├── 高頻雜事（分類/格式化/確認）
    │       └── → Claude Haiku / GPT-4o-mini（最便宜雲端）
    │
    ├── 日常工作（草稿/分析/規劃）
    │       └── → Claude Sonnet（主力）
    │
    └── 複雜推理（策略/創意/複雜程式）
            └── → Claude Opus / o1（最貴，但只用在值得的地方）
```

### 費用試算（每月 1,000 次 agent 呼叫）

| 策略 | 月費估算 | 說明 |
|------|---------|------|
| 全用 Opus | $150 USD | 大砲打小鳥 |
| 全用 Sonnet | $45 USD | 合理但仍有浪費 |
| 混合路由（無本地） | $15 USD | 70% 省下來 |
| 混合路由（有本地 Mac） | $5 USD | 隱私任務 + 高頻任務走本地 |

---

## 六、費用監控：必須搭配的工具

### LiteLLM 內建 Dashboard

```bash
# 啟動 LiteLLM proxy + dashboard
litellm --config litellm_config.yaml --port 4000 --ui

# → http://localhost:4000/ui
# 可以看到：每個模型的用量、費用、延遲
```

### 自製費用警報（Telegram 通知）

```python
# 每天早上 8 點，發送昨日費用報告到 Telegram
import litellm
from datetime import datetime, timedelta

def daily_cost_report():
    yesterday = datetime.now() - timedelta(days=1)
    spend = litellm.get_spend_logs(start_date=yesterday.date())
    
    report = f"""
📊 AI 費用日報 {yesterday.date()}

總費用：${spend['total_cost']:.4f} USD
最貴模型：{spend['top_model']}（${spend['top_model_cost']:.4f}）
總呼叫次數：{spend['total_calls']}

預計本月：${spend['monthly_estimate']:.2f} USD
"""
    send_telegram(report)
```

---

## 七、從哪裡開始（行動順序）

### 已有 Mac M 系列的人（立刻可做）

```
1. brew install ollama
2. ollama pull qwen2.5-coder:32b（程式碼）
3. ollama pull phi4:14b（快速任務）
4. 把 Hermes 的 ANTHROPIC_API_KEY 換成 LiteLLM proxy URL
5. 設定路由規則（隱私任務 → Ollama，其他 → Sonnet）
→ 預計立刻省 40–60%
```

### 沒有強力 Mac 的人（從混合路由開始）

```
1. pip install litellm[proxy]
2. 設定 litellm_config.yaml（fast/standard/powerful 三層）
3. 把所有 agent 呼叫改走 localhost:4000
4. 觀察 1 個月費用，找出高頻雜事改成 fast 模型
→ 預計省 50–70%
```
