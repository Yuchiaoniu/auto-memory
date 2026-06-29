# Project Kitchen 系統日誌

每次對話、迭代、重大決策都記錄於此。
格式：日期 → 事項 → 結果/學到的事。

---

## 2026-06-28

### 入口網站部署（niuyuchiao.duckdns.org）
- 建立 nginx site、申請 Let's Encrypt TLS
- 問題：DuckDNS 指向錯誤 IP（220.143.85.25 非 35.227.93.38）→ 更新正確 token 解決
- 問題：`/home/yuchi/project-kitchen/` 目錄權限 700，nginx 無法穿越 → 加 `o+x` 解決
- 結果：`https://niuyuchiao.duckdns.org/` 正常，HTTP 200

### Telegram Bot 建立
- Token：REDACTED_TELEGRAM_TOKEN
- Chat ID：7006586764（yuchiao niu）
- Bot 名稱：My Besu Analyst（@besu_agent_495113_bot）

### 認知強化 Bot — 第一輪迭代（30 輪）
- 時間：03:28–05:54，共 30 輪，每 5 分鐘一輪
- **重大缺陷發現**：
  1. `pick_subject()` 死鎖：stats 第一輪被選後，永遠是「已測中最弱」，finance/accounting 從未被選（29 輪全測 stats）
  2. 階段轉換依迭代次數而非覆蓋率，第 8 輪就進入「獲取」但基準未完整建立
  3. 缺少元分析層（metacognition），無法跨輪偵測自身行為異常
  4. 最小可行測試只驗證「執行能力」，未驗證「邏輯正確性」
- **學到的事**：
  - 設計時必須做邊界條件思考（只有一科有資料時會發生什麼）
  - 最小可行測試應連跑 3 輪確認全科輪流覆蓋
  - 啟動後需有早期預警（3 輪內偵測覆蓋缺口）

### GCP Claude CLI 誤判事件
- 用 `which claude`（非互動式 SSH）→ 回傳 not found → 誤判未安裝 → 執行不必要的 npm install
- 根本原因：非互動式 SSH 的 PATH 不含使用者目錄，`which` 視野不完整
- 實際狀況：Claude CLI 已在 tmux 裡運行 85 小時，ttyd 服務自 6/2 起正常運行
- 修正：建立「三層查驗」規則並寫入 rules/self-check.md

### 自檢規則更新
- 新增 `C:\Users\yuchi\.claude\rules\self-check.md`
- 內容：三層查驗原則、自動迭代優化自檢流程、探索模式要求、VM 驗證規範
- CLAUDE.md 對應段落縮為觸發規則（3 行），指向 rules/self-check.md

### GCP Web Terminal 確認
- URL：https://forest-carbon.duckdns.org/claude/
- 帳號：claude，密碼：claude2024
- 狀態：HTTP 200，ttyd 服務正常，Claude CLI 在 tmux session 中持續運行

---

## 2026-06-28（續）

### 自檢規則升級 — 六問自檢框架

- 把原本三問（優化、保留、累積問題）升級為六問
- 新增：Q4 降低認知負荷、Q5 跨時間宏觀視角、Q6 機制評分（0–10 分）
- 更新位置：`C:\Users\yuchi\.claude\rules\self-check.md`（自動迭代優化段落）

### 設計演化 Bot v1.0 啟動

- 腳本：`/home/yuchi/design_evolution_bot.py`（PID 4138441，nohup 背景執行）
- 輸出：`/home/yuchi/cognitive-tests/design_log.md`（每輪 append）
- 狀態：`/home/yuchi/cognitive-tests/design_state.md`（版本化更新）
- 主題：跨科目學習系統設計（push / analytics / briefing / cognitive load）
- 節奏：每 5 分鐘一輪，六問自檢 + 跨時間宏觀視角 + 版本號控制

**設計演化 Bot 已停止（07:52 前）**，改為跨科目學習 Bot v2.0。

**設計演化 Bot 第一輪結果（07:24，v0.0 → v0.1）：**
- 平均評分：1.6/10（基準期，大量機制尚未設計）
- 確立三個最高優先缺口：pick_subject 死鎖修復、答題回收機制、學習狀態持久化
- 核心決策：答題採 Telegram inline button；推送觸發方式為排程（cron）
- 識別跨時間風險：無持久化則 100 使用者後需要 key-value store

### 跨科目學習 Bot v2.0 啟動（07:52）

- 腳本：`/home/yuchi/cross_subject_bot.py`（PID 4141643，nohup -u 背景執行）
- 日誌：`/home/yuchi/cognitive-tests/practice_log.md`（統一 append，含實作備忘）
- 實作清單：`/home/yuchi/cognitive-tests/impl_items.md`（每 5 輪 META 更新）
- 狀態：`/home/yuchi/cognitive-tests/practice_state.json`（重啟不遺失）
- 科目：finance / psychology / stats / toefl（輪流輪詢，確保四科均等覆蓋）
- 節奏：10 分鐘一輪；每 5 輪六問全分析 + Claude 識別實作項目
- 實作項目記錄機制：每次 META 識別出的實作待辦同步寫入 impl_items.md

---

## 2026-06-29

### 對話架構重設 — fork 子代理改為一般 Sonnet 子代理

**問題：** fork 子代理（繼承完整對話脈絡）會：
1. 把完整探索輸出傳回主要對話視窗（應只傳 2-3 行摘要）
2. 自行排程下一輪 ScheduleWakeup（只有主對話應排程）

**根本原因：** fork 子代理看到歷史中的排程呼叫記錄，就會複製該行為。

**解法：** 改用一般 Sonnet 子代理（無歷史繼承），完整探索結果走 Telegram 通道，主對話只收摘要。已更新 loop-starter.md。

---

### Telegram 中文亂碼修正

**問題：** 傳到 Telegram 的中文顯示為問號。

**根本原因：** PowerShell 用 `Invoke-RestMethod` 傳送 JSON 時，預設不使用 UTF-8 編碼。

**解法：** 用 `[System.Text.Encoding]::UTF8.GetBytes($json)` 產生位元組陣列，並指定 `ContentType "application/json; charset=utf-8"`。輪次 7 之後確認中文顯示正常。

---

### 心智模型補充授權確認

使用者明確授權 Claude 可以自行為 48 個觀念補充心智模型描述（正向錨定＋常見錯誤路徑），以心理學專案的路徑＋錨定架構為主軸，不需等待人工介入。已寫入記憶檔。

輪次 12-14 進度：財務 12/12、統計 12/12、心理 12/12，共 36/48。英文 0/12 待設計框架。

---

### GitHub → GCP 同步機制討論（未實作）

討論方向：
- project-kitchen 資料夾上傳 GitHub（含 system-design.md、loop-starter.md、cross_subject_bot.py 等）
- GCP 設定 git pull 機制，本機發指令後 GCP 拉取最新版並執行
- 優點：迭代優化在 GCP 上執行，不受本機休眠影響
- GCP 計費：依虛擬機器運行時間，與迭代頻率無直接關係

尚未實作，下次繼續。

---

### 專案標準四檔結構規則（新規則）

確認所有新專案必須建立四個標準檔案：
- **log.md**：最近 20 條完整對話流水帳（使用者訊息 + Claude 回應）
- **state.md**：進行中現況與近期進展脈絡
- **memory.md**：重要數值資料、專案概況、歷年重大修改記錄
- **tasks.md**：任務清單

規則已寫入記憶系統（feedback_project_file_structure.md），本檔（log.md）為 project-kitchen 補建。

---

## 2026-06-29（續）

### GitHub 歷史記錄清理

Telegram Bot Token 曾明文出現在舊提交（`25428f9`）的 loop-starter.md 裡，GitHub Secret Scanning 發送警告信。
使用 git-filter-repo 把整條歷史中的明文 token 替換成 `REDACTED_TELEGRAM_TOKEN`，強制推送到 GitHub，警告已解除。

---

### GCP 推送 GitHub 憑證設定（今日完成）

從 Windows 憑證管理員取出本機已存的 GitHub OAuth token，透過 SSH 設定到 GCP 的 git remote URL。
GCP 現在可以直接執行 `git push origin main`，不需要額外輸入憑證。
同時修正了 force push 後 GCP 歷史記錄與 GitHub 不同步的問題（執行 `git fetch && git reset --hard origin/main`）。

---

### 學習系統迭代分析（第 17～28 輪，全部今日完成）

**關鍵數字：** 40 次答題、正確率 32.5%、38/48 觀念已接觸、0 個已掌握、6 個待加強。

**本輪系統自行修復的項目：**
- 第 17 輪：修正 pick_question 這個函式（負責選題）的 intro_done 積壓邏輯
- 第 18 輪：加入 almost_mastered 這個優先池（優先讓快達到掌握門檻的觀念出題）
- 第 21～22 輪：stats 指令加入 almost_mastered 和 weak_concepts 欄位
- 第 26 輪：query_concept_stats 這個統計查詢函式加入 30 天有效期過濾

**第 28 輪發現的根本性格式限制（最重要）：**
所有題目為開放問答，系統只能知道對錯，無法辨識使用者持有哪種錯誤心智模型。
CLT（中央極限定理）、Bandwagon Effect（從眾效應）、CorrVsCause（相關與因果混淆）等偏弱觀念
各有多種常見誤解路徑，但現行格式完全無法區分。

---

### 待實作任務：出題系統改為多選題格式

**背景：** 第 28 輪確認的根本性限制。

**具體修改項目：**
1. 在每個題目加入四個選項（一個正確答案＋三個錯誤選項）
2. 每個錯誤選項對應一條具體的錯誤心智模型路徑
3. 修改資料庫 schema，在題目資料表新增 options_json 欄位（儲存四個選項及對應的心智模型標籤）
4. 修改答題記錄資料表，新增 selected_option 欄位（記錄使用者選了哪個選項，不只記對錯）
5. 修改 Telegram 推送格式，用 inline button 顯示四個選項
6. 完成後執行 `git add && git commit && git push origin main`，並傳 Telegram 通知說明改了哪些檔案

**相關檔案：**
- 出題程式：`~/.claude/tools/project-kitchen/cross_subject_bot.py`
- 資料庫：`/home/yuchi/cognitive-tests/practice.db`
- 系統設計說明：`~/.claude/tools/project-kitchen/system-design.md`

確認所有新專案必須建立四個標準檔案：
- **log.md**：最近 20 條完整對話流水帳（使用者訊息 + Claude 回應）
- **state.md**：進行中現況與近期進展脈絡
- **memory.md**：重要數值資料、專案概況、歷年重大修改記錄
- **tasks.md**：任務清單

規則已寫入記憶系統（feedback_project_file_structure.md），本檔（log.md）為 project-kitchen 補建。

---
