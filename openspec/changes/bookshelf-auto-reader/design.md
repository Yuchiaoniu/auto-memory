## Context

VitalSource Bookshelf 是 Microsoft Store 的 UWP 應用程式，架構如下：
- `ApplicationFrameWindow`（hwnd=動態）：UWP 外框，用於 WGC 截圖與最小化控制
- `Windows.UI.Core.CoreWindow`（hwnd=動態）：實際書本內容渲染視窗（GPU 渲染）

**已知限制：**
- `PrintWindow` 可捕捉 UWP 框架但書本內容（GPU 渲染）顯示黑色 → 改用 WGC
- WGC 無法捕捉最小化視窗（GPU 停止渲染）→ 截圖前需 SW_SHOWNOACTIVATE 還原
- `pyautogui` 座標點擊無法觸發 UWP 翻頁按鈕（UWP input routing 問題）→ 改用 UIA

**DPI 環境：** 系統縮放 125%，腳本開頭呼叫 `SetProcessDPIAware()` 使用實體像素。

## Goals / Non-Goals

**Goals:**
- 自動截圖當前 Bookshelf 頁面（無需使用者手動截圖）
- 自動點擊翻頁（next/prev）
- 支援跳到指定頁碼（goto N）
- 不破壞使用者目前操作（腳本執行時 Bookshelf 短暫閃出後自動恢復背景）
- 每頁分析結果持久化儲存到 `bookshelf_notes/page_NNN.md`

**Non-Goals:**
- 完全背景執行（UWP 限制，需短暫前景截圖）
- 大量自動翻頁掃描（逐頁對話互動即可）
- 繞過 DRM 或直接解密 `.vbk` 檔案

## Decisions

### D1：截圖使用 Windows Graphics Capture API（WGC）
- **選擇**：`windows-capture` 套件，`WindowsCapture(window_hwnd=frame_hwnd)`
- **原因**：WGC 是唯一能捕捉 GPU 渲染內容（DirectX swapchain）的方法；不需前景焦點
- **替代**：`PrintWindow`（書本內容黑色）、`pyautogui.screenshot`（同樣無法捕捉 GPU 內容）

### D2：截圖前用 SW_SHOWNOACTIVATE 還原視窗（不搶焦點）
- **選擇**：`win32gui.ShowWindow(frame_hwnd, SW_SHOWNOACTIVATE=4)`，截圖後 `SW_MINIMIZE`
- **原因**：WGC 需要視窗可見且正在渲染；`SW_SHOWNOACTIVATE` 不切換鍵盤焦點
- **替代**：`SetForegroundWindow`（搶焦點，影響使用者工作）

### D3：翻頁使用 UI Automation InvokePattern / ValuePattern
- **選擇**：`uiautomation` 套件，直接操作 '閱讀器導覽工具列' 內的控件
  - `ButtonControl('上一頁'/'下一頁').GetInvokePattern().Invoke()`
  - `EditControl('前往頁面').GetValuePattern().SetValue(page) + SendKeys("{Enter}")`
  - `SliderControl('頁面位置').GetValuePattern().Value` 讀取當前頁碼
- **原因**：UWP app 雖然 accessibility tree 不完整，但導覽列控件已實作 UIA；完全不需焦點
- **替代**：`pyautogui.click`（UWP input routing 無效）、鍵盤快捷鍵（無效）

### D4：完成信號用檔案 bookshelf_done.txt
- **選擇**：腳本完成後寫入 `bookshelf_done.txt`，PowerShell 輪詢等待
- **原因**：簡單可靠，不需 IPC 或 socket
- **替代**：registry key、named pipe（過度複雜）

## Risks / Trade-offs

- **[截圖閃爍]** WGC 截圖時視窗短暫浮出 ~1.5 秒後自動最小化 → 可接受
- **[翻頁無閃爍]** UIA next/prev/goto 完全不搶焦點，視窗可保持最小化 → 已驗證
- **[hwnd 變動]** 每次 Bookshelf 重開 hwnd 會改變 → 腳本每次動態查詢，非硬編碼
- **[截圖保護]** 未來版本可能加截圖保護 → 目前無此問題
- **[WGC timeout]** 視窗未正常渲染時 WGC 永久等待 → 已加 8 秒 timeout + daemon thread
