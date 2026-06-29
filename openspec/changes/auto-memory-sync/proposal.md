## Why

每次 Claude Code session 結束後，對話中學到的資訊（專案進度、使用者偏好、技術決策）不會自動寫入記憶檔。目前依賴 Claude 在對話中手動呼叫 Write tool 更新 memory/*.md，容易遺漏。autoCompact 在壓縮對話時本身就在做摘要，這是最自然的時間點補上自動記憶更新。

## What Changes

- 新增 `post-compact-memory-update.ps1` 腳本，在 PostCompact 觸發後背景執行
- 腳本讀取壓縮摘要，呼叫 Claude Haiku API 分析並更新 memory/*.md
- 在 `~/.claude/settings.json` 加入 PostCompact hook（async，不阻塞使用體驗）
- 使用 `ANTHROPIC_API_KEY` 環境變數驗證 API

## Capabilities

### New Capabilities

- `compact-trigger`: 偵測 PostCompact 事件，從 stdin 取得壓縮摘要
- `memory-extractor`: 呼叫 Haiku API 分析摘要，判斷哪些內容需要寫入記憶
- `memory-writer`: 將分析結果更新至 memory/*.md 及 MEMORY.md 索引

### Modified Capabilities

（無現有 spec）

## Impact

- 修改 `~/.claude/settings.json`（加入 PostCompact hook）
- 新增 `~/.claude/post-compact-memory-update.ps1`
- 依賴 `ANTHROPIC_API_KEY` 環境變數
- 每次 autoCompact 觸發時額外呼叫一次 Haiku API（約 NT$0.5-1）
- 不影響正常對話流程（async 執行）
