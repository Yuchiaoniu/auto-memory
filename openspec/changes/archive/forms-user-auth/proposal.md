## Why

歷史記錄目前存在 localStorage，只有同一台電腦同一個瀏覽器才看得到，無頭瀏覽器測試的記錄不會出現在使用者的真實瀏覽器。加入後端使用者帳號後，記錄改存 SQLite，任何裝置登入都能看到自己的所有表單。

## What Changes

- 後端加入 SQLite 資料庫（users、forms 兩張表），Flask session 管理登入狀態
- `POST /analyze` 改為：分析完成後自動建立 Google 表單並存入 DB，一次回傳 fields + form URLs
- 新增 `POST /login`、`POST /logout`、`GET /history` endpoint
- `index.html` 改為 SPA：未登入顯示登入表單，登入後顯示分析區 + 歷史清單（從後端讀取）
- 移除 localStorage 歷史邏輯
- 預設帳號：admin / admin123

## Capabilities

### New Capabilities

- `user-auth`: 使用者登入/登出，session 管理
- `forms-db`: 表單記錄持久化到 SQLite，跨裝置可見

### Modified Capabilities

- `analyze-endpoint`: 分析後自動建立表單，回傳包含 form URLs

## Impact

- `app.py`：加入 DB init、login/logout/history route，修改 /analyze
- `src/db.py`：新增（DB 操作封裝）
- `requirements.txt`：加入 `bcrypt`
- `index.html`：SPA 登入/登出流程，移除 localStorage
- VM 建立 `~/form-automation-system/data/` 目錄
