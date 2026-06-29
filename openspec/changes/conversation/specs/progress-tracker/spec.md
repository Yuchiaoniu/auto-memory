## ADDED Requirements

### Requirement: 本機進度記錄
系統 SHALL 使用 localStorage 記錄每個情境的練習次數與最後練習日期，不需要帳號或網路。

#### Scenario: 完成情境後自動儲存
- **WHEN** 使用者完成一個情境的所有步驟
- **THEN** 系統在 localStorage 將該情境的完成次數加一，並更新最後練習日期

#### Scenario: 重新開啟網站後進度保留
- **WHEN** 使用者關閉並重新開啟網站
- **THEN** 進度頁面顯示上次記錄的練習次數與日期，與關閉前一致

### Requirement: 進度總覽頁面
系統 SHALL 提供一個進度頁面，列出所有情境的練習狀態。

#### Scenario: 查看進度頁面
- **WHEN** 使用者點擊導覽列的「我的進度」
- **THEN** 系統顯示所有情境清單，每個情境旁顯示完成次數與最後練習日期（或「尚未練習」）

### Requirement: 重置進度
系統 SHALL 提供重置按鈕，讓照護者或使用者清除所有進度記錄。

#### Scenario: 點擊重置按鈕
- **WHEN** 使用者在進度頁面點擊「重置所有進度」並確認
- **THEN** 系統清除 localStorage 中的所有進度資料，進度頁面顯示全部「尚未練習」
