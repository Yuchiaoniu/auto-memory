## ADDED Requirements

### Requirement: 單字動詞禁止縮略
回覆中所有動詞 SHALL 使用完整形式，禁止單字縮略版本。

#### Scenario: 說明新增操作
- **WHEN** 需要描述把某項目加入某處
- **THEN** 使用「加入」而非「加」；例如「加入子代理呼叫」而非「加子代理呼叫」

#### Scenario: 說明修改操作
- **WHEN** 需要描述更動某項設定或內容
- **THEN** 使用「修改」或「調整」而非「改」；例如「修改 settings.json」而非「改 settings.json」

#### Scenario: 說明刪除操作
- **WHEN** 需要描述移除某項內容
- **THEN** 使用「刪除」或「移除」而非「刪」；例如「刪除舊版本」而非「刪舊版本」
