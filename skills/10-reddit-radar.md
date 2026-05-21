# Skill：Reddit Radar（社群雷達）

> 每 12 小時自動抓取指定 subreddit，產出 markdown 雷達報告

## 前置條件

```bash
uv tool install rdt-cli   # 需要 Reddit 帳號 cookie
```

安裝完整版：`skills/reddit-radar/HERMES_TRANSFER_PROMPT.md`

## 觸發指令

| 指令 | 說明 |
|------|------|
| `/radar` | 立即執行一次爬取，產出報告 |
| `/radar [subreddit]` | 爬取指定 subreddit |
| `/radar summary` | 顯示最新報告的摘要 |
| `/radar schedule` | 確認 cron 排程狀態 |

## 監控清單

預設監控：
- r/hermesagent
- r/openclaw

修改方式：編輯 `skills/reddit-radar/scraper.py` 第 15 行的 `SUBREDDITS`

## 輸出格式

```markdown
# Reddit 雷達報告 — 2026-05-21 14:00

> 期間：02:00 ~ 14:00 | hermesagent: 5篇 | openclaw: 12篇

---

## r/hermesagent（5 篇）

### 1. [文章標題](permalink)
**Flair** | 分數：42 | 留言：15 | u/作者 | 02:35

> 文章摘要（400字以內）

**熱門留言：**
- **u/xxx** (+12): 留言內容...
```

## Cron 排程

```xml
<!-- ~/Library/LaunchAgents/com.reddit-radar.plist -->
<key>StartInterval</key>
<integer>43200</integer>  <!-- 每 12 小時 -->
<key>RunAtLoad</key>
<true/>
```

## 搭配 heartbeat（建議）

```python
# scraper.py 最後加入
update_heartbeat(status="SUCCESS", output="reports/latest.md")
notify_telegram(f"📡 雷達報告已更新：{post_count} 篇新文章")
```

## 組合使用

此 skill 常與以下搭配：
- `03-heartbeat`：記錄每次爬取是否成功
- `09-telegram-notify`：報告產出後推送摘要
- `02-goal-keeper`：爬取到的洞察是否推進業務目標
