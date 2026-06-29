## Why

Service Account 無法建立 Google Forms（500）；GAS 方案需要 4 個手動瀏覽器步驟；OAuth 自訂流程需要 GCP Console 設定 Client ID。gcloud ADC 是最乾淨的路徑：一個指令、一次瀏覽器「允許」，之後完全自動。

## What Changes

- 改寫 `src/forms_creator.py`：改用 `google.auth.default(scopes=[...])` 取得憑證，直接呼叫 Forms API
- 更新 `requirements.txt`：移除 `requests`（forms 用途）、`google-auth-oauthlib`；加回 `google-api-python-client`、`google-auth`
- 刪除 `gas/create_form.js` 與 `gas/` 資料夾

## Capabilities

### New Capabilities

- `adc-forms-auth`: 以 gcloud ADC 使用者憑證呼叫 Google Forms API

### Modified Capabilities

（無）

## Impact

- `src/forms_creator.py`：認證來源改為 ADC，邏輯回到直接呼叫 Forms API
- `requirements.txt`：依賴精簡為五個套件
- VM 部署：需 SCP ADC 憑證檔一次，之後無需任何更新
