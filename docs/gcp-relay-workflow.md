# GCP 任務轉交流程

## 核心概念

本機 Claude 負責對話與決策，GCP Claude 負責實作。
log.md 是兩端之間的唯一溝通媒介。
GitHub 是最終存放站，不是中繼站。

---

## 完整流程

```
【本機端】
本機 Claude 與使用者對話
    ↓
本機 Claude 更新 log.md（加入本次對話摘要與待實作任務）
    ↓
SCP 直接把 log.md 覆蓋到 GCP 的對應路徑
    ↓
透過 tmux send-keys 告訴 GCP Claude：
  「請讀取 log.md 最新一則，判斷是否有待實作任務，有的話執行」

【GCP 端】
GCP Claude 讀取 log.md 最新一則
    ↓
判斷有待實作任務 → 執行實作（修改程式碼、資料庫 schema 等）
    ↓
實作完成後，把本輪的對話記錄追加到 log.md
    ↓
git add && git commit && git push origin main

【本機端收尾】
git pull → 取得 GCP 實作結果與更新後的 log.md
```

---

## 各端分工

| 責任         | 本機 Claude | GCP Claude |
|--------------|-------------|------------|
| 對話與決策   | ✓           |            |
| 更新 log.md  | ✓（寫入本次對話）| ✓（追加實作記錄）|
| SCP 傳檔     | ✓           |            |
| 實作程式碼   |             | ✓          |
| git push     |             | ✓          |
| git pull     | ✓（取回結果）|            |

---

## 標準操作指令

### 步驟一：本機更新 log.md 並傳送到 GCP

```powershell
. ~/.claude/env.ps1
$logPath = "~/.claude/tools/project-kitchen/log.md"

# 把本機 log.md 直接覆蓋到 GCP
& $SCP_BIN -i $SSH_KEY -o StrictHostKeyChecking=no `
    $logPath "${SSH_USER}@35.227.93.38:~/.claude/tools/project-kitchen/log.md"
```

### 步驟二：通知 GCP Claude 讀取並執行

```powershell
. ~/.claude/env.ps1
$SSH_OPTS = @("-i", $SSH_KEY, "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes")
$task = "請讀取 ~/.claude/tools/project-kitchen/log.md 的最新一則內容，判斷是否有待實作任務。有的話完整執行，實作完成後把本輪記錄追加到 log.md，再執行 git add && git commit -m '實作：[任務名稱]' && git push origin main，最後傳 Telegram 通知說明改了什麼。"

& $SSH_BIN @SSH_OPTS "${SSH_USER}@35.227.93.38" "tmux send-keys -t claude:0 '$task' Enter"
```

### 步驟三：本機取回結果

```powershell
cd ~/.claude
git pull origin main
```

---

## log.md 格式規範

每一則記錄必須包含：

```markdown
## [日期] [主題]

### 對話摘要
[本次對話的決策與重點]

### 待實作任務
[具體任務描述，沒有就省略這一段]

### 實作結果（GCP 填寫）
[GCP Claude 完成後追加這段]
```

---

## 相關路徑

- 本機 log.md：`~/.claude/tools/project-kitchen/log.md`
- GCP log.md：`~/.claude/tools/project-kitchen/log.md`（同路徑）
- GCP 出題程式：`~/.claude/tools/project-kitchen/cross_subject_bot.py`
- GCP 資料庫：`/home/yuchi/cognitive-tests/practice.db`
- GitHub repo：`https://github.com/Yuchiaoniu/auto-memory.git`
