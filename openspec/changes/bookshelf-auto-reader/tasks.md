## 1. 環境準備（已完成）

- [x] 1.1 安裝 Python 套件：pyautogui, pygetwindow, pywin32, pillow, uiautomation
- [x] 1.2 確認 Bookshelf 視窗結構：CoreWindow hwnd、ApplicationFrameWindow hwnd
- [x] 1.3 確認 DPI 縮放問題（125%），加入 SetProcessDPIAware()

## 2. 截圖功能（已完成）

- [x] 2.1 改用 Windows Graphics Capture API（windows-capture 套件）取代 pyautogui.screenshot
- [x] 2.2 截圖前用 SW_SHOWNOACTIVATE 還原視窗（不搶焦點）
- [x] 2.3 截圖後立刻 SW_MINIMIZE 縮小視窗
- [x] 2.4 用 threading + 8 秒 timeout 防止 WGC 無限等待
- [x] 2.5 完成信號：bookshelf_done.txt，日誌：bookshelf_log.txt

## 3. 翻頁功能（已完成）

- [x] 3.1 放棄 pyautogui 座標點擊方式（▶ 按鈕對 UWP 無效）
- [x] 3.2 改用 UI Automation（uiautomation 套件）直接操作控件
- [x] 3.3 找到導覽工具列：WindowControl '閱讀器導覽工具列'
  - SliderControl '頁面位置'（讀取目前頁碼）
  - ButtonControl '上一頁' / '下一頁'（InvokePattern）
  - EditControl '前往頁面'（SetValue + SendKeys Enter）
- [x] 3.4 驗證 next：125 → 126，完全不搶焦點
- [x] 3.5 驗證 prev：130 → 129，完全不搶焦點
- [x] 3.6 驗證 goto：129 → 131 → 133，完全不搶焦點

## 4. 頁面分析流程（進行中）

- [x] 4.1 建立 bookshelf_notes/ 目錄
- [x] 4.2 手動存入第 125 頁分析：bookshelf_notes/page_125.md
- [x] 4.3 建立標準化分析模板（bookshelf_notes/_template.md）
- [x] 4.4 每次截圖分析後自動呼叫 Write 工具存檔（page_133.md 已驗證）
- [x] 4.5 截圖只保留最新一張（bookshelf_current.png），筆記永久累積在 bookshelf_notes/

## 5. 整合測試

- [x] 5.1 screenshot：SW_SHOWNOACTIVATE + WGC + minimize 完整流程
- [x] 5.2 goto + screenshot 完整流程（頁碼正確、截圖清晰）
- [ ] 5.3 連續多頁：next × N 頁 → 每頁分析存檔
- [ ] 5.4 確認視窗大小在操作前後不變
