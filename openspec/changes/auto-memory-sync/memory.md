# auto-memory-sync — 長期查詢／對照資料

## GitHub repo

- 腳本上傳位置：`https://github.com/Yuchiaoniu/pre-compact-memory-save.git`
- 本機乾淨 repo 資料夾：`C:\Users\yuchi\pre-compact-memory-save\`
- 內含檔案：`pre-compact-memory-save.ps1`、`session-start-inject-state.ps1`、
  `session-start-menu.ps1`、`CLAUDE.global.md`（全域 CLAUDE.md 備份）、`README.md`、`.gitignore`

## 腳本實際位置（生效中，皆在 C:\Users\yuchi\.claude\）

- 寫入端：`pre-compact-memory-save.ps1`（Stop hook，async）——更新該專案 memory.md 與 STATE.md
- 壓縮後讀取端：`session-start-inject-state.ps1`（SessionStart matcher=`compact`）——自動接續上次專案，不列選單
- 啟動/清空選單：`session-start-menu.ps1`（SessionStart matcher=`startup|clear`）——
  非專案位置時列出 openspec 全部專案請使用者選；若在專案資料夾啟動則直接念回該專案三檔
- 指標檔：`last-active-project.txt`（記錄上次作用中的專案完整路徑）

## 關鍵設定（settings.json）2026-06-09 更新

- `autoCompactEnabled = true`（已重新啟用自動壓縮，context 達 170000 tokens 時觸發）
- `autoCompactWindow = 170000`（壓縮門檻）
- `verbose = false`（工具執行只顯示摘要，不展開完整輸出）
- `permissions.allow` 含：PowerShell、Bash、Read、Write、Edit、Glob、Grep、WebFetch
- SessionStart 兩個入口：matcher=`compact` → inject-state；matcher=`startup|clear` → menu
- Stop hook：cache-check.ps1（timeout 10）＋ pre-compact-memory-save.ps1（timeout 40, async）
- 寫入端節流門檻：對話成長 20000 tokens 才存一次

## PreToolUse 封鎖清單（settings.json）2026-06-07 新增

主對話以下工具全部封鎖，強制走子代理（Agent, model: haiku）：
- 檔案搜尋工具（Glob）
- 內容搜尋工具（Grep）
- 網頁抓取工具（WebFetch）

子代理內部呼叫不受封鎖影響。

## CLAUDE.md 全域規則重要變動（2026-06-07）

- openspec-propose 完成後，不等使用者確認，直接呼叫 opsx:apply 進行實作
- 純中文敘述句中，工具名稱（Read、WebFetch、Bash 等）禁止直接作主詞或受詞；
  必須先用白話中文描述功能，原始名稱以括號補充。
  例：「要不要委派這個讀取動作（Read）」，不得寫「這個 Read 要不要委派」

## 三檔分工約定

- tasks.md = 主要進度；memory.md = 長期查詢/對照資料；STATE.md = 精簡現況快照
- 存檔時把 STATE.md 的長期資料搬進 memory.md，再從 STATE.md 剔除，防止 STATE.md 臃腫
- 機密（.credentials.json 等）由 .gitignore 擋下，不上傳

## memory.md 載入策略（2026-06-02 更新）

- 開啟專案時**只載入** tasks.md + STATE.md，不再自動載入 memory.md
- 需要查詢具體數值（IP、設定值、決策結論等）時，先用 Grep 掃描 memory.md 找相關段落，再用 Read 只讀那幾行
- 此規則已同步到：session-start-inject-state.ps1、session-start-menu.ps1、CLAUDE.md

## 已知平台限制

- 腳本無法在使用者打字前主動開口；啟動/clear 後需使用者先送任一則訊息，第一則回覆才會跳出專案選單
- 腳本與 Claude 都無法自動執行 `/clear`，clear 一定由使用者親手按
- 對話中看不到精確 token 數，「建議 clear」只能靠回合數與內容粗估，無精確數字門檻
- Read 和 Bash 無法靠 hook 強制委派（hook 在執行前觸發，無法預知輸出大小）；仍靠 CLAUDE.md 規則約束

## PDF 預處理工具（2026-06-09 建立）

- 腳本位置：`C:\Users\yuchi\.claude\tools\read_pdf.py`
- 使用方式：`python C:\Users\yuchi\.claude\tools\read_pdf.py "<路徑>" [--pages 1-5] [--mode auto|text|ocr]`
- auto 模式（預設）：PyMuPDF 偵測是否含文字 → 文字型走 pdfplumber，掃描型走 OCR
- 已安裝套件：pdfplumber、PyMuPDF、pytesseract、pdf2image、Pillow
- Tesseract OCR v5.4.0：已安裝於 `C:\Program Files\Tesseract-OCR\`，繁體中文語言包（chi_tra）已就緒
  - 注意：安裝時未自動加入 PATH；已手動加入使用者 PATH（下次新 session 自動生效）
  - 腳本內部有 `find_tesseract()` 備援，即使 PATH 未更新也能找到 exe

## 環境相依性自檢（session-start-menu.ps1，2026-06-11 新增）

- 每次啟動或 /clear 後自動執行
- 目前檢查項目：Tesseract 是否在 PATH（已安裝但不在 PATH → 自動補入 session + 顯示警告）
- 若要新增其他檢查，在 `session-start-menu.ps1` 的 `$envWarnings` 區塊追加即可

## 同步注意

- 腳本改動後，需複製到 `C:\Users\yuchi\pre-compact-memory-save\` 再 git commit/push 才會同步到 GitHub
- 設定改動後需重開分頁才生效（hook 設定在 claude 啟動那刻載入）
- GitHub 最新 commit：9cc34a3（session-start 加入環境自檢，2026-06-11）

## token-cost-optimizer 變更（已完成）

- `autoCompactWindow` 已調整為 170000（token-cost-optimizer 設為 80000，後因重新啟用 autoCompact 改為 170000）
- `cache-check.ps1` 三級警示：
  - 綠燈：cache_read < 5M → 靜默退出
  - 黃燈：cache_read 5M–10M → 建議存檔訊息
  - 紅燈：cache_read > 10M → 強烈警告
- `token-stats.ps1` 新增：
  - `CLAUDE_NTD_RATE` 環境變數（預設 32）
  - 「Today Total」區塊：彙整當天所有 session 的 cache_read、output、NT$

## Subagent Isolation Policy（CLAUDE.md，token-cost-optimizer 新增）

主要規則：
- 任何 Glob 或 Grep 若不針對單一已知路徑 → 強制用 Agent（Explore/Haiku）
- 搜尋結果超過 100 行 → 強制用 Agent
- 已知單一路徑的 Read 可在主 session 直接執行
- subagent 回傳只能是摘要，不貼完整原始輸出

## 部署相關規則（CLAUDE.md，2026-06-09 新增）

### VM 部署自檢要求
- 每次部署或更新服務到 VM 後，必須從外部 IP 或公開 URL 驗證服務可達
- 嚴禁只做 `curl localhost`——localhost 通過不代表外部可達

### API 服務加強版：測試矩陣自檢
- 部署含 REST API 的服務後，自檢前必須先列出端點 × Method × 驗證情境矩陣
- 必須覆蓋所有對外 method（GET/POST/OPTIONS/授權邊界等），全部通過才算完成

### GitHub Pages 部署位置規則
- 預設使用 main 分支根目錄，不使用 docs 資料夾
- 有特殊原因時需先與使用者討論確認

## 已完成變更清單（所有歸屬 auto-memory-sync 的歷史變更）

| 變更名稱 | 主要內容 |
|---|---|
| add-data-grammar-example | CLAUDE.md 補充數字資料型反例與正例 |
| fix-state-md-grammar | STATE.md 語法修正（「已知限制」→「我們已經知道的限制」） |
| reduce-verbosity-subagent-grammar | verbose=false；單字動詞禁縮略規則 |
| enforce-glob-grep-subagent | PreToolUse hook 封鎖 Glob\|Grep |
| enforce-style-and-subagent | 工具名稱白話規則；PreToolUse hook 封鎖 WebFetch |
| claude-strict-workflow-rules | OpenSpec 模式切換強制規則；全域設定歸屬規則 |
| auto-apply-after-propose | propose 完成後直接 apply，不等確認 |
| claude-md-deploy-rules | VM 外部自檢規則；GitHub Pages main 根目錄規則 |
| api-deploy-test-matrix | API 服務部署測試矩陣規則 |
| token-cost-optimizer | autoCompactWindow=80000；三級警示；token-stats.ps1；Subagent Isolation Policy |