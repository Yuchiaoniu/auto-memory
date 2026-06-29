## Context

目前 CLAUDE.md 的規則全靠我在每輪對話自覺遵守，沒有任何外部機制檢查。兩個問題分別對應兩種不同的強制手段：語法規則只能靠 CLAUDE.md 明文約束，WebFetch 委派則可以靠 hook 機制真正攔截。

## Goals / Non-Goals

**Goals:**
- CLAUDE.md 新增明確的中文書寫規則，讓我在生成回覆時有具體可遵守的條文
- settings.json 新增 PreToolUse hook，攔截直接呼叫網頁抓取工具並封鎖，強制走子代理路徑

**Non-Goals:**
- 不攔截子代理內部的網頁抓取呼叫（子代理本來就應該能直接抓取）
- 不處理其他工具的委派問題（讀取動作、搜尋等留待後續）

## Decisions

**中文書寫規則**：寫進 CLAUDE.md「回覆原則與寫作規則」區塊，與現有規則並列。

**WebFetch hook**：使用 PreToolUse + matcher `WebFetch`，hook 輸出 JSON 含 `hookSpecificOutput.permissionDecision: "deny"` 與 `permissionDecisionReason`，封鎖呼叫並說明原因。hook 用 PowerShell 執行，與現有 hook 風格一致。

## Risks / Trade-offs

[風險] 封鎖所有直接網頁抓取呼叫，若子代理本身也被攔截，會造成無限循環 → 需確認 PreToolUse hook 只在主對話觸發，子代理呼叫不受影響（Claude Code 的 hook 機制不會在子代理內觸發，此風險低）。
