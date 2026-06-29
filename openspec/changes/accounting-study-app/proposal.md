## Why

學生需要一個可隨時複習的會計學練習題靜態網頁，涵蓋調整分錄、永續盤存、定期盤存等核心章節，方便在無網路後端依賴的環境下練習。

## What Changes

- 建立全新靜態網頁 `accounting-study-app`（純 HTML/CSS/JS）
- 第一批收錄 5 題：Ch04 調整分錄 3 題、Ch05 永續盤存 1 題、Ch06 定期盤存 1 題
- 每題含章節標題、題目說明、題目內文，留空答案區供後續填入解答
- 支援章節篩選，方便學生依章節複習

## Capabilities

### New Capabilities

- `problem-display`：顯示會計練習題（章節、題號、題目說明、題目內文、空白答案區）
- `chapter-filter`：依章節篩選題目

### Modified Capabilities

（無）

## Impact

- 新建 `C:\Users\yuchi\openspec\changes\accounting-study-app\` 下的靜態網頁檔案
- 無後端、無外部 API 依賴
- 部署方式：直接開啟 index.html 或部署至 GitHub Pages
