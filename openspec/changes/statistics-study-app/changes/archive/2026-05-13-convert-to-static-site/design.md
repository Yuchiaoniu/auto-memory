## Context

`build-mvp-rv-continuous` 已實作完整 Node.js + Express + SQLite 後端，含 5 個 API 與兩張資料表。但實際檢視後發現後端對核心學習目標（看教材 → 拖滑桿理解 → 做題目）並無價值——題目的正解、解析本來就要 ship 到前端才能呈現，後端只是多繞一圈。

GitHub Pages 提供免費靜態託管 + HTTPS + 全球 CDN，網址形式為 `https://<user>.github.io/<repo>/`。

## Goals / Non-Goals

**Goals:**
- repo push 到 GitHub 即可線上瀏覽（無需 build 步驟）
- 任何裝置開瀏覽器都能用，無需 Node.js 環境
- 保留所有教材內容、互動圖表、選擇題判分
- 路徑可移植（不寫死 `/statistics-study-app/`，未來 fork 改名也能用）

**Non-Goals:**
- 不做使用者註冊或雲端同步（永遠單機體驗）
- 不引入前端框架 / build pipeline（Vite、Webpack 等）
- 不維持 Node.js 版本作為「正式版」（直接刪掉）
- 不做 PWA、離線快取（瀏覽器原生 HTTP 快取已足夠）

## Decisions

### 決策 1：扁平化到 repo 根（不用 /docs，也不用 /public）

**選擇**：把所有靜態檔案放在 repo 根目錄。

**理由**：
- GitHub Pages 預設從根部署，最少設定
- `index.html` 在根 = 進入 repo 連結即首頁
- 開發時直接 `npx serve .` 也能跑

**替代方案**：
- `/docs/`：適合「源碼 + 文件分離」的專案，但本專案本身就是靜態網站，沒必要分離
- `/public/`：Vue/React 慣例，但本專案是 vanilla，沒理由保留

### 決策 2：相對路徑而非 `<base href>`

**選擇**：所有 HTML 內的資源連結改成相對路徑（`./css/main.css`、`../css/main.css`），不使用 `<base href>`。

**理由**：
- 相對路徑天然可移植：fork 後改 repo 名也不用改 HTML
- `<base href>` 會影響所有錨點（連 `<a href="#section">` 也受影響），坑多
- 各章節頁在 `chapters/` 子目錄下，用 `../` 引用根目錄資源直觀

### 決策 3：題庫整份載入一次而非分觀念載入

**選擇**：頁面開啟時 fetch 整份 `data/questions.json`（約 30 題、< 20KB），所有觀念共用一份。

**理由**：
- 30 題壓縮後不到 10KB，多次 fetch 反而浪費
- 整份載入後可在前端篩選觀念，反應更快
- 未來題庫長到上百題再考慮拆分

### 決策 4：判分邏輯放 quiz.js（不混淆）

**選擇**：`quiz.js` 拿到題目時就已經含 `correct_index` 與 `explanation`，使用者點選時直接比對。

**理由**：
- 靜態網頁本來就「秘密無處可藏」，答案放前端是合理選擇
- 不再需要往返後端 → 反應立即
- 程式碼變短：刪除 fetch /api/attempts 整段

**權衡**：玩家可以開 DevTools 偷看答案——接受。本工具是給自己用的，不是考試系統。

### 決策 5：保留 openspec/ 在 repo 根

**選擇**：openspec 目錄與 .gitignore 保留在根，但加入 `.nojekyll` 避免 Pages 處理出錯。

**理由**：
- openspec 是專案的「規劃 source of truth」，需要 git 追蹤
- 不會被 GitHub Pages 當成內容呈現（路徑 `/openspec/` 沒有 index.html）
- `.nojekyll` 確保所有檔案原樣 serve，不被 Jekyll 處理

## Risks / Trade-offs

- **風險：未來想加紀錄功能要重寫** → 緩解：可用 localStorage 補救（不需重建後端），且本來就不是 must-have
- **風險：題目正解外露** → 接受：自我練習工具不需要保密；若日後有公開測驗需求再考慮
- **風險：GitHub Pages 部署延遲（push 後幾分鐘才生效）** → 接受：日常使用不影響
- **權衡：刪除 npm + SQLite 等於砍掉之前寫的後端程式碼** → 接受：先前的 spec 工作仍保存在 openspec/changes/build-mvp-rv-continuous/，文獻價值仍在

## Migration Plan

1. 建立新分支（或直接在現有 working tree 操作）
2. 移動檔案：`public/*` → 根目錄
3. 刪除：`src/`, `migrations/`, `seed/`, `data/app.db*`, `node_modules/`, `package*.json`
4. 把題庫 `seed/questions.json` 內容移到新位置 `data/questions.json`
5. 修改 HTML 路徑（絕對 → 相對、刪除 weak-points 連結）
6. 改寫 `quiz.js`：移除 fetch /api/* 全部呼叫
7. 刪除 `progress.js` 並從 `index.html` 移除引用
8. 新增 `.nojekyll`
9. 更新 README
10. 本機驗證 (`npx serve .`)
11. push 到 GitHub、啟用 Pages、用網址驗證

Rollback：撤回 commit 即可，因為這是 git-tracked 變更。

## Open Questions

- 是否需要在 GitHub 設定 custom domain？（暫不需要，預設 `*.github.io` 子網址就夠用）
- 是否要寫 GitHub Actions 做進階部署？（不需要，main 分支自動 deploy 已足夠）
- 開放 fork 給同學使用時要加 LICENSE 嗎？（建議 MIT，但獨立 PR 處理）
