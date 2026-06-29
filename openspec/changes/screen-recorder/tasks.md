## 1. 環境準備

- [x] 1.1 確認 ffmpeg 已安裝並可在 PATH 呼叫（執行 `ffmpeg -version`）
- [x] 1.2 建立專案資料夾與 `recorder.py` 空檔案
- [x] 1.3 安裝 pip 套件：mss、soundcard、sounddevice

## 2. ffmpeg 預檢與啟動驗證

- [x] 2.1 實作 `check_ffmpeg()` 函式，呼叫 `ffmpeg -version`，失敗時回傳錯誤訊息
- [x] 2.2 程式啟動時執行預檢，若失敗則顯示提示並禁用開始按鈕

## 3. 音訊擷取模組

- [x] 3.1 實作麥克風錄製函式（sounddevice），以背景執行緒持續寫入 numpy array
- [x] 3.2 實作 WASAPI loopback 錄製函式（soundcard），擷取喇叭輸出
- [x] 3.3 停止錄製後將兩個音訊 array 分別寫成暫存 WAV 檔

## 4. 螢幕擷取模組

- [x] 4.1 實作螢幕擷取函式（mss），以 15fps 截圖並寫入暫存資料夾
- [x] 4.2 MP3 模式下跳過截圖，只執行音訊錄製

## 5. 輸出編碼模組

- [x] 5.1 實作 `encode_mp4()` 函式：呼叫 ffmpeg 將影像序列＋混合音軌編碼為 MP4
- [x] 5.2 實作 `encode_mp3()` 函式：呼叫 ffmpeg 將混合音軌編碼為 MP3
- [x] 5.3 輸出檔名格式：`recording_YYYYMMDD_HHMMSS.mp4/.mp3`，存到腳本同目錄的 `recordings/` 資料夾
- [x] 5.4 編碼完成後清除暫存影像資料夾與暫存 WAV 檔

## 6. tkinter UI

- [x] 6.1 建立主視窗，包含模式選擇（MP4 / MP3 單選按鈕）
- [x] 6.2 加入開始／停止按鈕，按下開始後切換為停止狀態
- [x] 6.3 加入計時器標籤，錄製中每秒更新一次
- [x] 6.4 停止後顯示輸出檔案路徑

## 7. 整合測試

- [ ] 7.1 測試 MP4 模式：錄製 10 秒，確認輸出檔案有畫面＋聲音
- [ ] 7.2 測試 MP3 模式：錄製 10 秒，確認輸出為純音訊且可播放
- [x] 7.3 測試 ffmpeg 不存在時的錯誤提示流程
