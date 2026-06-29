## ADDED Requirements

### Requirement: Express 伺服器與靜態檔案

系統 SHALL 提供 Express 伺服器，預設監聽 port 3000，serve `public/` 為靜態前端、`/api/*` 為 JSON API。

#### Scenario: 啟動伺服器

- **WHEN** 執行 `npm start`
- **THEN** 終端顯示 `Server listening on http://localhost:3000`，瀏覽器開啟該網址可看到首頁

### Requirement: SQLite 連線與初始化

系統 SHALL 使用 better-sqlite3 連線至 `data/app.db`，啟動時若 DB 不存在則自動建立並執行 schema migration。

#### Scenario: 首次啟動建 DB

- **WHEN** 第一次執行 `npm start`，且 `data/app.db` 不存在
- **THEN** 系統自動建立檔案、執行建表 SQL、log「Database initialized」

### Requirement: 題庫 Seed 腳本

系統 SHALL 提供 `npm run seed` 指令，將 `seed/questions.json` 的題目寫入 questions 資料表（先清空再插入）。

#### Scenario: 重新 seed 不重複

- **WHEN** 連續執行 `npm run seed` 兩次
- **THEN** 題目數量保持原始 JSON 中的筆數，不會翻倍

### Requirement: 核心 API 路由

系統 SHALL 提供以下 REST API：
- GET /api/questions?concept=<id>：依觀念取題目
- GET /api/questions/:id：取單題詳情
- POST /api/attempts：提交作答
- GET /api/progress：取得章節完成度
- GET /api/weak-points：取得薄弱觀念

#### Scenario: 依觀念取題

- **WHEN** GET /api/questions?concept=normal
- **THEN** 回傳 200 與該觀念的所有題目 JSON 陣列

#### Scenario: 提交作答

- **WHEN** POST /api/attempts 含 question_id, selected_option
- **THEN** 後端寫入 attempts，回傳 200 與 `{ is_correct: true|false, explanation: "..." }`

### Requirement: 專案啟動文件

系統 SHALL 在專案根目錄提供 README.md，說明：（1）安裝指令、（2）seed 指令、（3）啟動指令、（4）資料庫位置、（5）如何新增題目。

#### Scenario: README 內容

- **WHEN** 開啟 README.md
- **THEN** 至少涵蓋上述五個段落，且每段都有對應指令範例
