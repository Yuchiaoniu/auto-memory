## 1. 程式碼修改

- [x] 1.1 新增 `gas/create_form.js`：GAS doPost handler，支援七種欄位類型，回傳 {form_id, edit_url, respond_url, error}
- [x] 1.2 改寫 `src/forms_creator.py`：移除所有 google-api-python-client 邏輯，改為 requests.post 呼叫 GOOGLE_FORMS_GAS_URL；URL 未設定時直接回傳 error
- [x] 1.3 更新 `requirements.txt`：移除 google-auth-oauthlib、google-api-python-client、google-auth；確認 requests 存在（若無則加入）
- [x] 1.4 刪除 `oauth_setup.py`

## 2. 手動操作（使用者）

- [ ] 2.1 開啟 Google Drive → 新增 → Google Apps Script → 將 gas/create_form.js 內容貼入編輯器（取代預設的 myFunction）
- [ ] 2.2 部署為「網路應用程式」：執行身份選「我」、存取權選「所有人」→ 複製部署 URL

## 3. VM 部署

- [ ] 3.1 在 VM 的 `~/form-automation-system/.env` 加入 `GOOGLE_FORMS_GAS_URL=<步驟2.2取得的URL>`
- [ ] 3.2 VM venv 重新安裝依賴：`venv/bin/pip install -r requirements.txt`
- [ ] 3.3 重啟 PM2：`pm2 restart form-automation`

## 4. 驗證

- [ ] 4.1 外部自檢：POST `https://forest-carbon.duckdns.org/forms/create-form`，帶測試欄位 JSON，確認回傳 `edit_url` 與 `respond_url`
- [ ] 4.2 從 GitHub Pages 前端點擊「建立 Google 表單」，確認表單出現在 yuchiao.niu@gmail.com Google Drive
