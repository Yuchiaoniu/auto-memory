## ADDED Requirements

### Requirement: propose 完成後自動觸發 apply
Claude 在 openspec-propose skill 完成所有 artifacts 後，SHALL 立即呼叫 `opsx:apply`，不等使用者再次確認。

#### Scenario: propose 完成後直接進入實作
- **WHEN** openspec-propose skill 完成並輸出最終狀態
- **THEN** Claude 不輸出確認提示，直接呼叫 `Skill(opsx:apply)` 開始實作
