# auto-memory-sync — 現況快照

## 目前狀態
所有任務已完成，記憶同步機制正常運行中。

## 系統架構（目前生效）
- 自動壓縮：`autoCompactEnabled: true`，門檻 170000 tokens
- Stop hook：`pre-compact-memory-save.ps1`（async, timeout 40）— 每輪對話結束後背景更新 STATE.md
- SessionStart compact：`session-start-inject-state.ps1` — 壓縮後自動念回專案狀態
- SessionStart startup|clear：`session-start-menu.ps1` — 啟動或 clear 後列專案選單，並執行環境自檢
- PreToolUse Glob|Grep：封鎖主對話直接呼叫，強制改用子代理（Agent, model: haiku）
- PreToolUse WebFetch：封鎖主對話直接呼叫，強制改用子代理（Agent, model: haiku）
- PostToolUse Write|Edit：`review-reminder.ps1` — 寫入後提醒執行測試驗證

## 環境自檢清單（session-start-menu.ps1）
- Tesseract PATH 檢查：已安裝但不在 PATH → 自動補入 + 警告
- Tesseract 未安裝 → 顯示 winget 安裝指令

## 三檔分工規則
- tasks.md：主要進度，程式不碰
- memory.md：長期查詢/對照資料，只增修去重，不刪有效舊資料
- STATE.md：短期現況快照，精簡；存檔時把長期資料搬到 memory.md 再從這裡剔除

## 我們已經知道的限制
- 腳本無法在使用者打字前主動開口，第一則回覆才會跳出選單
- 腳本與 Claude 都無法自動執行 /clear，clear 由使用者親手按
- 節流門檻：對話成長 20,000 tokens 才觸發一次 Haiku 更新
- Read 與 Bash 無法用 hook 預先封鎖（輸出大小只有執行後才知道），以 CLAUDE.md 規則補足

## 下一步
目前無待辦事項。
