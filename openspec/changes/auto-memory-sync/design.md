## Context

Claude Code 的 `autoCompact` 在 context 達到 150K tokens 時自動觸發，將對話壓縮成摘要後繼續 session。壓縮摘要包含該 session 的核心資訊，是更新記憶的最佳時間點。`PostCompact` hook 在壓縮完成後觸發，stdin 收到含 `summary` 欄位的 JSON。

記憶系統位於 `C:\Users\yuchi\.claude\projects\C--Users-yuchi\memory\`，包含 `MEMORY.md`（索引）和各個 `*.md` 記憶檔。

## Goals / Non-Goals

**Goals:**
- PostCompact 觸發時，在背景自動分析摘要並更新記憶檔
- 使用 Haiku（最便宜）降低每次更新成本
- async 執行，完全不影響使用者體驗
- 無 API key 時靜默退出，不報錯

**Non-Goals:**
- 不做 /clear 自動化（仍靠使用者開新視窗）
- 不在每次 Stop 時執行（太頻繁且 Stop 沒有對話內容）
- 不管理 session 之間的 cache（那是開新視窗的責任）

## Decisions

**D1：使用 Haiku 而非 Sonnet/Opus**
每次 PostCompact 呼叫一次 API，Haiku 成本約 NT$0.5，Sonnet 約 NT$2，一天觸發 3-5 次差距明顯。記憶摘要任務複雜度不高，Haiku 足夠。

**D2：async hook（不阻塞）**
設定 `"async": true`，腳本在背景執行。使用者不需等待，失敗也不影響對話。

**D3：腳本讀取現有 MEMORY.md 作為 context**
讓 Haiku 知道目前已有哪些記憶，避免重複寫入或衝突。

**D4：只更新有變化的記憶，無變化時靜默退出**
Haiku 回應 `NO_UPDATE` 時腳本直接 exit 0，不寫任何檔案。

**D5：腳本路徑固定在 `~/.claude/`**
與 `cache-check.ps1` 同目錄，便於管理。

## Risks / Trade-offs

- [API key 未設定] → 腳本開頭檢查 `$env:ANTHROPIC_API_KEY`，不存在則 exit 0
- [Haiku 判斷不準確] → 記憶更新仍可手動覆寫，不會破壞現有檔案
- [PostCompact 在任務中途觸發] → async 執行不中斷，但摘要只反映截至壓縮點的資訊，下次壓縮會補上
- [JSON 解析失敗] → 所有 try/catch 靜默退出，不影響主對話
