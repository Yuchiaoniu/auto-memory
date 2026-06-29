## ADDED Requirements

### Requirement: 環境自動偵測
腳本 SHALL 在啟動時自動偵測 VM 的 Internal IP（透過 GCP Metadata Server）和角色（透過 VM Label `node-role`），不需要任何人工輸入參數。

#### Scenario: 偵測 Internal IP
- **WHEN** 腳本在任意 GCP VM 上執行
- **THEN** 透過 `http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/ip` 取得 Internal IP，並顯示於 log

#### Scenario: 偵測節點角色
- **WHEN** 腳本執行
- **THEN** 透過 `gcloud compute instances describe` 讀取 `node-role` label，值為 `bootnode` 或 `member`

#### Scenario: 角色未設定時中止
- **WHEN** VM 沒有 `node-role` label
- **THEN** 腳本輸出錯誤訊息並退出，不繼續執行

---

### Requirement: Java 和 Besu 安裝
腳本 SHALL 自動安裝 OpenJDK 17 和最新穩定版 Hyperledger Besu（從 GitHub releases 下載）。若已安裝，SHALL 略過。

#### Scenario: 首次安裝 Java
- **WHEN** `java` 指令不存在
- **THEN** 透過 `apt-get` 安裝 `openjdk-17-jre-headless`

#### Scenario: 首次安裝 Besu
- **WHEN** `/opt/besu/bin/besu` 不存在
- **THEN** 下載最新 Besu release tar.gz，解壓至 `/opt/besu`

#### Scenario: 已安裝時略過
- **WHEN** Java 和 Besu 已存在
- **THEN** 跳過安裝步驟，繼續執行

---

### Requirement: Bootnode 模式 — 初始化私鏈
當角色為 `bootnode` 時，腳本 SHALL 生成 QBFT 私鏈所需的所有初始化資料，並上傳至 GCS。

#### Scenario: 生成節點金鑰
- **WHEN** bootnode 模式下 `/opt/besu/data/key` 不存在
- **THEN** 執行 `besu --data-path=/opt/besu/data public-key export-address` 生成 nodekey

#### Scenario: 生成 QBFT genesis.json
- **WHEN** bootnode 初始化
- **THEN** 生成包含三個 validator 地址（含 bootnode 自身）的 QBFT genesis.json，blockperiodseconds=5

#### Scenario: 上傳 genesis 至 GCS
- **WHEN** genesis.json 生成完成
- **THEN** 用 `gsutil cp` 上傳至 `gs://<BUCKET>/genesis.json`

#### Scenario: 啟動 Besu 並發布 enode
- **WHEN** genesis.json 上傳完成
- **THEN** 啟動 Besu（foreground），啟動後從日誌解析 enode URL，上傳至 `gs://<BUCKET>/bootnode.enode`

---

### Requirement: Member 模式 — 加入現有私鏈
當角色為 `member` 時，腳本 SHALL 從 GCS 取得初始化資料，並連上 bootnode。

#### Scenario: 等待 genesis.json 就緒
- **WHEN** member 模式啟動，GCS 尚無 genesis.json
- **THEN** 每 15 秒重試一次，最多等待 5 分鐘；超時則輸出錯誤並退出

#### Scenario: 下載 genesis 和 bootnode enode
- **WHEN** GCS 中 genesis.json 和 bootnode.enode 均存在
- **THEN** 下載至本地 `/opt/besu/`

#### Scenario: 啟動 Besu 並連上 bootnode
- **WHEN** genesis 和 enode 下載完成
- **THEN** 啟動 Besu，帶上 `--bootnodes=<enode_url>`，`--p2p-host=<internal_ip>`

---

### Requirement: 執行日誌輸出
腳本 SHALL 在每個步驟開始和完成時輸出帶有時間戳的 log 訊息，讓使用者清楚知道目前進度和是否成功。

#### Scenario: 步驟開始 log
- **WHEN** 每個主要步驟開始
- **THEN** 輸出格式 `[HH:MM:SS] [STEP] 開始: <描述>`

#### Scenario: 步驟成功 log
- **WHEN** 步驟完成
- **THEN** 輸出格式 `[HH:MM:SS] [OK] <描述>`

#### Scenario: 步驟失敗時中止
- **WHEN** 任何步驟執行失敗（非零退出碼）
- **THEN** 輸出 `[ERROR] <步驟名稱> 失敗，請檢查上方錯誤訊息`，並退出腳本
