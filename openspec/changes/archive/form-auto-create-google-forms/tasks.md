## 1. GCP Service Account 設定（手動操作，需在 GCP Console）

- [x] 1.1 在 level-up-374308 專案啟用 Google Forms API
- [x] 1.2 在 level-up-374308 專案啟用 Google Drive API
- [x] 1.3 建立 Service Account（名稱：form-automation-sa），下載 JSON 金鑰
- [x] 1.4 SCP 將 JSON 金鑰上傳至 VM `~/form-automation-system/service-account.json`
- [x] 1.5 確認 `.gitignore` 已排除 `service-account.json`

## 2. 依賴套件更新

- [x] 2.1 在 `requirements.txt` 加入 `google-api-python-client` 與 `google-auth`
- [x] 2.2 在 VM venv 執行安裝

## 3. Google Forms 建立模組（src/forms_creator.py）

- [x] 3.1 實作 `build_service()` 函式，從 `GOOGLE_APPLICATION_CREDENTIALS` 載入 Service Account 憑證
- [x] 3.2 實作 `field_to_item(field)` 函式，將 JSON 欄位物件轉換為 Forms API item 格式（含七種類型對應）
- [x] 3.3 實作 `create_form(title, fields)` 函式：建立空白表單後以 batchUpdate 加入所有題目，回傳 `{ form_id, edit_url, respond_url }`
- [x] 3.4 實作 `share_form(form_id)` 函式：呼叫 Drive API 以 writer 權限分享給 `yuchiao.niu@gmail.com`，失敗時只記錄警告

## 4. Flask endpoint（app.py）

- [x] 4.1 新增 `POST /create-form` route：接收 `{ fields: [...], title: "..." }`，呼叫 `create_form` 與 `share_form`，回傳 `{ edit_url, respond_url, error }`

## 5. 前端更新（index.html）

- [x] 5.1 分析結果區塊下方加入「建立 Google 表單」按鈕（預設隱藏）
- [x] 5.2 分析成功後顯示按鈕；點擊後呼叫 `/create-form`，顯示載入狀態
- [x] 5.3 建立成功後顯示編輯連結與填寫連結；失敗時顯示錯誤訊息

## 6. 部署與驗證

- [ ] 6.1 git commit 並推送到 GitHub（排除 service-account.json）
- [ ] 6.2 VM 執行 git pull 並重啟 form-automation
- [ ] 6.3 外部自檢：從 `https://forest-carbon.duckdns.org/forms/create-form` 發送 POST，確認回傳 edit_url 與 respond_url
- [ ] 6.4 從 GitHub Pages 前端點擊「建立 Google 表單」，確認表單出現在 yuchiao.niu@gmail.com 的 Google Drive
