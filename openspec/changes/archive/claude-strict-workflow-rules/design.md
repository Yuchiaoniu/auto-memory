## Context

CLAUDE.md 是 Claude Code 的全域規則檔，每次對話開始時自動載入。目前的 OpenSpec 模式切換規則使用「盡量」語氣，Claude 在實際執行時容易判斷為「這次不需要」而跳過。

## Goals / Non-Goals

**Goals:**
- 任何討論強制進入 explorer 模式，任何寫入強制走 propose→apply
- 全域設定變更（CLAUDE.md 等）歸屬 auto-memory-sync 專案
- 回覆問句使用完整動詞結構

**Non-Goals:**
- 不改變 openspec-explore / openspec-propose / opsx:apply 的內部行為
- 不改變 hook 腳本（review-reminder.ps1 等）

## Decisions

**決策一：「任何」而非「當判斷需要時」**
用絕對語氣取代條件語氣。原規則「使用者在討論想法時」讓 Claude 有判斷空間，新規則改為「只要不是在執行寫入，就是在討論，就進 explorer」。

**決策二：歸屬規則明確化**
CLAUDE.md 屬於 auto-memory-sync 管理範疇。任何全域設定（CLAUDE.md、settings.json、ps1 腳本）的 propose 一律建在 auto-memory-sync，不建新專案。

**決策三：問句語法規則放入回覆原則**
與現有中文寫作規則並列，確保每次對話開始就載入。

## Risks / Trade-offs

- [風險] propose→apply 增加每次小改動的步驟數 → 接受，因為 task 紀錄的價值高於便利性
- [風險] 規則仍是文字提示，無法 100% 強制執行 → 用「嚴禁」「必須」等強制語氣減少例外
