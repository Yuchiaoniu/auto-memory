## ADDED Requirements

### Requirement: 課程目錄頁面

系統 SHALL 提供 `/chapters/syllabus.html` 頁面，列出 Mendenhall《Introduction to Probability and Statistics, 15th Edition》全部 15 章的章節結構，分四階段呈現。

#### Scenario: 訪客進入課程目錄頁

- **WHEN** 使用者點選導覽列「課程目錄」
- **THEN** 系統顯示教科書資訊（書名 + 作者）、收錄狀態圖例、四階段段落，每階段下含對應章節卡片

#### Scenario: 章節卡片顯示子章節

- **WHEN** 使用者捲動到 Ch 6 卡片
- **THEN** 系統顯示「6.1 Probability Distributions for Continuous Random Variables、6.2 The Normal Probability Distribution、6.3 The Normal Approximation to the Binomial Probability Distribution」三個子章節

### Requirement: 收錄狀態指示

系統 SHALL 為每章節以三種狀態之一標記：`available`（已收錄）、`partial`（部分收錄）、`pending`（待補），用右上角 pill 與左側彩色細邊呈現。

#### Scenario: 已收錄章節有連結

- **WHEN** 章節狀態為 `available` 或 `partial`
- **THEN** 卡片底部 note 區出現「已收錄於 [章節名]」並附超連結指向對應頁面

#### Scenario: 待補章節視覺淡化

- **WHEN** 章節狀態為 `pending`
- **THEN** 卡片整體透明度略降、左邊細邊改為灰色，視覺上次於已收錄章節

### Requirement: 四階段邏輯分組

系統 SHALL 將 15 章依教科書邏輯分為四階段並各自有 stage-header：
- 第一階段：敘述統計學（Ch 1-3）
- 第二階段：機率論與機率分布（Ch 4-6）
- 第三階段：推論統計基礎（Ch 7-10）
- 第四階段：進階分析與預測模型（Ch 11-15）

#### Scenario: 階段標題呈現

- **WHEN** 使用者捲動目錄頁
- **THEN** 每階段有一個橘色 accent 的標題塊，顯示中文名 + 英文副標 + 一句說明

### Requirement: 從首頁與導覽列可達

系統 SHALL 在首頁加入一張寬卡片連結到課程目錄頁，並在所有章節頁的導覽列加入「課程目錄」連結（位於最左側）。

#### Scenario: 首頁入口

- **WHEN** 使用者訪問 `/`
- **THEN** 在「已收錄章節」段落下方看到「完整課程地圖」段落與寬卡片連結
