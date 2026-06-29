## Why

財務管理課程已有 Node.js 學習平台（finance-study-app）提供筆記與題庫，但缺乏讓學生實際輸入數字、即時驗算財務公式的計算工具。現有的 Django FMIS（nttu11402）功能完整但需要 Python 環境，啟動成本高。本次建立純靜態工具網站，讓學生不需執行任何伺服器就能練習 Ch01–Ch08 七章的核心計算。

## What Changes

- 在 `C:\Users\yuchi\OneDrive\Desktop\三下課程\財務管理資訊系統\fmis-app\` 建立全新靜態網站
- 七個獨立工具頁面，涵蓋財務報表分析、TVM、投資評估、證券評價、風險模擬、治理模擬
- 共用 Tailwind CSS（CDN）+ Chart.js（CDN）樣式與圖表，零 node_modules、零後端
- 財務報表分析頁預埋台積電 2015 範例數據，可一鍵載入

## Capabilities

### New Capabilities

- `dashboard`: 首頁儀表板，列出七個工具入口與章節對應說明
- `financial-statement`: Ch03 財務報表分析——手動輸入 BS/IS 科目金額，自動計算流動比率、負債比率、純益率、ROE 等十項比率
- `tvm-calculator`: Ch02 貨幣時間價值——PV/FV/PMT/NPER/EAR 計算機，輸入任三個已知數解第四個未知數
- `investment-evaluation`: Ch07/Ch08 NPV/IRR 投資評估——動態新增現金流序列，即時計算 NPV 與 IRR，含折現示意圖
- `securities-valuation`: Ch05 證券評價——債券定價（面額/票面利率/市場利率）與戈登成長模型股票評價
- `risk-simulation`: Ch04 風險報酬模擬——輸入多個情境（機率 + 報酬率），輸出 E(r)、標準差 σ、變異係數 CV，含機率分布圖
- `governance-simulation`: Ch01 公司治理模擬——滑桿調整績效獎金強度與監督強度，即時顯示代理成本曲線

### Modified Capabilities

（無）

## Impact

- 新增資料夾 `fmis-app/` 於財務管理資訊系統目錄下，不影響現有 finance-study-app
- 純前端，無後端依賴，無資料庫
- 依賴 CDN：Tailwind CSS、Chart.js（需要網路連線）
