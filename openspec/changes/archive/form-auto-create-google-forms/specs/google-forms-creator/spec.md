## ADDED Requirements

### Requirement: 將 JSON 欄位陣列轉換為 Google Form
系統 SHALL 接受符合 form-automation-system 輸出格式的 JSON 欄位陣列，呼叫 Google Forms API 建立包含所有欄位的表單，並回傳 formId 與 responderUri。

#### Scenario: 成功建立含多種欄位類型的表單
- **WHEN** 傳入包含 text / radio / checkbox / date 欄位的 JSON 陣列
- **THEN** 系統建立 Google Form，每個欄位對應正確的 Forms API 題型，並回傳 formId

#### Scenario: required 欄位標記為必填
- **WHEN** JSON 欄位中 required 為 true
- **THEN** 對應的 Forms 題目設定 isRequired: true

#### Scenario: radio / checkbox / select 欄位包含選項
- **WHEN** JSON 欄位 options 陣列非空
- **THEN** 對應題目的 choices 包含所有選項文字

#### Scenario: 未知 field_type 的處理
- **WHEN** field_type 不在支援清單內
- **THEN** 系統以 SHORT_ANSWER 作為 fallback，不拋出錯誤

### Requirement: 以 Service Account 認證呼叫 Forms API
系統 SHALL 從 `GOOGLE_APPLICATION_CREDENTIALS` 環境變數指定的 JSON 金鑰檔載入 Service Account 憑證，範圍包含 `https://www.googleapis.com/auth/forms.body` 與 `https://www.googleapis.com/auth/drive`。

#### Scenario: 金鑰檔存在且有效
- **WHEN** 環境變數指向有效的 Service Account JSON 金鑰
- **THEN** 系統成功取得 access token 並呼叫 API

#### Scenario: 金鑰檔不存在
- **WHEN** 環境變數未設定或檔案不存在
- **THEN** 系統回傳明確錯誤訊息，不崩潰
