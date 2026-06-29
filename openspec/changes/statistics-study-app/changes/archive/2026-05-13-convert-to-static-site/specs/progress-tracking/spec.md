## REMOVED Requirements

### Requirement: 答題記錄持久化

**Reason**：使用者明確表示「練習題的價值來自即時對錯回饋與解析，不需要長期紀錄」。靜態化後無後端可寫，且 localStorage 亦非必要。

**Migration**：未來若有需要，可改用 localStorage 在前端保存，但不在本變更範圍內。

### Requirement: 薄弱觀念識別

**Reason**：依賴答題紀錄，且使用者不再追蹤紀錄。

**Migration**：刪除 `/my/weak-points.html` 頁面與導覽列連結。

### Requirement: 章節完成度顯示

**Reason**：依賴答題紀錄。

**Migration**：刪除首頁章節卡片下方的進度提示與 `progress.js`。

### Requirement: 答題記錄資料表結構

**Reason**：不再有 SQLite 資料庫。

**Migration**：刪除 attempts 資料表的所有相關程式碼（已在 web-server capability 一併處理）。
