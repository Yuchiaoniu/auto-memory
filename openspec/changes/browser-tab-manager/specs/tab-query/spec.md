## ADDED Requirements

### Requirement: UIA 迴圈掃描取得所有分頁 URL（Chromium 系）
腳本 `Get-Tabs.ps1 -Browser <識別碼>` SHALL 透過 Windows UI Automation 切換每個分頁並讀取 omnibox，回傳所有分頁的標題與完整 URL。

#### Scenario: 正常掃描（Brave 執行中）
- **WHEN** 執行 `Get-Tabs.ps1 -Browser brave`
- **THEN**
  1. 提示「開始掃描，請勿操作 Brave（約 N 秒）」
  2. 逐一切換每個分頁，等待 150ms，讀取 omnibox URL
  3. 掃描完成後回到原本的活躍分頁
  4. 輸出格式化表格：序號、視窗、標題（50 字元截斷）、URL

#### Scenario: 多個 Brave 視窗
- **WHEN** Brave 開啟多個視窗
- **THEN** 逐一處理每個視窗，輸出時標注視窗編號（Window 1, Window 2...）

#### Scenario: omnibox 讀取失敗（單一分頁）
- **WHEN** 某個分頁的 omnibox 值無法讀取（超時或控制項找不到）
- **THEN** 該分頁記錄 url = "[無法讀取]"，繼續掃描下一個，不中斷整體流程

#### Scenario: 瀏覽器未執行
- **WHEN** brave.exe 未在執行
- **THEN** 顯示錯誤「Brave 未執行」

### Requirement: Firefox sessionstore 讀取
`Get-Tabs.ps1 -Browser firefox` SHALL 讀取 Firefox default profile 的 `recovery.jsonlz4`，靜默取得所有分頁 URL（不需切換分頁）。

#### Scenario: Firefox 正常執行
- **WHEN** 執行 `Get-Tabs.ps1 -Browser firefox`
- **THEN** 讀取 `%APPDATA%\Mozilla\Firefox\Profiles\<default-profile>\sessionstore-backups\recovery.jsonlz4`，解壓縮後解析 `windows[].tabs[]`，輸出標題與 URL 表格

#### Scenario: recovery.jsonlz4 不存在
- **WHEN** Firefox 剛啟動或 sessionstore 尚未寫入
- **THEN** 顯示「sessionstore 尚未就緒，請稍候再試」

### Requirement: 輸出 JSON 供 Claude 分析
`Get-Tabs.ps1 -Browser <識別碼> -Json` SHALL 輸出標準化 JSON：

```json
{
  "browser": "brave",
  "method": "uia-loop",
  "scanned_at": "2026-05-17T10:30:00",
  "tabs": [
    { "index": 1, "window": 1, "title": "GitHub - Explore", "url": "https://github.com/explore" },
    { "index": 2, "window": 1, "title": "Claude", "url": "https://claude.ai" }
  ]
}
```

- Firefox 的 `method` 欄位為 `"sessionstore"`
- URL 讀取失敗的分頁，`url` 欄位值為 `null`

### Requirement: UIA 掃描核心邏輯（`Scan-BraveTabs.ps1`）

掃描流程：
1. `Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes`
2. 透過 ProcessId 找到所有 Brave 視窗（`AutomationElement.RootElement.FindAll`）
3. 在每個視窗內找 `ControlType.Tab`（分頁列），再找所有 `ControlType.TabItem`
4. 記錄當前 `IsSelected = true` 的 TabItem（掃描結束後還原）
5. 迴圈：`SelectionItemPattern.Select()` → `Start-Sleep 150` → 讀 omnibox
6. omnibox 定位：視窗內 toolbar 區域的 `ControlType.Edit`，優先找 `AutomationId = "omnibox"`，fallback 找最靠近頂部的 Edit 控制項
7. `ValuePattern.Current.Value` 取得 URL
