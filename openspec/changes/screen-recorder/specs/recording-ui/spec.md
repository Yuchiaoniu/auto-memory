## ADDED Requirements

### Requirement: 模式切換
系統 SHALL 提供 MP4 和 MP3 兩個模式選項，使用者在錄製前可自由切換。

#### Scenario: 切換至 MP4 模式
- **WHEN** 使用者選擇 MP4 模式
- **THEN** 錄製時包含螢幕畫面與音訊

#### Scenario: 切換至 MP3 模式
- **WHEN** 使用者選擇 MP3 模式
- **THEN** 錄製時只擷取音訊，不截圖

### Requirement: 開始與停止錄製
系統 SHALL 提供開始錄製按鈕，按下後變為停止按鈕；按下停止後觸發編碼並儲存輸出檔案。

#### Scenario: 開始錄製
- **WHEN** 使用者按下開始錄製
- **THEN** 按鈕文字變為「停止錄製」，計時器開始計時

#### Scenario: 停止錄製
- **WHEN** 使用者按下停止錄製
- **THEN** 系統停止擷取，觸發 ffmpeg 編碼，完成後顯示輸出檔案路徑

### Requirement: 錄製計時顯示
系統 SHALL 在錄製中即時顯示已錄製時間（格式 HH:MM:SS）。

#### Scenario: 計時更新
- **WHEN** 錄製進行中
- **THEN** UI 每秒更新一次計時顯示

### Requirement: ffmpeg 預檢
系統 SHALL 在啟動時確認 ffmpeg 可在 PATH 中被呼叫，若找不到則顯示安裝說明並禁用錄製功能。

#### Scenario: ffmpeg 不存在
- **WHEN** 系統啟動時呼叫 `ffmpeg -version` 失敗
- **THEN** 顯示提示訊息「請安裝 ffmpeg 並加入 PATH」，開始按鈕設為不可用
