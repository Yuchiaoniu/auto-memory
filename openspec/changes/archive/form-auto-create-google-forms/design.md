## Context

系統已有 Flask 後端運行於 GCP bootnode（`35.227.93.38`），透過 nginx 代理於 `https://forest-carbon.duckdns.org/forms/`。Service Account 使用既有 GCP 專案 `level-up-374308`。

## Goals / Non-Goals

**Goals:**
- 以 Service Account 自動建立 Google Form 並分享給指定帳號
- 支援七種欄位類型（text / textarea / number / date / radio / checkbox / select）
- 前端一鍵觸發，顯示編輯連結與填寫連結

**Non-Goals:**
- 不支援 Google Workspace 網域帳號或多使用者授權
- 不儲存建立紀錄或歷史表單清單
- 不支援更新已建立的表單

## Decisions

**決策 1：架構**

```
前端（GitHub Pages）
    │  POST /forms/create-form  { fields: [...] }
    ▼
Flask /create-form
    │
    ├─▶ google-forms-creator.py
    │       │  Forms API batchUpdate
    │       ▼
    │   Google Form（owned by Service Account）
    │
    └─▶ drive-share.py
            │  Drive API permissions.create
            ▼
        分享給 yuchiao.niu@gmail.com（writer）
            │
            ▼
    回傳 { edit_url, respond_url }
```

**決策 2：欄位類型對應**

| JSON field_type | Forms API questionItem type | 備註 |
|---|---|---|
| text | SHORT_ANSWER | — |
| textarea | PARAGRAPH | — |
| number | SHORT_ANSWER | 加 numberValidation（INTEGER 或 NUMBER）|
| date | DATE | — |
| radio | MULTIPLE_CHOICE | — |
| checkbox | CHECKBOX | — |
| select | DROP_DOWN | — |

**決策 3：Service Account 金鑰管理**

金鑰 JSON 存於 VM `~/form-automation-system/service-account.json`，不加入 git（`.gitignore` 已含 `*.json` 需確認排除此檔）。Flask 以環境變數 `GOOGLE_APPLICATION_CREDENTIALS` 或直接讀路徑載入。

**決策 4：分享方式**

Forms API 建立的表單歸 Service Account 所有，無法直接轉移擁有者（跨帳號限制）。改以 Drive API 加入 writer 權限讓 `yuchiao.niu@gmail.com` 可編輯，表單擁有者仍為 Service Account，不影響功能使用。

## Risks / Trade-offs

- **Service Account Drive 空間累積**：每次建立都產生新表單，長期會累積在 Service Account 的 Drive 裡；緩解：定期手動清理，或後續加刪除 API
- **Forms API 配額**：預設每分鐘 300 次請求，正常使用不會觸及
- **金鑰洩漏風險**：`service-account.json` 絕不進 git，部署時由 SCP 手動傳至 VM
