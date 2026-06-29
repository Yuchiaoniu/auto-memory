## ADDED Requirements

### Requirement: 以 ADC 憑證呼叫 Google Forms API
`create_form()` SHALL 使用 `google.auth.default(scopes=[...])` 取得憑證並呼叫 Forms API 建立表單，不讀取任何自訂 JSON 金鑰檔。

#### Scenario: ADC 憑證存在
- **WHEN** VM 上 `~/.config/gcloud/application_default_credentials.json` 存在
- **THEN** `create_form()` 成功取得憑證、建立表單，回傳含 `edit_url` 與 `respond_url` 的 JSON，`error` 為 null

#### Scenario: ADC 憑證不存在
- **WHEN** ADC 憑證檔不存在且未設定 `GOOGLE_APPLICATION_CREDENTIALS`
- **THEN** `create_form()` 回傳 `{"error": "<google.auth 例外訊息>", ...}`
