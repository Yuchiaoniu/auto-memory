## Why

每次 openspec-propose 完成後，Claude 都會輸出確認提示，要求使用者再說一次「實作」才繼續，造成不必要的來回。使用者的意圖在說「幫我做 X」時已經明確，提案只是中間步驟，不需要再次確認。

## What Changes

- 在全域 `CLAUDE.md` 的「OpenSpec 模式切換」規則中新增一條：openspec-propose 完成後，Claude 不等使用者確認，直接接著呼叫 `opsx:apply` 進行實作。

## Capabilities

### New Capabilities
- `auto-apply-trigger`: 定義 Claude 在 openspec-propose 完成後應自動觸發 opsx:apply 的行為規則

### Modified Capabilities
（無既有 spec 需要修改）

## Impact

- 僅影響 `C:\Users\yuchi\.claude\CLAUDE.md`（全域規則）
- 不影響任何腳本或設定檔
