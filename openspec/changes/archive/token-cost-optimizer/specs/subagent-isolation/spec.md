## ADDED Requirements

### Requirement: CLAUDE.md 加入 subagent 隔離規則段落
全域 CLAUDE.md SHALL 包含明確的 subagent 隔離規則，說明何種操作必須透過 Agent tool 執行，而非直接在主 session 呼叫工具。

#### Scenario: 規則段落存在
- **WHEN** 讀取 `~/.claude/CLAUDE.md`
- **THEN** 包含「Subagent Isolation Policy」或等效段落，列出需要隔離的操作類型

### Requirement: 探索性搜尋必須透過 subagent
CLAUDE.md 的規則 SHALL 明確要求：當搜尋範圍超過 3 個檔案、或結果超過 100 行時，必須使用 Agent tool（subagent_type: Explore，model: haiku）執行。

#### Scenario: 大範圍 grep 操作
- **WHEN** 需要在整個 codebase 搜尋一個 pattern
- **THEN** Claude 使用 Agent tool 而非直接呼叫 Grep，避免大量結果進入主 context

#### Scenario: 單一明確路徑的 read
- **WHEN** 已知目標檔案路徑且只讀一個檔案
- **THEN** 可直接在主 session 使用 Read tool（不需要 subagent）

### Requirement: subagent 回傳結果簡潔化
CLAUDE.md 的規則 SHALL 要求 subagent 只回傳摘要或關鍵結果，不得將完整原始輸出貼回主 session。

#### Scenario: subagent 完成搜尋
- **WHEN** Explore subagent 完成搜尋任務
- **THEN** 只回傳「找到 X 個符合項目，位於 Y 和 Z」，而非完整的 grep 輸出
