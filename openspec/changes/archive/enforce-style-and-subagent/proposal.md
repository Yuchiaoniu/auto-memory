## Why

兩條規則在 CLAUDE.md 裡只是「對我的建議」，我在執行中會漏掉，使用者必須反覆糾正相同的問題。改成系統層級的強制執行，消除依賴我自覺遵守的弱點。

## What Changes

- `CLAUDE.md` 新增回覆規則：純中文敘述句禁止直接嵌入英文工具名稱當主詞或受詞，必須先用白話中文說明，原始名稱以括號補充。
- `settings.json` 新增 PreToolUse hook：攔截主對話直接呼叫網頁抓取工具（WebFetch），封鎖並注入提示，要求改用子代理（Agent, model: haiku）執行。

## Capabilities

### New Capabilities
- `chinese-style-rule`：中文句子禁止夾雜英文工具名稱的書寫規則
- `webfetch-subagent-gate`：強制網頁抓取走子代理的 hook 機制

### Modified Capabilities
（無）

## Impact

- `C:\Users\yuchi\.claude\CLAUDE.md`（全域規則）
- `C:\Users\yuchi\.claude\settings.json`（hook 設定）
