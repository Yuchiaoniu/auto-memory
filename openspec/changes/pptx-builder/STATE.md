# pptx-builder — 現況快照

## 目前做到哪

通用 python-pptx 框架已建好並驗證可跑。已用它產出林業碳匯測量系統
「系統設計」簡報（修訂版 v2，淡黃主色，14 頁，含兩張實機截圖）。

## 手上正在處理

系統設計簡報已交付，等使用者回饋。實驗設計章節尚未定稿，待補。

## 下一步

1. 使用者開檔檢視 `output/forest_carbon_system_design.pptx`，回饋內容/用字。
2. 待實驗設計定稿後，新增「系統評估」段落投影片。
3. 視需要擴充圖表版型（python-pptx 原生 chart）。

## 產出物

- `output\forest_carbon_system_design.pptx`（主交付，系統設計 14 頁）
- `screenshots\upload.png`、`screenshots\dashboard.png`（實機截圖）
- `output\demo.pptx`（框架示範）

## 系統設計簡報內容（已與使用者逐輪確認的定稿）

- 精度：單棵 ±20–25%、樣區平均 ±15%（對齊 Verra VCS）
- 七階段流程；③用 OpenCV 偵測信用卡規格參照物；④Pl@ntNet+iNaturalist+Gemini 取信心最高
- 三大支柱（一核心管線存全部元數據／二修正因子帳本／三上鏈工作分離）
- 部署：GitHub 動態抓腳本、Google Drive 存影片與關鍵幀、Besu 跨美東/美中/美西
- 智能合約 CarbonCredit.sol 規格；雙路徑（Path 0 皮尺／Path 1 AI）
- 網站三頁 + 兩張截圖；網址 forest-carbon.duckdns.org 與 GitHub Pages
