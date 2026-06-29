## MODIFIED Requirements

### Requirement: 分析結果區塊顯示建立表單按鈕與連結
分析完成顯示 JSON 結果後，系統 SHALL 在結果區塊下方呈現「建立 Google 表單」按鈕；點擊後呼叫後端 `/create-form`，成功時顯示編輯連結與填寫連結。

#### Scenario: 點擊建立按鈕成功
- **WHEN** 使用者點擊「建立 Google 表單」按鈕
- **THEN** 按鈕顯示載入狀態，後端回傳後顯示兩個連結（編輯用／填寫用）

#### Scenario: 建立失敗
- **WHEN** 後端回傳 error 欄位
- **THEN** 顯示友善錯誤訊息，按鈕恢復可點擊狀態

#### Scenario: 尚未分析時按鈕不顯示
- **WHEN** 頁面剛載入或尚未完成分析
- **THEN** 建立表單按鈕不可見
