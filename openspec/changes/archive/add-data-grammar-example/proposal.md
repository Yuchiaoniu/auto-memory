## Why

CLAUDE.md 的中文寫作規則只有技術術語型的反例（「梯度強度分不清」），缺乏數字/資料型的反例。導致 Claude 在輸出數值清單時，滑入「14 GB 用掉」這種話題化結構而未被規則攔截。

## What Changes

- 在「回覆原則與寫作規則」段落補充數字/資料型的主謂賓反例與正例

## Capabilities

### New Capabilities

- `data-grammar-example`: 數字資料型話題化反例，補入中文寫作規則

### Modified Capabilities

（無）

## Impact

- `C:\Users\yuchi\.claude\CLAUDE.md`：回覆原則與寫作規則段落新增一條反例說明
- GitHub repo `pre-compact-memory-save`：同步 push
