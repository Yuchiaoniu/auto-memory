## Why

`build-mvp-rv-continuous` 完成後檢視使用情境，發現幾件事讓「Node.js + SQLite 後端」變得不必要：

1. **練習題的學習價值來自即時回饋**：送出 → 看到對/錯 → 看到解析。這個循環完全可以在前端完成，不需要寫資料庫。
2. **不需要跨裝置同步紀錄**：本來規劃的「我的弱點」靠長期累積答題紀錄產生價值，但使用者明確表態紀錄不是必要的——學完當下就忘了沒關係，反正下次練習題還會出現。
3. **想部署到 GitHub Pages**：靜態網頁可以永久免費線上、手機平板都能用、改一改 fork 給同學也方便。Node.js 後端在 GitHub Pages 跑不起來。

簡而言之：**保留教材 + 互動圖表 + 即時判分的選擇題**，把後端拿掉、把追蹤功能拿掉，換來部署簡單、永久可用、跨裝置可開。

## What Changes

- **BREAKING**：刪除所有後端程式碼（`src/server.js`、`src/db.js`、`src/seed.js`、`migrations/`、`data/app.db`）
- **BREAKING**：刪除 `package.json`、`package-lock.json`、`node_modules/`（不再有 npm 依賴）
- **BREAKING**：刪除 `/my/weak-points.html` 頁面與後端弱點 API
- **BREAKING**：刪除首頁章節卡片上的「作答進度」顯示與 `progress.js`
- 題庫從 `seed/questions.json` 搬到 `data/questions.json`（位於 repo 根，可被前端直接 fetch）
- `public/` 目錄內容上移到 repo 根目錄（GitHub Pages 預設從根部署）
- 所有 HTML 中的絕對路徑 `/css/...` `/js/...` `/api/...` 改為相對路徑
- `quiz.js` 改成前端判分：fetch 整份題庫一次、依 `correct_index` 直接比對、不再 POST 任何 API
- README 重寫：刪除 npm 相關指令，加入「本機開發用 npx serve」與「推到 GitHub 啟用 Pages」兩段
- 加入 `.nojekyll` 空檔（防止 GitHub Pages 把底線開頭資料夾排除）

## Capabilities

### New Capabilities

- `static-site`: 純靜態網站架構與部署（GitHub Pages、本機 dev server、相對路徑、no-jekyll）

### Modified Capabilities

- `quiz-engine`: 改為前端判分（移除「POST /api/attempts」依賴）
- `content-rv`、`content-continuous`、`interactive-charts`: 保持邏輯不變，但路徑與資源載入方式調整
- `progress-tracking`: **移除整個 capability**（不再追蹤）
- `web-server`: **移除整個 capability**（不再有後端）

## Impact

- **檔案結構**：扁平化、根目錄即站點根
- **部署**：可直接 push 到 GitHub，Settings → Pages → main branch → root，幾分鐘後即線上可用
- **開發體驗**：本機開發改用 `npx serve` 或 VS Code Live Server，不需要 `npm install`
- **未來擴充**：若日後需要紀錄，可改用 localStorage 或外掛 Firebase / Supabase，無需重建後端
- **此前的 MVP**：`build-mvp-rv-continuous` 仍保留在 openspec/changes/，archive 時再決定是否歸檔
