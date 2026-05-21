# hermes-business

> Hermes Agent / OpenClaw 優化服務工具包
> 可直接銷售給客戶，或作為個人 agent 設定使用

---

## 服務目錄

### 🌐 Services（付費服務）

| 服務 | 說明 | 一鍵部署 | 難度 |
|------|------|---------|------|
| [web-tools](./services/web-tools/) | Camoufox + SearXNG，讓 agent 能真正上網，繞過封鎖 | ✅ | ⭐⭐ |
| [context-manager](./services/context-manager/) | 三層 context 保護，讓 agent 長 session 不失憶 | ✅ | ⭐ |
| [agent-ops](./services/agent-ops/) | Kanban Board + Gateway/Worker 雙 Profile，讓 agent 跑 8 小時不卡住 | ✅ | ⭐⭐ |
| [second-brain](./services/second-brain/) | Cloudflare Workers KV 記憶層，跨 session / 跨設備持久記憶 | ✅ | ⭐ |
| [cost-control](./services/cost-control/) | LiteLLM 混合路由，把 AI 月費壓低 60–95% | ✅ | ⭐⭐ |
| [local-model](./services/local-model/) | Ollama + Mac M 系列，本地跑 32B–70B 模型，inference 成本為零 | ✅ | ⭐ |
| [claude-subscription](./services/claude-subscription/) | Claude CLI OAuth 包成本地 API，走訂閱不付 API 費 | ✅ | ⭐ |

### 🛠️ Skills（免費/自用）

| Skill | 說明 |
|-------|------|
| [reddit-radar](./skills/reddit-radar/) | 每 12 小時自動抓取 Reddit 指定社群，產出雷達報告 |

### 💼 BusinessModel（商業模式文件）

| # | 服務 | 月費 | 建置費 |
|---|------|------|--------|
| 01 | [企業知識管理（公司大腦）](./BusinessModel/01-company-brain.md) | $500–$3,000 | — |
| 02 | [IT 自動化顧問](./BusinessModel/02-it-automation.md) | $5,000–$15,000 | $30,000–$80,000 |
| 03 | [AI 執行助理（EA-as-a-Service）](./BusinessModel/03-ai-ea.md) | $5,000–$15,000 | — |
| 04 | [Agent Ops 長跑架構](./BusinessModel/04-agent-ops.md) | $2,000–$5,000 | $8,000–$25,000 |
| 05 | [Second Brain 記憶層](./BusinessModel/05-second-brain.md) | $1,500–$6,000 | $6,000–$30,000 |
| 06 | [AI 費用控制顧問](./BusinessModel/06-cost-control.md) | $2,000–$3,000 | $5,000–$20,000 |
| 07 | [Claude Subscription OAuth](./BusinessModel/07-claude-subscription.md) | $1,000–$2,500 | $5,000–$12,000 |

---

## 快速開始

### 部署給客戶（一鍵安裝）

把任一服務的 `DEPLOY_PROMPT.md` 全文貼進客戶的 Hermes 或 OpenClaw：

```
services/
├── cost-control/DEPLOY_PROMPT.md    ← 費用控制路由（最推薦先裝）
├── local-model/DEPLOY_PROMPT.md     ← 本地模型 Ollama
├── agent-ops/DEPLOY_PROMPT.md       ← Kanban 長跑架構
├── second-brain/DEPLOY_PROMPT.md    ← Cloudflare 記憶層
├── context-manager/DEPLOY_PROMPT.md ← Context 三層保護
└── web-tools/DEPLOY_PROMPT.md       ← Camoufox + SearXNG
```

### 推薦安裝順序

```
第一步：claude-subscription（有訂閱就裝，立刻讓 API 帳單歸零）
第二步：cost-control（混合路由，訂閱額度不夠時 fallback）
第三步：local-model（有 Mac M 系列，隱私任務走本地）
第四步：context-manager（長 session 必裝）
第五步：agent-ops（需要複雜自動化時）
第六步：second-brain（需要跨設備記憶時）
第七步：web-tools（需要真實上網能力時）
```

---

## 資料夾結構

```
hermes-business/
├── services/
│   ├── web-tools/          # Camoufox + SearXNG + MCP Server
│   ├── context-manager/    # 三層 Context 保護
│   ├── agent-ops/          # Kanban Board + 多代理委派
│   ├── second-brain/       # Cloudflare Workers KV 記憶層
│   ├── cost-control/       # LiteLLM 混合路由
│   ├── local-model/        # Ollama 本地模型
│   └── claude-subscription/ # Claude CLI OAuth → 本地 API（走訂閱）
├── skills/
│   └── reddit-radar/       # Reddit 12 小時雷達爬蟲
├── BusinessModel/          # 六個商業模式完整文件
└── sales/
    └── web-tools-sales-guide.md
```

---

## 每個服務解決的問題

| 症狀 | 解法 |
|------|------|
| 有 Claude 訂閱但還在另付 API 費 | claude-subscription |
| AI 帳單太高（無訂閱） | cost-control + local-model |
| Agent 跑到一半卡住，要一直推 | agent-ops |
| Cron job 跑起來但 agent 不記得目標 | agent-ops（heartbeat + kanban） |
| 每次 session 都要重新介紹自己 | second-brain |
| 長 session 後 agent 忘記在做什麼 | context-manager |
| Agent 不能搜尋網路 / 被 bot 偵測 | web-tools |
