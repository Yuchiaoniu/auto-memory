## Context

使用者透過 Claude Code CLI 與 Claude 互動。Claude 執行 PowerShell 腳本，自動偵測當前執行中的瀏覽器，依瀏覽器類型選擇讀取方式，取得所有分頁的完整 URL，再以對話方式協助整理與群組管理。**不需要重啟瀏覽器，不需要 CDP，不需要解析私有二進位格式。**

## Goals / Non-Goals

**Goals:**
- 自動偵測執行中的瀏覽器（Brave、Chrome、Edge、Firefox）
- 不重啟瀏覽器即可讀取所有分頁的完整 URL 與標題
- 儲存命名群組至本地 JSON，支援多個群組並存
- 依群組名稱批次開啟所有 URL
- Claude 互動式建議可關閉的分頁

**Non-Goals:**
- 不做瀏覽器擴充功能（Extension）
- 不做雲端同步或多機共享
- 不自動關閉分頁（Claude 建議後需使用者確認）
- 不支援同時管理多個不同瀏覽器（一次針對一個）

## Decisions

**D1：主要讀取策略**

```
Brave / Chrome / Edge  →  UIA 迴圈掃描（切換每個分頁，讀 omnibox URL）
Firefox                →  讀取 sessionstore-backups/recovery.jsonlz4
```

兩種方式均無需重啟瀏覽器，均可取得完整 URL，均使用公開 API/格式。

**D2：Chromium UIA 迴圈掃描（核心設計）**

使用 .NET `UIAutomationClient` 依序掃描所有分頁：

```
1. Get-Process brave → 取得所有 Brave 視窗
2. 找到分頁列（ControlType.Tab），枚舉所有 TabItem
3. 記錄當前活躍分頁（IsSelected = true）
4. 迴圈：
   a. SelectionItemPattern.Select() → 切換至該分頁
   b. Start-Sleep 150ms → 等待 omnibox 更新
   c. 找 omnibox（ControlType.Edit，toolbar 區域內）
   d. ValuePattern.Current.Value → 取得 URL
   e. 記錄 { title, url, window_index, tab_index }
5. 返回原本的活躍分頁
```

**代價：** 使用者會看到分頁快速切換（每個分頁約 150ms；20 個分頁約 3 秒）。執行完自動回原分頁。這是無重啟取得 URL 的必要步驟。

**為何優於 SNSS 解析：**
- 使用標準 .NET UIAutomationClient API（已有文件、穩定）
- 不依賴私有二進位格式，Chromium 版本升級不受影響
- omnibox 是明確的 UIA 控制項，結構穩定

**D3：自動瀏覽器偵測**

透過 `Get-Process` 偵測已知瀏覽器：

| 瀏覽器 | ProcessName | 讀取方式 |
|--------|------------|---------|
| Brave  | brave      | UIA 迴圈 |
| Chrome | chrome     | UIA 迴圈 |
| Edge   | msedge     | UIA 迴圈 |
| Firefox | firefox   | sessionstore jsonlz4 |

- 若多個瀏覽器同時執行，列出清單請使用者選擇
- 使用者可直接告訴 Claude「我在用 Brave」跳過偵測

**D4：Firefox Sessionstore 讀取**

Firefox 在執行時定期將當前分頁狀態寫入：
```
%APPDATA%\Mozilla\Firefox\Profiles\<profile>\sessionstore-backups\recovery.jsonlz4
```
LZ4 壓縮的 JSON，包含所有視窗、所有分頁的 URL 和標題。無需切換分頁，靜默讀取。
- 限制：約每 15 秒更新一次，可能落後最新狀態幾秒

**D5：群組資料格式（JSON）**

```json
{
  "groups": {
    "工作群組": {
      "created": "2026-05-17",
      "browser": "brave",
      "tabs": [
        { "title": "GitHub", "url": "https://github.com" },
        { "title": "Claude", "url": "https://claude.ai" }
      ]
    }
  }
}
```
- 儲存路徑：`C:\Users\yuchi\.browser-groups.json`
- `browser` 欄位記錄來源，還原時用對應瀏覽器開啟

**D6：Claude 作為唯一互動層**

使用者說「我在用 Brave，幫我看分頁」→ Claude 執行 `Detect-Browser.ps1` 確認 → 執行 `Get-Tabs.ps1 -Browser brave` → UIA 迴圈掃描取得完整 URL 清單 → 分析並回應。

## Risks / Trade-offs

- [分頁切換畫面閃爍] → 使用者會看到 2-5 秒的快速切換；掃描完自動回原分頁；偶爾用、可接受
- [omnibox 更新有延遲] → 每個分頁等 150ms；若遇到特別慢的頁面可能讀到前一個 URL；可調高等待時間
- [分頁切換期間避免操作] → 掃描過程中使用者不應點擊瀏覽器，否則可能打亂流程；腳本開始時提示使用者
- [UIA 樹結構差異] → Brave 各版本的 omnibox 控制項 AutomationId 可能略有不同；以 ControlType.Edit + 位置篩選作為 fallback
- [Firefox sessionstore 延遲] → 15 秒內的變更可能遺失；告知使用者
- [URL 還原不代表頁面狀態] → 符合預期，只開啟 URL
