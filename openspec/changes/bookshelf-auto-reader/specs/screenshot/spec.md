## ADDED Requirements

### Requirement: 截圖當前 Bookshelf 頁面
腳本 SHALL 將 Bookshelf 帶到前景，截取 CoreWindow 的完整畫面，並儲存到 `bookshelf_current.png`。

#### Scenario: 正常截圖
- **WHEN** 執行 `python bookshelf_bg.py screenshot`
- **THEN** `bookshelf_current.png` 被更新為當前頁面內容，`bookshelf_done.txt` 寫入 "OK"

#### Scenario: 找不到 Bookshelf
- **WHEN** Bookshelf app 未開啟
- **THEN** `bookshelf_done.txt` 寫入 "ERROR"，`bookshelf_log.txt` 記錄錯誤訊息

### Requirement: 截圖不影響視窗狀態
腳本 SHALL 在截圖完成後取消 TOPMOST 設定，Bookshelf 視窗大小不得因腳本執行而改變。

#### Scenario: 視窗狀態還原
- **WHEN** 截圖完成
- **THEN** Bookshelf 回到非 TOPMOST 狀態，大小與執行前相同
