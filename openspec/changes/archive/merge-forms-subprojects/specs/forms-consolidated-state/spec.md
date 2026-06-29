## ADDED Requirements

### Requirement: form-automation-system 擁有完整的 memory.md
合併後，`form-automation-system/memory.md` 必須存在，並包含四代憑證演進結論與現行架構。

#### Scenario: memory.md 包含憑證演進歷程
WHEN 查看 memory.md
THEN 能看到 SA、OAuth、GAS、ADC 四代方案的演進順序與棄用原因

#### Scenario: memory.md 包含現行架構要點
WHEN 查看 memory.md
THEN 能看到現行服務 URL、預設帳號、部署方式（PM2 + nginx）

### Requirement: form-automation-system tasks.md 包含 ADC VM 部署待辦
合併後，tasks.md 中必須有來自 forms-adc-setup 的 VM 部署步驟（3.1–4.2）。

#### Scenario: ADC 部署任務可追蹤
WHEN 查看 tasks.md
THEN 能看到 ADC 憑證 SCP、依賴安裝、PM2 重啟、外部驗證等未完成任務

### Requirement: STATE.md 反映真實現況
STATE.md 必須說明 user auth 已完成、ADC 部署尚未執行。

#### Scenario: STATE.md 不為空
WHEN 查看 STATE.md
THEN 能看到目前系統狀態與下一步行動
