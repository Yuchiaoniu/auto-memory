## REMOVED Requirements

### Requirement: Express 伺服器與靜態檔案

**Reason**：靜態化後不再需要 Node.js 伺服器。GitHub Pages 直接 serve 靜態檔案；本機開發改用 `npx serve` 或 VS Code Live Server。

**Migration**：刪除 `src/server.js`、`package.json`、`package-lock.json`、`node_modules/`。

### Requirement: SQLite 連線與初始化

**Reason**：不再有資料庫。

**Migration**：刪除 `src/db.js`、`migrations/`、`data/app.db*`。

### Requirement: 題庫 Seed 腳本

**Reason**：題庫直接以靜態 JSON 提供，無需 seed 動作。

**Migration**：刪除 `src/seed.js`、`seed/questions.json`；題庫搬到 `data/questions.json`。

### Requirement: 核心 API 路由

**Reason**：所有功能改為前端處理。

**Migration**：刪除整份 `/api/*` 實作。前端對應改動：
- 取題：改 fetch 本地 `data/questions.json`
- 作答：前端直接以 correct_index 判分
- 進度與弱點：功能整體移除

### Requirement: 專案啟動文件

**Reason**：不再有 npm 啟動流程，文件改寫為「靜態網站啟動與部署」（已併入 static-site capability 的 README requirement）。

**Migration**：README 改寫，原內容以「靜態站」版本取代。
