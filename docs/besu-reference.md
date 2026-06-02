# Besu / GCP 操作參考資料

> 這份是「需要時才查」的參考資料，不每輪載入。
> 只要對話提到 besu、gcp、vm、rpc、節點、私鏈、bootnode、member 等關鍵字，就讀這份。
> 每輪都需要的精簡版（身份、Project ID、工具路徑、遠端執行寫法）放在 `C:\Users\yuchi\CLAUDE.md`。

## Besu 私鏈參數

- **共識機制:** QBFT
- **Chain ID:** 1337
- **出塊頻率:** 15 秒/塊
- **GCS bucket:** `gs://level-up-374308-besu-chain`
- **VPC:** `besu-vpc`
- **Service Account:** `besu-node-sa@level-up-374308.iam.gserviceaccount.com`

## VM 節點

| VM 名稱 | Zone | Internal IP | 角色 |
|---------|------|-------------|------|
| besu-bootnode | us-east1-b | 10.10.1.2 | bootnode |
| besu-member-1 | us-central1-a | 10.10.2.2 | member |
| besu-member-2 | us-west1-b | 10.10.3.2 | member |

> External IP 每次 VM 重啟後會變，重啟後先執行 `gcloud compute instances list` 取得新 IP。

## RPC 端點（VM 運行中時有效）

- HTTP: `http://<external-ip>:8545`
- WebSocket: `ws://<external-ip>:8546`

## Funded 測試帳號

- 地址: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`
- 私鑰: `0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80`
- 餘額: 1,000,000 ETH（genesis 預設）

## Besu 管理

- 服務: systemd (`sudo systemctl status/start/stop besu`)
- 日誌: `journalctl -u besu -f`
- VM 重啟後 Besu 自動啟動

## 常用腳本（VM 上）

| 腳本 | 用途 |
|------|------|
| `~/check-node.sh` | 確認 peers、區塊高度、funded 帳號餘額 |
| `~/get-enode.sh` | 取得 bootnode enode URL 並上傳 GCS |
| `~/setup-node.sh` | 重建節點（從 GCS 下載最新版本） |
| `~/query-tx.sh` | 查詢交易 receipt |

## 本機腳本位置

```
C:\Users\yuchi\besu-gcp\
  ├── setup-infra.sh    建立 GCP 資源
  ├── setup-node.sh     節點啟動腳本
  ├── check-node.sh     健康檢查
  ├── get-enode.sh      取得 enode
  ├── query-tx.sh       查詢交易
  └── decode-tx.sh      解碼交易 input data

C:\Users\yuchi\claude-gcp-besu\   GitHub repo
```

## VM 操作標準流程

### 停機
```powershell
$gcloud = "C:\Users\yuchi\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
& $gcloud compute instances stop besu-bootnode --zone=us-east1-b --project=level-up-374308 --quiet
& $gcloud compute instances stop besu-member-1 --zone=us-central1-a --project=level-up-374308 --quiet
& $gcloud compute instances stop besu-member-2 --zone=us-west1-b --project=level-up-374308 --quiet
```

### 啟動
```powershell
& $gcloud compute instances start besu-bootnode --zone=us-east1-b --project=level-up-374308 --quiet
& $gcloud compute instances start besu-member-1 --zone=us-central1-a --project=level-up-374308 --quiet
& $gcloud compute instances start besu-member-2 --zone=us-west1-b --project=level-up-374308 --quiet
# 啟動後取得新 External IP：
& $gcloud compute instances list --project=level-up-374308
```

### 健康檢查（取得新 IP 後）
```powershell
$SSH = "C:\WINDOWS\System32\OpenSSH\ssh.exe"
$KEY = "$env:USERPROFILE\.ssh\google_compute_engine"
foreach ($ENTRY in @("bootnode=<IP1>", "member-1=<IP2>", "member-2=<IP3>")) {
    $NAME = $ENTRY.Split("=")[0]; $IP = $ENTRY.Split("=")[1]
    $result = & $SSH -i $KEY -o StrictHostKeyChecking=no -o BatchMode=yes "yuchi@${IP}" "bash ~/check-node.sh" 2>&1
    Write-Host "${NAME}: $result"
}
```

## 相關專案

- Forest Carbon Measurement 系統使用此私鏈（RPC: `http://35.227.93.38:8545`）
- GitHub: `https://github.com/Yuchiaoniu/windows-claude-gcp`
