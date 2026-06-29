## ADDED Requirements

### Requirement: VM 部署後必須驗證外部存取
部署服務到 VM 後，Claude SHALL 從外部 IP 實際訪問服務，確認公開端點可達。不得以 localhost 或內部 curl 代替外部驗證。

#### Scenario: 部署完成後執行外部自檢
- **WHEN** Claude 在 VM 上部署或更新任何對外服務（HTTP/HTTPS）
- **THEN** Claude 必須從外部 IP 或公開 URL 發出請求，確認回傳預期狀態碼，不得只做 `curl localhost`

#### Scenario: 只做 localhost 驗證視為自檢不完整
- **WHEN** Claude 僅執行 `curl localhost` 或內部 IP 驗證
- **THEN** 該次自檢不符合要求，Claude 必須補做外部存取驗證
