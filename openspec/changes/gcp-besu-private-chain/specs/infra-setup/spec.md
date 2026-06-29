## ADDED Requirements

### Requirement: GCS bucket 建立
腳本 SHALL 在指定的 GCP project 中建立一個 GCS bucket，用於存放 `genesis.json` 和 `bootnode.enode`。bucket 名稱格式為 `<PROJECT_ID>-besu-chain`。若 bucket 已存在，SHALL 略過不報錯。

#### Scenario: 首次執行建立 bucket
- **WHEN** 腳本在新 project 中首次執行
- **THEN** 建立名為 `<PROJECT_ID>-besu-chain` 的 GCS bucket，region 為 `us-central1`

#### Scenario: bucket 已存在時冪等
- **WHEN** bucket 已存在
- **THEN** 腳本略過建立步驟，繼續執行，不報錯

---

### Requirement: Service Account 建立與 IAM 授權
腳本 SHALL 建立一個 Service Account（`besu-node-sa`），並授予以下 IAM roles：`roles/storage.objectAdmin`（讀寫 GCS）、`roles/compute.viewer`（讀取 VM metadata 和 labels）。

#### Scenario: 首次建立 Service Account
- **WHEN** `besu-node-sa` 不存在
- **THEN** 建立 Service Account 並綁定兩個 IAM roles

#### Scenario: Service Account 已存在時冪等
- **WHEN** `besu-node-sa` 已存在
- **THEN** 跳過建立，僅確保 IAM roles 已綁定

---

### Requirement: 防火牆規則建立
腳本 SHALL 建立一條 Firewall rule，允許 VPC 內部所有 VM 之間的 TCP/UDP 30303（Besu P2P port）流量。source range 為 `10.0.0.0/8`。

#### Scenario: 建立 P2P 防火牆規則
- **WHEN** 腳本執行且防火牆規則不存在
- **THEN** 建立名為 `allow-besu-p2p-internal` 的規則，允許 TCP/UDP 30303 from 10.0.0.0/8

#### Scenario: 防火牆規則已存在時冪等
- **WHEN** 規則已存在
- **THEN** 腳本略過，不報錯

---

### Requirement: 三臺 VM 建立
腳本 SHALL 建立三臺 Compute Engine VM，分別在 us-east1-b、us-central1-a、us-west1-b，各自設定 VM label、Service Account、所屬 subnet。第一臺 label 為 `node-role=bootnode`，其餘兩臺為 `node-role=member`。

#### Scenario: 建立 bootnode VM
- **WHEN** 腳本執行
- **THEN** 在 us-east1-b 建立 VM，label `node-role=bootnode`，附加 `besu-node-sa` Service Account，image 為 Debian 12

#### Scenario: 建立 member VM
- **WHEN** 腳本執行
- **THEN** 在 us-central1-a 和 us-west1-b 各建立一臺 VM，label `node-role=member`，附加 `besu-node-sa` Service Account

#### Scenario: VM 已存在時冪等
- **WHEN** VM 已存在
- **THEN** 腳本略過，不報錯，繼續建立其餘資源

---

### Requirement: 執行完成摘要輸出
腳本 SHALL 在執行結束後輸出所有已建立資源的清單，以及下一步操作說明（SSH 進入 VM 執行腳本二）。

#### Scenario: 腳本執行完成
- **WHEN** 所有資源建立成功
- **THEN** 輸出 VM 名稱、Internal IP、node-role，以及 SSH 指令範例
