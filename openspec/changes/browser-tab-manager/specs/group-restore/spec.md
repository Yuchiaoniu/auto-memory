## ADDED Requirements

### Requirement: 開啟指定群組的所有分頁
腳本 `Open-TabGroup.ps1 -GroupName <name>` SHALL 讀取 JSON 中指定群組的 URL 清單，透過 CDP 在當前 Chrome 視窗中逐一開啟每個 URL。

#### Scenario: 群組存在且 Chrome 在偵錯模式
- **WHEN** 執行 `Open-TabGroup.ps1 -GroupName "工作"`
- **THEN** 在 Chrome 逐一開啟群組內所有 URL，顯示「已開啟群組『工作』的 N 個分頁」

#### Scenario: 群組不存在
- **WHEN** 執行 `Open-TabGroup.ps1 -GroupName "不存在的群組"`
- **THEN** 顯示錯誤訊息「找不到群組『不存在的群組』」，並列出所有可用群組名稱

#### Scenario: Chrome 未在偵錯模式
- **WHEN** 執行 `Open-TabGroup.ps1` 但 CDP 端點無回應
- **THEN** 顯示提示並建議執行 `Start-DebugChrome.ps1`

### Requirement: 預覽群組內容（不開啟）
腳本 `Open-TabGroup.ps1 -GroupName <name> -Preview` SHALL 只列出群組內所有分頁的標題與 URL，不實際開啟。

#### Scenario: 預覽
- **WHEN** 執行 `Open-TabGroup.ps1 -GroupName "工作" -Preview`
- **THEN** 表格列出群組內每個分頁的標題與 URL，末行顯示「共 N 個分頁（加上 -Confirm 參數以實際開啟）」
