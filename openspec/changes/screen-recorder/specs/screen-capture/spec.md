## ADDED Requirements

### Requirement: 以固定幀率擷取全螢幕畫面
系統 SHALL 使用 mss 以 15fps 擷取主螢幕畫面，存成暫存影像序列供 ffmpeg 編碼。

#### Scenario: MP4 模式下擷取畫面
- **WHEN** 使用者選擇 MP4 模式並按下開始錄製
- **THEN** 系統以 15fps 持續截圖並寫入暫存資料夾

#### Scenario: MP3 模式下不擷取畫面
- **WHEN** 使用者選擇 MP3 模式
- **THEN** 系統跳過畫面擷取，只錄音訊

### Requirement: 暫存影像序列管理
系統 SHALL 在錄製結束後清除暫存影像序列，避免佔用磁碟空間。

#### Scenario: 編碼完成後清除暫存
- **WHEN** ffmpeg 完成編碼並輸出最終 MP4
- **THEN** 系統刪除暫存影像資料夾及其中所有檔案
