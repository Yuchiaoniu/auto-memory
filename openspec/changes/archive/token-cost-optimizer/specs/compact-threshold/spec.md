## ADDED Requirements

### Requirement: autoCompactWindow 設為 80K
settings.json 的 `autoCompactWindow` SHALL 設定為 80000，取代目前的 150000。

#### Scenario: context 達到 80K tokens
- **WHEN** 單一 session 的 context 累積至 80,000 tokens
- **THEN** Claude Code 自動觸發 compact，壓縮對話歷史

### Requirement: Stop hook 分三級警示
cache-check.ps1 SHALL 依照 cache_read_input_tokens 總量輸出分級警示訊息。

#### Scenario: cache_read 低於 5M（綠燈）
- **WHEN** session 的累計 cache_read < 5,000,000 tokens
- **THEN** 腳本靜默退出，不輸出任何訊息

#### Scenario: cache_read 介於 5M 至 10M（黃燈）
- **WHEN** session 的累計 cache_read 介於 5,000,000 至 10,000,000 tokens
- **THEN** 輸出 systemMessage：`Cache Read: {X}M tokens — Context growing. Consider /compact soon.`

#### Scenario: cache_read 超過 10M（紅燈）
- **WHEN** session 的累計 cache_read > 10,000,000 tokens
- **THEN** 輸出 systemMessage：`Cache Read: {X}M tokens — Context is large. Run /compact now (NOT /clear).`
