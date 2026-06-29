## Context

Windows 上的錄製工具通常要麼太重（OBS）、要麼不支援同時錄製喇叭輸出，或需要複雜安裝流程。目標是一個單檔 Python 腳本，只依賴少數 pip 套件和系統已有的 ffmpeg。

## Goals / Non-Goals

**Goals:**
- 同時錄製麥克風＋喇叭輸出，混合成單一音軌
- 可切換 MP4（螢幕＋音訊）和 MP3（純音訊）兩種模式
- tkinter UI，操作只需開始／停止兩個按鈕
- 輸出檔案自動以時間戳命名，存到指定資料夾

**Non-Goals:**
- 跨平台支援（Windows 專屬，WASAPI loopback 不可移植）
- 多螢幕選擇、區域擷取、攝影機輸入
- 打包成 exe 或內建 ffmpeg

## Decisions

**D1：音訊擷取用 soundcard + sounddevice**
- soundcard 封裝了 WASAPI loopback，可直接讀取喇叭輸出，是目前 Python 生態裡最乾淨的做法
- sounddevice 負責麥克風輸入，兩者都以 numpy array 輸出，方便混合

**D2：麥克風與喇叭先分別錄成暫存 WAV，再由 ffmpeg 混合**
- 替代方案：即時混合後再傳給 ffmpeg
- 選暫存 WAV 的原因：避免即時混合的時序問題，ffmpeg amerge 濾鏡合併兩軌更穩定可靠

**D3：螢幕擷取用 mss，逐幀存成暫存影像序列，交給 ffmpeg 編碼**
- 替代方案：用 OpenCV + numpy 做即時編碼串流
- 選 mss 的原因：mss 擷取速度快、相依少；影像序列方式讓音視訊同步更容易控制

**D4：ffmpeg 透過 subprocess 呼叫，不使用 ffmpeg-python 套件**
- 減少套件依賴，ffmpeg 指令本身已足夠簡單直接

**D5：UI 使用 tkinter，錄製邏輯在背景執行緒運行**
- tkinter 為 Python 內建，不需額外安裝
- 錄製用 threading.Thread 跑，避免 UI 凍結

## Risks / Trade-offs

- **音視訊同步偏移** → 以錄製開始時間戳對齊兩個暫存檔，ffmpeg 合併時指定相同起始點
- **幀率不穩定** → mss 盡力維持目標幀率（預設 15fps），低配機器可能掉幀，但 Meeting 用途可接受
- **soundcard 找不到 loopback 裝置** → 啟動時先做裝置偵測，找不到時顯示錯誤訊息提示使用者檢查音效卡設定
- **ffmpeg 不在 PATH** → 啟動時呼叫 `ffmpeg -version` 做預檢，失敗時提示安裝說明

## Migration Plan

無需遷移，全新獨立腳本，放到任何目錄執行即可。
移機器時：安裝 Python、pip install 三個套件、安裝 ffmpeg 加入 PATH。
