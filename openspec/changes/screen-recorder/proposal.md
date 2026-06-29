## Why

在 Windows 上缺乏一個輕量、無需安裝的錄製工具，能同時捕捉螢幕畫面、麥克風和系統喇叭輸出，滿足 Meeting 錄音和影片內容留存兩種日常需求。

## What Changes

- 新增一個 Python 單檔工具 `recorder.py`，提供 tkinter 視窗介面
- 支援 MP4 模式（螢幕＋麥克風＋喇叭）和 MP3 模式（純音訊）兩種錄製模式
- 透過 WASAPI loopback 錄製系統喇叭輸出
- 使用 ffmpeg 進行編碼，ffmpeg 不打包、需預先安裝並加入 PATH

## Capabilities

### New Capabilities
- `audio-capture`: 同時錄製麥克風輸入與系統喇叭輸出（WASAPI loopback），並混合成單一音軌
- `screen-capture`: 以固定幀率擷取螢幕畫面
- `recording-ui`: tkinter 視窗，提供模式切換、開始／停止錄製、計時顯示
- `output-encoding`: 呼叫 ffmpeg 將音視訊素材編碼輸出為 MP4 或 MP3

### Modified Capabilities

## Impact

- 新增獨立 Python 腳本，不影響現有任何專案
- 外部依賴：ffmpeg（PATH）、pip 套件 mss、soundcard、sounddevice
- 僅支援 Windows（WASAPI loopback 為 Windows 專屬機制）
