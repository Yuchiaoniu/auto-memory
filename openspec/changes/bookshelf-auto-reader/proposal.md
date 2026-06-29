## Why

VitalSource Bookshelf 是 UWP 電子書閱讀器，沒有 API 可直接取得書本內容。手動截圖翻頁效率低落，需要一個自動化工具讓 Claude 能夠逐頁讀取書本內容並分析摘要。

## What Changes

- 新增 `bookshelf_bg.py`：Python 自動化腳本，可截圖、翻頁、跳頁
- 新增 `bookshelf_notes/` 目錄：儲存每頁的 Claude 分析結果（.md 格式）
- 腳本透過 `python.exe -WindowStyle Minimized` 執行，不干擾使用者桌面
- 使用 `SwitchToThisWindow(ApplicationFrameWindow)` 取得前景權限後截圖

## Capabilities

### New Capabilities
- `screenshot`: 將 Bookshelf 拉到前景並截圖，儲存到 `bookshelf_current.png`
- `page-navigation`: 點擊底部 ◀ / ▶ 按鈕或輸入頁碼跳頁
- `page-analysis`: Claude 讀取截圖後產生中文摘要，存入 `bookshelf_notes/page_NNN.md`

### Modified Capabilities
（無現有 spec）

## Impact

- **依賴套件**：`pyautogui`, `pygetwindow`, `pywin32`, `pillow`（已安裝）
- **主腳本**：`C:\Users\yuchi\bookshelf_bg.py`
- **截圖輸出**：`C:\Users\yuchi\bookshelf_current.png`
- **完成信號**：`C:\Users\yuchi\bookshelf_done.txt`
- **執行日誌**：`C:\Users\yuchi\bookshelf_log.txt`
- **分析筆記**：`C:\Users\yuchi\bookshelf_notes\page_NNN.md`
- **目標 App**：VitalSource Bookshelf（Microsoft Store UWP，CoreWindow hwnd 需每次動態查找）
