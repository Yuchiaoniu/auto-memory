## Context

settings.json 已有 WebFetch 的 PreToolUse 封鎖 hook，Glob 和 Grep 採相同模式新增即可。評估過工作流程，封鎖後的影響如下：Edit 前的準備讀取使用 Read 工具（非 Glob/Grep），openspec 指令使用 Bash 呼叫，不受影響。

## Goals / Non-Goals

**Goals:**
- 新增 PreToolUse hook，matcher 為 `Glob|Grep`，封鎖並注入說明

**Non-Goals:**
- 不修改 CLAUDE.md（規則已存在，這裡只補 hook 強制層）
- 不封鎖 Read 和 Bash（有合法的主對話使用情境）

## Decisions

matcher 寫成 `Glob|Grep` 合併為單一 hook 條目，與 WebFetch hook 並列在 PreToolUse 陣列中。PowerShell 指令與現有 hook 風格一致。

## Risks / Trade-offs

[風險] 子代理啟動有 1-2 秒 overhead，搜尋操作會略慢 → 接受，換取 context 乾淨。
[風險] 子代理若回傳摘要過於模糊，主對話可能遺失具體路徑或行號 → 委派時在指令中明確要求「具體路徑與行號必須逐一列出」。
