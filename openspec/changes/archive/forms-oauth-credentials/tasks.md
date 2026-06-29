## 1. 本地檔案修改

- [x] 1.1 新增 `oauth_setup.py`：讀取 `oauth-client-credentials.json`，執行 `InstalledAppFlow.run_local_server()`，將 token/refresh_token/client_id/client_secret/token_uri/scopes 輸出到 `user-credentials.json`
- [x] 1.2 改寫 `src/forms_creator.py`：移除 Service Account 邏輯，改用 `google.oauth2.credentials.Credentials` 載入 `user-credentials.json`；token 過期時呼叫 `creds.refresh(Request())` 並回寫 JSON
- [x] 1.3 更新 `requirements.txt`：加入 `google-auth-oauthlib>=1.0.0`
- [x] 1.4 更新 `.gitignore`：加入 `user-credentials.json` 與 `oauth-client-credentials.json`

## 2. 手動操作（使用者）

- [ ] 2.1 GCP Console → APIs & Services → Credentials → 建立 OAuth 2.0 用戶端 ID（桌面應用程式）→ 下載 JSON 存為專案根目錄的 `oauth-client-credentials.json`
- [ ] 2.2 本機執行 `python oauth_setup.py`，瀏覽器授權後確認產生 `user-credentials.json`

## 3. VM 部署

- [ ] 3.1 SCP `user-credentials.json` 到 VM `~/form-automation-system/user-credentials.json`
- [ ] 3.2 VM venv 安裝新依賴：`venv/bin/pip install google-auth-oauthlib`
- [ ] 3.3 重啟 PM2 process：`pm2 restart form-automation`

## 4. 驗證

- [ ] 4.1 外部自檢：從外部發 `POST https://forest-carbon.duckdns.org/forms/create-form`，帶測試欄位 JSON，確認回傳 `edit_url` 與 `respond_url`
- [ ] 4.2 從 GitHub Pages 前端點擊「建立 Google 表單」，確認表單出現在 yuchiao.niu@gmail.com Google Drive
