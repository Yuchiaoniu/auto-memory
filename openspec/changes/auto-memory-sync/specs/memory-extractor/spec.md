## ADDED Requirements

### Requirement: Haiku API 分析壓縮摘要
系統 SHALL 將壓縮摘要與現有 MEMORY.md 索引一起送給 Haiku API，請其判斷是否有新資訊需要寫入記憶。

#### Scenario: 摘要含新資訊
- **WHEN** Haiku 判斷摘要中有需要持久化的新資訊
- **THEN** Haiku 回傳 JSON 陣列，包含 file、action、content 三個欄位

#### Scenario: 摘要無新資訊
- **WHEN** Haiku 判斷摘要中沒有需要更新的記憶
- **THEN** Haiku 回傳純文字 `NO_UPDATE`，腳本 exit 0

#### Scenario: API 呼叫失敗
- **WHEN** API 回應錯誤或網路逾時
- **THEN** 腳本 catch 錯誤後靜默 exit 0，不寫任何檔案
