## 1. 環境準備

- [x] 1.1 建立專案目錄 `C:\Users\yuchi\browser-tab-manager\`
- [x] 1.2 確認 Brave 執行中，`UIAutomationClient` assembly 可在 PowerShell 載入

## 2. 瀏覽器偵測（browser-detect）

- [x] 2.1 撰寫 `Detect-Browser.ps1`：`Get-Process` 比對已知 process name，輸出執行中瀏覽器清單
- [x] 2.2 實作 `-Browser <識別碼>` 參數：直接驗證指定瀏覽器是否執行中
- [x] 2.3 處理多瀏覽器同時執行（列表讓使用者選）

## 3. 分頁查詢（tab-query）

- [x] 3.1 撰寫 `Scan-ChromiumTabs.ps1`（Chromium UIA 迴圈核心）：
      a. Add-Type UIAutomationClient、UIAutomationTypes
      b. 透過 ProcessId 找所有 Brave 視窗
      c. 找 ControlType.TabItem 枚舉所有分頁
      d. 記錄當前活躍分頁（IsSelected）
      e. 迴圈：SelectionItemPattern.Select() → Sleep → 讀 omnibox ValuePattern
      f. omnibox 定位：Name 包含 Address/search bar，fallback 找最寬 Edit 控制項
      g. 收集 { Title, URL, Window, Index }
      h. 還原至原本活躍分頁
- [ ] 3.2 撰寫 Firefox sessionstore 讀取路徑（低優先，使用者主要用 Brave）
- [x] 3.3 撰寫 `Get-Tabs.ps1 -Browser <識別碼>`：依瀏覽器類型分流，格式化輸出
- [x] 3.4 加入 `-Json` 參數；加入 `-Raw` 參數供腳本間呼叫
- [x] 3.5 加入掃描前提示與掃描後回原分頁的確認訊息

## 4. 群組儲存（group-save）

- [x] 4.1 撰寫 `Save-TabGroup.ps1 -GroupName <name> -Browser <識別碼>`
- [x] 4.2 處理 JSON 不存在時自動建立初始結構
- [x] 4.3 處理覆寫已存在群組（顯示原 N → 新 M 個分頁的摘要）
- [x] 4.4 撰寫 `List-TabGroups.ps1`：讀取 JSON，格式化列出所有群組

## 5. 群組還原（group-restore）

- [x] 5.1 撰寫 `Open-TabGroup.ps1 -GroupName <name>`
- [x] 5.2 依群組的 `browser` 欄位決定用哪個瀏覽器開啟
- [x] 5.3 實作 `-Preview` 參數：只列出群組內分頁，不實際開啟
- [x] 5.4 群組不存在時列出所有可用群組名稱

## 6. 分頁整理（tab-cleanup）

- [ ] 6.1 由 Claude 呼叫 `Get-Tabs.ps1 -Json` 分析後，以條列式建議可關閉的分頁（重複網域、空白頁等）
- [ ] 6.2 使用者確認後，Claude 呼叫 UIA 關閉動作或提示手動關閉清單

## 7. 整合測試

- [x] 7.1 Brave 開啟 10+ 個分頁，執行 `Scan-ChromiumTabs.ps1`，確認所有分頁都能正確取得 URL
- [x] 7.2 測試多視窗情境（2 個 Brave 視窗，共 70 個分頁全部正確掃描）
- [x] 7.3 測試 `Save-TabGroup.ps1`、`List-TabGroups.ps1`、`Open-TabGroup.ps1 -Preview`
- [ ] 7.4 與 Claude 對話測試完整流程（偵測 → 掃描分頁 → 建議整理 → 儲存群組 → 還原群組）
