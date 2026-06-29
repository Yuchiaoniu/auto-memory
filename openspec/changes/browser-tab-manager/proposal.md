## Why

使用者日常工作中開啟大量瀏覽器分頁，難以管理。目前沒有工具能讓 Claude 直接讀取並分析當前分頁狀態，也無法將常用的分頁組合儲存為命名群組、下次一鍵還原。希望透過 PowerShell 腳本搭配 Claude 互動，實現「偵測瀏覽器 → 讀取分頁 → 整理建議 → 群組儲存 → 一鍵還原」的完整流程，且**不需要使用者重啟瀏覽器**。

## What Changes

- 建立 `Detect-Browser.ps1`：自動識別當前執行中的瀏覽器（Brave、Chrome、Edge、Firefox）
- 建立 `Get-Tabs.ps1`：依瀏覽器類型選擇最佳讀取方式（UIA 或 Firefox sessionstore）
- Claude 作為互動層，分析分頁清單，建議可關閉的分頁
- 本地 JSON 檔案記錄命名群組（群組名稱 → URL 清單）
- Claude 可依使用者指令開啟指定群組的所有分頁

## Capabilities

### New Capabilities

- `browser-detect`: 偵測當前執行中的瀏覽器類型，回傳可供後續腳本使用的瀏覽器識別碼
- `tab-query`: 依瀏覽器類型讀取所有開啟中的分頁；Chromium 系用 UIA 讀標題，Firefox 用 sessionstore 讀完整 URL
- `group-save`: 將指定分頁（或當前所有分頁）儲存為命名群組，寫入本地 JSON
- `group-restore`: 讀取本地群組 JSON，批次開啟指定群組的所有 URL
- `tab-cleanup`: Claude 分析分頁清單，標記重複/長時間堆積的分頁，由使用者確認後關閉

### Modified Capabilities

（無現有 spec，全為新建）

## Impact

- 純 PowerShell 腳本 + 本地 JSON，無後端、無雲端依賴
- 支援 Brave、Chrome、Edge（UIA 讀標題）、Firefox（sessionstore 讀完整 URL）
- 不需重啟瀏覽器即可使用基本功能；需要 URL 時可選擇性升級至 CDP 模式
- 群組資料儲存於 `C:\Users\yuchi\.browser-groups.json`
- Claude 作為唯一互動介面，使用者不需直接操作腳本
