## ADDED Requirements

### Requirement: 選擇題顯示與作答

系統 SHALL 顯示題目（含 MathJax 公式）、四個選項、提交按鈕。使用者點選選項後立即顯示對錯與解析。

#### Scenario: 答對顯示綠色與解析

- **WHEN** 使用者選擇正確答案
- **THEN** 該選項變綠、其他變灰；下方顯示「正確！」與解析（含相關公式）

#### Scenario: 答錯顯示紅色與正解

- **WHEN** 使用者選擇錯誤答案
- **THEN** 所選變紅、正解變綠；下方顯示「再想想」與「正解解析」

### Requirement: 互動參數調整題（看圖理解題）

系統 SHALL 提供一種特殊題型：題目要求使用者透過調整參數讓 PDF 曲線達成指定條件（例如「讓常態分配的 95% 集中在 [40, 60]」），系統判斷是否達成。

#### Scenario: 達成目標條件

- **WHEN** 題目要求「將 σ 調到使 1σ 區間長度為 4」，使用者拖到 σ = 2
- **THEN** 系統判定達成，顯示綠色勾號與解析「1σ 區間長度 = 2σ，故 σ = 2 時長度為 4」

### Requirement: 題目按觀念標籤分組

系統 SHALL 將每題標記其所屬 chapter 與 concept（例如 chapter=continuous-distributions, concept=normal）。題目列表頁可依標籤篩選。

#### Scenario: 依觀念篩選

- **WHEN** 使用者在題目列表選擇「常態分配」標籤
- **THEN** 系統只列出 concept=normal 的題目

### Requirement: 每觀念至少 5 題

系統 SHALL 在 seed 階段為「機率分配本質」「PMF/PDF/CDF」「均勻分配」「常態分配」「指數分配」「無記憶性」六個觀念各準備至少 5 題（合計至少 30 題）。

#### Scenario: seed 後題庫筆數檢查

- **WHEN** 執行 `npm run seed` 後查詢 questions 資料表
- **THEN** 結果至少 30 筆，且每個 concept 至少 5 題
