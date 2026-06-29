## Context

學習者是統計學在學學生（非軟體工程師背景），目標是用網站工具強化記憶。本機開發，單一使用者，不需多人或公開部署。已存在 `finance-study-app` 專案採用 Node.js + SQLite，本專案沿用同套架構降低學習成本。

## Goals / Non-Goals

**Goals:**
- 跑得起來、能用：`npm start` 後開瀏覽器即可使用
- 三種互動：閱讀觀念 / 拖滑桿看圖 / 做選擇題
- 答錯題目能被「標記」，下次優先重出
- 程式碼結構簡單，未來複製到其他章節時只需要新增資料、不用改框架

**Non-Goals:**
- 不做使用者註冊、不做雲端同步、不做行動裝置 App
- 不寫單元測試（個人專案，先以「能跑」為主）
- MVP 階段不做題庫管理介面（直接編輯 seed 檔加題目）
- 不支援 LaTeX 編輯器，純前端用 MathJax 渲染預寫好的公式

## Decisions

### 決策 1：後端用 Express + better-sqlite3

**選擇**：Express 4 + better-sqlite3 同步 API。

**理由**：
- Express 是 Node.js 最熟知的框架，文件多
- better-sqlite3 比 sqlite3 簡單（同步 API，不用 callback），效能也好
- 單機應用不需要連線池、不需要非同步擴展

**替代方案**：
- Next.js / Remix — 框架重，對單機學習工具是 over-engineering
- 純前端 + IndexedDB — 沒後端，但題庫管理不便；未來想加管理頁面會卡

### 決策 2：前端用 vanilla JS + Chart.js + MathJax

**選擇**：純 HTML/CSS/JS，視覺化用 Chart.js，公式用 MathJax CDN。

**理由**：
- 不引入 React/Vue 學習成本，重點是「學統計」不是「學前端框架」
- Chart.js 對基礎統計圖表（PDF、CDF、直方圖）完全足夠
- MathJax 寫公式 $f(x) = \frac{1}{\sigma\sqrt{2\pi}}e^{-(x-\mu)^2/(2\sigma^2)}$ 直接渲染漂亮

**替代方案**：
- D3.js — 更強大但學習曲線陡，MVP 不需要
- KaTeX — 比 MathJax 快但相容性差一點

### 決策 3：題庫先用 JSON seed，未來再上 SQLite

**選擇**：MVP 將題目放 `seed/questions.json`，啟動時讀入 SQLite。

**理由**：
- 用 JSON 直接編輯比寫 SQL INSERT 快
- 啟動時 seed 進 DB，後續答題記錄寫 DB，分工清楚
- 未來要做題庫管理介面時，DB 已準備好

### 決策 4：互動圖表的核心三件套

**選擇**：每個分配的互動頁面都有三個固定元件：
1. **參數滑桿區**（μ, σ, λ, a, b 等可調）
2. **PDF/CDF 雙圖**（左 PDF、右 CDF，同步更新）
3. **即時計算區**（顯示當前 E(X), Var(X), 以及 P(a ≤ X ≤ b) 的查詢框）

**理由**：
- 統一介面減少前端工作量
- 學生看每個分配都用同樣框架，降低認知負擔
- 第三件「即時計算區」直接連結到考試題型

### 決策 5：選擇題判分採前端即時 + 後端記錄

**選擇**：點選項立刻在前端顯示對錯與解析，背景非同步 POST 給後端記錄。

**理由**：
- 前端即時回饋對學習動機很重要
- 後端記錄不阻塞 UI
- 失敗也只是記錄丟失，不影響本次學習

## Risks / Trade-offs

- **風險：MathJax CDN 載入慢** → 緩解：MathJax 設定 `tex-svg.js` 較輕量版本；公式不過於密集
- **風險：Chart.js 動畫更新過於頻繁滑桿卡頓** → 緩解：用 `requestAnimationFrame` 節流，動畫關閉（`animation: false`）
- **風險：題庫太少很快做完失去意義** → 緩解：MVP 每個觀念至少 5 題，後續可持續新增
- **權衡：不寫測試** → 接受。個人專案、單機使用、出錯不致命；如未來開放給他人使用再補

## Migration Plan

無遷移（新專案）。但需處理「種子題庫」初始化：

1. 安裝後執行 `npm run seed` 將 `seed/questions.json` 寫入 SQLite
2. 已答題記錄表（attempts）建好但不預填
3. Rollback 直接 `rm data/app.db && npm run seed` 即可

## Open Questions

- 題目要分難度等級嗎？（暫不做，所有題目同級）
- 互動圖表要支援匯出截圖嗎？（暫不做，未來再評估）
- 是否要支援「離散→連續」動畫過渡？這是學習專案中討論到的核心觀念之一（**MVP 嘗試做，作為亮點功能**）
