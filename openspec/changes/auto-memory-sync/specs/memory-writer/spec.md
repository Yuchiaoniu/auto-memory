## ADDED Requirements

### Requirement: 寫入記憶檔案
系統 SHALL 根據 Haiku 回傳的 JSON 陣列，建立或更新對應的 memory/*.md 檔案，並同步更新 MEMORY.md 索引。

#### Scenario: 建立新記憶檔
- **WHEN** Haiku 回傳 `action: "create"` 且指定新檔名
- **THEN** 在 memory/ 目錄建立新 .md 檔，內容含正確的 frontmatter（name、description、type）

#### Scenario: 更新現有記憶檔
- **WHEN** Haiku 回傳 `action: "update"` 且指定已存在的檔名
- **THEN** 覆寫該 .md 檔的完整內容（UTF-8 無 BOM）

#### Scenario: MEMORY.md 索引同步
- **WHEN** 任何記憶檔被新增或更新
- **THEN** MEMORY.md 的索引列表同步反映最新狀態（由 Haiku 在 content 中一併更新）
