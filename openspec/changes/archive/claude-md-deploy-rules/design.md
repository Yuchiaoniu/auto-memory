## Context

CLAUDE.md 的程式碼寫入後測試要求規則目前只說「必須執行測試腳本驗證」，沒有指定 VM 部署場景下的驗證範圍。GitHub Pages 部署位置也無預設，每次都要現場討論。

## Goals / Non-Goals

**Goals:**
- 在 CLAUDE.md 補一條 VM 部署自檢規則，要求外部 IP 驗證
- 在 CLAUDE.md 補一條 GitHub Pages 部署位置預設規則

**Non-Goals:**
- 不修改 settings.json 或任何 hook
- 不變更現有測試要求規則的其他內容

## Decisions

兩條規則都作為獨立段落插入 CLAUDE.md，緊接在「程式碼寫入後的測試要求」區塊之後，避免與現有規則混淆。

VM 自檢規則明確列出「不得只做 localhost 確認」的負面範例，讓規則邊界清晰。

GitHub Pages 規則採「預設 + 例外流程」結構：有特殊原因時觸發討論，而不是一律禁止其他位置。

## Risks / Trade-offs

[風險] 「特殊原因」定義模糊，未來可能產生灰色地帶 → 接受，保留彈性；遇到真實案例再收窄定義。
