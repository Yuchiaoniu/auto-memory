## Why

部署完成後的自檢範圍不夠具體，導致 Claude 只做 localhost 驗證而跳過外部存取確認；GitHub Pages 部署位置也沒有預設規範，造成重複討論與修正。補上這兩條規則可消除兩類可預見的錯誤。

## What Changes

- CLAUDE.md 新增 VM 部署自檢規則：部署後必須從外部 IP 實際驗證服務可達，不得只做 localhost 確認
- CLAUDE.md 新增 GitHub Pages 部署位置規則：預設使用 main 分支根目錄；有特殊原因時需先與使用者討論再決定

## Capabilities

### New Capabilities
- `vm-deploy-external-check`：VM 部署完成後的外部存取自檢要求
- `github-pages-deploy-default`：GitHub Pages 部署位置預設規範

### Modified Capabilities
（無）

## Impact

- `C:\Users\yuchi\.claude\CLAUDE.md`（全域指令）
