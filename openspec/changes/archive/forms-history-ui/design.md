## Context

純靜態 GitHub Pages 前端，無後端狀態，localStorage 是唯一可用的持久化方式。

## Goals / Non-Goals

**Goals:**
- 歷史清單跨重新整理持久
- 每筆記錄以上傳的 .docx 檔名命名
- 清單即時更新（建立成功後立刻出現）

**Non-Goals:**
- 不跨裝置同步
- 不編輯或刪除單筆記錄（只提供全部清除）

## Decisions

**D1：localStorage key 為 `form_history`，值為 JSON 陣列**
- 每筆：`{ fileName, title, editUrl, respondUrl, createdAt }`
- 新記錄插入陣列最前面（最新在上）

**D2：表單標題取自 `file.name`（去 `.docx` 副檔名）**
- `file.name.replace(/\.docx$/i, "")`
- 同時作為歷史清單的顯示名稱

**D3：歷史清單放在上傳區塊下方、分析結果上方**
- 頁面載入時立即渲染，無需分析動作觸發

## Risks / Trade-offs

- localStorage 上限約 5 MB，表單記錄只存 URL 字串，百筆內不會超過

## Open Questions

（無）
