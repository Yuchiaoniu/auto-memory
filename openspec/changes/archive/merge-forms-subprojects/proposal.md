## Why

6 個 forms 子專案（form-auto-create-google-forms、forms-oauth-credentials、forms-gas-integration、forms-adc-setup、forms-history-ui、forms-user-auth）是同一個系統在不同開發階段產生的，邏輯上全部隸屬 form-automation-system。封存前需先將有效資訊合併進主專案，確保待辦任務與架構決策不遺失。

## What Changes

- 新建 `form-automation-system/memory.md`：記錄四代憑證演進決策（SA → OAuth → GAS → ADC）、現行架構、預設帳號、服務 URL
- 更新 `form-automation-system/tasks.md`：加入 ADC VM 部署待辦（來自 forms-adc-setup 3.1–4.2）
- 更新 `form-automation-system/STATE.md`：反映 user auth 已完成、ADC 部署尚未執行的現況

## Capabilities

### New Capabilities
- `forms-consolidated-state`: 將 6 個子專案的有效資訊整合至主專案的 memory/tasks/STATE 三檔

### Modified Capabilities

## Impact

- 僅影響 `C:\Users\yuchi\openspec\changes\form-automation-system\` 下的 3 個 Markdown 檔
- 6 個子專案於合併完成後封存至 `archive/`
