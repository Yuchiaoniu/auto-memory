## Why

目前 CLAUDE.md 的模式切換規則過於寬鬆，Claude 在實際執行時常常跳過 explorer 和 propose→apply 流程，導致缺乏任務紀錄、變更缺乏可追溯性。需要強制執行嚴格模式，讓所有討論和所有檔案寫入都有對應的 openspec 紀錄。

## What Changes

- 任何討論、問題、評估 → 強制呼叫 `openspec-explore`，標示【探索模式】
- 任何檔案寫入（.md、.json、.ps1、設定檔、程式碼）→ 強制先 `openspec-propose` 再 `opsx:apply`，標示【提案模式】/【實作模式】
- CLAUDE.md 等全域設定的 propose 歸屬 `auto-memory-sync` 專案
- 緊急修復、typo fix 同樣走完整流程（確保 task 紀錄存在）
- 回覆問句規則：禁止截斷式問法（「X 能用嗎」），改用完整動詞結構（「能使用 X 嗎」）

## Capabilities

### New Capabilities

- `strict-mode-switching`: 嚴格的 openspec 模式自動切換規則，含模式標示與歸屬邏輯
- `reply-grammar-rules`: 回覆問句的完整動詞結構語法規則

### Modified Capabilities

（無既有 spec 需要修改）

## Impact

- `C:\Users\yuchi\.claude\CLAUDE.md`：OpenSpec 模式切換段落全面改寫，回覆規則新增問句語法
- GitHub repo `pre-compact-memory-save`：需同步 push
