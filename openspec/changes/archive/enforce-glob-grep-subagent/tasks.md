## 1. 修改 settings.json

- [x] 1.1 在 PreToolUse 陣列中新增 hook，matcher 為 `Glob|Grep`，封鎖呼叫並注入訊息：「請改用子代理（Agent, model: haiku）執行檔案搜尋，不得在主對話直接呼叫 Glob 或 Grep」
