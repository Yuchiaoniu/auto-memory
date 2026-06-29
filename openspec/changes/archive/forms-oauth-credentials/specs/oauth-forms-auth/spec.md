## ADDED Requirements

### Requirement: OAuth 2.0 使用者憑證建立 Google Forms
系統 SHALL 使用儲存於 `user-credentials.json` 的 OAuth 2.0 使用者憑證呼叫 Google Forms API，不得使用 Service Account。

#### Scenario: 憑證存在且有效
- **WHEN** `user-credentials.json` 存在且 token 未過期
- **THEN** 直接使用 token 建立表單，不發出 refresh 請求

#### Scenario: token 已過期
- **WHEN** `user-credentials.json` 存在但 token 已過期
- **THEN** 系統自動使用 refresh_token 換取新 token，並回寫更新後的 token 到 `user-credentials.json`

#### Scenario: 憑證檔案不存在
- **WHEN** `user-credentials.json` 不存在
- **THEN** `create_form()` 回傳 `{"error": "User credentials not found: <path>", ...}`，HTTP status 500

### Requirement: 一次性本機授權工具
系統 SHALL 提供 `oauth_setup.py` 供使用者在本機完成一次性 OAuth 授權，產生 `user-credentials.json`。

#### Scenario: 執行授權流程
- **WHEN** 使用者執行 `python oauth_setup.py`（`oauth-client-credentials.json` 存在）
- **THEN** 瀏覽器開啟 Google 授權頁面，授權後在當前目錄產生 `user-credentials.json`

#### Scenario: 缺少用戶端金鑰
- **WHEN** `oauth-client-credentials.json` 不存在
- **THEN** 腳本印出明確錯誤訊息並結束，不產生 `user-credentials.json`
