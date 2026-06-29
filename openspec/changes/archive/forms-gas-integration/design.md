## Context

Flask 後端需要建立 Google Forms。Service Account 與 OAuth 使用者憑證方案均有阻礙（前者 API 限制，後者需要手動授權且難以複製）。Google Apps Script 以部署者的 Google 帳號身份執行，適合作為無狀態的 Forms 建立中介層。

## Goals / Non-Goals

**Goals:**
- Flask 只需一個 `GOOGLE_FORMS_GAS_URL` 環境變數即可建立 Google Forms
- 複製步驟：部署 GAS（約 5 分鐘）+ 填入 URL，不需要 GCP Console

**Non-Goals:**
- 不處理 GAS 的認證機制（GAS Web App 設定「所有人可存取」，無需 token）
- 不修改 `/analyze` 端點

## Decisions

**D1：GAS Web App 存取權設定為「所有人」（不驗證呼叫者）**
- Prototype 階段可接受；URL 本身即為存取控制（URL 不公開即可）
- 若日後需要保護，可在 GAS 加入 secret token 比對

**D2：Flask 端使用 `requests` 套件呼叫 GAS**
- 移除 `google-api-python-client`、`google-auth`、`google-auth-oauthlib`（三個套件都不再需要）
- `requests` 輕量、已是 Python 生態系標準套件

**D3：GAS 程式碼存放於 `gas/create_form.js`（純文件用途）**
- GAS 無法透過 CI/CD 自動部署，存放於 repo 僅作為「貼上用程式碼」的版本控制
- 使用者手動建立 Apps Script 並貼入

**D4：欄位類型對應沿用原有邏輯**
- text/number → `addTextItem()`
- textarea → `addParagraphTextItem()`
- date → `addDateItem()`
- radio → `addMultipleChoiceItem()`
- checkbox → `addCheckboxItem()`
- select → `addListItem()`

## Risks / Trade-offs

- **GAS URL 洩漏** → 任何人都能建立表單（表單建在部署者帳號下）；Prototype 可接受，日後可加 token
- **GAS 執行逾時**（6 分鐘上限）→ 一般表單不會觸及，可忽略
- **GAS 免費配額**：每天 6,000 次執行，Prototype 不會超過

## Migration Plan

1. 寫 `gas/create_form.js`
2. 改寫 `src/forms_creator.py`
3. 更新 `requirements.txt`
4. 刪除 `oauth_setup.py`
5. 使用者在 Google Drive 建立 Apps Script，部署為 Web App，取得 URL
6. VM `.env` 加入 `GOOGLE_FORMS_GAS_URL=<URL>`
7. VM pip install、重啟 PM2、外部自檢

## Open Questions

（無）
