# auto-memory-sync 任務清單

> 本檔記錄已完成的實作。最終架構與最初的 PostCompact 版本不同，
> 舊版任務保留在最下方「歷史紀錄」供對照。

## 核心架構決策

- [x] A.1 確立原則：「規則」全域共用一份（放 `CLAUDE.md`，手動維護，程式不碰）；
  「記憶」每個專案各自保存一份（各自資料夾的 `STATE.md`，由程式維護）
- [x] A.2 確認自動壓縮會抹掉細節，因此需要在壓縮前先把專案事實存下、壓縮後再念回來

## 1. 壓縮後：自動念回專案狀態（讀取端）

- [x] 1.1 建立 `C:\Users\yuchi\.claude\session-start-inject-state.ps1`
- [x] 1.2 程式從 SessionStart hook 的 stdin JSON 取得 cwd（目前專案資料夾）
- [x] 1.3 程式讀取該資料夾的 `STATE.md` 與 `tasks.md`，印到 stdout 注入接手 Claude 的 context
- [x] 1.4 兩個檔都不存在時程式靜默退出（代表此資料夾不是專案）
- [x] 1.5 在 `settings.json` 掛 SessionStart（matcher = `compact`，timeout 10）
- [x] 1.6 測試壓縮後接手 Claude 能讀到專案最新狀態，不再重新詢問

## 2. 壓縮前：自動存下專案狀態（寫入端）

- [x] 2.1 建立 `C:\Users\yuchi\.claude\pre-compact-memory-save.ps1`
- [x] 2.2 程式從 Stop hook 的 stdin JSON 取得 cwd；無 `tasks.md` 時直接結束，連 Haiku 都不呼叫，省 API 費用
- [x] 2.3 程式找最新的對話逐字稿（.jsonl），抽最近 40 句（USER 留 800 字、ASSISTANT 留 1500 字）
- [x] 2.4 程式實作 token 成長節流：每個逐字稿各自記錄門檻，成長未達 2 萬 tokens 就跳過；新 session 自動歸零基準
- [x] 2.5 程式取得 API key（優先 `ANTHROPIC_API_KEY`，否則讀 `.credentials.json` 的 OAuth token）
- [x] 2.6 程式把既有 `STATE.md` 當底稿，請 Haiku 增修，輸出更新後的完整 `STATE.md`
- [x] 2.7 程式只記具體事實與資料（完成哪個功能、建了哪支腳本、文章寫了哪段、查到的 IP/地址/餘額/數字），不記來回閒聊
- [x] 2.8 程式把結果寫進該專案資料夾的 `STATE.md`，由壓縮後的讀取端念回
- [x] 2.9 在 `settings.json` 掛 Stop（async，timeout 40），背景跑、不卡使用者

## 3. 編碼問題修正（Windows PowerShell 5.1）

- [x] 3.1 修正中文亂碼：`Invoke-RestMethod` 會誤判 API 回應編碼，改用 `Invoke-WebRequest -UseBasicParsing`
  並手動 `[System.Text.Encoding]::UTF8.GetString($resp.RawContentStream.ToArray())` 解碼
- [x] 3.2 寫 `STATE.md` 時用 UTF-8 帶 BOM（`New-Object System.Text.UTF8Encoding $true`），確保中文不亂碼
- [x] 3.3 `.ps1` 腳本本身存成 UTF-8 帶 BOM，避免 PS 5.1 以 Big5 解讀而把中文註解弄壞

## 4. 移除舊版、避免重複扣費

- [x] 4.1 從 `settings.json` 移除舊的 PostCompact hook（原本會額外呼叫一次 Haiku，與新版重複）
- [x] 4.2 確認每輪只剩一次 Haiku 呼叫（Stop hook）

## 5. 其他設定調整

- [x] 5.1 `settings.json` 設 `"verbose": true`，讓使用者看到實際工具動作
- [x] 5.2 `CLAUDE.md` 新增「回答風格」規則：預設只給一個最佳解、回答簡要

## 6. 文件更新

- [x] 6.1 改寫 `C:\Users\yuchi\.claude\docs\memory-mechanism.md` 成現行架構
  （規則全域/記憶各專案、壓縮前存 STATE.md + 壓縮後念回、40 句與 800/1500 字截斷、UTF-8 BOM 與 API 解碼修正、與舊 PostCompact 版的差異）

## 7. 工作流程規則調整（2026-06-09）

- [x] 7.1 CLAUDE.md 修正「提案＋實作模式」：小改動直接追加 tasks.md 實作，不建新 openspec change；只有使用者明確要求或跨系統大改動才走完整 propose→apply
- [x] 7.2 同規則適用其他專案：不在主專案內另外建立子專案，除非使用者明確要求

## 8. PDF 預處理工具（2026-06-09）

- [x] 8.1 安裝 pdfplumber、PyMuPDF、pytesseract、pdf2image
- [x] 8.2 建立 `C:\Users\yuchi\.claude\tools\read_pdf.py`
- [x] 8.3 CLAUDE.md 新增 PDF 讀取觸發規則
- [x] 8.4 測試腳本（文字型 PDF 測試通過；掃描型需 Tesseract，見下方說明）
- [x] 8.5 session-start-menu.ps1 加入 Tesseract PATH 自檢：已安裝但不在 PATH 時自動補入 session 並顯示警告

## 9. 單一視窗多專案管理（子進程模式，2026-06-14）

- [x] 9.1 建立 `C:\Users\yuchi\.claude\tools\spawn-project.ps1`
  - 接受 `-ProjectName`、`-Task`、`-Async` 參數
  - 自動注入目標專案的 STATE.md + tasks.md 作為 prompt context
  - 同步模式：等待子進程完成後印出結果
  - 非同步模式：背景啟動 PowerShell Job，不卡主視窗
  - 子進程完成後 Stop hook 自動更新 STATE.md
- [x] 9.2 建立 `C:\Users\yuchi\.claude\tools\project-dashboard.ps1`
  - 讀取所有 openspec 專案的 tasks.md，統計待辦與已完成數量
  - 顯示各專案狀態總覽（emoji 狀態、待辦數、下一步摘要）
  - 支援 `-PendingOnly` 只顯示有未完成任務的專案
- [x] 9.3 `CLAUDE.md` 新增「子進程多專案管理」規則
  - 說明何時使用 spawn-project.ps1 啟動子進程
  - 說明同步 vs 非同步模式的選擇時機
  - 說明查看所有專案狀態的 dashboard 指令

---

## 10. Project Kitchen 網頁（單視窗多專案 + 金字塔框架，2026-06-14）

- [x] 10.1 建立 `C:\Users\yuchi\.claude\tools\project-kitchen\` 資料夾
- [x] 10.2 建立 `server.py`（Flask 後端：/api/projects、/api/chat SSE 串流、/api/spawn）
- [x] 10.3 建立 `index.html`（爐子總覽 + 展開 + 金字塔 + 串流對話，深色主題）
- [x] 10.4 建立 `start.ps1`（安裝依賴、背景開瀏覽器、前景執行 server）
- [x] 10.5 `CLAUDE.md` 新增 Project Kitchen 啟動指令
- [x] 10.6 端對端測試：server 啟動正常，/api/projects 回傳 22 個專案（HTTP 200），首頁載入 14KB HTML
- [x] 10.7 重構 `/api/chat` 改為 `claude --print` 子進程架構（每輪讀 STATE.md + tasks.md + log.md 最近 8 輪，寫臨時 prompt 檔，pipe 給 claude，回應以 SSE 串流回爐子）
- [x] 10.8 新增 log.md 機制（每個專案各自 log.md，Flask 每輪末尾 append；/api/projects 回傳最近 5 輪供爐子載入歷史）
- [x] 10.9 更新 `index.html`：拖入爐子時從 logTurns 還原歷史（取代原 autoGreet），send() 只傳 userMsg、history 改由 server 端 log.md 管理
- [x] 10.10 log.md 讀取策略改為「讀上一次 [IMPL] 之後的全部輪次」（無上限），確保完整探索記錄傳入子進程
- [x] 10.11 /api/spawn 成功後自動寫入 `## [IMPL] {時間}` 標記，區隔每次實作前後的探索區間
- [x] 10.12 修正 PowerShell pipe 中文亂碼：加 `[Console]::OutputEncoding = UTF8` 確保中文 prompt 正確傳遞給子進程
- [x] 10.13 子進程 prompt 加入 memory.md context（上限 2000 字），補行為規則：查詢具體數值先讀 memory、發現長期資料才寫入
- [x] 10.14 子進程 prompt 補提案規則：確認實作前先把計劃任務寫進 tasks.md [ ] 條目，完成後改 [x]
- [x] 10.15 子進程 prompt 加入 memory.md 搜索索引規則：寫入時更新 `## 索引` 段落（標題+行號）；查詢時先讀索引定位，Grep+Read offset+limit 取段落，不讀整份

## 11. Project Kitchen 子進程 prompt 品質修正（2026-06-14）

- [x] 11.1 加入 psutil watchdog：3 分鐘無回應且無活躍工具子進程時自動終止，UI 顯示警告
- [x] 11.2 修正歷史記錄與當前問題的分隔：用 `===== 歷史記錄 =====` / `===== 現在要回答的問題 =====` 明確框住，
  防止子進程把 log.md 歷史對話誤判成這次的問題

## 12. Project Kitchen UI 三欄佈局重構（2026-06-14）

- [x] 12.1 移除 `<header>` navbar（含重新整理按鈕），釋放垂直空間
- [x] 12.2 新增三欄 `#app` flex 佈局：`#col-left`（專案清單）| `#col-center`（爐子+對話輸入）| `#col-right`（其他爐子）
- [x] 12.3 左欄可收合（◀/▶ 切換按鈕），拖拉調整寬度功能保留
- [x] 12.4 選中爐子時：中欄縮為單爐（`.single`）、另外兩爐移入右欄（`#stoves-right`）；右欄以 `col-hidden` 隱藏直到有選中爐子
- [x] 12.5 右欄可收合（▶/◀ 切換按鈕）
- [x] 12.6 DOM 移動：`updateLayout()` 以 `appendChild()` 在 `#stoves` 與 `#stoves-right` 之間移動爐子元素，保留 onclick 屬性
- [x] 12.7 兩個容器（`#stoves`、`#stoves-right`）均加入 dragover/drop/click 事件監聽，支援右欄爐子點選切換

---

## 歷史紀錄（舊 PostCompact 版本，已被上方架構取代）

- [x] 確認 OAuth token 可用（從 .credentials.json 讀取，成功驗證 API 呼叫）
- [x] 確認 PostCompact hook stdin 格式（JSON 含 summary 欄位）
- [x] 建立 `post-compact-memory-update.ps1`（後續移除，改為 Stop + SessionStart 兩支）
- [x] 實作 stdin 讀取、token 取得、讀既有記憶當 context、Haiku 呼叫、NO_UPDATE 判斷、寫入記憶檔
- [x] 掛 PostCompact hook 並測試（後續因改架構而移除）
