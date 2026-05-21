# Web Tools Service — 銷售指南

## 你在賣什麼

**一句話：讓客戶的 AI agent 能真的「上網」，而且不會被封鎖。**

---

## 客戶的痛點

使用 OpenClaw / Hermes 的人，80% 都會遇到這個問題：

> 「我的 agent 想要幫我爬 LinkedIn、Zillow、Redfin…結果都被封鎖了」

原因：
- VPS 的 datacenter IP 早就被各大網站列為黑名單
- 沒有偽裝瀏覽器指紋，一眼就看出是 bot
- Reddit 社群今天也在討論這個：有人因為 datacenter IP 連 Zillow 都進不去

**你的解法**：在客戶的家用電腦上跑這套服務，居家 IP + Camoufox 反偵測，看起來就像真人在瀏覽。

---

## 目標客戶

| 客戶類型 | 痛點 | 付費意願 |
|----------|------|----------|
| OpenClaw / Hermes 重度用戶 | 被封鎖，agent 無法正常抓資料 | 高 |
| 做自動化副業的人 | 需要穩定爬蟲但不想維護 | 中高 |
| 小型企業主 | 競品監控、自動報價、潛客研究 | 高 |
| 開發者/Vibe Coder | 快速跑通 PoC，不想自己搭環境 | 中 |

---

## 定價策略

### 方案一：一次性建置（最好賣）

```
建置費：$3,000 – $8,000 TWD
內容：
  ✅ 遠端幫客戶安裝整套服務
  ✅ 設定好 OpenClaw/Hermes MCP 連接
  ✅ 測試確認可用
  ✅ 教學 30 分鐘（怎麼用 web_search 和 browse_url）
  ✅ 1 個月內免費支援
```

**為什麼定這個價**：
客戶自己搞要花 4–8 小時，你 30 分鐘搞定，省的時間遠超過費用。

---

### 方案二：月費維護（穩定現金流）

```
月費：$1,500 – $3,000 TWD/月
內容：
  ✅ 套件版本更新（Camoufox、SearXNG）
  ✅ 封鎖問題排查（某網站又換反爬蟲了）
  ✅ 新增搜尋引擎來源
  ✅ 月度使用報告
```

**銷售話術**：
「Camoufox 每隔幾個月就要更新一次對應新的 bot 偵測，不更新就會失效。月費方案我幫你持續維護，你不用管。」

---

### 方案三：套餐（建置 + 維護）

```
首月：$6,000 TWD（建置 + 第一個月維護）
次月起：$2,000 TWD/月
```

這是利潤最高的方案，建議主推。

---

## 銷售流程

### 第一步：找客戶在哪裡

1. **Reddit** — r/hermesagent、r/openclaw 找在討論「被封鎖」、「datacenter IP」的人，私訊
2. **Discord** — OpenClaw/Hermes 的官方 Discord，在 #help 頻道找卡關的人
3. **Facebook 社團** — AI 自動化、Claude、ChatGPT 相關社團
4. **PTT/Dcard** — 台灣用戶多，競爭少

### 第二步：開場話術

針對在社群發文說「被封鎖」的人：

> 「Hi，看到你在討論 datacenter IP 被封鎖的問題。我最近幫幾個 OpenClaw 用戶搭了一套 Camoufox + SearXNG 的組合，跑在居家 IP 上，Cloudflare 封鎖的問題基本上解決了。有興趣了解看看嗎？」

---

### 第三步：展示價值（關鍵）

不要用文字解釋，直接錄一段 Demo 影片：

```
Demo 流程（3 分鐘）：
1. 打開 OpenClaw，對著 Zillow 說「幫我抓這個房源的資訊」
2. 沒裝這套：顯示 403 / 被擋
3. 裝了這套：成功抓到，顯示結果
4. 說：「這就是差別」
```

影片放 YouTube 或 Twitter，貼在社群回文時附上。

---

### 第四步：遠端安裝

客戶付款後：
1. 用 Zoom / Google Meet 開視訊
2. 讓客戶把 `DEPLOY_PROMPT.md` 貼進自己的 agent
3. Agent 自動跑完安裝
4. 你在旁邊確認、排錯
5. 跑一次 Demo 確認成功

**整個過程 20–45 分鐘**，你可以同時開 2–3 個客戶的 session。

---

## 常見客戶問題 Q&A

**Q：為什麼一定要在家裡的電腦跑？**
A：網站透過 IP 判斷你是不是真人。住宅 IP（你家的網路）被信任，機房 IP 早就被列黑名單。把這套跑在 VPS 上沒有意義。

**Q：我的電腦要 24 小時開著嗎？**
A：SearXNG 和 Camoufox 只在 agent 需要的時候才會用到。如果你的 agent 只在你電腦開著的時候工作，就不需要 24 小時。如果需要全天候，可以另外買台 Mac Mini 或 NUC 放家裡（一次性硬體投資，我可以幫你設定好）。

**Q：這樣合法嗎？**
A：工具本身合法。你用的是你自己家的 IP，瀏覽公開的網站。具體的使用方式要符合各網站的服務條款，這是客戶自己的責任。

**Q：SearXNG 的搜尋結果夠好嗎？**
A：SearXNG 同時查 Google、Bing、DuckDuckGo、Brave，結果比單一搜尋引擎更全面。

---

## 怎麼擴大規模

當你有 5–10 個穩定月費客戶後：

1. **寫成教學文** → 賣課程或 PDF（$500–$1500 一份）
2. **做成 SaaS**（進階）→ 幫客戶管居家 IP，走 residential proxy 路線
3. **打包成更大的服務** → 結合 Context Manager Skill + Web Tools，賣「OpenClaw 最佳化套餐」

---

## 技術支援備忘

常見問題處理：

```bash
# SearXNG 沒有回應
docker logs searxng
docker compose restart searxng

# Camoufox 更新
pip install -U "camoufox[geoip]"
python3 -m camoufox fetch

# 確認 MCP server 可用
python3 ~/web-tools-service/web_tools_server.py
# 應該顯示「啟動 MCP server（web-tools）...」

# 重置 SearXNG 設定
docker compose down -v
docker compose up -d
```
