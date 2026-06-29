# pptx-builder — 長期查詢／對照資料

## 程式位置（生效中）

- 程式庫資料夾：`C:\Users\yuchi\pptx-builder\`
- `theme.py`：主題設定（顏色/字型/字級）。改這支就能換風格。
- `pptx_builder.py`：核心 Deck 類別與版型方法。
- `example_deck.py`：各版型示範。
- `forest_carbon_deck.py`：植樹造林區塊鏈「系統展示與評估」簡報腳本。
- 輸出資料夾：`C:\Users\yuchi\pptx-builder\output\`

## 環境

- Python 3.13.0；python-pptx 1.0.2（已安裝，import 名稱是 `pptx`）。
- 執行方式：`cd C:\Users\yuchi\pptx-builder; python forest_carbon_deck.py`

## 框架設計重點

- 全部用空白版面 `slide_layouts[6]` 手動畫，不依賴範本母片 → 跨機一致。
- 預設 16:9（13.333 x 7.5 吋）。
- 每個版型方法回傳 slide 物件，要細調可再抓回來改。
- 條列 items 可放字串或 `(文字, 縮排層級)` tuple。

## Theme 欄位（淡黃需求催生的拆分）

- `bg`：內容頁底色。`cover_bg`：封面/章節頁底色。`on_cover`：封面/章節頁文字色。
- `primary`：內容頁標題與表頭色。`accent`：強調條。`text`/`muted`：內文/次要。
- 教訓：淡黃當底配白字會看不清 → 封面底色與文字色一定要分成兩個欄位。

## 內建主題

- `DEFAULT`：商業藍（深藍底白字）。
- `ACADEMIC`：暖褐學術風。
- `LIGHT_YELLOW`：淡黃底(0xFBF0B8) + 深褐字(0x4A3F1A)，標題深褐金(0x6B5712)，強調琥珀(0xD9A806)。

## 版型方法速查

| 方法 | 用途 |
|---|---|
| `cover(title, subtitle)` | 封面，主色滿版 |
| `section(title)` | 章節分隔頁，置中大標 |
| `bullets(title, items)` | 條列，支援多層縮排 |
| `two_column(title, L, R, left_head, right_head)` | 左右兩欄對照 |
| `image(title, path, caption)` | 單張圖片置中 |
| `table(title, rows, header=True)` | 表格，首列為表頭 |
| `save(path)` | 輸出 .pptx |

## forest_carbon 簡報用到的關鍵數據（來源：forest-carbon-measurement 專案）

- 精度目標：單棵 ±20–25%，樣區 ≥25 棵平均 ±5%（對齊 Verra VCS）。
- 已上鏈 17 棵皆有 manual tape、誤差 ≤15%。
- 代表案例 5813：opencv 重抽 29.1cm 誤差 11.5%，優於歷史值 30cm(14.9%)。
- 成本：Gemini Flash 1500/日、Pl@ntNet 500/日，皆免費。
- 服務：VM 35.227.93.38 pm2 online；GroundTruth 合約 0xC9a4…Aaec。
