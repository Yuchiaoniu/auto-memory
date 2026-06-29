# AWS CLF-C02 備考知識庫

## 任務 1.1：雲端運算定義、六大優勢、三種部署模型

### 雲端運算定義
透過網際網路按需提供 IT 資源，採隨用隨付（pay-as-you-go）計費，由 AWS 管理底層基礎設施。

### 六大優勢（考試高頻）
1. 將資本支出（CapEx）換為可變支出（OpEx）
2. 龐大規模經濟效益（Benefit from massive economies of scale）
3. 無需猜測容量（Stop guessing capacity）
4. 速度與敏捷性（Increase speed and agility）
5. 不再花錢維護機房（Stop spending money running data centers）
6. 分鐘內佈署到全球（Go global in minutes）

記憶訣竅：資本→變動 / 規模經濟 / 彈性容量 / 速度敏捷 / 省機房 / 全球佈署

### 三種部署模型
| 模型 | 定義 | 典型情境 |
|------|------|----------|
| Public Cloud | 全部資源在 AWS，透過網路存取 | 新創、SaaS、快速上市 |
| Private Cloud | 資源在自有/租用機房，僅供內部使用 | 金融、政府（法規限制）|
| Hybrid Cloud | Public + Private 透過 VPN 或 Direct Connect 連線 | 漸進遷移、資料主權、舊系統整合 |

考題陷阱：法規要求資料不能離開本地但又要用 AWS → Hybrid Cloud
