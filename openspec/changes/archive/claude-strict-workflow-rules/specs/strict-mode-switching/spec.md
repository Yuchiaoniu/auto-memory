## ADDED Requirements

### Requirement: 任何討論強制進入 explorer 模式
只要對話內容是討論、提問、評估、探索，Claude SHALL 立即呼叫 Skill(openspec-explore) 並在回覆第一句標示【探索模式】。「正在寫入檔案」是唯一不進 explorer 的狀態。

#### Scenario: 使用者提出新想法
- **WHEN** 使用者描述一個想法或問題，且尚未要求寫入任何檔案
- **THEN** Claude 呼叫 Skill(openspec-explore) 並回覆以【探索模式】開頭

#### Scenario: 使用者詢問技術問題
- **WHEN** 使用者問「為什麼」「怎麼做」「能使用 X 嗎」等問題
- **THEN** Claude 進入 explorer 模式再回答，而非直接回答

### Requirement: 任何檔案寫入強制走 propose→apply
任何檔案寫入（含 .md、.json、.ps1、.html、設定檔、程式碼）在執行前 Claude SHALL 先呼叫 Skill(openspec-propose) 產生提案，提案確認後再呼叫 Skill(opsx:apply)。緊急修復與 typo fix 不得例外。

#### Scenario: 修改 CLAUDE.md
- **WHEN** 需要修改 CLAUDE.md 或任何全域設定檔
- **THEN** Claude 先在 auto-memory-sync 專案下建立 propose，確認後再 apply，不得直接 Edit

#### Scenario: 緊急修復 nginx 設定
- **WHEN** nginx 設定出錯需要立即修正
- **THEN** Claude 仍先呼叫 propose（可快速建立單一任務的輕量提案），apply 後再執行修復

#### Scenario: typo fix
- **WHEN** 發現一個字的拼字錯誤需要修正
- **THEN** Claude 仍走完整 propose→apply 流程以留下 task 紀錄

### Requirement: 全域設定 propose 歸屬 auto-memory-sync
CLAUDE.md、settings.json、全域 ps1 腳本等全域設定的 propose SHALL 建在 auto-memory-sync 專案底下，不建立新專案。

#### Scenario: 新增 CLAUDE.md 規則
- **WHEN** 需要在 CLAUDE.md 新增或修改任何規則
- **THEN** propose 建在 `openspec/changes/` 底下並歸屬 auto-memory-sync，而非建立獨立新專案
