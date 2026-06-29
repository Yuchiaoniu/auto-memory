# gcp-web-terminal — 現況快照

## 目前狀態

Phase 1–6 全部完成。ttyd 已 systemd enabled，VM 重開機後自動恢復。
Project Kitchen Flask 後端也已部署在 bootnode，外部 API 可用。

## 可用服務

| 服務 | 網址 | 狀態 |
|------|------|------|
| Claude CLI 網頁終端 | https://forest-carbon.duckdns.org/claude/ | ✅ 運行中 |
| Project Kitchen API | https://forest-carbon.duckdns.org/kitchen/api/projects | ✅ 運行中 |
| Project Kitchen UI（GitHub Pages）| https://yuchiaoniu.github.io/claude/ | ⏳ 待啟用 |

## 剩餘待辦

- [ ] 手動到 GitHub 把 claude repo 改為 public → 設定頁面：https://github.com/Yuchiaoniu/claude/settings
- [ ] 啟用 GitHub Pages：Pages → Branch: master / root → Save
- [ ] 6.3 tmux 視窗重新命名為實際專案名稱（minor）
- [ ] 6.4 將 OAuth 改為 ANTHROPIC_API_KEY（消除憑證過期風險）

## 下一步

完成 GitHub repo 改 public + GitHub Pages 設定後，
https://yuchiaoniu.github.io/claude/ 即可直接存取 Project Kitchen，
無需登入、無需本機 server。