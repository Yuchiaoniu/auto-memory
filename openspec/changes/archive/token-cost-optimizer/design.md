## Context

Claude Code 的計費由四種 token 組成：input（1x）、cache_write（1.25x）、cache_read（0.1x）、output（1x）。長 session 中 cache_read 雖然單價低，但會隨每次 API 呼叫累積：若 context 有 50K tokens 且進行 100 次呼叫，實際讀取量達 5M tokens。目前 autoCompactWindow 設定為 150K，代表 context 要長到相當大才會壓縮；Stop hook 的 cache_read 警示門檻也設在 10M，偏晚介入。

現有腳本：
- `cache-check.ps1`：Stop hook，超過 10M cache_read 才警告
- `token-stats.ps1`：手動執行，顯示最近 5 個 session 的用量

## Goals / Non-Goals

**Goals:**
- 讓 autoCompact 更早觸發，限制單 session 的最大 context 大小
- 提供分級警示，讓使用者在成本擴大前就收到提示
- 強化 token-stats 輸出，加入跨 session 累計與每日成本估算
- 在 CLAUDE.md 明確規範何時必須用 subagent 做探索，避免大量 read 結果污染主 context

**Non-Goals:**
- 不查詢 Anthropic API 取得帳戶餘額（需瀏覽器登入，無法自動化）
- 不限制使用者的對話行為，只提供資訊和建議
- 不修改 Claude Code 核心運作邏輯

## Decisions

**D1：autoCompactWindow 從 150K 降至 80K**
- 80K tokens 約等於 60-80 輪對話，足夠完成一個完整的實作任務
- 更早壓縮 = 後續每次 API 呼叫讀取的 cache 前綴更小
- 替代方案：手動 /compact，但依賴使用者記得執行，不可靠

**D2：cache 警示分三級**
- 綠燈（< 5M）：靜默，不干擾
- 黃燈（5M-10M）：顯示提示訊息，建議考慮 /compact
- 紅燈（> 10M）：強烈警告，建議開新視窗
- 原因：只有一個門檻會導致使用者忽略；分級讓訊號更有意義

**D3：subagent 規則寫進 CLAUDE.md（指引層），不設 hook 強制**
- 強制 hook 會造成誤判（有些 Read 在主 session 是合理的）
- CLAUDE.md 的規則是 Claude 自己要遵守的原則，有足夠的判斷彈性
- 替代方案：PreToolUse hook 攔截 Read/Grep，但過於激進

**D4：token-stats.ps1 加入跨 session 累計**
- 目前只顯示個別 session，無法看今日總花費
- 加入「今日所有 session 合計」區塊，用 LastWriteTime 過濾當天檔案

## Risks / Trade-offs

- [autoCompactWindow 降低] → 壓縮更頻繁，每次 PostCompact 會觸發 Haiku API 呼叫（約 NT$0.5）。若一天壓縮 10 次，額外成本約 NT$5，可接受。
- [分級警示] → 需要在 Stop hook 裡讀取 JSONL 並計算，增加每次對話結束的延遲約 1-2 秒。

## Migration Plan

1. 修改 settings.json（autoCompactWindow）
2. 強化 cache-check.ps1（分三級）
3. 強化 token-stats.ps1（加跨 session 累計）
4. 更新 CLAUDE.md（加 subagent 隔離規則段落）
5. 手動執行 token-stats.ps1 確認輸出格式正確

回滾：settings.json 改回 150K，cache-check.ps1 改回單一門檻。

## Open Questions

- token-stats.ps1 的 NT$ 匯率是否需要設為可設定的環境變數？（目前寫死 32）
