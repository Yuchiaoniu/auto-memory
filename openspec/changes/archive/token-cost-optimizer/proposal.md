## Why

Claude Code session 的 context 會隨著對話進行持續累積，每次 API 呼叫都會重新讀取整個 cache 前綴（0.1x 計費），導致長 session 的 cache_read 成本隨呼叫次數線性增長。目前已有零散的監控腳本（cache-check.ps1、token-stats.ps1），但缺乏系統性的預防與可視化機制，無法在成本擴大前主動介入。

## What Changes

- 整合並強化現有 `cache-check.ps1` 與 `token-stats.ps1`，提供每個 session 的完整成本分解
- 降低 `autoCompactWindow` 門檻（150K → 80K），更早觸發 compact 以限制 cache 前綴大小
- 在 CLAUDE.md 加入強制性的 subagent 隔離規則，讓 Grep/Read 等探索操作不污染主 context
- 建立 Stop hook 的成本警示標準，依據不同閾值給出分級提示

## Capabilities

### New Capabilities

- `cost-dashboard`: 跨 session 的 token 用量統計與 NT$ 成本估算，含每 session 摘要
- `compact-threshold`: autoCompactWindow 設定管理與分級 cache 警示規則
- `subagent-isolation`: CLAUDE.md 的 subagent 強制使用規則，搭配範例說明何時必須開 Agent

### Modified Capabilities

（無現有 spec）

## Impact

- 修改 `~/.claude/settings.json`（autoCompactWindow 從 150K 降至 80K）
- 修改 `~/.claude/CLAUDE.md`（加入 subagent 隔離規則）
- 強化 `~/.claude/token-stats.ps1`（加入跨 session 累計、NT$ 試算）
- 強化 `~/.claude/cache-check.ps1`（分級警示：5M / 10M / 20M tokens）
