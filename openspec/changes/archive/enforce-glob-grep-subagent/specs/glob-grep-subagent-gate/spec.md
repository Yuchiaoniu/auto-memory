## ADDED Requirements

### Requirement: 主對話禁止直接呼叫檔案搜尋與內容搜尋工具
主對話 SHALL NOT 直接呼叫檔案搜尋工具（Glob）或內容搜尋工具（Grep）。系統必須透過 PreToolUse hook 攔截此類呼叫，封鎖並注入說明，要求改用子代理執行。

#### Scenario: 直接呼叫被攔截並封鎖
- **WHEN** 主對話嘗試直接執行檔案搜尋工具或內容搜尋工具
- **THEN** hook 封鎖呼叫，並注入提示：「請改用子代理（Agent, model: haiku）執行檔案搜尋，不得在主對話直接呼叫 Glob 或 Grep」

#### Scenario: 子代理內部呼叫不受影響
- **WHEN** 子代理內部執行檔案搜尋工具或內容搜尋工具
- **THEN** hook 不觸發，子代理正常完成搜尋
