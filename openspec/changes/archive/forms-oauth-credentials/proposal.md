## Why

Google Forms API 不支援 Service Account 直接建立表單（固定回傳 500 Internal error），必須改用使用者 OAuth 2.0 憑證（附 refresh token）。在本機授權一次後，伺服器之後自動換 token，不需再次手動介入。

## What Changes

- 新增 `oauth_setup.py`：本機執行一次的授權工具，讀取 OAuth 用戶端金鑰、走瀏覽器授權流程、輸出 `user-credentials.json`
- 改寫 `src/forms_creator.py`：改用 `google.oauth2.credentials.Credentials` 載入 `user-credentials.json`；token 過期時自動 refresh 並回寫檔案
- 更新 `requirements.txt`：加入 `google-auth-oauthlib`
- 更新 `.gitignore`：排除 `user-credentials.json` 與 `oauth-client-credentials.json`
- 移除 `service-account.json` 依賴（Forms 用途）

## Capabilities

### New Capabilities

- `oauth-forms-auth`: 使用 OAuth 2.0 使用者憑證建立 Google Forms，支援自動 token refresh

### Modified Capabilities

（無）

## Impact

- `src/forms_creator.py`：認證方式從 Service Account 改為 OAuth 使用者憑證
- `requirements.txt`：新增 `google-auth-oauthlib`
- `.gitignore`：新增兩個敏感檔案排除規則
- VM 部署：需 SCP `user-credentials.json` 到 VM 並 pip install 新依賴
