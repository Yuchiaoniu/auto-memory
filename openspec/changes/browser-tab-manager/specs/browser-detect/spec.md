## ADDED Requirements

### Requirement: 自動偵測執行中的瀏覽器
腳本 `Detect-Browser.ps1` SHALL 透過 `Get-Process` 比對已知瀏覽器 process name，回傳正在執行的瀏覽器清單（識別碼、顯示名稱、視窗數量）。

已知對應表：
| ProcessName | 識別碼 | 顯示名稱 |
|------------|--------|---------|
| brave | brave | Brave |
| chrome | chrome | Google Chrome |
| msedge | edge | Microsoft Edge |
| firefox | firefox | Firefox |
| opera | opera | Opera |
| vivaldi | vivaldi | Vivaldi |

#### Scenario: 單一瀏覽器執行中
- **WHEN** 執行 `Detect-Browser.ps1` 且只有一個已知瀏覽器在執行
- **THEN** 輸出「偵測到：Brave（3 個視窗）」並輸出識別碼 `brave`（供管線傳遞）

#### Scenario: 多個瀏覽器同時執行
- **WHEN** 執行 `Detect-Browser.ps1` 且有多個已知瀏覽器在執行
- **THEN** 列出所有執行中的瀏覽器清單，要求使用者指定使用哪一個

#### Scenario: 無已知瀏覽器執行
- **WHEN** 執行 `Detect-Browser.ps1` 且無已知瀏覽器在執行
- **THEN** 顯示「未偵測到執行中的瀏覽器」，列出支援的瀏覽器清單

### Requirement: 手動指定瀏覽器（跳過偵測）
`Detect-Browser.ps1 -Browser <識別碼>` SHALL 直接驗證該瀏覽器是否執行中，不執行自動偵測。

#### Scenario: 使用者告知 Claude 正在用哪個瀏覽器
- **WHEN** 執行 `Detect-Browser.ps1 -Browser brave`
- **THEN** 驗證 brave.exe 是否執行中，若是則確認並回傳識別碼；若否則顯示錯誤
