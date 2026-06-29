## Context

CLAUDE.md 現有規則：「CLAUDE.md、settings.json、全域 ps1 腳本等全域設定的 propose，一律建在 auto-memory-sync 專案底下，不建立新專案。」只改這一句的範圍描述即可，其他規則不動。

## Goals / Non-Goals

**Goals:**
- 把歸屬規則的觸發條件從「全域設定」擴大為「所有 Claude 工作流程相關變更」

**Non-Goals:**
- 不影響其他專案的 openspec 變更（非工作流程性質的功能開發仍各自建立專案）

## Decisions

只修改 CLAUDE.md 中該規則的一句描述，新措辭：「任何對 Claude 工作流程的新功能或改進（含 CLAUDE.md、settings.json、hooks、記憶機制、部署規則等），一律建在 auto-memory-sync 專案底下，不建立新專案。」

## Risks / Trade-offs

[風險] 「工作流程相關」邊界仍有模糊空間 → 接受，遇到邊界案例時再討論；規則已比原來精確。
