# 自動迭代啟動說明

## 啟動指令

在 Claude Code 輸入以下指令即可啟動自動迭代：

```
/loop 出題系統自動迭代自我檢查
```

---

## 每次迭代的執行流程

所有重工作由 fork 子代理在內部完成，完整探索結果傳送到 Telegram，
主要對話視窗只收 2-3 行摘要，避免對話視窗被塞滿而觸發壓縮。

### 步驟一：啟動 fork 子代理

用 Agent(subagent_type: "fork") 啟動子代理，傳入以下任務（子代理的完整 prompt 見下方「子代理 prompt 範本」）。

子代理在內部完成：
1. SSH 到 GCP 取得觀念統計（`python3 /home/yuchi/cross_subject_bot.py stats`）
2. 讀取系統設計說明（`C:\Users\yuchi\.claude\tools\project-kitchen\system-design.md`）
3. 呼叫 `Skill(openspec-explore)` 進行六問自我檢查
4. 把完整探索結果整理成 Telegram 訊息傳送（格式見下方「Telegram 訊息格式」）
5. 如果探索工具決定修改系統，修改 `system-design.md`
6. 把本輪記錄追加到 GCP 的 `/home/yuchi/cognitive-tests/meta_log.md`
7. 回傳 2-3 行摘要給主要對話視窗

### 步驟二：記錄摘要

主要對話視窗只記錄子代理回傳的 2-3 行摘要。

### 步驟三：排程下一輪

呼叫 ScheduleWakeup，600 秒後繼續下一輪，prompt: `出題系統自動迭代自我檢查`

---

## 子代理 prompt 範本

```
你是迭代自我檢查子代理。請執行以下七個步驟，不要詢問使用者，全部自行完成。
所有輸出（Telegram 訊息、回傳摘要）一律用白話中文，禁止使用縮寫或技術術語。

【步驟一】SSH 到 GCP 取得觀念統計
  指令：python3 ~/.claude/tools/project-kitchen/cross_subject_bot.py stats
  SSH 資訊（Windows 本機執行時）：
    主機：35.227.93.38
    使用者：yuchi
    金鑰：~/.ssh/google_compute_engine
  （若已在 GCP 上執行，直接在本機跑上面的指令，不需要 SSH）

【步驟二】讀取系統設計說明
  路徑：~/.claude/tools/project-kitchen/system-design.md

【步驟三】呼叫 Skill(openspec-explore) 進行六問自我檢查
  傳入系統設計說明全文和觀念統計，圍繞以下六個問題進行探索：
  Q1. 這套系統有沒有哪裡值得改進？
  Q2. 系統哪些功能值得保留？未來規模更大時仍然適用的部分有哪些？
  Q3. 有沒有我還沒注意到、正在悄悄出問題的地方？
  Q4. 系統推給使用者的資訊有沒有太多、太亂？
  Q5. 這樣修改後有沒有可能出現什麼問題？
  Q6. 現有每個機制給 0-10 分評分，說明理由。

  重要提醒：探索的核心是「使用者對每個觀念持有什麼心智模型」，
  不是答對率統計。禁止以答對率、掌握次數為分析中心。

【步驟四】整理完整 Telegram 訊息並傳送

  訊息格式：
  ────────────────────────────────
  【迭代自我檢查完整記錄 #N】

  觀念覆蓋：X 個已接觸 / Y 個已掌握 / Z 個待加強

  Q1（值得改進的地方）
  選項 A：...
  選項 B：...
  選項 C：...
  選擇：X
  理由：...

  （Q2-Q6 同格式）

  決策摘要：
  修改：...（或「本輪不修改」）
  ────────────────────────────────

  傳送方式（PowerShell，必須用 UTF-8 位元組陣列，否則中文會變成問號）：
  $TOKEN   = (Get-Content (Join-Path $HOME ".claude/.telegram-config") | Where-Object { $_ -match "^TOKEN=" }) -replace "^TOKEN=",""
  $CHAT_ID = (Get-Content (Join-Path $HOME ".claude/.telegram-config") | Where-Object { $_ -match "^CHAT_ID=" }) -replace "^CHAT_ID=",""
  $msg = "（把完整訊息內容放這裡）"
  $json = @{ chat_id = $CHAT_ID; text = $msg } | ConvertTo-Json -Compress
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
  Invoke-RestMethod -Uri "https://api.telegram.org/bot$TOKEN/sendMessage" -Method Post -ContentType "application/json; charset=utf-8" -Body $bytes

【步驟五】如果探索工具決定修改
  - 修改 ~/.claude/tools/project-kitchen/system-design.md
  - 如需改出題邏輯，修改 cross_subject_bot.py 並 SCP 到 GCP

【步驟六】追加本輪記錄到 GCP
  追加到：/home/yuchi/cognitive-tests/meta_log.md
  格式：
  ## 迭代 #N — [日期時間]
  [本輪六問的簡短摘要]
  [決策結果]

【步驟七】回傳摘要給主要對話視窗（只要 2-3 行）
  格式：「第 N 輪完成。Q1→X（一句話理由），Q5→X（一句話理由）。[有修改/未修改]。已傳 Telegram。」
```

---

## 六個自我檢查問題（完整說明版）

Q1 有沒有什麼值得優化的地方？
  上一輪的行為是否產生預期外的結果？資料分布是否出現偏斜、死鎖或覆蓋不全？

Q2 系統哪些功能值得保留下來？未來會很有用處
  哪些機制現在正常運作，而且未來規模更大時仍然適用？不要因為想優化而破壞這些部分。

Q3 有沒有什麼沒有注意到的問題？
  是否有某個狀態在持續惡化而沒被修正？任何「早就該發現但一直忽略」的警訊？

Q4 有沒有可以降低認知負荷的可能？
  推送的內容是否過量、過密、過雜？有沒有辦法用更少的資訊傳達更清楚的訊息？

Q5 這樣修改後有沒有可能出現什麼問題？
  準備做的改動，會不會讓原本正常運作的部分出問題？有沒有邊緣情況？

Q6 有沒有為各項機制做評分？
  針對每個機制給出 0-10 的評分，說明理由。評分必須有比較基準。

---

## GCP 相關路徑

- 出題程式：`~/.claude/tools/project-kitchen/cross_subject_bot.py`
- 資料庫：`/home/yuchi/cognitive-tests/practice.db`
- 探索記錄：`/home/yuchi/cognitive-tests/meta_log.md`

## Telegram 發送方式（PowerShell，必須用 UTF-8 位元組陣列）

```powershell
$TOKEN   = (Get-Content (Join-Path $HOME ".claude/.telegram-config") | Where-Object { $_ -match "^TOKEN=" }) -replace "^TOKEN=",""
$CHAT_ID = (Get-Content (Join-Path $HOME ".claude/.telegram-config") | Where-Object { $_ -match "^CHAT_ID=" }) -replace "^CHAT_ID=",""
$msg = "訊息內容"
$json = @{ chat_id = $CHAT_ID; text = $msg } | ConvertTo-Json -Compress
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
Invoke-RestMethod -Uri "https://api.telegram.org/bot$TOKEN/sendMessage" -Method Post -ContentType "application/json; charset=utf-8" -Body $bytes
```
