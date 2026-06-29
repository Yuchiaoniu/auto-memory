## ADDED Requirements

### Requirement: 理解共同責任模型
學習者 SHALL 能區分 AWS 負責的安全項目（of the cloud）與客戶負責的項目（in the cloud）。

#### Scenario: 判斷責任歸屬
- **WHEN** 考題問到「誰負責 EC2 上的作業系統修補」
- **THEN** 學習者能回答「客戶負責」，因為 OS 層以上屬於客戶責任

#### Scenario: 判斷 AWS 責任範圍
- **WHEN** 考題問到「資料中心的實體安全由誰負責」
- **THEN** 學習者能回答「AWS 負責」，硬體與設施屬於 AWS 責任

### Requirement: 掌握 IAM 核心概念
學習者 SHALL 能說明 IAM Users、Groups、Roles、Policies 的用途與最小權限原則。

#### Scenario: 選擇正確 IAM 設計
- **WHEN** 考題描述「EC2 需要存取 S3」
- **THEN** 學習者能識別應使用 IAM Role 附加到 EC2，而非建立 IAM User

#### Scenario: 應用最小權限原則
- **WHEN** 考題問到 IAM 最佳實踐
- **THEN** 學習者能選出「僅授予執行任務所需的最小權限」

### Requirement: 識別 AWS 安全服務
學習者 SHALL 能區分 Shield（DDoS防護）、WAF（Web應用防火牆）、GuardDuty（威脅偵測）、Inspector（漏洞掃描）、Macie（S3敏感資料偵測）的功能。

#### Scenario: 選擇 DDoS 防護服務
- **WHEN** 考題描述「需要保護 Web 應用免受 DDoS 攻擊」
- **THEN** 學習者能識別 AWS Shield（Standard/Advanced）為正確答案

#### Scenario: 區分安全服務用途
- **WHEN** 考題問到「哪個服務可以偵測 S3 中的個人識別資訊（PII）」
- **THEN** 學習者能選出 Amazon Macie
