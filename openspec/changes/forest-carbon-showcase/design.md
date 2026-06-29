## Context

來源資料：
- **設計模板**：`forest-carbon-measurement/dashboard02_new.html`（654 行）— 綠色設計系統，含 CSS 變數、header、stats 卡片、卡片組件、toolbar
- **內容來源**：`forest-carbon-measurement/journey-rewrite/index.rewritten.html`（568 行）— 暗底頁面，含 RQ/RO 區塊與 §1～§9 全部章節

輸出目標：單一 `index.html`，部署至靜態主機（無後端），放在 `forest-carbon-showcase/` 資料夾根目錄。

## Goals / Non-Goals

**Goals:**
- 完整移植 index.rewritten.html 的所有文字與資料（不遺漏任何章節）
- 套用 dashboard02 的 CSS 設計系統（顏色、字型、卡片、陰影）
- 頁面可獨立運作（無 JS 框架依賴，只用原生 JS 做章節折疊）
- 各章節有錨點，可從 header 導覽列直接跳轉

**Non-Goals:**
- 不做搜尋／篩選功能（dashboard02 的 toolbar 不移植）
- 不連接後端 API 或資料庫
- 不做 RWD 行動版優化（以桌面版為主）
- 不處理 RQ3 / RO3（原始頁面以 `display:none` 隱藏，維持隱藏）

## Decisions

### D1：CSS 架構 — 直接移植 dashboard02 CSS 變數，不引入外部 CSS 框架

dashboard02 已定義完整的 CSS 變數系統（`--green-*`、`--bg`、`--text`、`--shadow-*`），足以支撐所有設計需求。直接複用這組變數，避免引入 Tailwind 或 Bootstrap 等額外依賴。

### D2：卡片左邊條顏色規則

| 類型 | 邊條顏色 | CSS |
|------|---------|-----|
| RQ（研究問題）| 藍色 | `#3b82f6` |
| RO（研究目標）| 橘色 | `#f97316` |
| 一般章節（§1～§9）| 綠色 | `var(--green-600)` |
| aside 引言 | 黃色 | `#eab308` |

### D3：§3 演進旅程改用 timeline 組件

原始頁面用 `.timeline` CSS 類別做左側線條，設計系統風格偏暗底。新頁面改為白色卡片堆疊的 timeline，每個階段一張卡片，左側加綠色圓點標記，視覺上更清晰。

### D4：§4 實驗結果表格 — PASS/FAIL 顏色沿用，表頭改為淺綠

原始的 `.green/.yellow/.red/.gray` 行底色標記直接保留（顏色值微調以配合白底）。表頭改為 `var(--green-100)` 底色、`var(--green-800)` 字色，與整體設計一致。

### D5：隱藏內容（display:none）維持不顯示

原始頁面的 Caveat 區塊、RQ3、RO3 皆以 `display:none` 隱藏，新頁面保持相同處理，不刪除 HTML，便於日後取消隱藏。

## Risks / Trade-offs

- **外部連結有效性**：頁面含多個 Google Drive 影片連結與 Verra 官方 PDF 連結，這些連結的有效性取決於原始資料，移植時只照搬，不驗證。
- **字型載入**：Inter 字型依賴 Google Fonts CDN，離線環境會 fallback 到 system-ui，不影響可讀性。
- **長頁面捲動體驗**：全頁約 500+ 行 HTML，建議 header 導覽列加 `position: sticky`，讓使用者隨時可跳轉章節。
