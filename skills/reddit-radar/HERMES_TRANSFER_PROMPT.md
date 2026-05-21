請幫我完整安裝並設定 Reddit Radar 爬蟲系統。這是一個每 12 小時自動抓取 r/hermesagent 和 r/openclaw 最新文章與留言，並產出 markdown 報告的工具。請依照以下步驟逐一執行，每步驟完成後確認成功再繼續。

---

## 步驟 1：安裝 rdt-cli

```bash
uv tool install rdt-cli
```

確認安裝成功：
```bash
rdt --version
```

如果 uv 不存在，先安裝：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv tool install rdt-cli
```

---

## 步驟 2：建立目錄

```bash
mkdir -p ~/reddit-radar/reports
```

---

## 步驟 3：建立爬蟲腳本

建立檔案 `~/reddit-radar/scraper.py`，內容如下：

```python
#!/usr/bin/env python3
"""
Reddit 雷達爬蟲 — 每 12 小時抓取 r/hermesagent 和 r/openclaw
使用 rdt-cli (https://github.com/public-clis/rdt-cli) 抓取資料
產出 markdown 報告至 reports/ 目錄
"""

import json
import shutil
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

SUBREDDITS = ["hermesagent", "openclaw"]
HOURS = 12
TOP_COMMENTS = 10
OUTPUT_DIR = Path(__file__).parent / "reports"
RDT = shutil.which("rdt") or "/usr/local/bin/rdt"


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def rdt_json(*args) -> dict:
    """執行 rdt 指令並回傳 JSON 結果"""
    cmd = [RDT] + list(args) + ["--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"rdt 錯誤: {result.stderr.strip()}")
    data = json.loads(result.stdout)
    if not data.get("ok"):
        raise RuntimeError(f"rdt 回傳失敗: {data}")
    return data


def get_posts(subreddit: str, cutoff_ts: float) -> list[dict]:
    """抓取 subreddit 最新文章，過濾指定時間內"""
    data = rdt_json("sub", subreddit, "-s", "new", "-n", "100")
    posts = []
    for item in data["data"]["data"]["children"]:
        if item["kind"] != "t3":
            continue
        p = item["data"]
        if p["created_utc"] < cutoff_ts:
            continue
        posts.append({
            "id": p["id"],
            "title": p["title"],
            "author": p.get("author", "[deleted]"),
            "score": p.get("ups", 0),
            "num_comments": p.get("num_comments", 0),
            "created_utc": p["created_utc"],
            "permalink": f"https://www.reddit.com{p['permalink']}",
            "selftext": (p.get("selftext") or "")[:400],
            "flair": p.get("link_flair_text") or "—",
        })
    return posts


def get_top_comments(post_id: str) -> list[dict]:
    """抓取文章的頂層留言（依分數排序，最多 TOP_COMMENTS 則）"""
    data = rdt_json("read", post_id)
    comments = []
    listings = data["data"]
    if not isinstance(listings, list) or len(listings) < 2:
        return comments

    for item in listings[1]["data"]["children"]:
        if item.get("kind") != "t1":
            continue
        c = item["data"]
        body = (c.get("body") or "").strip()
        if not body:
            continue
        comments.append({
            "author": c.get("author", "[deleted]"),
            "score": c.get("ups", 0),
            "body": body[:300].replace("\n", " "),
        })
        if len(comments) >= TOP_COMMENTS:
            break

    comments.sort(key=lambda x: x["score"], reverse=True)
    return comments[:TOP_COMMENTS]


def render_report(all_data: dict[str, list], now: datetime, cutoff: datetime) -> str:
    total_posts = sum(len(v) for v in all_data.values())
    summary_parts = " | ".join(
        f"r/{sub}: {len(posts)}篇" for sub, posts in all_data.items()
    )

    lines = [
        f"# Reddit 雷達報告 — {now.strftime('%Y-%m-%d %H:%M')}",
        "",
        f"> 資料期間：{cutoff.strftime('%Y-%m-%d %H:%M')} ~ {now.strftime('%Y-%m-%d %H:%M')} | 共 {total_posts} 篇 | {summary_parts}",
        "",
    ]

    for subreddit, posts in all_data.items():
        lines += ["---", "", f"## r/{subreddit}（{len(posts)} 篇）", ""]

        if not posts:
            lines += ["_過去 12 小時無新文章_", ""]
            continue

        posts.sort(key=lambda x: x["score"], reverse=True)

        for i, post in enumerate(posts, 1):
            post_time = datetime.fromtimestamp(post["created_utc"]).strftime("%m-%d %H:%M")
            lines.append(f"### {i}. [{post['title']}]({post['permalink']})")
            lines.append(
                f"**{post['flair']}** | 分數：{post['score']} | "
                f"留言：{post['num_comments']} | u/{post['author']} | {post_time}"
            )
            lines.append("")

            if post["selftext"] and post["selftext"] not in ("[removed]", "[deleted]"):
                preview = post["selftext"].replace("\n", " ")
                lines += [f"> {preview}", ""]

            if post.get("top_comments"):
                lines.append("**熱門留言：**")
                for c in post["top_comments"]:
                    lines.append(f"- **u/{c['author']}** (+{c['score']}): {c['body']}")
                lines.append("")

    lines += ["---", "", f"_報告產生時間：{now.strftime('%Y-%m-%d %H:%M:%S')}_", ""]
    return "\n".join(lines)


def main():
    now = datetime.now()
    cutoff = now - timedelta(hours=HOURS)
    cutoff_ts = cutoff.timestamp()

    log(f"開始爬取（rdt-cli），截止時間：{cutoff.strftime('%Y-%m-%d %H:%M')}")
    OUTPUT_DIR.mkdir(exist_ok=True)

    all_data: dict[str, list] = {}

    for subreddit in SUBREDDITS:
        log(f"抓取 r/{subreddit} 文章...")
        try:
            posts = get_posts(subreddit, cutoff_ts)
            log(f"  找到 {len(posts)} 篇新文章")

            for j, post in enumerate(posts, 1):
                log(f"  [{j}/{len(posts)}] 抓留言：{post['title'][:50]}")
                try:
                    post["top_comments"] = get_top_comments(post["id"])
                except Exception as e:
                    log(f"    留言抓取失敗：{e}")
                    post["top_comments"] = []
                time.sleep(1)

            all_data[subreddit] = posts
        except Exception as e:
            log(f"  r/{subreddit} 失敗：{e}")
            all_data[subreddit] = []

        time.sleep(1)

    report = render_report(all_data, now, cutoff)

    filename = f"radar_{now.strftime('%Y%m%d_%H%M')}.md"
    report_path = OUTPUT_DIR / filename
    report_path.write_text(report, encoding="utf-8")
    log(f"報告儲存至：{report_path}")

    latest_path = OUTPUT_DIR / "latest.md"
    shutil.copy2(report_path, latest_path)
    log(f"已更新：{latest_path}")

    total = sum(len(v) for v in all_data.values())
    log(f"完成。共 {total} 篇文章。")


if __name__ == "__main__":
    main()
```

---

## 步驟 4：建立 macOS 自動排程（每 12 小時）

建立 launchd plist 檔案 `~/Library/LaunchAgents/com.reddit-radar.plist`，內容如下（請將 USERNAME 替換為實際使用者名稱，可用 `whoami` 查詢）：

```bash
WHOAMI=$(whoami)
PYTHON=$(which python3)
SCRIPT="$HOME/reddit-radar/scraper.py"
PLIST="$HOME/Library/LaunchAgents/com.reddit-radar.plist"

cat > "$PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.reddit-radar</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${SCRIPT}</string>
    </array>
    <key>StartInterval</key>
    <integer>43200</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${HOME}/reddit-radar/scraper.log</string>
    <key>StandardErrorPath</key>
    <string>${HOME}/reddit-radar/scraper.log</string>
</dict>
</plist>
EOF

echo "plist 已建立：$PLIST"
```

---

## 步驟 5：載入 cronjob 並測試

```bash
# 載入排程
launchctl load ~/Library/LaunchAgents/com.reddit-radar.plist

# 確認已載入
launchctl list | grep reddit-radar

# 立即執行一次測試
python3 ~/reddit-radar/scraper.py

# 確認報告產出
ls -lh ~/reddit-radar/reports/
```

---

## 步驟 6：確認完成

安裝完成後請確認以下事項：

1. `rdt --version` 有顯示版本號
2. `~/reddit-radar/scraper.py` 檔案存在
3. `launchctl list | grep reddit-radar` 有顯示 job
4. `~/reddit-radar/reports/latest.md` 有產出報告

全部完成後，系統將每 12 小時自動爬取 r/hermesagent 和 r/openclaw，報告存於 `~/reddit-radar/reports/latest.md`。

---

## 注意事項

- **新增 subreddit**：編輯 `~/reddit-radar/scraper.py` 第 15 行的 `SUBREDDITS` 列表
- **更改爬取頻率**：修改 plist 的 `StartInterval`（單位：秒，43200 = 12 小時）
- **查看 log**：`tail -f ~/reddit-radar/scraper.log`
- **rdt-cli 更新**：`uv tool upgrade rdt-cli`
