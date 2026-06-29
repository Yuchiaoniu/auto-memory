## Context

`form-automation-system` 使用 Google Forms API v1 建立表單。原本以 Service Account 認證，但 Google 的 Forms API 不支援 Service Account 直接建立表單（server 固定回傳 500 Internal error）。改用 OAuth 2.0 使用者憑證是唯一可行路徑（無 Google Workspace，無法啟用 Domain-Wide Delegation）。

## Goals / Non-Goals

**Goals:**
- 以 OAuth 2.0 使用者憑證取代 Service Account 進行 Forms API 呼叫
- refresh token 儲存於 VM，token 過期時自動換新，不需再次手動授權
- 提供 `oauth_setup.py` 讓使用者在本機完成一次性授權

**Non-Goals:**
- 不修改 `/analyze` 端點（Gemini API 仍用 API Key）
- 不做多使用者 OAuth 流程（只針對 `yuchiao.niu@gmail.com` 一個帳號）

## Decisions

**D1：以 JSON 檔案儲存 OAuth token，不用 pickle**
- 選 JSON：人類可讀、跨 Python 版本相容、方便 SCP 傳輸
- 棄 pickle：二進位格式、版本相依、不易審查

**D2：token refresh 在 `_load_credentials()` 時同步進行**
- 每次呼叫 `create_form()` 前先檢查 expiry，過期則 refresh 並回寫 JSON
- 不另設背景排程，因 Flask 每次請求都重新載入，成本低
- 若 refresh 失敗（refresh_token 失效）則拋例外，由 Flask 回傳 500

**D3：OAuth 用戶端 ID 類型為「桌面應用程式」**
- 支援 `InstalledAppFlow.run_local_server()` 在本機完成授權
- 不選 Web 應用程式（需 redirect URI 設定）

## Risks / Trade-offs

- **refresh_token 失效** → 需重新本機授權並上傳新的 user-credentials.json；發生機率低（token 通常長期有效）
- **JSON 明文儲存 token** → 與 service-account.json 一樣敏感，同樣排入 `.gitignore`，VM 上以 chmod 600 保護
- **Forms 表單擁有者是 yuchiao.niu@gmail.com**（而非 Service Account），符合需求

## Migration Plan

1. GCP Console 建立 OAuth 2.0 用戶端 ID（桌面應用程式），下載 `oauth-client-credentials.json`
2. 本機執行 `python oauth_setup.py`，瀏覽器授權後產生 `user-credentials.json`
3. SCP `user-credentials.json` 到 VM `~/form-automation-system/`
4. VM venv 安裝 `google-auth-oauthlib`
5. 重啟 PM2 process `form-automation`
6. 外部自檢：`POST /create-form` 確認回傳 `edit_url` 與 `respond_url`

Rollback：保留 `service-account.json` 不刪，若需還原則 revert `forms_creator.py`。

## Open Questions

（無）
