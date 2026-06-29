## Why

在 GCP 跨三個地區（美東 us-east1、美中 us-central1、美西 us-west1）部署並維運 Hyperledger Besu 企業私鏈，作為 Forest Carbon Measurement 系統的區塊鏈基礎設施。目標是讓鏈上能穩定記錄植物元數據（物種、GPS 座標、影片 hash 等），並透過 Claude 直接操作 GCP，不需要手動開終端機或 SSH。

## What Changes

- **GCP 基礎設施**：跨三地區的 VPC、subnet、VM（e2-small）、Service Account、GCS bucket、Firewall rules
- **Besu QBFT 私鏈**：三節點 QBFT 共識，15 秒出塊，Chain ID 1337，systemd 自啟動
- **Genesis 設定**：含 funded 測試帳號（1,000,000 ETH），供合約部署與交易使用
- **節點協調機制**：透過 GCS bucket 傳遞 genesis.json 和 bootnode enode URL
- **Claude 操作能力**：透過 Windows OpenSSH + gcloud CLI，Claude 可直接遠端操作所有 VM，不需使用者手動 SSH

## Current State（實際完成狀態）

- ✅ 三台 VM 跨地區運行中（besu-bootnode / besu-member-1 / besu-member-2）
- ✅ QBFT 私鏈正常出塊（每 15 秒），已超過 600+ 個區塊
- ✅ Forest Carbon 合約已部署，7 筆植物元數據已上鏈（Fraxinus griffithii 等）
- ✅ RPC HTTP: `http://35.227.93.38:8545`，WebSocket: `ws://35.227.93.38:8546`
- ✅ Claude 可透過 OpenSSH（user: yuchi）直接遠端執行指令
- ✅ 腳本已上傳 GitHub: `https://github.com/Yuchiaoniu/windows-claude-gcp`

## Capabilities

### New Capabilities

- `infra-setup`: GCP 資源建立腳本（GCS、SA、IAM、Firewall、VM×3）
- `node-bootstrap`: 通用節點腳本，自動偵測角色（bootnode/member），安裝 Besu，連上私鏈，設定 systemd

### Modified Capabilities

## Impact

- **GCP 資源**：Project `level-up-374308`，GCS bucket `level-up-374308-besu-chain`
- **VM 節點**：besu-bootnode（us-east1-b / 10.10.1.2）、besu-member-1（us-central1-a / 10.10.2.2）、besu-member-2（us-west1-b / 10.10.3.2）
- **Funded 帳號**：`0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`，私鑰 `0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80`
- **共識機制**：QBFT，Chain ID 1337，blockperiodseconds 15
- **依賴**：Hyperledger Besu 24.12.0、OpenJDK 21（Temurin）、gsutil、gcloud CLI、Windows OpenSSH
