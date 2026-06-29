## ADDED Requirements

### Requirement: GAS Web App 接收欄位建立 Google Forms
GAS doPost handler SHALL 接收 JSON body `{title, fields[]}`，以 `FormApp` API 建立表單並加入所有題目，回傳 `{form_id, edit_url, respond_url, error}`。

#### Scenario: 正常建立含多欄位的表單
- **WHEN** POST body 包含 `title` 與至少一個 `fields` 項目
- **THEN** GAS 建立表單、加入所有題目，回傳含有效 `edit_url` 與 `respond_url` 的 JSON，`error` 為 null

#### Scenario: GAS 內部例外
- **WHEN** FormApp API 拋出例外
- **THEN** 回傳 `{error: "<訊息>", form_id: null, edit_url: null, respond_url: null}`

### Requirement: Flask 透過環境變數 URL 呼叫 GAS
`create_form()` 函式 SHALL 讀取 `GOOGLE_FORMS_GAS_URL` 環境變數，以 `requests.post` 發送請求，逾時設定 30 秒。

#### Scenario: GAS URL 已設定且呼叫成功
- **WHEN** `GOOGLE_FORMS_GAS_URL` 存在且 GAS 回傳 200
- **THEN** `create_form()` 回傳 GAS 的 JSON 結果

#### Scenario: GAS URL 未設定
- **WHEN** `GOOGLE_FORMS_GAS_URL` 環境變數不存在或為空
- **THEN** `create_form()` 回傳 `{"error": "GOOGLE_FORMS_GAS_URL 未設定", ...}`，不發出 HTTP 請求

#### Scenario: GAS 呼叫逾時或失敗
- **WHEN** requests.post 拋出例外（逾時、連線錯誤等）
- **THEN** `create_form()` 回傳 `{"error": "<例外訊息>", ...}`
