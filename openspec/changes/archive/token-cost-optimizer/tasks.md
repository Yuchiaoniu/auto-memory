## 1. 調整 autoCompactWindow

- [x] 1.1 修改 `~/.claude/settings.json`，將 `autoCompactWindow` 從 150000 改為 80000
- [x] 1.2 確認 settings.json JSON 語法正確

## 2. 強化 cache-check.ps1（分三級警示）

- [x] 2.1 加入黃燈邏輯：cache_read 介於 5M-10M 輸出建議訊息
- [x] 2.2 確認紅燈邏輯：cache_read > 10M 輸出強烈警告（現有）
- [x] 2.3 確認綠燈邏輯：cache_read < 5M 靜默退出（現有）
- [x] 2.4 測試三級警示各自觸發正確

## 3. 強化 token-stats.ps1

- [x] 3.1 加入 `CLAUDE_NTD_RATE` 環境變數支援（預設 32）
- [x] 3.2 加入「Today Total」區塊，篩選當天所有 session 並累計 cache_read、output、NT$
- [x] 3.3 測試執行輸出格式正確

## 4. 更新 CLAUDE.md（subagent 隔離規則）

- [x] 4.1 在 `~/.claude/CLAUDE.md` 的 Subagent Model Policy 段落之後加入「Subagent Isolation Policy」
- [x] 4.2 規則內容：搜尋超過 3 個檔案或結果超過 100 行時必須用 Agent tool（Explore/Haiku）
- [x] 4.3 規則內容：已知單一路徑的 Read 可在主 session 直接執行
- [x] 4.4 規則內容：subagent 回傳只能是摘要，不貼完整原始輸出

## 5. 驗收測試

- [x] 5.1 手動執行 token-stats.ps1，確認顯示格式與 Today Total 正確
- [x] 5.2 確認 cache-check.ps1 在模擬低/中/高 cache_read 時各輸出正確訊息
- [x] 5.3 確認 settings.json 的 autoCompactWindow 已更新
- [x] 5.4 確認 CLAUDE.md 包含新的 Subagent Isolation Policy 段落
