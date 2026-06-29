## 1. 腳本一：Infra 建立腳本（gcloud）

- [x] 1.1 建立腳本骨架：`setup-infra.sh`，加上變數區（PROJECT_ID、REGION、VPC_NAME 等）和 log 函式
- [x] 1.2 實作 GCS bucket 建立邏輯（冪等：已存在則略過）
- [x] 1.3 實作 Service Account 建立和 IAM roles 綁定邏輯（冪等）
- [x] 1.4 實作 Firewall rule 建立（allow TCP/UDP 30303 from 10.0.0.0/8，冪等）
- [x] 1.5 實作 VM 建立：bootnode（us-east1-b，label node-role=bootnode）
- [x] 1.6 實作 VM 建立：member-1（us-central1-a，label node-role=member）
- [x] 1.7 實作 VM 建立：member-2（us-west1-b，label node-role=member）
- [x] 1.8 實作執行完成摘要：列出所有 VM 的名稱、Internal IP、角色，以及 SSH 指令範例

## 2. 腳本二：節點啟動腳本（Besu bootstrap）

- [x] 2.1 建立腳本骨架：`setup-node.sh`，加上 log 函式（帶時間戳，區分 STEP / OK / ERROR）和 `set -e`
- [x] 2.2 實作環境偵測：透過 Metadata Server 取得 Internal IP
- [x] 2.3 實作角色偵測：用 gcloud 讀取 VM label `node-role`，未設定時退出並顯示錯誤
- [x] 2.4 實作 Java 安裝（冪等：已安裝則略過）
- [x] 2.5 實作 Besu 安裝：從 GitHub 抓最新 release，解壓至 `/opt/besu`（冪等）
- [x] 2.6 實作 Bootnode 模式：生成 nodekey（`/opt/besu/data/key`）
- [x] 2.7 實作 Bootnode 模式：生成 QBFT `genesis.json`（blockperiodseconds=5，含自身 validator 地址）
- [x] 2.8 實作 Bootnode 模式：上傳 `genesis.json` 至 GCS bucket
- [x] 2.9 實作 Bootnode 模式：啟動 Besu，解析 log 中的 enode URL，上傳至 GCS `bootnode.enode`
- [x] 2.10 實作 Member 模式：輪詢 GCS 等待 `genesis.json` 出現（15 秒重試，最多 5 分鐘）
- [x] 2.11 實作 Member 模式：下載 `genesis.json` 和 `bootnode.enode`
- [x] 2.12 實作 Member 模式：啟動 Besu，帶上 `--bootnodes` 和 `--p2p-host=<internal_ip>`

## 3. 驗證

- [x] 3.1 在本地用 `bash --dry-run` 或 `shellcheck` 檢查兩支腳本語法
- [x] 3.2 執行 `setup-infra.sh`，確認 GCS bucket、SA、firewall rule、3 臺 VM 均建立成功
- [x] 3.3 SSH 進 bootnode VM，執行 `setup-node.sh`，確認 GCS 出現 `genesis.json` 和 `bootnode.enode`
- [x] 3.4 SSH 進 member-1，執行 `setup-node.sh`，確認 Besu log 顯示連上 bootnode peer
- [x] 3.5 SSH 進 member-2，執行 `setup-node.sh`，確認 Besu log 顯示連上 bootnode peer
- [x] 3.6 在任一節點確認 QBFT 正在出塊（`eth_blockNumber` RPC 持續增加）
