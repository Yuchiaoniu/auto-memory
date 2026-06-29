## ADDED Requirements

### Requirement: PostCompact hook 觸發腳本
系統 SHALL 在 `~/.claude/settings.json` 中設定 PostCompact hook，以 async 方式呼叫 `post-compact-memory-update.ps1`。

#### Scenario: autoCompact 觸發後
- **WHEN** Claude Code 的 autoCompact 壓縮對話完成
- **THEN** hook 在背景啟動腳本，不阻塞使用者操作

#### Scenario: 腳本收到空摘要
- **WHEN** PostCompact stdin 的 `summary` 欄位為空或長度小於 50 字元
- **THEN** 腳本靜默 exit 0，不呼叫 API

#### Scenario: API key 未設定
- **WHEN** `ANTHROPIC_API_KEY` 環境變數不存在
- **THEN** 腳本靜默 exit 0，不報錯
