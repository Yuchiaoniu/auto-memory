## Context

現有財務管理資訊系統目錄下有兩個 app：
- `finance-study-app`（Node.js + SQLite，port 3000）：學習平台，提供筆記與題庫
- `financial-teaching-app`（Node.js，2026/4 遺留，未完成）

`fmis-app` 作為第三個網站，定位為「輸入數字即時驗算」的純工具集，與前兩者互補而不重疊。

## Goals / Non-Goals

**Goals:**
- 七頁工具網站，每頁對應一個財務章節的核心計算
- 零依賴——直接開 index.html 即可使用，不需要任何伺服器或 npm install
- 財務計算邏輯全部在前端 JS 實作，精確度達小數點後兩位
- Chart.js 繪製互動圖表（折現示意圖、機率分布圖、代理成本曲線）
- 台積電 2015 範例數據預埋於財務報表分析頁，一鍵載入

**Non-Goals:**
- 不做資料持久化（不需要 DB 或 localStorage）
- 不做使用者登入或帳號系統
- 不做 Excel 上傳（financial-teaching-app 已有）
- 不做行動版 RWD 優化（桌機版為主）

## Decisions

### 決策 1：純靜態而非 Node.js

**選擇**：純 HTML + CSS + JS，不建 server.js

**理由**：finance-study-app 已佔 port 3000，再開一個 Node.js app 需要管理 port 衝突與啟動步驟。純靜態直接雙擊 index.html，無啟動成本，對學生最友善。

**捨棄方案**：Node.js + Express（同現有 finance-study-app 架構）

---

### 決策 2：Tailwind CSS via CDN

**選擇**：`<script src="https://cdn.tailwindcss.com">` + 少量自訂 CSS

**理由**：零 build step，與 nttu11402 Django 版本使用相同視覺語言，日後互相參照不會有風格落差。

**捨棄方案**：Bootstrap（需額外 JS bundle）、自訂 CSS（開發成本高）

---

### 決策 3：計算邏輯集中於 `js/finance.js`

**選擇**：所有財務公式（NPV、IRR 迭代、TVM、戈登模型、EAR）集中在 `js/finance.js`，各頁面 import 後呼叫

**理由**：便於日後加測試、便於與 nttu11402 的 `FinanceCalculator` 類別對照驗證

---

### 決策 4：IRR 使用牛頓法迭代

**選擇**：牛頓-拉弗森法（Newton-Raphson），最多 1000 次迭代，收斂門檻 1e-7

**理由**：numpy-financial 的 IRR 同樣使用此方法，結果可互相驗證

## Risks / Trade-offs

- **CDN 斷線** → 無網路時頁面樣式失效。緩解：核心計算邏輯不依賴 CDN，只有樣式受影響
- **IRR 無解** → 某些現金流組合（如全正值）IRR 不存在，頁面需顯示「無法計算 IRR」而非當機
- **EAR 連續複利** → 使用 e^r - 1 計算，需與離散版本在 UI 上明確區分

## Migration Plan

1. 建立 `fmis-app/` 資料夾結構
2. 實作 `js/finance.js` 計算核心
3. 實作共用 `css/style.css`
4. 依序實作七個 HTML 頁面
5. 以瀏覽器手動開啟 index.html 驗證

無部署步驟（純靜態，本機直接開啟）。

## Open Questions

（無）
