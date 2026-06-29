## Why

檔案搜尋工具（Glob、Grep）在主對話直接執行時，回傳的大量結果會汙染主對話的 context。目前 CLAUDE.md 只是建議委派，沒有強制機制，執行中容易遺漏。改用 hook 封鎖，強制走子代理路徑，與已完成的網頁抓取工具（WebFetch）封鎖一致。

## What Changes

- `settings.json` 新增 PreToolUse hook：攔截主對話直接呼叫檔案搜尋工具（Glob）和內容搜尋工具（Grep），封鎖並注入提示，要求改用子代理執行。

## Capabilities

### New Capabilities
- `glob-grep-subagent-gate`：強制檔案搜尋與內容搜尋走子代理的 hook 機制

### Modified Capabilities
（無）

## Impact

- `C:\Users\yuchi\.claude\settings.json`（全域 hook 設定）
