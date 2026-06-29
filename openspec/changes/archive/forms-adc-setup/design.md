## Context

Flask 後端需要以 `yuchiao.niu@gmail.com` 身份建立 Google Forms。gcloud 已安裝且已驗證，ADC 是最短路徑。

## Goals / Non-Goals

**Goals:**
- 一個 `!` 指令 + 一次瀏覽器「允許」完成所有授權
- Claude 負責 SCP 憑證、pip install、重啟 PM2，使用者不需再操作

**Non-Goals:**
- 不處理多使用者或 token 自動 refresh 以外的情境
- 不修改 `/analyze` 端點

## Decisions

**D1：使用 `google.auth.default(scopes=[...])` 取得憑證**
- ADC 優先查找順序：env var `GOOGLE_APPLICATION_CREDENTIALS` → gcloud ADC 檔案
- VM 上只要 `~/.config/gcloud/application_default_credentials.json` 存在即可，無需設定任何 env var
- token 過期時 google-auth 函式庫自動用 refresh_token 換新，不需額外程式碼

**D2：ADC 憑證檔從本機 SCP 到 VM**
- 本機路徑：`%APPDATA%\gcloud\application_default_credentials.json`
- VM 路徑：`~/.config/gcloud/application_default_credentials.json`
- 只需做一次；換機器時重新執行一次 `gcloud auth application-default login` 再 SCP

**D3：forms_creator.py 邏輯回歸直接呼叫 Forms API**
- 移除 GAS URL 呼叫，移除 Service Account 邏輯
- 結構與第一版相同，只有認證方式改變

## Risks / Trade-offs

- **ADC 憑證含 refresh_token**，屬敏感資訊，VM 上須 `chmod 600`
- **憑證綁定個人帳號**：換人使用要重新授權；Prototype 階段可接受

## Migration Plan

1. 使用者執行：`gcloud auth application-default login --scopes=...`（瀏覽器點「允許」）
2. Claude SCP 憑證到 VM，建立目錄並設定 chmod 600
3. 更新程式碼，VM pip install，重啟 PM2
4. 外部自檢

## Open Questions

（無）
