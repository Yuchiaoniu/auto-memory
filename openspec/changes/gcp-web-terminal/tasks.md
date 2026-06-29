# gcp-web-terminal 任務清單

目標：在 GCP VM 上架設 Claude CLI + ttyd，透過 DuckDNS HTTPS 網址從手機/瀏覽器操作，支援 tmux 多視窗與 Basic Auth。

## Phase 1：環境安裝

- [x] 1.1 確認目標 VM 資源（選 besu-member-2，查 CPU/RAM 使用率）
- [x] 1.2 安裝 Node.js 20.x（nvm）
- [x] 1.3 安裝 Claude CLI（npm install -g @anthropic-ai/claude-code）
- [x] 1.4 確認 tmux 已安裝（或安裝）
- [x] 1.5 安裝 ttyd

## Phase 2：Claude CLI 設定

- [x] 2.1 複製 CLAUDE.md（全域規則）到 VM 的 ~/.claude/CLAUDE.md
- [x] 2.2 建立 Linux 版 settings.json（暫時不掛 hooks，先讓 Claude 能跑）
- [x] 2.3 複製 .credentials.json（OAuth token）到 VM，跳過手動 Google auth
- [x] 2.4 確認 claude 版本正常（2.1.160）

## Phase 3：tmux 多視窗設定

- [x] 3.1 建立 tmux 預設 session 腳本（start-claude-sessions.sh）
       4 個 window（main / project-2 / project-3 / project-4），每個都 source nvm
- [x] 3.2 測試在 tmux 裡切換視窗、新增視窗

## Phase 4：ttyd 架設

- [x] 4.1 啟動 ttyd 連進 tmux session（port 7681，--base-path /claude）
- [x] 4.2 設定 Basic Auth（帳號：claude，密碼：claude2024）
- [x] 4.3 建立 ttyd.service（systemd，開機自啟）

## Phase 5：nginx 反代設定

- [x] 5.1 在 bootnode nginx 加 location /claude/ block，proxy_pass 到 member-2 內網 10.10.3.2:7681
- [x] 5.2 設定 WebSocket upgrade header（ttyd 需要）
- [x] 5.3 確認 HTTPS 正常（DuckDNS 憑證已在 bootnode）
- [x] 5.4 新增 GCP 防火牆規則 allow-ttyd-internal（tcp:7681，內網 10.0.0.0/8）
- [x] 5.5 從 Windows 測試 HTTPS 全鏈路（HTTP 200 ✓）

## Phase 6：收尾

- [x] 6.1 從手機瀏覽器實際連線測試（輸入網址、登入、開 claude）✓ 可連入
- [x] 6.2 確認 VM 重開機後 ttyd + tmux session 自動恢復（2026-06-16 systemctl enable ttyd 補齊，已驗證外部 HTTPS 200）
- [ ] 6.3 tmux 視窗重新命名為實際專案名稱
