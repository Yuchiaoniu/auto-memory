# project-kitchen — 長期知識庫

## 專案概況

跨科目學習系統的管理中心與自動迭代優化介面。
包含出題機器人、自我檢查框架、心智模型管理，以及網頁管理介面（project-kitchen 入口）。

**核心目標：** 辨識使用者對每個觀念的心智模型（正確或錯誤），引導向正確路徑，而非只統計答題正確率。

---

## 重要路徑與數值

### GCP 出題機器人
- 主機 IP：35.227.93.38
- 使用者名稱：yuchi
- 金鑰路徑：`C:\Users\yuchi\.ssh\google_compute_engine`
- 出題腳本：`/home/yuchi/cross_subject_bot.py`
- 資料庫：`/home/yuchi/cognitive-tests/practice.db`（SQLite，answers 表）
- 練習日誌：`/home/yuchi/cognitive-tests/practice_log.md`
- 迭代記錄：`/home/yuchi/cognitive-tests/meta_log.md`

### Telegram Bot
- 名稱：My Besu Analyst（@besu_agent_495113_bot）
- Token：8786889760:AAGr_a9mNaAwPG2yyESXnrbkLnkkrJxLsIY
- Chat ID：7006586764（yuchiao niu）

### 本機工具路徑
- 出題腳本本機備份：`C:\Users\yuchi\.claude\tools\project-kitchen\cross_subject_bot.py`
- 迭代啟動說明：`C:\Users\yuchi\.claude\tools\project-kitchen\loop-starter.md`
- 系統設計文件：`C:\Users\yuchi\.claude\tools\project-kitchen\system-design.md`

### 網頁入口
- GCP 網頁終端機：https://forest-carbon.duckdns.org/claude/
- 帳號：claude，密碼：claude2024

---

## 48 個觀念心智模型補充進度

| 科目 | 完成數 | 總數 |
|------|--------|------|
| 財務 | 12 | 12 |
| 統計 | 12 | 12 |
| 心理 | 12 | 12 |
| 英文 | 0  | 12 |
| **合計** | **36** | **48** |

心智模型格式：正向錨定（使用者應建立的正確理解）＋常見錯誤路徑一、二。
完整描述存放於 system-design.md 的「心智模型框架」段落。

---

## 重大架構決策記錄

### 2026-06-28：改採路徑＋錨定架構

捨棄「答對率統計」作為自我檢查中心，改為「心智模型偵測」：
- 每個觀念設計正向錨定（正確理解）
- 每個觀念設計常見錯誤路徑（使用者最容易犯的錯誤認知形式）
- 系統目標：讓使用者從錯誤路徑走向正向錨定，而非讓答對率提高到某個數字

### 2026-06-29：fork 子代理改為一般 Sonnet 子代理

fork 子代理繼承完整對話脈絡，會把完整探索輸出傳回主要對話視窗，且會自行排程下一輪。
改用一般 Sonnet 子代理（不繼承歷史），完整內容走 Telegram 通道，主要對話只收摘要。

### 2026-06-29：Telegram 傳送必須用 UTF-8 位元組陣列

PowerShell 用 `Invoke-RestMethod` 傳送 JSON 時，預設不使用 UTF-8，中文會顯示為問號。
修正方式：
```powershell
$json = @{ chat_id = $CHAT_ID; text = $msg } | ConvertTo-Json -Compress
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
Invoke-RestMethod -Uri "https://api.telegram.org/bot$TOKEN/sendMessage" -Method Post -ContentType "application/json; charset=utf-8" -Body $bytes
```
