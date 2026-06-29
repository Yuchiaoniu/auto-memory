## Why

VM 部署自檢規則要求從外部 IP 驗證，但只打 GET / 回傳 200 仍不足——POST 端點、CORS preflight、授權邊界都可能在「服務活著」的狀態下悄悄失效。沒有結構化的測試矩陣，自檢範圍由 Claude 當場判斷，容易只測最容易的那條路徑。

## What Changes

- CLAUDE.md 在「VM 部署自檢要求」下方新增 API 服務測試矩陣規則：部署含 REST API 的服務後，必須先列出端點 × method × 驗證情境矩陣，再逐一從外部發出請求，全部通過才算自檢完成。

## Capabilities

### New Capabilities
- `api-test-matrix`：API 服務部署後的測試矩陣自檢規範

### Modified Capabilities
（無）

## Impact

- `C:\Users\yuchi\.claude\CLAUDE.md`（全域指令）
