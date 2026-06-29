# browser-tab-manager memory.md

## 技術架構

**核心機制：** Windows UI Automation (UIA)，透過 `UIAutomationClient` assembly 操控 Brave 分頁。
不需要 CDP 偵錯模式，不需要重啟瀏覽器，Brave 正常執行即可掃描。

**UIA Patterns 對應：**
- `SelectionItemPattern` → 切換分頁（Select）
- `ValuePattern` → 讀取 omnibox URL
- `InvokePattern` → 點擊分頁關閉按鈕

**Omnibox 定位：**
Brave 中文版 omnibox 名稱為 `網址與搜尋列`；
正確做法是先比對名稱包含 `*Address*`、`*address*`、`*search*`、`*網址*`，
若都不符則改用「最寬 Edit 控制項」作為 fallback。
**重要：Close-LocalhostTabs.ps1 的 Find-Omnibox 未包含 `*網址*`，可能導致找到錯誤的 Edit 控制項。**

**分頁關閉機制（兩段 fallback）：**
1. 找 TabItem 的 Button 子元素並呼叫 InvokePattern → 點關閉按鈕
2. SetForegroundWindow + WScript.Shell SendKeys("^w") → 送出 Ctrl+W

## 編碼限制（重要）

PowerShell 5.1 在繁體中文 Windows 上，讀取 UTF-8 無 BOM 的 .ps1 時會用 CP950 解碼，
導致中文字元損毀，造成未關閉字串或 parse error。
**所有 .ps1 腳本必須只用 ASCII 字元，禁止在腳本內放任何中文字串。**
（.md、.json 等非 PowerShell 執行的檔案不受此限制）

## 腳本清單（腳本位於 C:\Users\yuchi\browser-tab-manager\）

| 腳本 | 用途 |
|------|------|
| `Detect-Browser.ps1` | 偵測目前執行中的瀏覽器，`-AutoSelect` 自動選第一個 |
| `Scan-ChromiumTabs.ps1` | UIA 掃描 Chromium 系瀏覽器所有分頁，回傳 PSObject 陣列（Window, Index, Title, URL）|
| `Get-Tabs.ps1` | 呼叫 Scan-ChromiumTabs；`-Raw` 回傳物件、`-Json` 輸出 JSON、預設 Format-Table |
| `Save-TabGroup.ps1` | 呼叫 Get-Tabs -Raw，儲存當前分頁為命名群組至 JSON 資料庫 |
| `List-TabGroups.ps1` | 列出 JSON 資料庫中所有群組 |
| `Open-TabGroup.ps1` | 開啟指定群組分頁；`-Preview` 只列出不開啟 |
| `Close-LocalhostTabs.ps1` | 掃描並關閉所有 localhost URL 分頁（有 omnibox 偵測缺陷，建議用 inline 腳本） |

## 資料儲存

群組 JSON 資料庫路徑：`C:\Users\yuchi\.browser-groups.json`
格式：
```json
{ "groups": { "群組名稱": { "created": "2026-06-02", "browser": "brave", "tabs": [{ "title": "...", "url": "..." }] } } }
```

## Brave 原生分頁群組偵測

Brave 的原生分頁群組名稱會附加在 UIA tab title 末尾，格式為 ` - 屬於「群組名稱」群組`。
用 `-replace ' - 屬於.*',''` 可取得純分頁標題。

## 已掃描到的 Brave 分頁群組

- **碩士申請**：40 個分頁（各校招生簡章、GCP、GitHub、Gemini、學術論文）
- **臨時分頁**：27 個分頁（管理會計論文、翻譯工具、教育資源、TOEFL）