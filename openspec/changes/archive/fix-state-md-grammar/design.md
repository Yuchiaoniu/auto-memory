## Context

auto-memory-sync 專案的 STATE.md 沿用了「已知限制」這個縮略 section header，以及需確認是否有「正在…中」冗餘寫法。這兩者不符合 CLAUDE.md 規定的完整主謂賓語法規則。

## Goals / Non-Goals

**Goals:**
- 將 `## 已知限制` 改為 `## 我們已經知道的限制`
- 掃描並修正 STATE.md 中任何「正在…中」冗餘（去掉「正在」，保留「中」）

**Non-Goals:**
- 不修改任何腳本或設定檔
- 不改變 STATE.md 的其他內容或結構

## Decisions

直接用 Edit 工具修改 STATE.md，只改兩處目標文字，其餘內容不動。

## Risks / Trade-offs

風險極低：純文字替換，不影響任何程式邏輯。
