## Context

純靜態網站，目標使用者為國中生（12-15歲）及其數位家教。無後端需求，所有內容以 JSON 資料檔儲存，JavaScript 動態渲染。可部署至 GitHub Pages。整體設計參考 Grade 4 English Tutor 專案架構（同為靜態教育網站）。

## Goals / Non-Goals

**Goals:**
- 零伺服器成本的靜態網站，一鍵部署 GitHub Pages
- 涵蓋七至九年級五大學習模組
- 題目與內容以 JSON 資料檔維護，不需修改 HTML
- 行動裝置友善（RWD）

**Non-Goals:**
- 使用者帳號、學習記錄持久化（localStorage 暫存即可）
- 後端 API 或資料庫
- 完整課本內容（版權限制，僅提供公版或自編示例）
- 即時 AI 批改（可選加分項，不列入核心範圍）

## Decisions

### 決策 1：純靜態 vs. 輕量後端
採用純靜態 HTML/CSS/JS，無 Node.js/Python 後端。
- **理由**：與現有 Grade 4 English Tutor 一致，部署簡單，無維護負擔。
- **替代方案**：Next.js SSG — 過度工程，此規模不需要。

### 決策 2：內容資料格式
使用 `data/*.json` 儲存課文、題目、修辭例句。
- **理由**：非技術人員（家教）可直接編輯 JSON 新增內容，不需碰 HTML。
- **替代方案**：Markdown + front-matter — 需要 build step。

### 決策 3：單頁應用 vs. 多頁
多頁（每個模組一個 HTML 檔）+ 共用 `common.js`。
- **理由**：靜態主機友善，URL 清楚，SEO 較佳。
- **替代方案**：SPA with hash routing — 增加 JS 複雜度無明顯好處。

### 決策 4：樣式框架
使用 Tailwind CSS（CDN play版）。
- **理由**：快速原型，無 build step，與 Grade 4 English Tutor 風格一致。

### 決策 5：字型
Noto Sans TC（Google Fonts）確保中文正確顯示。

## Risks / Trade-offs

- **版權風險**：課本原文受版權保護 → 僅使用公版古文（先秦至清）及自編現代文示例
- **JSON 維護門檻**：格式錯誤導致頁面空白 → 加入基本 JSON schema 驗證說明
- **離線使用**：依賴 Google Fonts/CDN → 可接受，目標環境有網路
