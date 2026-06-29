## MODIFIED Requirements

### Requirement: STATE.md section header 使用完整主謂賓
STATE.md 的「已知限制」section header SHALL 改為「我們已經知道的限制」，使用完整的主詞＋動詞＋受詞結構，不得使用縮略語。

#### Scenario: section header 符合語法規則
- **WHEN** 讀取 auto-memory-sync 的 STATE.md
- **THEN** 文件中不得出現「## 已知限制」，必須出現「## 我們已經知道的限制」

### Requirement: STATE.md 不含「正在…中」冗餘
STATE.md 中描述系統運行狀態時，SHALL 使用「…中」或「正在…」其中一種，不得同時出現「正在」與「中」形成冗餘進行式。

#### Scenario: 無「正在…中」冗餘
- **WHEN** 讀取 auto-memory-sync 的 STATE.md
- **THEN** 文件中不得出現「正在…中」的模式（例如「正在運行中」）
