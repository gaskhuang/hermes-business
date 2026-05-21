請幫我安裝「Context Manager Pro」Skill，這會讓你自動管理 context，在長時間工作中不再失憶。請依序執行以下步驟：

---

## 步驟 1：確認 skills 目錄

```bash
# OpenClaw 用戶
ls ~/.openclaw/skills/ 2>/dev/null || ls ~/openclaw/skills/ 2>/dev/null || find ~ -name "skills" -type d 2>/dev/null | head -5

# Hermes 用戶
ls ~/.hermes/skills/ 2>/dev/null || find ~ -name "skills" -type d 2>/dev/null | head -5
```

找到 skills 目錄後記下路徑，後續步驟會用到。

---

## 步驟 2：建立 context_manager.md skill 檔案

在 skills 目錄建立 `context_manager.md`，內容如下：

```markdown
# Skill: Context Manager Pro

## 這個 Skill 在做什麼
自動管理 context，避免長 session 失憶。每 10–15 輪把任務狀態寫進 .task_state.md，session 重開時自動讀取恢復進度。

## 行為規則

### Session 開始時
1. 執行 `find . -maxdepth 2 -name ".task_state.md" 2>/dev/null` 檢查是否有舊狀態
2. 找到的話讀取並告知使用者：「找到上次任務記錄，目標是 [XXX]，是否繼續？」
3. 沒有的話正常開始

### 每 10–15 輪，或以下時機主動觸發：
- 完成一個子任務
- 使用者說「等等」、「先停」、「待會繼續」
- Context 使用率超過 75%
- 即將執行大量 token 的操作

執行：更新當前目錄的 .task_state.md

### .task_state.md 格式
每次用以下格式完整覆寫：

    # Task State
    更新時間：{timestamp}
    輪次：{turn}

    ## 🎯 當前目標
    {goal}

    ## ✅ 已完成
    {completed}

    ## ⏭️ 下一步
    {next_steps}

    ## 🚧 障礙 / 決策
    {blockers}

    ## 📁 關鍵檔案
    {files}

    ## 💬 最後 3 輪重點
    {recent_summary}

### Context 接近上限時
1. 先更新 .task_state.md
2. 告知使用者「即將壓縮 context，已儲存狀態」
3. 壓縮後讀取 .task_state.md 重新定向

### 使用者指令
- 「存狀態」→ 立即更新 .task_state.md
- 「從哪裡停的」→ 讀取並摘要 .task_state.md
- 「清除狀態」→ 刪除 .task_state.md
```

---

## 步驟 3：加入 AGENTS.md（OpenClaw）或 soul.md（Hermes）

在設定檔末尾加入以下內容：

```
## Context 管理（必讀）

你必須主動管理自己的 context 狀態：

1. 每 10–15 輪，把當前目標、已完成步驟、下一步、障礙，寫進 .task_state.md
2. 每次 session 開始，先檢查是否有 .task_state.md，有的話讀取並問使用者是否繼續
3. Context 接近上限時，先存 .task_state.md，壓縮後再讀取找回方向
4. 使用者說「存狀態」立即執行；說「從哪裡停的」讀取摘要；說「清除」刪除檔案

格式固定，永遠覆寫，不要 append。
```

**OpenClaw：**
```bash
echo "" >> ~/.openclaw/AGENTS.md
cat >> ~/.openclaw/AGENTS.md << 'EOF'

## Context 管理（必讀）

你必須主動管理自己的 context 狀態：

1. 每 10–15 輪，把當前目標、已完成步驟、下一步、障礙，寫進 .task_state.md
2. 每次 session 開始，先檢查是否有 .task_state.md，有的話讀取並問使用者是否繼續
3. Context 接近上限時，先存 .task_state.md，壓縮後再讀取找回方向
4. 使用者說「存狀態」立即執行；說「從哪裡停的」讀取摘要；說「清除」刪除檔案

格式固定，永遠覆寫，不要 append。
EOF
```

**Hermes：**
```bash
echo "" >> ~/.hermes/soul.md
cat >> ~/.hermes/soul.md << 'EOF'

## Context 管理（必讀）

你必須主動管理自己的 context 狀態：

1. 每 10–15 輪，把當前目標、已完成步驟、下一步、障礙，寫進 .task_state.md
2. 每次 session 開始，先檢查是否有 .task_state.md，有的話讀取並問使用者是否繼續
3. Context 接近上限時，先存 .task_state.md，壓縮後再讀取找回方向
4. 使用者說「存狀態」立即執行；說「從哪裡停的」讀取摘要；說「清除」刪除檔案

格式固定，永遠覆寫，不要 append。
EOF
```

---

## 步驟 4：Hermes Skill Bundle（選用）

如果使用 Hermes 且想用 slash command 一鍵啟動：

```bash
mkdir -p ~/.hermes/bundles
cat > ~/.hermes/bundles/protected_session.yaml << 'EOF'
name: protected_session
description: 帶 context 保護的工作 session，不再失憶
skills:
  - context_manager
triggers:
  on_session_start: true
  on_compaction: true
EOF
```

之後輸入 `/protected_session` 啟動。

---

## 步驟 5：驗證安裝

重新開啟一個 session，輸入：

```
你現在有沒有 context 管理功能？會不會自動存 .task_state.md？
```

agent 應該回答「會」，並說明何時觸發存檔。

然後隨便開始一個任務，說「存狀態」，確認當前目錄出現 `.task_state.md`。

---

## 安裝完成後你會得到

✅ 長 session 不再因為 compaction 失憶  
✅ 電腦關掉重開，agent 記得昨天做到哪  
✅ 手動一句話儲存/恢復狀態  
✅ Compaction 前自動備份，壓縮後自動找回方向  
