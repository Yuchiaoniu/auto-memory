## ADDED Requirements

### Requirement: 每個 session 顯示 token 成本分解
token-stats.ps1 SHALL 輸出每個 session 的 turns、cache_read、cache_write、output token 數量，並以 NT$ 顯示估算費用。

#### Scenario: 正常執行
- **WHEN** 使用者執行 `token-stats.ps1`
- **THEN** 顯示最近 5 個 session，每個 session 含 turns、cache_read（NT$）、output（NT$）、cache_create

#### Scenario: cache_read 超過 5M
- **WHEN** 某 session 的 cache_read 超過 5,000,000 tokens
- **THEN** 在該 session 旁顯示 `>> High cache -- consider /compact` 警示

### Requirement: 跨 session 當日累計成本
token-stats.ps1 SHALL 在輸出末尾顯示當日（依 LastWriteTime）所有 session 的 token 累計與 NT$ 合計。

#### Scenario: 同一天有多個 session
- **WHEN** 當天有 3 個以上的 session 檔案
- **THEN** 顯示「Today Total」區塊，列出合計 cache_read、output、估算 NT$

#### Scenario: 只有今天的 session
- **WHEN** 所有 session 都是今天建立的
- **THEN** Today Total 與各 session 加總一致

### Requirement: NT$ 匯率可設定
token-stats.ps1 SHALL 優先讀取環境變數 `CLAUDE_NTD_RATE`，若未設定則使用預設值 32。

#### Scenario: 設定環境變數
- **WHEN** `$env:CLAUDE_NTD_RATE = "30"` 且執行 token-stats.ps1
- **THEN** 所有 NT$ 估算以 30 為匯率計算
