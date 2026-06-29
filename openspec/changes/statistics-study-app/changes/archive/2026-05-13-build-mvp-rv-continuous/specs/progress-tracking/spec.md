## ADDED Requirements

### Requirement: 答題記錄持久化

系統 SHALL 在使用者每次提交答案後，將「題目 ID、選擇的選項、是否正確、時間戳」寫入 SQLite 的 `attempts` 資料表。

#### Scenario: 答完一題後紀錄寫入

- **WHEN** 使用者提交一題的作答
- **THEN** 系統呼叫 POST /api/attempts，後端寫入新一筆 attempt 記錄

### Requirement: 薄弱觀念識別

系統 SHALL 提供「我的弱點」頁面，列出最近 30 天答錯率最高的前 5 個觀念，並提供「立刻練習」按鈕。

#### Scenario: 弱點頁面

- **WHEN** 使用者進入 `/my/weak-points`
- **THEN** 系統依各 concept 的近 30 天錯誤率排序，顯示前 5 名與「練習此觀念」連結

### Requirement: 章節完成度顯示

系統 SHALL 在章節首頁的每張觀念卡片右上角顯示「已練習題數 / 總題數」與「正確率 %」。

#### Scenario: 完成度即時顯示

- **WHEN** 使用者完成一道常態分配題
- **THEN** 重新整理章節首頁，常態分配卡片的完成度數字 +1

### Requirement: 答題記錄資料表結構

系統 SHALL 在 SQLite 建立 `attempts` 資料表，欄位至少包含：id (PK)、question_id (FK)、selected_option、is_correct (boolean)、created_at (timestamp)。

#### Scenario: 資料表結構驗證

- **WHEN** 啟動後檢查 schema
- **THEN** `attempts` 表存在且具備上述五個欄位
