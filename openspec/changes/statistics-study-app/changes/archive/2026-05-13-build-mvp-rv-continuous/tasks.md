## 1. 專案骨架

- [x] 1.1 初始化 `package.json`，加入 dependencies: express, better-sqlite3 v12.9.0（v11 沒有 Node 24 prebuild）
- [x] 1.2 建立目錄結構：`src/`, `public/`, `data/`, `seed/`, `migrations/`
- [x] 1.3 撰寫 `src/server.js`（Express 伺服器、靜態檔案、API 掛載）
- [x] 1.4 撰寫 `src/db.js`（better-sqlite3 連線與 migration 執行）
- [x] 1.5 撰寫 `migrations/001_init.sql`（questions、attempts 兩張表）
- [x] 1.6 撰寫 `src/seed.js`（讀 JSON 寫入 questions 表）
- [x] 1.7 在 `package.json` 加入 scripts: start, seed
- [x] 1.8 撰寫 README.md（安裝、seed、啟動、加題目流程）

## 2. 共用前端框架

- [x] 2.1 建立 `public/index.html` 首頁（導覽列：隨機變數 / 連續型分配）
- [x] 2.2 建立 `public/css/main.css`（基本版型、卡片樣式）
- [x] 2.3 整合 MathJax CDN，測試公式渲染
- [-] 2.4 整合 Chart.js CDN（**改用 vanilla Canvas 自繪**，減少外部依賴、控制更精準）
- [x] 2.5 撰寫共用元件 `public/js/quiz.js`（選擇題顯示與判分邏輯）
- [x] 2.6 撰寫共用元件 `public/js/chart-panel.js`（PDF/CDF 雙圖 + 滑桿）

## 3. 隨機變數章節（content-rv）

- [x] 3.1 建立 `/chapters/random-variables` 頁面骨架
- [x] 3.2 製作「機率分配本質」觀念頁
- [ ] 3.3 製作「Σ 與 ∫ 統一性」動畫頁（按鈕觸發直方圖細分）— MVP 文字版已寫，動畫待補
- [x] 3.4 製作 PMF/PDF/CDF 對比說明
- [ ] 3.5 「離散→連續過渡」動畫實作（柱數翻倍邏輯）— v1 後再做

## 4. 連續型分配章節（content-continuous）

- [x] 4.1 建立 `/chapters/continuous-distributions` 頁面骨架
- [x] 4.2 均勻分配頁：公式、互動圖、區間機率計算
- [x] 4.3 常態分配頁：公式、互動圖
- [ ] 4.4 常態分配的「反查 Z 值」功能 — v1 後再做
- [x] 4.5 指數分配頁：公式、互動圖
- [x] 4.6 無記憶性說明（驗證工具 v1 後再做）

## 5. 互動圖表（interactive-charts）

- [x] 5.1 PDF / CDF 雙圖元件（接受分配類型與參數，輸出圖表）
- [x] 5.2 滑桿元件（含即時數值顯示）
- [x] 5.3 區間機率即時計算（接收 a、b，回傳 P(a ≤ X ≤ b)）
- [x] 5.4 PDF 陰影標示功能（區間查詢時自動標示）
- [x] 5.5 動畫效能（vanilla Canvas，無動畫框架）

## 6. 選擇題引擎（quiz-engine）

- [x] 6.1 題目顯示元件（題幹支援 MathJax）
- [x] 6.2 選項點擊判分（即時變色 + 解析顯示）
- [ ] 6.3 互動參數題型（判定滑桿值是否符合條件）— v1 後再做
- [ ] 6.4 題目列表頁與觀念篩選器 — v1 後再做（目前在章節頁按觀念分組）
- [x] 6.5 撰寫 `seed/questions.json`：6 個觀念 × 5 題 = 30 題
  - [x] 6.5.1 機率分配本質（5 題）
  - [x] 6.5.2 PMF/PDF/CDF（5 題）
  - [x] 6.5.3 均勻分配（5 題）
  - [x] 6.5.4 常態分配（5 題）
  - [x] 6.5.5 指數分配（5 題）
  - [x] 6.5.6 無記憶性（5 題）

## 7. 進度追蹤（progress-tracking）

- [x] 7.1 POST /api/attempts 路由實作
- [x] 7.2 GET /api/progress 路由實作（章節完成度）
- [x] 7.3 GET /api/weak-points 路由實作（薄弱觀念）
- [x] 7.4 章節首頁卡片右上角顯示完成度
- [x] 7.5 `/my/weak-points` 頁面實作

## 8. 後端 API（web-server）

- [x] 8.1 GET /api/questions（含 concept 查詢參數）
- [x] 8.2 GET /api/questions/:id
- [x] 8.3 確保所有 API 回傳一致的 JSON 格式
- [x] 8.4 加入基本錯誤處理（404、500）

## 9. 驗收與收尾

- [x] 9.1 本機完整跑一遍：npm install → seed → start → 答題（curl 驗證通過）
- [x] 9.2 確認三個分配的滑桿都能順暢拖動（待瀏覽器人工驗證）
- [x] 9.3 確認答對答錯記錄都成功寫入 DB
- [x] 9.4 確認「我的弱點」頁面能正確排序（API 已驗證錯誤率高的排前面）
- [x] 9.5 README 內容檢查與更新
- [x] 9.6 將本專案位置與技術棧寫入 Claude memory
- [ ] 9.7 執行 `openspec archive build-mvp-rv-continuous` — 待使用者瀏覽器驗收後再 archive
