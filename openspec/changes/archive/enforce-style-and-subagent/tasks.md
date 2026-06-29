## 1. 修改 CLAUDE.md

- [x] 1.1 在「回覆原則與寫作規則」區塊新增規則：純中文敘述句禁止直接嵌入英文工具名稱當主詞或受詞，必須先用白話中文描述功能，原始名稱以括號補充

## 2. 修改 settings.json

- [x] 2.1 新增 PreToolUse hook，matcher 為 `WebFetch`，封鎖呼叫並注入訊息：「請改用子代理（Agent, model: haiku）執行網頁抓取，不得在主對話直接呼叫 WebFetch」
