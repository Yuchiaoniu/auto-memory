## Why

學生在統計學考試中**必須會查 Z 表與 t 表**，否則就算觀念都懂、計算題也算不下去。目前網站雖然解釋了：
- Z 化公式與五種查表轉換（在連續型分配頁）
- 經驗法則完整數值（在常態分配段）
- 用 Z 表算機率的解題步驟（在 glossary 公式卡）

但仍缺乏**實際可用的查表工具**。剛看完 PDF 附表才發現這是空缺：

1. 學生想驗證解題時，沒辦法在網站上「即時查到 P(0 ≤ Z ≤ 1.96) = 0.475」
2. t 分配在網站完全沒有獨立內容（只在 glossary 提過一次），但**期末考小樣本檢定一定會考**
3. 自由度（df）、臨界值（critical value）等核心概念沒有正式解釋

新增兩個互動查表工具一次補齊：
- **Z 表查詢**：輸入 z 值 → 即時回傳 P(0 ≤ Z ≤ z) 與圖示陰影
- **t 表查詢**：輸入自由度 ν 與右尾面積 α → 回傳臨界值 $t_{\nu, \alpha}$

放在現有 glossary（速查頁）下方，使用者隨手切到速查頁就能用。

## What Changes

- 新增 `lookup-tables` capability：兩個互動查表元件
  - Z 表查詢工具（`js/ztable-lookup.js`）：精確計算 PDF 積分（用 erf 函數），不需查靜態表
  - t 表查詢工具（`js/ttable-lookup.js`）：用 hardcoded 表資料 + 線性插補
- 修改 `glossary` capability：在頁面下方加「📊 查表工具」section，含兩個工具
- 修改 `glossary` 專詞段第 8 類「抽樣與推論」：補上「自由度」「臨界值」「t 分配」三個專詞的詳細解釋
- 修改 `glossary` 公式段：加入「t 分配與 Z 分配對照」公式卡
- 在連續型分配頁的「Z 表的結構」段尾加一行連結，引導讀者跳到 glossary 查表工具

## Capabilities

### New Capabilities

- `lookup-tables`：互動式統計查表工具（Z 表、t 表），支援即時計算與視覺化呈現

### Modified Capabilities

- `glossary`：新增「查表工具」section、補強 t 分配相關專詞與公式卡

## Impact

- **新檔案**：`js/ztable-lookup.js`、`js/ttable-lookup.js`
- **修改檔案**：`chapters/glossary.html`、`chapters/continuous-distributions.html`、`css/main.css`
- **無依賴變動**：仍是純靜態 vanilla JS
- **教育價值**：把網站從「教材」延伸成「能直接幫忙解題的工具」
