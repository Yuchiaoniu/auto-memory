## Why

三個獨立問題需要同時修正：工具呼叫區塊洗版面、skill 腳本未使用子代理導致 context 膨脹、回覆規則缺少單字動詞縮略的禁止說明。

## What Changes

- `settings.json`：`verbose` 改為 `false`，隱藏 Layer 1 工具呼叫區塊
- `opsx:apply` skill 腳本：`openspec status` 與 `openspec instructions` 的 Bash 查詢改為派 Haiku 子代理執行，只傳摘要回主 session
- `CLAUDE.md`：回覆規則新增單字動詞禁止縮略規則

## Capabilities

### New Capabilities

- `single-char-verb-rule`：單字動詞禁止縮略，必須使用完整動詞形式

### Modified Capabilities

（無既有 spec 需要修改）

## Impact

- `C:\Users\yuchi\.claude\settings.json`：verbose 改 false
- `C:\Users\yuchi\.claude\skills\` 下的 opsx:apply skill 腳本
- `C:\Users\yuchi\.claude\CLAUDE.md`：回覆原則與寫作規則新增一條
- GitHub repo `pre-compact-memory-save`：同步 push
