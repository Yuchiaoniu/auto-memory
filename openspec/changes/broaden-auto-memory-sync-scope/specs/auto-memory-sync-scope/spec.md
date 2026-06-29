## MODIFIED Requirements

### Requirement: 工作流程相關變更歸屬 auto-memory-sync
任何對 Claude 工作流程的新功能或改進（含 CLAUDE.md、settings.json、hooks、記憶機制、部署規則等）SHALL 一律在 auto-memory-sync 專案下建立 openspec 變更，不另外建立新的獨立專案。

#### Scenario: 全域設定類變更歸屬正確
- **WHEN** 需要對 CLAUDE.md、settings.json 或全域 ps1 腳本提出 propose
- **THEN** 在 auto-memory-sync 專案底下建立變更，不建立新專案

#### Scenario: 工作流程改進類變更歸屬正確
- **WHEN** 需要對 hooks、記憶機制、部署規則、自檢規範等工作流程功能提出 propose
- **THEN** 在 auto-memory-sync 專案底下建立變更，不建立新專案
