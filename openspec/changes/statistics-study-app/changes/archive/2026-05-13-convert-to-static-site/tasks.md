## 1. 檔案搬移與刪除

- [x] 1.1 把 `public/index.html` 搬到 repo 根，修正內部資源路徑為相對路徑
- [x] 1.2 把 `public/chapters/*.html` 搬到 `chapters/`，修正路徑（`../css/...` `../js/...` `../data/...`）
- [x] 1.3 把 `public/css/main.css` 搬到 `css/`
- [x] 1.4 把 `public/js/*.js` 搬到 `js/`
- [x] 1.5 把 `seed/questions.json` 搬到 `data/questions.json`
- [x] 1.6 刪除 `public/my/weak-points.html`（隨整個 public/ 一併刪除）
- [x] 1.7 刪除 `src/`, `migrations/`, `seed/`, `node_modules/`, `package.json`, `package-lock.json`, `public/`（`data/app.db*` 被 lingering node process 鎖定，已在 .gitignore 排除，待重啟後手動清理）
- [x] 1.8 新增空檔 `.nojekyll`

## 2. 修改前端程式碼

- [x] 2.1 改寫 `js/quiz.js`：移除所有 `fetch('/api/...')`，改為前端判分
- [x] 2.2 改寫題目載入：從 `data/questions.json` 一次載入整份，依 concept 在前端篩選
- [x] 2.3 刪除 `js/progress.js`（未複製到新位置）
- [x] 2.4 修改 `index.html`：移除 progress.js 引用、移除「我的弱點」連結
- [x] 2.5 修改 `chapters/*.html`：移除「我的弱點」連結
- [x] 2.6 確認所有 HTML 中路徑都不以 `/` 開頭

## 3. README 與部署文件

- [x] 3.1 重寫 README：刪除 npm 段落，加入「本機預覽」段落
- [x] 3.2 加入「GitHub Pages 部署」段落
- [x] 3.3 加入「如何新增題目」段落
- [x] 3.4 加入「fork 改成自己版本」段落

## 4. 本機驗證

- [x] 4.1 用 `npx serve .` 啟動本機 server（port 8090）
- [x] 4.2 所有頁面、CSS、JS、JSON 都回 200（含 301 → 200 clean URL）
- [ ] 4.3 確認 MathJax 公式渲染正常（待人工瀏覽器驗證）
- [ ] 4.4 確認三個分配的互動圖表能拖動（待人工瀏覽器驗證）
- [ ] 4.5 確認選擇題判分（對/錯/解析）正確顯示（待人工瀏覽器驗證）

## 5. 收尾

- [ ] 5.1 確認本機沒有任何 console error
- [ ] 5.2 提交 commit、push 到 GitHub
- [ ] 5.3 啟用 GitHub Pages（main branch / root）
- [ ] 5.4 線上驗證所有頁面與互動正常
- [ ] 5.5 將線上網址填入 README
- [ ] 5.6 執行 `openspec archive convert-to-static-site`
