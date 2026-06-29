## ADDED Requirements

### Requirement: 動態現金流序列輸入
投資評估頁 SHALL 提供動態新增現金流列的介面，使用者輸入初始投資（負值）及各期現金流後，系統計算 NPV 與 IRR。

#### Scenario: 新增現金流列
- **WHEN** 使用者點擊「新增期間」
- **THEN** 表格新增一列，使用者可輸入該期現金流量

#### Scenario: 刪除現金流列
- **WHEN** 使用者點擊某列的「刪除」按鈕
- **THEN** 該列從表格移除，NPV/IRR 重新計算

### Requirement: 即時計算 NPV 與 IRR
填入折現率與現金流後，系統 SHALL 即時顯示 NPV 與 IRR，並以顏色區分可行性（NPV > 0 顯示綠色，NPV < 0 顯示紅色）。

#### Scenario: NPV 為正
- **WHEN** 使用者輸入折現率 10%、現金流 [-100000, 30000, 40000, 50000, 30000]
- **THEN** 系統計算並顯示 NPV 正值（綠色）與對應 IRR

#### Scenario: IRR 無法計算
- **WHEN** 現金流全為正值（例如 [10000, 20000, 30000]，沒有初始負投資）
- **THEN** 系統在 IRR 欄位顯示「無法計算（現金流符號未改變）」

### Requirement: NPV 折現示意圖
投資評估頁 SHALL 以 Chart.js 長條圖顯示各期現金流，並疊加一條顯示不同折現率下 NPV 變化的折線圖。

#### Scenario: 繪製 NPV 圖
- **WHEN** 使用者完成現金流輸入並計算
- **THEN** 圖表顯示各期現金流長條，以及 NPV vs. 折現率折線，IRR 點以垂直虛線標注
