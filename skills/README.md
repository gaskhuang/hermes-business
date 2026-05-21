# Skills 導覽

> 11 個獨立 skill + 5 個預設 bundle，自由組合成你的 workflow

---

## Skill 一覽

| # | Skill | 觸發指令 | 解決什麼問題 | 需要前置服務 |
|---|-------|---------|------------|------------|
| 01 | [kanban-board](./01-kanban-board.md) | `/kanban` | 任務追蹤，不重複不遺漏 | 無 |
| 02 | [goal-keeper](./02-goal-keeper.md) | `/goal` | 長期目標，防止漂移 | 無 |
| 03 | [heartbeat](./03-heartbeat.md) | `/heartbeat` | 執行健康記錄，失敗診斷 | 無 |
| 04 | [second-brain](./04-second-brain.md) | `/remember` `/recall` | 跨 session 持久記憶 | Cloudflare Worker |
| 05 | [context-manager](./05-context-manager.md) | `/save` `/load` | Session 內記憶保護 | 無 |
| 06 | [smart-router](./06-smart-router.md) | `/route` | 自動選最省錢的模型 | LiteLLM Proxy |
| 07 | [local-llm](./07-local-llm.md) | `/local` | 本地模型，零成本/隱私保護 | Ollama |
| 08 | [cost-watcher](./08-cost-watcher.md) | `/cost` | 費用監控，發現浪費點 | LiteLLM Proxy |
| 09 | [telegram-notify](./09-telegram-notify.md) | `/notify` | 任務完成/失敗即時通知 | Telegram Bot |
| 10 | [reddit-radar](./10-reddit-radar.md) | `/radar` | Reddit 社群情報自動爬取 | rdt-cli |
| 11 | [web-search](./11-web-search.md) | `/search` `/browse` | 真實網路搜尋和瀏覽 | SearXNG + Camoufox |

---

## Bundle（預設組合）

| Bundle | 包含 Skills | 適合場景 |
|--------|-----------|---------|
| [agent-ops](./bundles/agent-ops.yaml) | 01+02+03+(09) | 長跑自動化，不需要人工推動 |
| [memory-stack](./bundles/memory-stack.yaml) | 04+05 | 永不失憶，跨設備同步 |
| [cost-saver](./bundles/cost-saver.yaml) | 06+07+08 | API 費用降低 60-95% |
| [community-intel](./bundles/community-intel.yaml) | 10+09+(03+11) | 自動社群情報 + Telegram 推送 |
| [full-stack](./bundles/full-stack.yaml) | 全部 11 個 | 完整 AI 工作站 |

---

## 依症狀選 Skill

```
「Agent 跑到一半就卡住，要一直推」
  → Bundle: agent-ops（01+02+03）

「每次 session 都要重新說明背景」
  → Bundle: memory-stack（04+05）

「AI 帳單太貴，每個月 $100 USD 以上」
  → Bundle: cost-saver（06+07+08）

「想自動監控 Reddit，每天收到摘要」
  → Bundle: community-intel（10+09）

「需要處理隱私資料，不能上雲端」
  → Skill: 07-local-llm

「Cron job 跑了但 agent 不記得目標」
  → Skill: 02-goal-keeper + 03-heartbeat

「長時間任務做到一半，隔天繼續做」
  → Skill: 01-kanban-board + 05-context-manager
```

---

## 如何把 Skill 加入 Hermes

### 方法一：單個 skill

把 skill 文件的內容複製，貼入 `soul.md` 或 `AGENTS.md` 的對應區塊。

### 方法二：Bundle 一鍵安裝

找到 bundle 的 `deploy.prompt_files`，依序把每個 DEPLOY_PROMPT.md 貼給 agent：

```
# 以 agent-ops bundle 為例：
1. 打開 services/agent-ops/DEPLOY_PROMPT.md
2. 全文複製
3. 貼給 Hermes 或 OpenClaw
4. Agent 自動完成安裝
```

### 方法三：全部一起裝（full-stack）

依照 `bundles/full-stack.yaml` 的 `deploy.order`，按順序執行各個 DEPLOY_PROMPT.md。

---

## Skill 相依圖

```
09-telegram-notify ←──────────────────────────┐
                                               │
10-reddit-radar ──→ 03-heartbeat ──→ 通知     │
                         ↑                    │
01-kanban-board ─────────┤                    │
02-goal-keeper ──────────┤                    │
                         │                    │
06-smart-router ──→ 07-local-llm              │
      ↑                  │                    │
08-cost-watcher ─────────┘                    │
                                              │
04-second-brain ──→ 05-context-manager        │
                         │                    │
11-web-search ───────────┘                    │
                                              │
所有 skills ──────────────────────────────────┘
```

---

## 安裝進度追蹤

複製到你自己的文件，打勾記錄安裝狀態：

```
### 基礎層（建議全裝）
- [ ] 01-kanban-board    （無需安裝，修改 soul.md 即可）
- [ ] 02-goal-keeper     （無需安裝，修改 soul.md 即可）
- [ ] 03-heartbeat       （無需安裝，修改 soul.md 即可）
- [ ] 05-context-manager （services/context-manager/DEPLOY_PROMPT.md）

### 記憶層
- [ ] 04-second-brain    （services/second-brain/DEPLOY_PROMPT.md）

### 費用控制
- [ ] 06-smart-router    （services/cost-control/DEPLOY_PROMPT.md）
- [ ] 07-local-llm       （services/local-model/DEPLOY_PROMPT.md）
- [ ] 08-cost-watcher    （services/cost-control/DEPLOY_PROMPT.md 含）

### 通知
- [ ] 09-telegram-notify （Telegram BotFather 設定 token）

### 情報收集
- [ ] 10-reddit-radar    （skills/reddit-radar/HERMES_TRANSFER_PROMPT.md）
- [ ] 11-web-search      （services/web-tools/DEPLOY_PROMPT.md）
```
