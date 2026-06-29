## ADDED Requirements

### Requirement: 理解雲端運算定義與優勢
學習者 SHALL 能說明雲端運算的定義、六大優勢（規模經濟、無需預付、彈性擴展等）與三種部署模型（Public/Private/Hybrid）。

#### Scenario: 回答雲端優勢題型
- **WHEN** 考題問到「採用 AWS 雲端的主要好處是什麼」
- **THEN** 學習者能選出「將資本支出轉為營運支出」或「隨需付費」等正確選項

#### Scenario: 區分部署模型
- **WHEN** 考題描述某企業部分資源在地端、部分在雲端
- **THEN** 學習者能正確識別為 Hybrid Cloud 部署模型

### Requirement: 掌握 AWS Well-Architected Framework
學習者 SHALL 能列舉並說明六大支柱：卓越營運、安全性、可靠性、效能效率、成本最佳化、永續性。

#### Scenario: 對應支柱與設計原則
- **WHEN** 考題描述「自動復原故障、水平擴展」等設計原則
- **THEN** 學習者能對應到「可靠性（Reliability）」支柱

### Requirement: 理解 6R 雲端遷移策略
學習者 SHALL 能識別 Rehost、Replatform、Refactor、Repurchase、Retire、Retain 各策略的適用情境。

#### Scenario: 情境選擇遷移策略
- **WHEN** 考題描述「直接將 VM 搬上 EC2，不修改程式碼」
- **THEN** 學習者能識別為 Rehost（Lift and Shift）策略
