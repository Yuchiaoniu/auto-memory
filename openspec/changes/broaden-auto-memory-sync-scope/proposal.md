## Why

目前「全域設定歸屬 auto-memory-sync」規則只列了 CLAUDE.md、settings.json、全域 ps1 腳本。但 Claude 工作流程改進的範圍更廣——部署規則、自檢要求、hook 設定、記憶機制等都屬於同一類，卻沒有被規則覆蓋，導致仍會另開新專案。

## What Changes

- CLAUDE.md「全域設定歸屬規則」的歸屬範圍從「全域設定」擴大為「所有對 Claude 工作流程的新功能或改進」

## Capabilities

### New Capabilities
（無）

### Modified Capabilities
- `auto-memory-sync-scope`：擴大歸屬規則的適用範圍

## Impact

- `C:\Users\yuchi\.claude\CLAUDE.md`（全域指令）
