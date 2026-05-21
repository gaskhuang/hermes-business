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
    """抓取 subreddit 最新文章，過濾 12 小時內"""
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

    # 依分數排序取前 TOP_COMMENTS
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
                time.sleep(1)  # rdt-cli 內建速率限制，額外保護

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
