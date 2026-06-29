## ADDED Requirements

### Requirement: 理解 AWS 費用模型
學習者 SHALL 能比較 On-Demand、Reserved Instances（1年/3年）、Spot Instances、Savings Plans 的費用結構與適用情境。

#### Scenario: 選擇最低成本運算方案
- **WHEN** 考題描述「工作負載可以被中斷，需要最低成本」
- **THEN** 學習者能選出 Spot Instances

#### Scenario: 選擇預測性工作負載方案
- **WHEN** 考題描述「24/7 穩定運行的生產環境，需要降低費用」
- **THEN** 學習者能識別 Reserved Instances（1年或3年預付）可節省最多 72%

### Requirement: 掌握費用管理工具
學習者 SHALL 能說明 AWS Pricing Calculator（預估費用）、Cost Explorer（分析費用趨勢）、Budgets（設定預算警報）的用途差異。

#### Scenario: 選擇費用預估工具
- **WHEN** 考題描述「在部署前想預估每月 AWS 費用」
- **THEN** 學習者能選出 AWS Pricing Calculator

#### Scenario: 選擇費用分析工具
- **WHEN** 考題描述「想要視覺化查看過去三個月的費用趨勢」
- **THEN** 學習者能選出 AWS Cost Explorer

### Requirement: 理解 AWS 支援方案
學習者 SHALL 能比較 Basic、Developer、Business、Enterprise 四種支援方案的回應時間與功能差異。

#### Scenario: 識別生產環境最低支援需求
- **WHEN** 考題描述「生產系統停機需要 1 小時內回應」
- **THEN** 學習者能識別需要 Business Support（含 < 1 小時生產系統回應）

#### Scenario: 識別免費支援範圍
- **WHEN** 考題問到「Basic Support 包含哪些內容」
- **THEN** 學習者能回答「文件、論壇、Service Health Dashboard，不含技術支援」
