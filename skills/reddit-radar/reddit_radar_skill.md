# Skill: Reddit Radar 雷達爬蟲

## 說明

每 12 小時自動抓取指定 subreddit 的最新文章與熱門留言，產出結構化 markdown 雷達報告。
目前監控：**r/hermesagent**、**r/openclaw**

## 觸發方式

- `運行 reddit radar` — 立即爬取並產出報告
- `讀取最新 reddit 報告` — 讀取 `~/reddit-radar/reports/latest.md`
- `reddit radar 狀態` — 顯示 cronjob 狀態與最後執行時間

## 依賴套件

| 套件 | 安裝方式 | 用途 |
|------|----------|------|
| uv | `brew install uv` 或 `curl -LsSf https://astral.sh/uv/install.sh \| sh` | Python 套件管理 |
| rdt-cli | `uv tool install rdt-cli` | Reddit 爬蟲 CLI |
| Python 3.10+ | 系統內建 | 執行爬蟲腳本 |

## 檔案結構

```
~/reddit-radar/
├── scraper.py          # 主爬蟲腳本
├── scraper.log         # 執行 log
└── reports/
    ├── latest.md       # 最新報告（每次覆寫）
    └── radar_YYYYMMDD_HHMM.md  # 歷史報告
```

launchd plist（macOS cronjob）：
```
~/Library/LaunchAgents/com.reddit-radar.plist
```

## 常用指令

```bash
# 立即執行一次
python3 ~/reddit-radar/scraper.py

# 查看最新報告
cat ~/reddit-radar/reports/latest.md

# 查看執行 log
tail -20 ~/reddit-radar/scraper.log

# 確認 cronjob 狀態
launchctl list | grep reddit-radar

# 手動觸發 cronjob
launchctl start com.reddit-radar

# 停止 cronjob
launchctl unload ~/Library/LaunchAgents/com.reddit-radar.plist

# 重新載入 cronjob
launchctl unload ~/Library/LaunchAgents/com.reddit-radar.plist
launchctl load ~/Library/LaunchAgents/com.reddit-radar.plist
```

## 新增 subreddit

編輯 `~/reddit-radar/scraper.py`，修改第一行設定：

```python
SUBREDDITS = ["hermesagent", "openclaw", "新的subreddit名稱"]
```

## 調整爬取時間範圍

修改 `HOURS = 12` 可改為任意小時數（建議與 cronjob 間隔一致）。
