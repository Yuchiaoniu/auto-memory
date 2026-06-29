## ADDED Requirements

### Requirement: 翻到下一頁
腳本 SHALL 點擊 Bookshelf 底部導航列的 ▶ 按鈕，使書本前進一頁後截圖。

#### Scenario: 翻頁成功
- **WHEN** 執行 `python bookshelf_bg.py next`
- **THEN** Bookshelf 顯示下一頁內容，`bookshelf_current.png` 為新頁面截圖

#### Scenario: 已在最後一頁
- **WHEN** 執行 `python bookshelf_bg.py next` 且目前在最後一頁
- **THEN** 頁面不變，`bookshelf_current.png` 為當前頁面截圖

### Requirement: 翻到上一頁
腳本 SHALL 點擊 ◀ 按鈕，使書本後退一頁後截圖。

#### Scenario: 翻頁成功
- **WHEN** 執行 `python bookshelf_bg.py prev`
- **THEN** Bookshelf 顯示上一頁內容，`bookshelf_current.png` 為新頁面截圖

### Requirement: 跳到指定頁碼
腳本 SHALL 點擊頁碼輸入框，輸入目標頁碼並按 Enter，跳到指定位置後截圖。

#### Scenario: 跳頁成功
- **WHEN** 執行 `python bookshelf_bg.py goto 130`
- **THEN** Bookshelf 跳到第 130 頁，`bookshelf_current.png` 為該頁截圖

### Requirement: ▶ 按鈕座標（已知問題）
▶ 按鈕的實體像素座標為 x=1766, y=974（1920x1020 視窗），比例 NEXT_X_RATIO=0.920, NAV_Y_RATIO=0.946。
**目前狀態**：點擊可到達 Bookshelf（其他元素有回應），但 ▶ 按鈕無翻頁反應，原因待查。

#### Scenario: 備案 — 使用頁碼輸入跳頁
- **WHEN** ▶ 點擊無效
- **THEN** 使用 goto 指令輸入頁碼替代翻頁
