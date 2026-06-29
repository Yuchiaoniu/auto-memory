## ADDED Requirements

### Requirement: 分析頁面內容並儲存
Claude SHALL 讀取 `bookshelf_current.png`，以繁體中文產生頁面摘要，並存入 `bookshelf_notes/page_NNN.md`。

#### Scenario: 新頁面分析
- **WHEN** 截圖完成後，使用者要求分析
- **THEN** Claude 讀取截圖，輸出包含章節標題、重點摘要的 markdown，存入對應頁碼檔案

#### Scenario: 重複讀取已分析頁面
- **WHEN** 使用者要求複習某頁（如「複習第 125 頁」）
- **THEN** Claude 直接讀取 `bookshelf_notes/page_125.md`，不重新執行腳本

### Requirement: 筆記檔案格式
每個 `page_NNN.md` SHALL 包含：頁碼、章節名稱、重點條列摘要。

#### Scenario: 檔案命名
- **WHEN** 分析第 N 頁
- **THEN** 存為 `bookshelf_notes/page_NNN.md`（三位數補零，如 page_125.md）
