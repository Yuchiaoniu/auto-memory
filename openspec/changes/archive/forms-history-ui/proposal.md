## Why

目前每次建立 Google 表單後，連結只在當次會話顯示，重新整理就消失。使用者需要一個持久的歷史清單，可隨時查閱所有建立過的表單，並以分析的檔案名稱作為識別。

## What Changes

- `index.html`：加入「已建立表單」歷史清單區塊，以 localStorage 持久化
- 建立表單時以 .docx 檔名（去副檔名）作為表單標題
- 提供「清除所有記錄」按鈕

## Capabilities

### New Capabilities

- `forms-history`: 以 localStorage 儲存並展示所有已建立表單的連結與檔案名稱

### Modified Capabilities

（無）

## Impact

- 只改 `index.html`，後端不動
- localStorage key：`form_history`
