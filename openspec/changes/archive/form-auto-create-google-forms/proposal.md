## Why

現有系統已能將 .docx 文件分析為結構化 JSON，但使用者仍需手動把欄位一一建入 Google Forms。本功能讓系統在分析完成後直接呼叫 Google Forms API 自動建立表單，消除這段人工操作。

## What Changes

- 新增 GCP Service Account 並啟用 Google Forms API 與 Google Drive API
- 新增後端 endpoint `POST /create-form`：接收欄位 JSON、建立 Google Form、分享給指定帳號、回傳連結
- 前端在 JSON 結果下方新增「建立 Google 表單」按鈕，顯示建立後的編輯連結與填寫連結

## Capabilities

### New Capabilities

- `google-forms-creator`：呼叫 Forms API 將 JSON 欄位陣列轉換為 Google Form，支援七種欄位類型
- `drive-share`：呼叫 Drive API 將新建表單以 writer 權限分享給 `yuchiao.niu@gmail.com`

### Modified Capabilities

- `doc-upload-interface`：分析結果區塊新增「建立 Google 表單」按鈕與連結顯示區

## Impact

- 執行環境：現有 Flask 後端（Python 3.x，GCP VM bootnode）
- 新增依賴：`google-api-python-client`、`google-auth`
- GCP 資源：`level-up-374308` 專案需啟用 Forms API 與 Drive API，建立 Service Account
- Service Account 金鑰 JSON 存放於 VM `~/form-automation-system/service-account.json`（不進 git）
- Google Forms API 免費，無額外費用
