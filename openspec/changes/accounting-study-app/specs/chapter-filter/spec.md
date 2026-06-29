## ADDED Requirements

### Requirement: Filter problems by chapter
頁面 SHALL 提供章節篩選按鈕（全部／Ch04／Ch05／Ch06），點擊後只顯示對應章節的題目。

#### Scenario: Show all problems
- **WHEN** 使用者點擊「全部」按鈕
- **THEN** 所有題目全部顯示

#### Scenario: Filter to one chapter
- **WHEN** 使用者點擊某章節按鈕（如 Ch04）
- **THEN** 只顯示該章節的題目，其他章節題目隱藏

#### Scenario: Active filter button highlighted
- **WHEN** 使用者選擇某個篩選按鈕
- **THEN** 該按鈕顯示為已選中狀態（視覺區別於未選中按鈕）
