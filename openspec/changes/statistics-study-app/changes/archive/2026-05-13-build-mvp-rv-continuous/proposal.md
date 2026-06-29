## Why

學習者正在修讀大三下統計學課程，已建立 `learn-statistics-course` 學習專案（位於三下課程資料夾）追蹤整門課的觀念。但靜態的 markdown 筆記無法支援：

1. **互動式視覺化**：常態分配的 μ、σ 怎麼改變曲線形狀？離散直方圖如何過渡到連續密度？這些觀念需要「動手調」才會記住，純文字看十遍也不如拖一次滑桿。
2. **即時練習**：選擇題與計算題若分散在 docx / pdf 裡，做完不能立刻知道對錯，更無法追蹤「我哪一類題目錯最多」。
3. **錯題回顧**：人腦會自動忘記答錯過的題目，需要系統幫忙標記與重複出題。

優先做 MVP（範圍縮小到「隨機變數」與「連續型機率分配」兩個 capability），因為：
- 這兩章是目前正在上的單元，最需要立刻能用
- 範圍小可以快速驗證技術架構是否可行
- 未來其他章節照同樣模板複製即可

## What Changes

- 建立 Node.js + Express + SQLite 後端，提供題庫、進度、答題記錄 API
- 建立純前端頁面（HTML/CSS/JS + Chart.js + MathJax）呈現觀念、公式、互動圖表
- 內容範圍只涵蓋「隨機變數」與「連續型機率分配」兩章
- 每個觀念附帶兩種練習：**選擇題**（即時對錯回饋）+ **互動式參數調整**（拖滑桿看分配變化）
- 後端追蹤每題的「答對 / 答錯 / 最後一次作答時間」，前端顯示薄弱觀念
- 不做使用者註冊系統（單一使用者本機使用，省去登入流程）

## Capabilities

### New Capabilities

- `content-rv`: 隨機變數章節的教材內容呈現（觀念、公式、CDF/PMF/PDF 對比圖、機率分配本質、Σ 與 ∫ 統一性）
- `content-continuous`: 連續型機率分配章節的教材內容（均勻、常態、指數，先不做卡方/t/F）
- `interactive-charts`: 互動式圖表（拖拉 μ、σ、λ 即時更新分配圖；離散到連續的動畫過渡）
- `quiz-engine`: 選擇題作答引擎（題目顯示、選項點擊、即時對錯、公式提示）
- `progress-tracking`: 學習進度與答題記錄追蹤（SQLite 儲存、薄弱觀念辨識）
- `web-server`: Node.js + Express 伺服器架構與 API 路由

### Modified Capabilities

無（新建專案，無既有 capability）。

## Impact

- **新專案目錄**：`C:\Users\yuchi\projects\statistics-study-app\`
- **技術依賴**：Node.js（runtime）、Express、better-sqlite3、Chart.js（CDN）、MathJax（CDN）
- **資料儲存**：`data/app.db`（SQLite，題庫 + 作答記錄）
- **與 learn-statistics-course 的關係**：兩者**不同步、不耦合**。學習專案是個人筆記與檢核表；網站是可重複使用的學習工具。但網站內容會 reference 學習專案的 spec 作為參考。
- **記憶系統**：將新專案位置與技術架構寫入 Claude memory
