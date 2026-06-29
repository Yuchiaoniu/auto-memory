## ADDED Requirements

### Requirement: 輸出 MP4 檔案
系統 SHALL 呼叫 ffmpeg 將影像序列與混合音軌編碼為 MP4，輸出至使用者指定或預設資料夾。

#### Scenario: 成功輸出 MP4
- **WHEN** 停止錄製且模式為 MP4
- **THEN** ffmpeg 輸出 `recording_YYYYMMDD_HHMMSS.mp4` 到輸出資料夾

### Requirement: 輸出 MP3 檔案
系統 SHALL 呼叫 ffmpeg 將混合音訊編碼為 MP3。

#### Scenario: 成功輸出 MP3
- **WHEN** 停止錄製且模式為 MP3
- **THEN** ffmpeg 輸出 `recording_YYYYMMDD_HHMMSS.mp3` 到輸出資料夾

### Requirement: 輸出檔案自動命名
系統 SHALL 以錄製開始時的時間戳自動命名輸出檔案，格式為 `recording_YYYYMMDD_HHMMSS`。

#### Scenario: 檔案命名
- **WHEN** 錄製停止後開始編碼
- **THEN** 輸出檔案名稱包含錄製開始時間戳，不覆蓋舊檔案
