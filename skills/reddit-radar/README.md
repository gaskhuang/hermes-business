# Reddit Radar Skill

> 每 12 小時自動抓取 Reddit 社群最新文章與留言，產出 markdown 雷達報告。

## 預設監控

- r/hermesagent
- r/openclaw

## 依賴

```bash
uv tool install rdt-cli
```

## 安裝

```bash
python3 scraper.py
```

## 部署給 Hermes

把 `HERMES_TRANSFER_PROMPT.md` 全文貼進 Hermes，agent 會自動：
1. 安裝 rdt-cli
2. 建立目錄與 scraper.py
3. 設定 macOS launchd（每 12 小時自動跑）
4. 執行第一次測試

## 輸出

- `reports/latest.md` — 最新報告（每次覆寫）
- `reports/radar_YYYYMMDD_HHMM.md` — 歷史紀錄

## 新增 subreddit

編輯 `scraper.py` 第 15 行：

```python
SUBREDDITS = ["hermesagent", "openclaw", "你的subreddit"]
```
