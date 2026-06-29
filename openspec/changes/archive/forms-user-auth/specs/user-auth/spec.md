## ADDED Requirements

### Requirement: 使用者登入
系統 SHALL 提供 `POST /login` endpoint，驗證 username/password，成功後設定 session cookie。

#### Scenario: 帳號密碼正確
- **WHEN** POST /login 帶正確的 username 與 password
- **THEN** 回傳 200 `{"ok": true}`，設定 session cookie（SameSite=None; Secure）

#### Scenario: 帳號密碼錯誤
- **WHEN** POST /login 帶錯誤的 username 或 password
- **THEN** 回傳 401 `{"error": "帳號或密碼錯誤"}`

### Requirement: 登出
系統 SHALL 提供 `POST /logout`，清除 session。

#### Scenario: 已登入使用者登出
- **WHEN** POST /logout（帶有效 session）
- **THEN** 回傳 200，session 清除

### Requirement: 歷史記錄 API
系統 SHALL 提供 `GET /history`，回傳登入使用者所有表單記錄（倒序）。

#### Scenario: 已登入
- **WHEN** GET /history（帶有效 session）
- **THEN** 回傳 `{"records": [{file_name, edit_url, respond_url, created_at}, ...]}`

#### Scenario: 未登入
- **WHEN** GET /history（無 session）
- **THEN** 回傳 401

### Requirement: 分析自動建立表單
`POST /analyze` SHALL 在分析完成後自動呼叫 create_form()，將結果存入 DB，回傳含 form URLs 的完整回應。

#### Scenario: 已登入且分析成功
- **WHEN** 已登入使用者 POST /analyze 上傳有效 .docx
- **THEN** 回傳 `{fields, form_id, edit_url, respond_url, truncated, error: null}`，記錄寫入 forms 表

#### Scenario: 未登入
- **WHEN** 未登入使用者 POST /analyze
- **THEN** 回傳 401
