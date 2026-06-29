# screen-recorder memory.md

## 檔案路徑

| 名稱 | 路徑 |
|------|------|
| 主程式 | C:\Users\yuchi\screen-recorder\recorder.py |
| 輸出資料夾 | C:\Users\yuchi\screen-recorder\recordings\ |
| 暫存資料夾 | C:\Users\yuchi\screen-recorder\_rec_tmp\（錄製中存在，完成後自動刪除） |

## 已安裝套件

| 套件 | 版本 | 用途 |
|------|------|------|
| ffmpeg | 8.1.1（winget Gyan.FFmpeg） | 編碼 MP4/MP3 |
| faster-whisper | 1.2.1 | 音訊轉文字 |
| mss | - | 截圖 |
| soundcard | - | WASAPI loopback（喇叭聲音） |
| sounddevice | - | 麥克風 |
| Pillow | - | PNG 影格處理 |

faster-whisper medium 模型快取位置：
C:\Users\yuchi\.cache\huggingface\hub\models--Systran--faster-whisper-medium

## 主要設定值（recorder.py）

| 常數 | 值 | 說明 |
|------|----|------|
| SAMPLE_RATE | 44100 | 音訊取樣率 |
| CHANNELS | 2 | 立體聲 |
| FPS | 5 | MP4 截圖幀率（2026-06-11 從 15 降為 5） |

## 重要技術決策

### 音訊錄製改為逐段寫磁碟（2026-06-11）
原本設計是把所有 frames 累積在 mic_frames / spk_frames 記憶體陣列，停止時才整批寫入。
一小時錄音會在 RAM 累積 ~2.5 GB float32 資料，
p.concatenate 時記憶體暴漲到 3–4 GB 導致卡死。
修法：兩個音訊執行緒改成邊錄邊寫 WAV 到磁碟（每 0.1 秒寫一次），停止後直接讓 ffmpeg 讀磁碟上的 WAV。

### ffmpeg 安裝來源
安裝在本機（非 GCP VM），用 winget install Gyan.FFmpeg 安裝。
植樹造林區塊鏈專案的 ffmpeg 是裝在 GCP VM 上，與本機無關。

## 音訊轉文字指令範例

`python
from faster_whisper import WhisperModel
model = WhisperModel('medium', device='cpu', compute_type='int8')
segments, info = model.transcribe('audio.mp3', beam_size=5)
for seg in segments:
    print(f'[{seg.start:.1f}s - {seg.end:.1f}s] {seg.text.strip()}')
`
輸出 txt 存到同資料夾，檔名與音檔相同（副檔名換成 .txt）。
若要更高準確率，換用 large-v3 模型（需下載 ~3 GB）。