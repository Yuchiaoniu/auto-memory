## ADDED Requirements

### Requirement: 理解核心運算服務
學習者 SHALL 能說明 EC2（虛擬機器）、Lambda（無伺服器函數）、ECS/EKS（容器）的用途與適用情境。

#### Scenario: 選擇適合的運算服務
- **WHEN** 考題描述「需要執行短暫任務且不想管理伺服器」
- **THEN** 學習者能識別 AWS Lambda 為正確答案

#### Scenario: 區分 EC2 與 Lambda
- **WHEN** 考題描述「需要長時間執行、需要完整 OS 控制的工作負載」
- **THEN** 學習者能選出 EC2 而非 Lambda

### Requirement: 理解儲存服務
學習者 SHALL 能區分 S3（物件儲存）、EBS（區塊儲存）、EFS（檔案儲存）、Glacier（長期歸檔）的特性與用途。

#### Scenario: 選擇物件儲存服務
- **WHEN** 考題描述「需要儲存靜態網站檔案或圖片」
- **THEN** 學習者能選出 Amazon S3

#### Scenario: 識別歸檔儲存
- **WHEN** 考題描述「需要長期保存合規資料，存取頻率極低」
- **THEN** 學習者能識別 S3 Glacier 為最低成本方案

### Requirement: 理解網路與內容傳遞服務
學習者 SHALL 能說明 VPC（虛擬私有雲）、CloudFront（CDN）、Route 53（DNS）、ELB（負載平衡）的功能。

#### Scenario: 識別 CDN 服務
- **WHEN** 考題描述「需要降低全球使用者的網頁載入延遲」
- **THEN** 學習者能選出 Amazon CloudFront

#### Scenario: 說明 VPC 用途
- **WHEN** 考題問到「如何隔離 AWS 資源的網路環境」
- **THEN** 學習者能識別 VPC 可建立邏輯隔離的私有網路

### Requirement: 理解資料庫服務
學習者 SHALL 能區分 RDS（關聯式）、DynamoDB（NoSQL）、Aurora（高效能關聯式）、ElastiCache（快取）的適用情境。

#### Scenario: 選擇 NoSQL 資料庫
- **WHEN** 考題描述「需要毫秒級回應、不規則結構的資料」
- **THEN** 學習者能選出 Amazon DynamoDB

### Requirement: 理解訊息與整合服務
學習者 SHALL 能區分 SNS（發布/訂閱通知）與 SQS（訊息佇列）的差異與使用情境。

#### Scenario: 選擇訊息佇列服務
- **WHEN** 考題描述「需要解耦兩個服務，確保訊息不遺失」
- **THEN** 學習者能選出 Amazon SQS

#### Scenario: 選擇推播通知服務
- **WHEN** 考題描述「需要同時通知多個訂閱者（email、SMS、Lambda）」
- **THEN** 學習者能選出 Amazon SNS
