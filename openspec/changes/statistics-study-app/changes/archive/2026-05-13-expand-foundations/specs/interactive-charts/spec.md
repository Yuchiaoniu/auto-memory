## ADDED Requirements

### Requirement: 機率藏在面積裡互動視覺化

系統 SHALL 在 `js/area-viz.js` 提供獨立的 Canvas 元件：渲染標準常態 PDF 曲線、根據 a 與 b 輸入即時繪製陰影、即時顯示對應的 P(a ≤ X ≤ b) 數值。

#### Scenario: 拖 a 或 b 值

- **WHEN** 使用者在輸入框輸入 a = −1、b = 1
- **THEN** Canvas 陰影更新為 [−1, 1] 區間，旁邊顯示「P(a ≤ X ≤ b) = 0.6827」

#### Scenario: 與其他 chart-panel 元件相容

- **WHEN** 使用者同時在隨機變數頁與連續型分配頁開啟（不同分頁）
- **THEN** area-viz 與 chart-panel 各自獨立渲染，互不干擾

### Requirement: 自適應寬度

系統 SHALL 讓 area-viz Canvas 自動填滿其容器寬度，且在視窗縮放時重新繪製。

#### Scenario: 視窗縮放

- **WHEN** 使用者縮小瀏覽器寬度
- **THEN** Canvas 寬度同步縮小，PDF 曲線與標籤位置正確
