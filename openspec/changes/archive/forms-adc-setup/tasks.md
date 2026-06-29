## 1. 使用者執行（一次性）

- [ ] 1.1 執行授權指令（在 Claude Code 輸入框輸入）：
  `! gcloud auth application-default login --scopes=https://www.googleapis.com/auth/forms.body,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform`
  瀏覽器開啟後選 yuchiao.niu@gmail.com 帳號，點「允許」

## 2. 程式碼修改

- [x] 2.1 改寫 `src/forms_creator.py`：用 `google.auth.default(scopes=[...])` 取得憑證，呼叫 Forms API 建立表單並分享
- [x] 2.2 更新 `requirements.txt`：移除 `google-auth-oauthlib`；確認含 `google-api-python-client>=2.100.0` 與 `google-auth>=2.23.0`；移除 forms 用途的 `requests`（若其他地方無需則移除）
- [x] 2.3 刪除 `gas/` 資料夾

## 3. VM 部署

- [ ] 3.1 SCP 本機 ADC 憑證到 VM：`%APPDATA%\gcloud\application_default_credentials.json` → `~/.config/gcloud/application_default_credentials.json`
- [ ] 3.2 VM 建立目錄並設定權限：`mkdir -p ~/.config/gcloud && chmod 600 ~/.config/gcloud/application_default_credentials.json`
- [ ] 3.3 SCP 更新後的 `src/forms_creator.py` 與 `requirements.txt` 到 VM
- [ ] 3.4 VM venv 重新安裝依賴：`venv/bin/pip install -r requirements.txt`
- [ ] 3.5 重啟 PM2：`pm2 restart form-automation`

## 4. 驗證

- [ ] 4.1 外部自檢：POST `https://forest-carbon.duckdns.org/forms/create-form`，帶測試欄位 JSON，確認回傳 `edit_url` 與 `respond_url`
- [ ] 4.2 從 GitHub Pages 前端點擊「建立 Google 表單」，確認表單出現在 yuchiao.niu@gmail.com Google Drive
