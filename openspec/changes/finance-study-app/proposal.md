## Why

學生在學習財務管理課程時，缺乏一個能整合「筆記、題庫、財務模型」的互動學習工具，導致複習效率低落。此網站讓每讀完一章就能立即累積對應資源，並透過 SQLite 持久化答題紀錄以追蹤學習進度。

## What Changes

- 新建 `finance-study-app/` 專案目錄於課程資料夾下
- 建立 Node.js (Express) 後端伺服器，提供 REST API
- 建立 SQLite 資料庫，儲存章節筆記、題目、答題紀錄
- 建立純 HTML/CSS/JS 前端（四頁：首頁、筆記、題庫、財務模型）
- 植入第一章（財務管理基礎）完整資料：筆記 9 節、選擇題 ≥ 20 題

## Capabilities

### New Capabilities
- `chapter-notes`: 從資料庫讀取並展示各章節結構化筆記，支援章節切換
- `quiz-engine`: 選擇題題庫，支援練習模式（即時對答）與考試模式（全部作答後批改），並將分數記錄至 SQLite
- `financial-models`: 可互動的財務概念視覺化圖表（資產負債表結構、三大領域關係、代理問題流程）
- `api-server`: Express REST API，提供 `/api/chapters`、`/api/notes`、`/api/questions`、`/api/quiz-results` 等端點

### Modified Capabilities
- （無，全新專案）

## Impact

- **新依賴**：`express`、`better-sqlite3`
- **資料庫**：`finance.db`（SQLite），含 `chapters`、`notes`、`questions`、`quiz_results` 四張表
- **部署**：本機執行 `node server.js`，預設 port 3000
- **擴充設計**：所有資料表均以 `chapter_id` 作為外鍵，未來加入新章節只需插入資料，不需修改程式碼
