## 1. 新建 form-automation-system/memory.md

- [x] 1.1 建立 memory.md，記錄四代憑證演進（SA → OAuth → GAS → ADC）與棄用原因
- [x] 1.2 記錄現行架構：Flask + SQLite + bcrypt、ADC 建立 Google Forms、nginx proxy、PM2
- [x] 1.3 記錄服務 URL（https://forest-carbon.duckdns.org/forms/）、預設帳號（admin/admin123）

## 2. 更新 form-automation-system/tasks.md

- [x] 2.1 加入「ADC VM 部署」任務群組，包含以下步驟：
  - SCP 本機 ADC 憑證到 VM（%APPDATA%\gcloud\application_default_credentials.json → ~/.config/gcloud/）
  - VM 建立目錄並設定權限
  - SCP 更新後的 forms_creator.py 與 requirements.txt 到 VM
  - VM venv 重新安裝依賴
  - 重啟 PM2：pm2 restart form-automation
  - 外部自檢：POST /forms/create-form 確認回傳 edit_url 與 respond_url
  - GitHub Pages 端對端驗證

## 3. 更新 form-automation-system/STATE.md

- [x] 3.1 重寫 STATE.md：說明 user auth 已完成部署、ADC 部署尚未執行、下一步是執行 ADC VM 部署

## 4. 封存子專案

- [x] 4.1 封存 6 個子專案至 archive/（form-auto-create-google-forms、forms-oauth-credentials、forms-gas-integration、forms-adc-setup、forms-history-ui、forms-user-auth）
