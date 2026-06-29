## 1. 後端程式碼

- [x] 1.1 新增 `src/db.py`：init_db()（建表 + 寫入預設帳號 admin/admin123）、get_user()、save_form()、get_forms()
- [x] 1.2 修改 `app.py`：加入 SECRET_KEY、session cookie 設定（SameSite=None/Secure）、呼叫 init_db()
- [x] 1.3 新增 `POST /login` route：驗證帳密、設定 session
- [x] 1.4 新增 `POST /logout` route：清除 session
- [x] 1.5 新增 `GET /history` route：需登入、回傳該使用者的 forms 記錄
- [x] 1.6 修改 `POST /analyze` route：需登入、分析後自動呼叫 create_form()、存入 DB、回傳含 form URLs
- [x] 1.7 新增 `GET /me` route：回傳目前登入的 username（用於頁面重整後的 session 恢復）

## 2. 依賴與設定

- [x] 2.1 `requirements.txt` 加入 `bcrypt>=4.0.0`
- [x] 2.2 `.env` 加入 `SECRET_KEY`（隨機字串）
- [x] 2.3 更新 nginx 設定：/forms/ location 加入 `add_header 'Access-Control-Allow-Credentials' 'true' always`

## 3. 前端

- [x] 3.1 改寫 `index.html`：未登入顯示登入表單（username/password + 登入按鈕），登入後顯示主畫面
- [x] 3.2 登入成功後 fetch `/history` 渲染歷史清單；移除 localStorage 邏輯
- [x] 3.3 `/analyze` 回應改為直接顯示 form URLs，移除「建立 Google 表單」按鈕
- [x] 3.4 加入登出按鈕，呼叫 POST /logout 後回到登入畫面
- [x] 3.5 頁面載入時呼叫 GET /me，有效 session 自動恢復登入狀態

## 4. VM 部署

- [x] 4.1 SCP 所有更新檔案到 VM（app.py、src/db.py、requirements.txt）
- [x] 4.2 VM 建立 `~/form-automation-system/data/` 目錄
- [x] 4.3 SCP nginx 設定並 reload
- [x] 4.4 VM pip install bcrypt，重啟 PM2

## 5. 驗證

- [x] 5.1 外部自檢：未登入 POST /analyze → 401
- [x] 5.2 外部自檢：POST /login → session cookie 設定正確
- [x] 5.3 外部自檢：登入後 POST /analyze → 回傳含 edit_url 的完整結果
- [x] 5.4 端對端 Playwright 測試：登入 → 上傳 → 自動建立表單 → 歷史清單出現 → 重新整理仍保留
