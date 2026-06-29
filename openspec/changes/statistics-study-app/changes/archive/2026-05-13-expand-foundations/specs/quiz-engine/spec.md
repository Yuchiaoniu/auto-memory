## ADDED Requirements

### Requirement: 易度較低題目

系統 SHALL 為現有 6 個 concept 各新增 2-4 道基礎題（測詞彙、符號意義、直觀理解），插入於原有題目之前，使學習者由淺入深。

#### Scenario: 進入觀念題組

- **WHEN** 使用者作答「常態分配」題組
- **THEN** 前 4 題為基礎題（如「μ 代表什麼」、「σ 代表什麼」、「標準常態 N(0,1) 的意義」、「曲線形狀」），後 5 題為原本中階題

### Requirement: `continuous-foundation` 觀念題組

系統 SHALL 新增 `continuous-foundation` 觀念並提供至少 8 道題目，涵蓋 PDF 三性質、CDF 定義、F(b)−F(a)、左/中/右尾、E(X) 與 Var(X) 積分版、≤/< 等價。

#### Scenario: 在連續型分配頁顯示

- **WHEN** 使用者捲動到「選擇題 · 連續型基礎」區段
- **THEN** 顯示至少 8 題並可正確判分

#### Scenario: 題庫總量

- **WHEN** 載入 `data/questions.json`
- **THEN** 總題數至少 56 題（probability-essence 8 + pmf-pdf-cdf 8 + continuous-foundation 8 + uniform 8 + normal 9 + exponential 8 + memoryless 7）
