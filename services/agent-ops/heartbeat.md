# Agent Heartbeat Log Template

> 複製到專案根目錄，每次 cron 執行時自動更新

---

## 最近一次執行

- **時間**：{{LAST_RUN_TIME}}
- **狀態**：{{STATUS}}（✅ 成功 / ❌ 失敗 / ⚠️ 部分完成）
- **執行時間**：{{DURATION}} 秒
- **任務完成數**：{{TASKS_DONE}} / {{TASKS_TOTAL}}
- **產出**：{{OUTPUT_PATH}}
- **通知**：{{NOTIFICATION_STATUS}}

---

## 執行歷史（最近 10 次）

| 時間 | 狀態 | 秒數 | 完成任務 | 備注 |
|------|------|------|---------|------|
| — | — | — | — | — |

---

## 系統健康狀態

| 元件 | 狀態 | 最後確認 |
|------|------|---------|
| rdt-cli | — | — |
| Telegram Bot | — | — |
| 磁碟空間 | — | — |
| API 連線 | — | — |

---

## Agent 操作規則

每次 cron 執行結束時，Agent **必須**更新這個文件：

```python
# Agent 在啟動時讀取
with open("heartbeat.md") as f:
    last_status = parse_last_status(f.read())

if last_status == "FAILED":
    # 先診斷失敗原因，再繼續
    handle_failure()

# Agent 在完成時寫入
update_heartbeat(
    status="SUCCESS",
    duration=elapsed_seconds,
    tasks_done=completed_count,
    output=output_path
)
```

---

## 警告條件（超過這些就要人工介入）

- 連續 3 次失敗 → 發 Telegram 告警給管理員
- 執行時間超過 10 分鐘 → 可能卡住，強制終止重啟
- 磁碟空間低於 500MB → 清理舊報告
