## ADDED Requirements

### Requirement: 提供章節列表 API
系統 SHALL 提供 `GET /api/chapters` 端點，回傳所有章節的 id、title、summary。

#### Scenario: 取得章節列表
- **WHEN** 客戶端 GET `/api/chapters`
- **THEN** 系統回傳 JSON 陣列，每筆含 `id`、`title`、`summary`，HTTP 200

### Requirement: 提供筆記 API
系統 SHALL 提供 `GET /api/notes?chapter_id=<n>` 端點，回傳指定章節的所有筆記節。

#### Scenario: 取得指定章節筆記
- **WHEN** 客戶端 GET `/api/notes?chapter_id=1`
- **THEN** 系統回傳該章節所有筆記，每筆含 `section_title`、`content`，HTTP 200

#### Scenario: 章節不存在
- **WHEN** 客戶端 GET `/api/notes?chapter_id=999`
- **THEN** 系統回傳空陣列，HTTP 200

### Requirement: 提供題目 API
系統 SHALL 提供 `GET /api/questions?chapter_id=<n>` 端點，回傳指定章節題目。

#### Scenario: 取得指定章節題目
- **WHEN** 客戶端 GET `/api/questions?chapter_id=1`
- **THEN** 系統回傳題目陣列，每筆含 `id`、`question`、`option_a/b/c/d`、`correct_answer`、`explanation`，HTTP 200

### Requirement: 記錄答題結果 API
系統 SHALL 提供 `POST /api/quiz-results` 端點，接受 `chapter_id`、`score`、`total`，儲存至 SQLite 並回傳新建紀錄。

#### Scenario: 成功記錄答題結果
- **WHEN** 客戶端 POST `/api/quiz-results` 帶有合法 JSON body
- **THEN** 系統插入一筆紀錄並回傳 `{ id, chapter_id, score, total, timestamp }`，HTTP 201

### Requirement: 提供答題歷史 API
系統 SHALL 提供 `GET /api/quiz-results?chapter_id=<n>` 端點，回傳最近 10 筆答題紀錄，依時間降冪排序。

#### Scenario: 取得答題歷史
- **WHEN** 客戶端 GET `/api/quiz-results?chapter_id=1`
- **THEN** 系統回傳最多 10 筆紀錄，每筆含 `score`、`total`、`timestamp`，HTTP 200

### Requirement: 靜態檔案服務
系統 SHALL 將 `public/` 目錄下所有檔案作為靜態資源服務，根路徑 `/` 對應 `public/index.html`。

#### Scenario: 存取首頁
- **WHEN** 瀏覽器 GET `/`
- **THEN** 伺服器回傳 `public/index.html`，HTTP 200
