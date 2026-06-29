## Why

Service Account 無法建立 Google Forms（Google 伺服器端固定回傳 500）；OAuth 使用者憑證需要每次部署手動跑一次瀏覽器授權，難以複製。Google Apps Script Web App 以使用者身份執行、不需要任何 credentials 傳給伺服器，是最易複製的中介層方案。

## What Changes

- 新增 `gas/create_form.js`：Google Apps Script 程式碼，供使用者貼入 Google Drive 部署
- 改寫 `src/forms_creator.py`：移除 google-api-python-client 邏輯，改為 `requests.post` 呼叫 `GOOGLE_FORMS_GAS_URL`
- 更新 `requirements.txt`：移除 `google-auth-oauthlib`、`google-api-python-client`、`google-auth`；加入 `requests`
- 刪除 `oauth_setup.py`（不再需要）

## Capabilities

### New Capabilities

- `gas-forms-creation`: 透過 Google Apps Script Web App 建立 Google Forms，Flask 後端只需一個 URL 環境變數

### Modified Capabilities

（無）

## Impact

- `src/forms_creator.py`：認證與 API 呼叫方式全面替換
- `requirements.txt`：移除三個 Google 認證套件，加入 `requests`
- VM `.env`：新增 `GOOGLE_FORMS_GAS_URL`
- 複製步驟簡化：fork 者只需部署 GAS、填入 URL，不需要 GCP Console 或 OAuth 授權流程
