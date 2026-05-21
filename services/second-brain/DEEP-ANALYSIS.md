# Second Brain on Cloudflare — 深度解析

> Cloudflare Worker 上的輕量記憶層（免費方案）

---

## 一、這是什麼？為什麼需要它？

### 問題背景

Hermes / OpenClaw 預設只有「對話內記憶」：

```
Session A：用戶說「我喜歡簡短的回覆風格」
  → Agent 記住了
  → Session 結束

Session B（隔天）：
  → Agent 完全不知道上面說過的話
  → 用戶又要重新說一次
```

**每次重新解釋，就是用戶體驗的損耗。**

現有解法的問題：
- `.task_state.md`（本地文件）：只在單機有效，換設備就沒了
- Notion/Google Drive：需要 OAuth，設定複雜
- 向量資料庫（Pinecone）：貴、需要管理

### Cloudflare Worker 解法

**用 Cloudflare 的免費基礎設施做持久記憶層：**

```
Agent → HTTP 請求 → Cloudflare Worker → KV Store（全球同步）
                                            ↓
                    任何設備、任何 session 都能讀到
```

**免費方案限制（對個人 Agent 完全夠用）：**

| 項目 | 免費額度 |
|------|---------|
| Worker 請求 | 100,000 次/天 |
| KV 讀取 | 100,000 次/天 |
| KV 寫入 | 1,000 次/天 |
| KV 儲存空間 | 1 GB |

> Agent 就算每分鐘存一次記憶，一天才 1,440 次，遠低於上限。

---

## 二、架構圖

```
Hermes Agent（任何設備）
    ↓  HTTP POST/GET
Cloudflare Worker（你的 API endpoint）
    ├── POST /remember  → 寫入 KV
    ├── GET /recall     → 查詢 KV
    ├── GET /list       → 列出所有記憶
    └── DELETE /forget  → 刪除記憶
    ↓
Cloudflare KV Store（全球分佈，毫秒回應）
```

---

## 三、三種記憶類型（用途不同）

### Type 1：用戶偏好（Preferences）

```json
{
  "key": "pref:reply_style",
  "value": "簡短、條列式、不要廢話",
  "updated": "2026-05-21"
}
```

**用途**：Agent 每次啟動讀取，套用到所有回覆

### Type 2：長期事實（Facts）

```json
{
  "key": "fact:company_name",
  "value": "Hermes Business",
  "context": "用戶創業公司的名稱",
  "updated": "2026-05-21"
}
```

**用途**：儲存用戶告知的固定資訊，不用每次重複說明

### Type 3：工作紀錄（Work Log）

```json
{
  "key": "log:2026-05-21",
  "value": "完成：Reddit 雷達報告、分析三個商業模式、建立 GitHub repo",
  "updated": "2026-05-21T23:00"
}
```

**用途**：跨 session 的工作連續性，Agent 知道「昨天做了什麼」

---

## 四、Cloudflare Worker 程式碼

### worker.js（完整版）

```javascript
// Cloudflare Worker — Second Brain Memory Layer
// 部署到 Cloudflare Workers（免費方案）

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const headers = {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    };

    // 簡易 API Key 驗證
    const apiKey = request.headers.get('X-API-Key');
    if (apiKey !== env.API_KEY) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401, headers
      });
    }

    // POST /remember — 儲存記憶
    if (request.method === 'POST' && path === '/remember') {
      const body = await request.json();
      const { key, value, type = 'fact', ttl } = body;

      const memory = {
        key,
        value,
        type,         // 'pref' | 'fact' | 'log'
        updated: new Date().toISOString(),
      };

      const options = ttl ? { expirationTtl: ttl } : {};
      await env.MEMORY.put(key, JSON.stringify(memory), options);

      return new Response(JSON.stringify({ ok: true, key }), { headers });
    }

    // GET /recall?key=xxx — 查詢特定記憶
    if (request.method === 'GET' && path === '/recall') {
      const key = url.searchParams.get('key');
      if (!key) {
        return new Response(JSON.stringify({ error: 'key required' }), {
          status: 400, headers
        });
      }

      const raw = await env.MEMORY.get(key);
      if (!raw) {
        return new Response(JSON.stringify({ found: false }), { headers });
      }

      return new Response(JSON.stringify({ found: true, ...JSON.parse(raw) }), { headers });
    }

    // GET /list?type=pref — 列出所有（或特定類型的）記憶
    if (request.method === 'GET' && path === '/list') {
      const type = url.searchParams.get('type');
      const prefix = type ? `${type}:` : '';

      const list = await env.MEMORY.list({ prefix });
      const memories = await Promise.all(
        list.keys.map(async ({ name }) => {
          const raw = await env.MEMORY.get(name);
          return raw ? JSON.parse(raw) : null;
        })
      );

      return new Response(JSON.stringify({
        count: memories.length,
        memories: memories.filter(Boolean)
      }), { headers });
    }

    // DELETE /forget?key=xxx — 刪除記憶
    if (request.method === 'DELETE' && path === '/forget') {
      const key = url.searchParams.get('key');
      await env.MEMORY.delete(key);
      return new Response(JSON.stringify({ ok: true }), { headers });
    }

    return new Response(JSON.stringify({ error: 'Not found' }), {
      status: 404, headers
    });
  }
};
```

### wrangler.toml（部署設定）

```toml
name = "second-brain"
main = "worker.js"
compatibility_date = "2024-01-01"

[[kv_namespaces]]
binding = "MEMORY"
id = "YOUR_KV_NAMESPACE_ID"   # 部署後填入

[vars]
# API_KEY 透過 Secrets 設定，不要寫在這裡
```

---

## 五、Agent 怎麼使用（Hermes skill 版）

### 把以下加入 soul.md / AGENTS.md

```markdown
# Second Brain 記憶系統

你有能力透過 HTTP 儲存和讀取跨 session 的記憶。

## API 端點
- Base URL: https://second-brain.YOUR_SUBDOMAIN.workers.dev
- Header: X-API-Key: [你的 API Key]

## 指令對應

「記住 [事情]」
→ POST /remember { key: "fact:[摘要key]", value: "[內容]", type: "fact" }

「我喜歡 [偏好]」/ 「以後 [習慣]」
→ POST /remember { key: "pref:[類別]", value: "[偏好描述]", type: "pref" }

「你記得什麼？」/ 「你知道哪些關於我的事？」
→ GET /list?type=pref（偏好）
→ GET /list?type=fact（事實）

「忘記 [事情]」
→ DELETE /forget?key=[key]

## 啟動時自動載入

每次 session 開始，自動執行：
GET /list?type=pref → 載入所有用戶偏好 → 套用到本次 session
GET /list?type=fact → 載入背景資訊 → 不需用戶重複說明
```

---

## 六、部署步驟（10 分鐘完成）

```bash
# 1. 安裝 Wrangler CLI
npm install -g wrangler

# 2. 登入 Cloudflare
wrangler login

# 3. 建立 KV namespace
wrangler kv:namespace create "MEMORY"
# 複製輸出的 id，填入 wrangler.toml

# 4. 設定 API Key（Secrets）
wrangler secret put API_KEY
# 輸入你想要的 API Key（記住它，要給 Hermes 用）

# 5. 部署
wrangler deploy

# 6. 測試
curl -X POST https://second-brain.xxx.workers.dev/remember \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key":"pref:style","value":"簡短條列式","type":"pref"}'
```

---

## 七、進階用法

### 組合技：Second Brain + Kanban Board

```
Session 結束時：
  Agent → POST /remember 本次 kanban.md 快照
  
下次 Session 開始時：
  Agent → GET /recall?key=kanban:latest
  Agent → 恢復上次的工作狀態
```

### 多設備同步

```
電腦上的 Hermes 存記憶 → Cloudflare KV
手機上的 Telegram Bot 讀記憶 → Cloudflare KV
→ 兩個設備共享同一套記憶
```

### 客戶隔離（多客戶服務時）

```
Key 命名規則：{client_id}:{type}:{name}
例：client123:pref:style、client123:fact:company
→ 一個 Worker 服務多個客戶，資料互不干擾
```
