# hermes-business

> Hermes Agent / OpenClaw 優化服務工具包
> 可直接銷售給客戶，或作為個人 agent 設定使用

---

## 服務目錄

### 🌐 Services（付費服務）

| 服務 | 說明 | 部署難度 |
|------|------|----------|
| [web-tools](./services/web-tools/) | Camoufox + SearXNG，讓 agent 能真正上網，繞過封鎖 | ⭐⭐ |
| [context-manager](./services/context-manager/) | 三層 context 保護，讓 agent 長 session 不失憶 | ⭐ |

### 🛠️ Skills（免費/自用）

| Skill | 說明 |
|-------|------|
| [reddit-radar](./skills/reddit-radar/) | 每 12 小時自動抓取 Reddit 指定社群，產出雷達報告 |

### 💼 Sales（銷售資料）

| 文件 | 說明 |
|------|------|
| [web-tools-sales-guide](./sales/web-tools-sales-guide.md) | Web Tools 服務的定價、話術、Demo 腳本 |

---

## 快速開始

### 安裝 Web Tools（給自己用）

```bash
cd services/web-tools
chmod +x install.sh
./install.sh
```

### 部署給客戶

把對應服務的 `DEPLOY_PROMPT.md` 全文貼進客戶的 Hermes 或 OpenClaw，agent 會自動完成安裝。

### 使用 Reddit Radar

```bash
cd skills/reddit-radar
python3 scraper.py
```

---

## 資料夾結構

```
hermes-business/
├── services/
│   ├── web-tools/          # Camoufox + SearXNG + MCP Server
│   └── context-manager/    # 三層 Context 保護 Skill
├── skills/
│   └── reddit-radar/       # Reddit 12 小時雷達爬蟲
└── sales/
    └── web-tools-sales-guide.md
```

---

## 依賴需求

| 工具 | 版本 | 必要性 |
|------|------|--------|
| Python | 3.10+ | 必要 |
| Docker Desktop | 最新 | web-tools 需要 |
| uv | 最新 | reddit-radar 需要（安裝 rdt-cli） |
| rdt-cli | 0.4.1+ | reddit-radar 需要 |
