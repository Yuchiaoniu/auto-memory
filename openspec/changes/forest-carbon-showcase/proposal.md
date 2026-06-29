## Why

此專案的研究成果目前分散在兩個頁面：風格老舊的暗底展示頁（index.rewritten.html）與資料豐富但僅限內部使用的 dashboard02。需要一個公開展示用的單頁靜態網頁，讓指導教授、審查委員或公眾能清晰閱讀論文核心內容，同時具備足夠的視覺專業度。

## What Changes

- 新建 `index.html`，以 dashboard02_new.html 的綠色設計系統為視覺框架
- 將 index.rewritten.html 全部 9 個章節（§1～§9）與 RQ/RO 區塊的文字與資料完整移植
- 頂部 header 加入章節快速跳轉導覽列
- KPI 數據列顯示 4 個核心指標（樣本數、Pipeline 數、PASS rate、API 成本）
- 各章節以白色卡片排版，左側彩色邊條區分卡片類型（RQ 藍、RO 橘、一般章節綠）
- 表格樣式升級為白底淺綠 header
- §3 演進旅程改用 timeline 組件排版
- PASS/FAIL 標記沿用綠紅色標

## Capabilities

### New Capabilities

- `showcase-page`: 公開展示用論文成果靜態頁面，整合 dashboard02 設計語言與 index.rewritten.html 全部內容

### Modified Capabilities

（無現有規格需修改）

## Impact

- 輸出：單一靜態檔案 `index.html`，無後端依賴，可直接部署至任何靜態主機
- 來源依賴：讀取 dashboard02_new.html（設計）與 index.rewritten.html（內容），兩者皆在 forest-carbon-measurement 專案目錄
- 不影響現有任何專案的執行中服務
