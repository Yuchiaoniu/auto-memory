## ADDED Requirements

### Requirement: 儲存當前所有分頁為群組
腳本 `Save-TabGroup.ps1 -GroupName <name>` SHALL 讀取當前所有開啟分頁（呼叫 CDP），將標題與 URL 寫入 `C:\Users\yuchi\.browser-groups.json` 的指定群組名稱下。

#### Scenario: 新建群組
- **WHEN** 執行 `Save-TabGroup.ps1 -GroupName "工作"` 且該群組名稱不存在
- **THEN** 在 JSON 新增「工作」群組，包含當前所有非內部頁面的分頁，顯示「已儲存 N 個分頁至群組『工作』」

#### Scenario: 覆寫已存在的群組
- **WHEN** 執行 `Save-TabGroup.ps1 -GroupName "工作"` 且群組已存在
- **THEN** 以當前分頁覆寫群組內容，顯示「已更新群組『工作』（原 M 個 → 現 N 個分頁）」

#### Scenario: JSON 檔案不存在
- **WHEN** `C:\Users\yuchi\.browser-groups.json` 尚未建立
- **THEN** 自動建立檔案並寫入初始結構，再執行儲存流程

### Requirement: 列出所有已儲存群組
腳本 `List-TabGroups.ps1` SHALL 讀取 JSON，顯示所有群組名稱、建立日期、分頁數量。

#### Scenario: 有已儲存群組
- **WHEN** 執行 `List-TabGroups.ps1`
- **THEN** 表格列出群組名稱、日期、分頁數量

#### Scenario: 尚無任何群組
- **WHEN** 執行 `List-TabGroups.ps1`
- **THEN** 顯示「尚無已儲存群組。使用 Save-TabGroup.ps1 儲存第一個群組。」
