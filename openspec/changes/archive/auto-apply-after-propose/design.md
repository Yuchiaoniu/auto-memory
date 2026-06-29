## Context

目前 Claude 在 openspec-propose 完成後，會照著 skill 腳本的 Output 段落輸出確認提示（「Run /opsx:apply or ask me to implement」），導致使用者需要多說一次才能繼續。改法是在 CLAUDE.md 加一條全域規則，讓 Claude 的行為覆蓋 skill 腳本的提示。

## Goals / Non-Goals

**Goals:**
- 在 CLAUDE.md 的 OpenSpec 模式切換規則中，新增「propose 完成後直接呼叫 opsx:apply」這條指令
- 讓這條規則全域生效，適用於所有專案的所有提案

**Non-Goals:**
- 不修改 openspec-propose skill 腳本本身
- 不區分大小變更（一律直接實作）

## Decisions

將規則寫進 CLAUDE.md 的「提案＋實作模式」區塊，緊接在現有規則後面，格式與現有規則一致。CLAUDE.md 的規則優先級高於 skill 腳本的輸出提示，Claude 會遵循 CLAUDE.md 而非跟著 skill 輸出確認。

## Risks / Trade-offs

[風險] 使用者有時只想看提案、不想立刻實作 → 目前接受這個取捨，使用者可以在 apply 開始後隨時中斷。
