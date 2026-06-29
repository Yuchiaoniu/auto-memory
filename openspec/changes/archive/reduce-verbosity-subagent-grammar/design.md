## Context

- `verbose: true` 目前讓所有工具呼叫區塊顯示在對話框，造成版面被洗掉
- `openspec-apply-change/SKILL.md` 的步驟 2（openspec status）與步驟 3（openspec instructions apply）直接在主 session 跑 Bash，回傳 JSON 塞入 context
- CLAUDE.md 的單字動詞問題（加/改/刪）尚未在規則裡明確列出

## Goals / Non-Goals

**Goals:**
- 隱藏 Layer 1 工具呼叫區塊
- openspec-apply-change SKILL.md 的純查詢 Bash 改為委派 Haiku 子代理
- CLAUDE.md 補充單字動詞規則

**Non-Goals:**
- 不修改 Layer 2（Claude 文字輸出）的 skill 進度訊息
- 不修改其他 skill（openspec-propose、openspec-explore）

## Decisions

**verbose: false**：直接改 settings.json，立即生效於新對話。

**SKILL.md 子代理委派**：在步驟 2 與步驟 3 的說明文字加入一段指示：
「使用 Agent tool（subagent_type: Explore, model: haiku）執行此 Bash 指令，只傳回 JSON 文字摘要，不把原始輸出帶回主 session。」

**單字動詞規則**：加入「回覆原則與寫作規則」段落，與現有主謂賓規則並列。

## Risks / Trade-offs

- [風險] verbose: false 後若需要 debug，工具呼叫會看不到 → 可隨時改回 true
- [風險] SKILL.md 加子代理指示後，Claude 是否確實遵守仍依賴規則執行品質
