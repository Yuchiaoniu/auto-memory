## ADDED Requirements

### Requirement: 分析分頁並提供整理建議
腳本 `Get-Tabs.ps1 -Analyze` SHALL 輸出 JSON 格式的分頁清單，供 Claude 分析後以對話方式提出整理建議。Claude SHALL 識別以下可關閉類型：
- 重複網域（同一網站開了多個分頁）
- 明顯暫時性頁面（搜尋結果頁、錯誤頁、空白頁）
- 標題為「新分頁」或 `about:blank`

#### Scenario: Claude 分析分頁清單
- **WHEN** 使用者說「幫我看看有哪些分頁可以關掉」
- **THEN** Claude 執行 `Get-Tabs.ps1 -Analyze`，解讀 JSON，以條列方式回報：「建議可關閉的分頁（共 N 個）」及各項建議理由

#### Scenario: 使用者確認關閉
- **WHEN** 使用者確認要關閉某些分頁
- **THEN** Claude 執行 `Close-Tab.ps1 -TabIds <id1,id2,...>`，透過 CDP 關閉指定分頁

### Requirement: 關閉指定分頁
腳本 `Close-Tab.ps1 -TabIds <id1,id2,...>` SHALL 透過 CDP 的 `close` 端點關閉指定 tabId 的分頁。

#### Scenario: 成功關閉
- **WHEN** 執行 `Close-Tab.ps1 -TabIds "abc123,def456"`
- **THEN** 兩個分頁被關閉，顯示「已關閉 2 個分頁」

#### Scenario: 部分 tabId 無效（分頁已關閉）
- **WHEN** 指定的 tabId 中有些已不存在
- **THEN** 關閉存在的分頁，對不存在的顯示警告但不中斷流程
