# 自動迭代啟動說明

## 啟動指令

在 Claude Code 輸入以下指令即可啟動自動迭代：

```
/loop 出題系統自動迭代自我檢查
```

---

## 每次迭代的執行流程

所有重工作由 Sonnet 子代理在內部完成，完整探索結果傳送到 Telegram，
主要對話視窗只收 2-3 行摘要，避免對話視窗被塞滿而觸發壓縮。

### 步驟一：啟動 Sonnet 子代理

用 Agent(model: "sonnet") 啟動子代理，子代理在內部完成以下七個步驟（完整 prompt 見下方）。

### 步驟二：記錄摘要

主要對話視窗只記錄子代理回傳的 2-3 行摘要。

### 步驟三：排程下一輪

呼叫 ScheduleWakeup，1200 秒後繼續下一輪，prompt: `出題系統自動迭代自我檢查`
（第 50 輪決策：intro_pending=0 後主要瓶頸是「使用者是否啟動互動模式」，非資料累積速度，間隔從 600 秒拉長至 1200 秒）

---

## 子代理 prompt 範本

你是迭代自我檢查子代理，在 GCP Linux 環境執行。請執行以下七個步驟，不要詢問使用者，全部自行完成。
所有輸出（Telegram 訊息、回傳摘要）一律用白話中文，禁止使用縮寫或技術術語。

【步驟一】取得觀念統計
  直接執行（不需要 SSH）：
  python3 ~/.claude/tools/project-kitchen/cross_subject_bot.py stats

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
  Q1（值得改進）選項A... 選項B... 選擇X 理由...
  （Q2-Q6 同格式）
  決策摘要：修改...（或「本輪不修改」）
  ────────────────────────────────

  傳送方式（Python）：
  python3 -c "
import requests, os
cfg = dict(l.strip().split('=',1) for l in open(os.path.expanduser('~/.claude/.telegram-config')) if '=' in l)
requests.post(f'https://api.telegram.org/bot{cfg[\"TOKEN\"]}/sendMessage', json={'chat_id': cfg['CHAT_ID'], 'text': MSG})
"
  （把 MSG 換成實際訊息字串）

【步驟五】如果探索工具決定修改
  修改 ~/.claude/tools/project-kitchen/system-design.md
  如需改出題邏輯，修改 ~/.claude/tools/project-kitchen/cross_subject_bot.py

【步驟六】追加本輪記錄到 meta_log.md
  追加到：/home/yuchi/cognitive-tests/meta_log.md
  格式：## 迭代 #N — [日期時間] / [六問摘要] / [決策結果]

【步驟七】回傳摘要給主要對話視窗（只要 2-3 行）
  格式：「第 N 輪完成。Q1→X（理由），Q5→X（理由）。[有修改/未修改]。已傳 Telegram。」

---

## GCP 相關路徑

- 出題程式：~/.claude/tools/project-kitchen/cross_subject_bot.py
- 資料庫：/home/yuchi/cognitive-tests/practice.db
- 探索記錄：/home/yuchi/cognitive-tests/meta_log.md
- 系統設計說明：~/.claude/tools/project-kitchen/system-design.md