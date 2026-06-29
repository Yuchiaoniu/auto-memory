# Forest Carbon Showcase — 長期對照資料

## 部署位置（雙軌）

| 環境 | 靜態檔路徑 | 公開 URL |
|---|---|---|
| GCP Express | `~/forest-carbon-measurement/public/showcase.html` | https://forest-carbon.duckdns.org/showcase.html |
| GitHub Pages | `C:\Users\yuchi\forest-carbon-measurement\showcase.html`（repo 根目錄） | https://yuchiaoniu.github.io/forest-carbon-measurement/showcase.html |

**重點**：GCP Express 從 `public/` 子目錄提供靜態檔；GitHub Pages 從 repo 根目錄提供。
兩個位置都要同步更新，否則兩邊會不一致。

## 原始碼主檔

- **主檔（master source）**：`C:\Users\yuchi\openspec\changes\forest-carbon-showcase\index.html`
- 每次改主檔後，必須同步複製到 GCP `public/showcase.html` 和 repo 根目錄 `showcase.html`

## KPI 數值（截至 2026-06-02）

| KPI | 數值 |
|---|---|
| 樣本數 | 30 棵 |
| Pipeline 數量 | 5 條 |
| PASS rate | 73.3% |
| API 成本 | 622 TWD（舊版為 ~$1.5 USD，已改） |

## RQ3 / RO3 狀態

- 內容已寫入頁面（含 ESG audit compliance matrix、ToC 因果鏈、驗證設計）
- 目前以 `style="display:none"` 隱藏，不對外顯示
- 判斷：RQ3（ESG audit compliance）超出目前研究能量範圍，留作未來擴充

## 導覽按鈕（「📈 評估與演進旅程」）

已加入以下三個頁面：
| 頁面 | 位置 | 連結目標 |
|---|---|---|
| `public/index.html`（GCP + repo） | 原本指向 `journey/index.rewritten.html` 的按鈕，改指 | `showcase.html` |
| `public/dashboard.html`（GCP + repo） | 新增連結 | `/showcase.html` |
| VM 上的 `public/dashboard02.html`（僅 VM，未納入 git） | 用 Python 腳本插入 | `./showcase.html` |

## dashboard02.html 特殊狀態

- 檔案**不在 git repo** 裡，只存在 VM（`~/forest-carbon-measurement/public/dashboard02.html`）
- 為了讓 GitHub Pages 也能存取，SCP 下載後另存為 `C:\Users\yuchi\forest-carbon-measurement\dashboard02.html`（repo 根目錄），已 commit
- VM 版本的導覽按鈕修改用 Python 腳本完成（sed 無法處理 emoji）

## SCP / SSH 標準指令（此專案）

```powershell
$SSH = "C:\WINDOWS\System32\OpenSSH\ssh.exe"
$SCP = "C:\WINDOWS\System32\OpenSSH\scp.exe"
$KEY = "$env:USERPROFILE\.ssh\google_compute_engine"
$USER = "yuchi"
$VM_IP = "35.227.93.38"
$SSH_OPTS = @("-i", $KEY, "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes")

# 上傳 showcase.html 到 GCP
& $SCP -i $KEY -o "StrictHostKeyChecking=no" `
  "C:\Users\yuchi\forest-carbon-measurement\public\showcase.html" `
  "${USER}@${VM_IP}:~/forest-carbon-measurement/public/showcase.html"
```
