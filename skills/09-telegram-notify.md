# Skill：Telegram Notify（任務通知）

> 任務完成、失敗、費用超限時，發送 Telegram 通知

## 前置條件

```bash
# 在 .env 或環境變數設定：
TELEGRAM_BOT_TOKEN=你的 bot token
TELEGRAM_CHAT_ID=你的 chat id
```

取得方式：[@BotFather](https://t.me/BotFather) 建立 bot → 取得 token → 傳任意訊息給 bot → 用 getUpdates 取得 chat_id

## 觸發指令

| 指令 | 說明 |
|------|------|
| `/notify test` | 發送測試訊息確認設定正確 |
| `/notify on` | 啟用自動通知 |
| `/notify off` | 關閉自動通知 |
| `/notify [訊息]` | 立即發送一則訊息 |

## 自動發送時機

```
任務完成（✅）→ 發送完成通知（含結果摘要）
任務失敗（❌）→ 立即發送告警
連續 3 次失敗 → 發送緊急告警
月費超過 80%  → 費用預警
Heartbeat 超時 → 發送系統告警
週報（每週一早上 9 點）→ 本週工作摘要
```

## 通知格式範例

```
✅ 任務完成
Reddit 雷達報告已產出
文章：r/hermesagent 3篇 | r/openclaw 8篇
報告：reports/latest.md
耗時：47 秒

---

❌ 任務失敗
Reddit 爬蟲 — rdt-cli 連線超時
錯誤：ConnectionTimeout after 30s
已重試 3 次，移入 BLOCKED
請確認網路或 rdt-cli 狀態

---

📊 週報 2026-W21
完成任務：12 個
失敗任務：1 個（已解決）
本週 AI 費用：$4.20 USD
目標推進：✅ 商業模式文件完成
```

## 發送程式碼

```python
import os, httpx

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

def notify(message: str, parse_mode: str = "Markdown"):
    httpx.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": parse_mode,
        }
    )

# 使用範例
notify("✅ 任務完成：Reddit 雷達報告已產出")
```

## 組合使用

此 skill 幾乎與所有 skill 搭配：
- `03-heartbeat`：失敗時觸發告警
- `08-cost-watcher`：費用超限時發預警
- `10-reddit-radar`：報告產出後發摘要
- `01-kanban-board`：重大任務完成時通知
