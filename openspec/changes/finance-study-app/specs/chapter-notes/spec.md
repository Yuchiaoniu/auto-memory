## ADDED Requirements

### Requirement: 顯示章節筆記列表
筆記頁面 SHALL 在載入時呼叫 `/api/chapters` 取得章節列表，並渲染為可點擊的章節選單。

#### Scenario: 載入筆記頁
- **WHEN** 使用者開啟 `notes.html`
- **THEN** 頁面顯示所有章節標題選單，預設選中第一章

### Requirement: 顯示章節筆記內容
系統 SHALL 根據選中章節呼叫 `/api/notes?chapter_id=<n>`，將各節標題與內容渲染至頁面。

#### Scenario: 切換章節
- **WHEN** 使用者點擊章節選單中的某章
- **THEN** 右側內容區更新為該章所有節的標題與內容，無需重新載入頁面

### Requirement: 筆記節可折疊
每個筆記節 SHALL 支援點擊標題以展開或折疊內容，預設全部展開。

#### Scenario: 折疊筆記節
- **WHEN** 使用者點擊某節標題
- **THEN** 該節內容收起，標題旁箭頭圖示改變方向

#### Scenario: 展開筆記節
- **WHEN** 使用者再次點擊已折疊的節標題
- **THEN** 該節內容展開
