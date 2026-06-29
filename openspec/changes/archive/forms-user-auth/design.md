## Context

Flask 後端運行在 VM，前端是 GitHub Pages 靜態頁面，兩者跨域。Session cookie 需要設定 `SameSite=None; Secure` 才能在跨域情境下運作。

## Goals / Non-Goals

**Goals:**
- 登入後跨裝置/跨瀏覽器都能看到自己的表單記錄
- 上傳分析後自動建立表單，不需要額外按鈕

**Non-Goals:**
- 不做使用者註冊（只有預設 admin 帳號）
- 不做權限分級

## Decisions

**D1：Flask 內建 session（signed cookie），不用 flask-session**
- 只需設定 `SECRET_KEY`，無需額外 Redis/DB
- session 儲存 `user_id`，每次請求驗證

**D2：跨域 session cookie 設定**
- `SESSION_COOKIE_SAMESITE = "None"`
- `SESSION_COOKIE_SECURE = True`
- nginx 已處理 HTTPS，Flask 不需要額外設定

**D3：`/analyze` 合併分析 + 建立表單**
- 原本兩個步驟（分析 → 按鈕建立）合為一個 POST
- 未登入時回傳 401
- 回傳格式：`{ fields, form_id, edit_url, respond_url, truncated }`

**D4：密碼用 bcrypt hash**
- `bcrypt.hashpw(password.encode(), bcrypt.gensalt())`
- 初始化 DB 時寫入預設帳號

**D5：CORS 允許憑證（credentials）**
- nginx 需加 `Access-Control-Allow-Credentials: true`
- 前端 fetch 加 `credentials: "include"`

## Risks / Trade-offs

- **Secret key 若洩漏** → session 可被偽造；存在 .env，不進 git
- **單一預設帳號** → 無法多人隔離；Prototype 可接受

## Migration Plan

1. 新增 `src/db.py`
2. 修改 `app.py`
3. 更新 `requirements.txt`（加 bcrypt）
4. 更新 nginx 設定（CORS credentials）
5. 更新 `index.html`（SPA 登入流程）
6. VM 建立 data 目錄，pip install，重啟 PM2
7. 端對端測試

## Open Questions

（無）
