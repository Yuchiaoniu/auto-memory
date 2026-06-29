# project-kitchen — 任務清單

## 進行中

- [ ] 設計英文科目 12 個觀念的路徑＋錨定心智模型框架
  - 英文科目的學習性質和財務/統計/心理不同，需要先確認 12 個觀念選題
  - 格式沿用其他三科：正向錨定＋常見錯誤路徑一、二

## 待辦

- [ ] 實作 GitHub → GCP 同步機制
  - 把 project-kitchen 資料夾上傳 GitHub（含 system-design.md、loop-starter.md、cross_subject_bot.py）
  - GCP 設定 git pull 機制，讓本機發指令後 GCP 自動拉取最新版並執行
  - 目的：迭代優化在 GCP 上執行，不受本機休眠影響

- [ ] 確認 GCP 上的 Claude Code 認證是否仍有效
  - 檢查 `~/.config/claude/` 目錄下的 token 是否過期
  - 若過期需重新複製本機登入紀錄

- [ ] 建立 project-kitchen 的 GitHub 倉儲
  - 決定倉儲名稱與哪些檔案需要版本控制（排除 `__pycache__`、`server.log`）

## 已完成

- [x] 跨科目學習 Bot v2.0 啟動（cross_subject_bot.py）
- [x] 自動迭代優化架構（loop-starter.md + ScheduleWakeup）
- [x] Telegram Bot 建立（中文顯示 UTF-8 位元組陣列修正）
- [x] fork 子代理改為一般 Sonnet 子代理（解決完整內容污染主對話視窗問題）
- [x] 財務科目 12 個觀念心智模型補充
- [x] 統計科目 12 個觀念心智模型補充
- [x] 心理科目 12 個觀念心智模型補充
- [x] 補建 log.md / state.md / memory.md / tasks.md 四個標準檔案
