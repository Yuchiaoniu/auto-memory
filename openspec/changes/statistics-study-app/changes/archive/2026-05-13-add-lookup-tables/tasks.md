## 1. Z 表互動工具（js/ztable-lookup.js）

- [x] 1.1 建立 erf 函數（Abramowitz-Stegun 近似），計算 P(0 ≤ Z ≤ z)
- [x] 1.2 Canvas 繪製標準常態 PDF 曲線
- [x] 1.3 z 輸入框（範圍 [-4, 4]、步進 0.01）
- [x] 1.4 機率類型切換按鈕（半邊 / 左尾 / 右尾 / 雙側中段）
- [x] 1.5 陰影區域依模式動態更新
- [x] 1.6 結果區顯示機率值 4 位小數
- [x] 1.7 視窗縮放自適應 + z 值垂直虛線標記

## 2. t 表互動工具（js/ttable-lookup.js）

- [x] 2.1 把 PDF 附表 2 的 t 表資料 hardcode 進 JS 物件（37 列 × 8 欄 = 296 個值）
- [x] 2.2 ν 輸入框（1 到 200）、α 選擇器（8 個常用值）
- [x] 2.3 ν 未列出時用線性插補
- [x] 2.4 結果顯示 $t_{\nu, \alpha}$，並列出對應 Z 值供對比
- [x] 2.5 雙尾快捷按鈕（單尾/雙尾 95%、單尾/雙尾 99%）
- [x] 2.6 提示文字：「ν → ∞ 時 t → Z」、提示插補狀態

## 3. 嵌入 glossary 頁

- [x] 3.1 在「公式速查」段之後加入 `<h2 id="lookup">📊 查表工具</h2>`
- [x] 3.2 加入 Z 表查詢區塊（內含元件容器）
- [x] 3.3 加入 t 表查詢區塊（內含元件容器）
- [x] 3.4 在頁面頂端 anchor-bar 加入「📊 查表工具」連結
- [x] 3.5 引入 `js/ztable-lookup.js` 與 `js/ttable-lookup.js`

## 4. 補強 glossary 內容

- [x] 4.1 第 8 段「抽樣與推論」新增 4 個專詞：自由度、t 分配（詳細）、臨界值、信賴水準
- [x] 4.2 公式段新增「t 分配對應」公式類別含兩張卡（t 統計量、t 與 Z 對比）

## 5. 連續型分配頁的引導

- [x] 5.1 在「Z 表的結構」段尾加 note-soft 連結到 glossary#lookup

## 6. CSS

- [x] 6.1 lookup-tool 容器樣式
- [x] 6.2 lookup-big-number 結果突顯
- [x] 6.3 lookup-result-grid 雙欄並排
- [x] 6.4 lookup-input / lookup-modes / lookup-quick 控制區樣式

## 7. 驗證、commit、push、archive

- [x] 7.1 JS 檔本機載入 200 OK
- [x] 7.2 HTML wiring 驗證（2 個容器元素）
- [x] 7.3 openspec validate 通過
- [ ] 7.4 commit、push（本任務後續執行）
- [ ] 7.5 線上版驗證（push 後）
- [ ] 7.6 `openspec archive add-lookup-tables`（本任務最後執行）
