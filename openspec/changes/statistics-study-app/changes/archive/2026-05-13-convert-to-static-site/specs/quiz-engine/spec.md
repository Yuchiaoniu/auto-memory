## MODIFIED Requirements

### Requirement: 選擇題顯示與作答

系統 SHALL 顯示題目（含 MathJax 公式）、四個選項、提交按鈕。使用者點選選項後立即在前端判分並顯示對錯與解析（無需後端呼叫）。

#### Scenario: 答對顯示綠色與解析

- **WHEN** 使用者選擇正確答案
- **THEN** 該選項變綠、其他變灰；下方顯示「正確！」與解析（含相關公式）

#### Scenario: 答錯顯示紅色與正解

- **WHEN** 使用者選擇錯誤答案
- **THEN** 所選變紅、正解變綠；下方顯示「再想想」與「正解解析」

#### Scenario: 完全前端判分

- **WHEN** 使用者作答
- **THEN** 不發出任何 HTTP 請求（除最初載入 questions.json 之外），判分邏輯完全在瀏覽器執行

## REMOVED Requirements

### Requirement: 題目按觀念標籤分組

**Reason**：靜態化後不再有「題目列表頁與篩選器」這個獨立頁面；觀念分組改為在章節頁直接以 section 區分。

**Migration**：章節頁面已以 section 分組呈現各觀念的題目，使用者無需另一個篩選介面。

### Requirement: 每觀念至少 5 題

**Reason**：題庫筆數要求改寫在 static-site 章節（已透過 `data/questions.json` 提供 30 題，每觀念 5 題），不再以「資料庫筆數」形式驗收。

**Migration**：見 `data/questions.json` 內容。
