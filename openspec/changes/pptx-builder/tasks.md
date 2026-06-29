# pptx-builder 任務清單

專門用 python-pptx 程式化產生 PowerPoint 簡報的通用框架。

## 1. 通用框架核心

- [x] 1.1 確認環境：Python 3.13 + python-pptx 1.0.2 已安裝
- [x] 1.2 建立 `theme.py`：顏色／字型／字級集中設定，支援多主題
- [x] 1.3 建立 `pptx_builder.py`：Deck 類別，全空白母片手動排版（跨機一致）
- [x] 1.4 實作版型方法：cover / section / bullets / two_column / image / table
- [x] 1.5 條列支援多層縮排（tuple 指定層級）、自動頁碼、標題強調條
- [x] 1.6 建立 `example_deck.py` 示範各版型，驗證可正常輸出

## 2. 主題

- [x] 2.1 內建 DEFAULT（商業藍）、ACADEMIC（暖色學術）
- [x] 2.2 新增 LIGHT_YELLOW（淡黃主色）：封面底色與文字色拆開，確保可讀
- [ ] 2.3 視需要再擴充主題（深色、簡約黑白等）

## 3. 應用：植樹造林區塊鏈「系統展示與評估」簡報

- [x] 3.1 讀取 forest-carbon-measurement 專案文件擷取架構與評估數據
- [x] 3.2 建立 `forest_carbon_deck.py`，用 LIGHT_YELLOW 主題
- [x] 3.3 系統展示：設計目標、七階段流程、技術堆疊、核心方法、三路徑、區塊鏈整合
- [x] 3.4 系統評估：評估方法、實測精度表、關鍵發現、成本與限制、現況、結語
- [x] 3.5 輸出 `output/forest_carbon_demo_eval.pptx`（17 頁）
- [ ] 3.6 待使用者插入實機截圖（投影片已留 4 個佔位提示）
- [ ] 3.7 待使用者回饋後微調內容與用字

## 4. 應用：兩性平等學校簡報

- [x] 4.1 建立 `gender_equality_deck.py`，使用 LIGHT_YELLOW 主題，共 15 頁
- [x] 4.2 輸出 `output/gender_equality.pptx`

## 5. 後續可擴充（未排程）

- [ ] 4.1 圖表版型（python-pptx 原生 chart：長條、折線、圓餅）
- [ ] 4.2 從 Markdown 或 JSON 大綱自動生成投影片
- [ ] 4.3 母片範本載入模式（template + 內容填入）
