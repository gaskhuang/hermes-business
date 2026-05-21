# Local Model Setup — 一鍵部署指令

> 把以下全文貼入你的 Hermes / OpenClaw，agent 會自動完成安裝。
> 建議搭配 cost-control 服務一起使用。

---

```
請幫我安裝「本地模型（Ollama）」，依以下步驟執行，每步完成後告訴我結果。

## 步驟 1：確認 Mac 規格

```bash
system_profiler SPHardwareDataType | grep -E "Memory|Chip|Model"
```

告訴我記憶體大小，我會根據這個決定下載哪些模型。

## 步驟 2：安裝 Ollama

```bash
# 確認是否已安裝
which ollama && ollama --version && echo "✅ 已安裝，跳過" || (
  echo "安裝 Ollama..."
  brew install ollama
)
```

## 步驟 3：設定 Ollama 為背景服務

```bash
brew services start ollama
sleep 3
curl -s http://localhost:11434/api/tags | python3 -m json.tool | head -5
```

應該看到 JSON 回應，代表 Ollama 正在運行。

## 步驟 4：根據記憶體下載模型

根據步驟 1 的記憶體大小，執行對應指令：

### 如果是 16GB：
```bash
ollama pull phi4:14b          # 快速雜事（9GB）
ollama pull qwen2.5:14b       # 繁中通用（9GB）
```

### 如果是 32GB（最推薦）：
```bash
ollama pull phi4:14b           # 快速雜事（9GB）
ollama pull qwen2.5-coder:32b  # 程式碼，媲美 GPT-4o（20GB）
ollama pull qwen2.5:32b        # 繁中通用（20GB）
```

### 如果是 48GB 以上：
```bash
ollama pull phi4:14b            # 快速雜事（9GB）
ollama pull qwen2.5-coder:32b   # 程式碼（20GB）
ollama pull llama3.3:70b        # 最強通用（43GB）
ollama pull nomic-embed-text    # Embedding（300MB）
```

下載完成後執行：
```bash
ollama list
```
列出所有已下載模型。

## 步驟 5：測試模型

```bash
# 快速測試（不要超過 30 秒）
ollama run phi4:14b "用一句話介紹你自己，繁體中文" --nowordwrap
```

## 步驟 6：確認 OpenAI 相容 API

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi4:14b",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": false
  }'
```

應該看到正常的 JSON 回應。

## 步驟 7：整合到 LiteLLM（若已安裝 cost-control）

若你已安裝 cost-control 服務，在 ~/cost-control-proxy/litellm_config.yaml 的 model_list 加入以下（依據你下載的模型）：

```yaml
  - model_name: "local-fast"
    litellm_params:
      model: "ollama/phi4:14b"
      api_base: "http://localhost:11434"

  - model_name: "local-coder"
    litellm_params:
      model: "ollama/qwen2.5-coder:32b"
      api_base: "http://localhost:11434"

  - model_name: "local-general"
    litellm_params:
      model: "ollama/qwen2.5:32b"
      api_base: "http://localhost:11434"
```

然後重啟 LiteLLM Proxy：
```bash
launchctl stop com.cost-control.proxy
launchctl start com.cost-control.proxy
sleep 3
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"local-fast","messages":[{"role":"user","content":"Hello"}]}'
```

## 步驟 8：建立模型管理腳本

建立 ~/cost-control-proxy/manage_models.sh：

---
#!/bin/bash
# 本地模型管理工具

case "$1" in
  list)
    echo "=== 已安裝模型 ==="
    ollama list
    ;;
  status)
    echo "=== Ollama 狀態 ==="
    curl -s http://localhost:11434/api/tags | python3 -c "
import json,sys
d=json.load(sys.stdin)
for m in d.get('models',[]):
    size=m['size']/1e9
    print(f\"  {m['name']}: {size:.1f}GB\")
"
    ;;
  test)
    echo "=== 測試所有模型 ==="
    for model in phi4:14b qwen2.5-coder:32b qwen2.5:32b; do
      echo -n "  $model: "
      result=$(ollama run $model "說你好" --nowordwrap 2>/dev/null | head -1)
      [ -n "$result" ] && echo "✅" || echo "❌"
    done
    ;;
  update)
    echo "=== 更新所有模型 ==="
    ollama list | tail -n +2 | awk '{print $1}' | xargs -I{} ollama pull {}
    ;;
  *)
    echo "用法：$0 [list|status|test|update]"
    ;;
esac
---

```bash
chmod +x ~/cost-control-proxy/manage_models.sh
~/cost-control-proxy/manage_models.sh test
```

## 步驟 9：驗證安裝完成

```bash
echo "=== 本地模型安裝狀態 ==="
brew services list | grep ollama | grep started > /dev/null && echo "✅ Ollama 服務運行中" || echo "❌ Ollama 服務未啟動"
curl -s http://localhost:11434/api/tags > /dev/null && echo "✅ API 可用" || echo "❌ API 不可用"
ollama list | wc -l | xargs -I{} echo "✅ 已安裝 {} 個模型"
echo "=== 完成 ==="
ollama list
```

全部 ✅ 後，說「本地模型安裝完成」並告訴我：
1. 下載了哪些模型、各佔多少空間
2. 測試呼叫是否正常
3. 若已安裝 cost-control，本地模型是否已整合進路由
```
