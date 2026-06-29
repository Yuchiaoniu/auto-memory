## ADDED Requirements

### Requirement: 數字資料型句子禁止話題化結構
數字或資料值作受詞時，SHALL 放在動詞之後，不得提前當話題。

#### Scenario: 輸出磁碟用量
- **WHEN** 需要描述磁碟、記憶體、流量等數值
- **THEN** 使用「已經用掉 14 GB」而非「14 GB 用掉」；使用「還剩 15 GB」而非「15 GB 剩餘」
