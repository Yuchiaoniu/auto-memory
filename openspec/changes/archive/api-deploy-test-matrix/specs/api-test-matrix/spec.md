## ADDED Requirements

### Requirement: API 服務部署後必須建立並執行測試矩陣
部署含 REST API 的服務到 VM 後，Claude SHALL 在執行自檢前先列出測試矩陣（端點 × Method × 驗證情境），再逐一從外部發出請求，全部通過才算自檢完成。

#### Scenario: 部署 API 服務後列出測試矩陣
- **WHEN** Claude 部署或更新任何包含 REST API 端點的服務
- **THEN** Claude 必須先列出所有對外端點的測試矩陣，包含端點路徑、HTTP method、驗證情境（正常回應、CORS preflight、未授權等），再逐一從外部實際發出請求

#### Scenario: 跳過矩陣直接自檢視為不完整
- **WHEN** Claude 未列出測試矩陣，直接只打單一端點確認 200
- **THEN** 該次自檢不符合要求，必須補列矩陣並重新逐一驗證
