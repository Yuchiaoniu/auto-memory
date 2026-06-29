## Context

全新獨立專案，不依賴任何既有程式碼。目標是在本機執行的輕量學習網站，讓學生讀完每一章後能立即使用對應的筆記、題庫與財務模型，並透過 SQLite 持久化答題紀錄。

## Goals / Non-Goals

**Goals:**
- 單一 Node.js 進程（Express）同時服務 API 與靜態檔案
- SQLite 作為唯一持久層，零配置、零額外服務
- 純 HTML/CSS/JS 前端，無需 build step，開箱即用
- 資料與程式碼分離：新章節只需插入資料，程式碼不動

**Non-Goals:**
- 使用者帳號 / 多人同時使用
- 部署至雲端（純本機）
- 前端框架（React/Vue）
- 圖表庫（用 CSS + SVG 手刻）

## Decisions

### D1：使用 `better-sqlite3` 而非 `sqlite3`
`better-sqlite3` 為同步 API，避免 async/await 混用的複雜度，且效能更佳。對單一使用者本機應用不需要非同步 IO。

### D2：前端以 Fetch API 呼叫 REST 端點，不做 SSR
頁面為靜態 HTML，資料透過 `fetch('/api/...')` 載入並用 JS 動態渲染。
優點：前後端完全分離，之後可獨立替換；缺點：首次渲染需等 JS 執行。

### D3：財務模型用純 CSS + SVG，不引入第三方圖表庫
保持零依賴、零 CDN。圖表為靜態互動（hover/click 展開說明），不需要動態資料綁定。

### D4：資料以 JS 常數檔案 seed，不從外部 JSON 匯入
`database.js` 在初始化時直接以 INSERT 語句植入 ch01 資料，日後加章節只需在同檔案新增 INSERT 區塊，或另建 `seed-ch02.js`。

### D5：目錄結構
```
finance-study-app/
├── server.js          ← Express 入口，掛載 API 路由與 static
├── database.js        ← SQLite 初始化 + seed 資料
├── package.json
├── finance.db         ← 自動生成
└── public/
    ├── index.html     ← 首頁（章節卡片）
    ├── notes.html     ← 筆記
    ├── quiz.html      ← 題庫
    ├── models.html    ← 財務模型
    └── style.css      ← 共用樣式（深色學術風）
```

## Risks / Trade-offs

- **SQLite 並發寫入** → 單使用者本機應用，無此風險
- **資料硬寫在 database.js** → 未來章節多時維護成本上升；屆時可改為從 JSON 檔案匯入
- **無前端路由**：多頁面切換為 `<a href>` 跳頁，不是 SPA；對學習用途已足夠
- **CSS + SVG 手刻圖表** → 彈性低，但維護透明；第一章圖表數量少，可接受
