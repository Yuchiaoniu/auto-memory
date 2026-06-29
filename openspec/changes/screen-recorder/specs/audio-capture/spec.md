## ADDED Requirements

### Requirement: 錄製麥克風輸入
系統 SHALL 透過 sounddevice 錄製預設麥克風輸入，以 numpy array 形式儲存至暫存 WAV 檔。

#### Scenario: 成功錄製麥克風
- **WHEN** 使用者按下開始錄製
- **THEN** 系統開始持續從預設麥克風擷取音訊，直到按下停止

#### Scenario: 找不到麥克風裝置
- **WHEN** 系統啟動時偵測不到麥克風
- **THEN** 顯示錯誤提示，但仍可以純喇叭模式繼續錄製

### Requirement: 錄製系統喇叭輸出（WASAPI loopback）
系統 SHALL 透過 soundcard 的 WASAPI loopback 機制錄製系統喇叭輸出，儲存至獨立暫存 WAV 檔。

#### Scenario: 成功錄製喇叭輸出
- **WHEN** 使用者按下開始錄製
- **THEN** 系統同步錄製喇叭播放的所有聲音

#### Scenario: 找不到 loopback 裝置
- **WHEN** 系統啟動時找不到可用的 loopback 裝置
- **THEN** 顯示錯誤訊息，提示使用者確認音效卡設定

### Requirement: 混合麥克風與喇叭為單一音軌
系統 SHALL 在停止錄製後，透過 ffmpeg amerge 將麥克風與喇叭兩個暫存 WAV 混合成單一音軌。

#### Scenario: 混合成功
- **WHEN** 停止錄製後兩個暫存 WAV 皆存在
- **THEN** ffmpeg 混合兩軌並輸出到最終檔案
