# gcp-web-terminal — 長期查詢/對照資料

## 網址與登入

- 網址：https://forest-carbon.duckdns.org/claude/
- 帳號：claude
- 密碼：claude2024
- 認證方式：HTTP Basic Auth（ttyd 內建）

## 架構

```
手機/瀏覽器
    │ HTTPS
    ▼
forest-carbon.duckdns.org → besu-bootnode（35.227.93.38）
    │ nginx proxy_pass（內網）
    ▼
besu-member-2（10.10.3.2:7681）
    │ WebSocket
    ▼
ttyd → tmux session "claude" → Claude CLI
```

## VM 設定

- Claude CLI 主機：besu-member-2（us-west1-b，35.252.217.29）
- nginx / SSL 主機：besu-bootnode（us-east1-b，35.227.93.38）
- SSL 憑證：/etc/letsencrypt/live/forest-carbon.duckdns.org/（Certbot 管理）
- nginx 設定：/etc/nginx/sites-enabled/forest-carbon
- claude-proxy snippet：/etc/nginx/snippets/claude-proxy.conf

## member-2 上的服務

- ttyd systemd service：/etc/systemd/system/ttyd.service
  - port 7681，--base-path /claude，--credential claude:claude2024
  - ExecStartPre 執行 ~/start-claude-sessions.sh
- tmux session 名稱："claude"（4 個 window：main / project-2 / project-3 / project-4）
- 啟動腳本：~/start-claude-sessions.sh
- Claude CLI 版本：2.1.160
- Node.js：v20.20.2（nvm）
- 認證方式：~/.claude/.credentials.json（從 Windows PC scp 複製的 OAuth token）

## GCP 防火牆規則

- allow-ttyd-internal：tcp:7681，source 10.0.0.0/8，target-tags: besu-node（besu-vpc）

## tmux 快捷鍵（在瀏覽器裡用）

- Ctrl+B 然後 c：新增 window
- Ctrl+B 然後 數字：切換到第 N 個 window
- Ctrl+B 然後 ,：重新命名目前 window
- Ctrl+B 然後 d：detach（ttyd 會斷線但 session 繼續跑）

## 已知限制

- settings.json 目前沒掛 hooks（未移植 pre-compact-memory-save 等 bash 版本）
- VM 重開機後 ttyd 會自動啟動（systemd enable），但 tmux session 需要 ttyd ExecStartPre 重建
- .credentials.json 的 OAuth token 有時效，過期時需從 Windows 重新 scp

## Project Kitchen 後端（bootnode 上）

- Flask 服務：kitchen.service（systemd enabled，自動重啟）
- 監聽 port：7800（0.0.0.0，外部透過 nginx /kitchen/ 路由）
- Python venv：/home/yuchi/.venv-kitchen（flask 3.1.3、flask-cors 6.0.5）
- 工作目錄：/home/yuchi/project-kitchen/
- 環境變數：
  - CHANGES_DIR=/home/yuchi/openspec/changes
  - PORT=7800
- 外部 API 網址：https://forest-carbon.duckdns.org/kitchen/api/projects（已驗證 200 OK + CORS）
- CORS 允許來源：https://yuchiaoniu.github.io、http://localhost:7799

## nginx 重要注意事項

- /etc/nginx/sites-enabled/forest-carbon 是**複本（非 symlink）**
  - 每次修改 sites-available 後，必須手動 cp 到 sites-enabled 再 reload
  - 指令：sudo cp /etc/nginx/sites-available/forest-carbon /etc/nginx/sites-enabled/forest-carbon && sudo nginx -t && sudo systemctl reload nginx
- /kitchen/ 區塊已加入 HTTPS server block，proxy_pass → 127.0.0.1:7800

## GitHub repo（claude）

- URL：https://github.com/Yuchiaoniu/claude.git（目前 private）
- 本機路徑：C:\Users\yuchi\claude\
- 需要改為 public 才能啟用 GitHub Pages
- credentials/.credentials.json 已從 git 追蹤移除（加入 .gitignore）
- index.html 已複製到 repo 根目錄，供 GitHub Pages 使用
- GitHub Pages 啟用後網址：https://yuchiaoniu.github.io/claude/