## ADDED Requirements

### Requirement: 主對話禁止直接呼叫網頁抓取工具
主對話 SHALL NOT 直接呼叫網頁抓取工具（WebFetch）。系統必須透過 PreToolUse hook 攔截此類呼叫，封鎖並注入說明，要求改用子代理執行。

#### Scenario: 直接呼叫被攔截並封鎖
- **WHEN** 主對話嘗試直接執行網頁抓取工具
- **THEN** hook 封鎖呼叫，並注入提示：「請改用子代理（Agent, model: haiku）執行網頁抓取，不得在主對話直接呼叫 WebFetch」

#### Scenario: 子代理內部呼叫不受影響
- **WHEN** 子代理內部執行網頁抓取工具
- **THEN** hook 不觸發，子代理正常完成抓取
