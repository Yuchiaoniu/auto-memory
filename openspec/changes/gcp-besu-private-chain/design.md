## Context

目標是在 GCP 三個地區（us-east1、us-central1、us-west1）各建一臺 Compute Engine VM，組成 Hyperledger Besu QBFT 企業私鏈。所有 VM 在同一個 GCP VPC 中，透過 Internal IP 溝通。

部署分兩層：
1. **Infra 層**（腳本一）：建立 GCP 資源，在本地或 Cloud Shell 執行一次
2. **節點層**（腳本二）：在每臺 VM 上手動執行，按順序（bootnode 先，member 後）

## Goals / Non-Goals

**Goals:**
- 可重複執行的 infra 腳本，冪等設計（已存在則略過）
- 通用節點腳本，同一支腳本不同 VM 自動適應角色
- 步驟分離，每個階段可獨立驗證，方便除錯
- 使用 GCS 作節點間狀態協調（genesis.json + bootnode enode）

**Non-Goals:**
- VPC 和 subnet 建立（手動處理）
- 監控、告警、日誌收集
- Besu 節點的 TLS 加密（簡化版 PoC）
- 動態新增節點（固定三節點）
- 自動重啟或 systemd 服務管理（腳本執行後前景運行）

## Decisions

### 1. GCS 作為協調點，而非 Secret Manager 或 Instance Metadata

**選擇**：GCS bucket 存放 `genesis.json` 和 `bootnode.enode`

**理由**：
- Secret Manager 需要額外費用且對大型檔案（genesis.json）不適合
- Instance Metadata 只能存單一 VM 的資料，無法跨 VM 共享
- GCS 免費額度充裕、支援 `gsutil` 簡單讀寫、權限透過 Service Account 控制

**替代方案放棄理由**：
- Instance labels：只能存短字串，enode URL 可能超長

---

### 2. VM Label 決定角色，而非腳本偵測或參數傳入

**選擇**：VM 建立時設定 `node-role=bootnode` 或 `node-role=member`

**理由**：
- 明確且不依賴競態邏輯（誰先起來誰是 bootnode）
- 腳本用 `gcloud compute instances describe` 讀取，一行搞定
- 腳本一（infra）建 VM 時就設好，不需要人工干預

**替代方案放棄理由**：
- GCS 競態搶 bootnode 角色：在三台同時啟動時有競態風險，且難以重現除錯

---

### 3. Internal IP 做 P2P，不用 External IP

**選擇**：Besu `--p2p-host` 綁定 VM 的 Internal IP，bootnodes enode 也用 Internal IP

**理由**：
- 同一 GCP VPC 的跨 region 流量走 Google 私有骨幹，延遲低、安全
- 不需要 External IP 就能節點互連，減少攻擊面
- Firewall rule 只開 VPC 內部流量（source: 10.0.0.0/8）

---

### 4. QBFT 共識機制

**選擇**：QBFT

**理由**：Besu 官方推薦，未來可擴展至 4+ 節點獲得 Byzantine 容錯能力

**注意**：3 節點下 QBFT 的容錯 = 0（任一節點掉線，出塊暫停）。這是 PoC 可接受的限制。

---

### 5. 兩支獨立腳本，手動分步執行

**選擇**：腳本一和腳本二分離，不用 VM Startup Script 自動執行

**理由**：
- Startup Script 失敗時難以即時看到 log 和除錯
- 分步執行讓每個階段可以暫停確認（GCS 內容、VM 狀態、Besu 日誌）
- 腳本二本身加詳細 log，執行時即時顯示進度

## Risks / Trade-offs

- **3 節點 QBFT 無容錯** → PoC 接受，正式環境需升至 4 節點
- **bootnode 的 Internal IP 變更**（VM 砍掉重建）→ 重建後需重新上傳 enode 到 GCS，member 重新執行腳本二
- **GCS bucket 名稱全球唯一** → 腳本一使用 `PROJECT_ID` 作為 bucket 名稱前綴避免衝突
- **腳本一冪等性**：`gcloud` 指令如果資源已存在會報錯 → 加 `--quiet` 和存在性檢查處理

## Migration Plan

1. 手動建立 VPC + 3 個 subnet（GCP Console）
2. 在 Cloud Shell 執行腳本一，建立其餘 GCP 資源和 3 臺 VM
3. SSH 進入 VM #1（bootnode），執行腳本二，等待確認 GCS 有 `genesis.json` 和 `bootnode.enode`
4. SSH 進入 VM #2、#3（member），各自執行腳本二
5. 驗證三節點出塊

**Rollback**：刪除 GCS bucket 內容後，可在任一 VM 重新執行腳本二重置節點。

## Open Questions

- Besu 版本：使用最新穩定版（腳本動態抓取 GitHub latest release），還是固定版本號？
- VM 規格：e2-micro（免費額度）是否記憶體足夠跑 Besu？（建議 e2-small 或以上，Besu 需要至少 2GB RAM）
