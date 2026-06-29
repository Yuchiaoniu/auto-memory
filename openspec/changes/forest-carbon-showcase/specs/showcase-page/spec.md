## ADDED Requirements

### Requirement: Header with navigation
頁面 SHALL 在頂部呈現深綠漸層 header，包含標題、副標題，以及連結至 §1～§9 各章節的快速跳轉導覽列（sticky 固定在頂部）。

#### Scenario: 導覽連結跳轉
- **WHEN** 使用者點擊 header 導覽列中任一章節連結
- **THEN** 頁面平滑捲動至對應章節的錨點位置

### Requirement: KPI stats row
頁面 SHALL 在 header 正下方呈現 4 個 KPI 數字卡，數值固定為：樣本數 30、Pipeline 5 條、PASS rate 73.3%、API 成本 ~$1.5 USD。

#### Scenario: KPI 卡片顯示
- **WHEN** 頁面載入完成
- **THEN** 4 個 KPI 卡片以 2×2 grid（行動版）或 4 欄水平排列（桌面版）顯示，每卡片含圖示、數字、標籤

### Requirement: RQ/RO section cards
頁面 SHALL 將研究問題（RQ1、RQ2）與研究目標（RO1、RO2）各自呈現為帶有左側邊條的白色卡片，RQ 卡片邊條為藍色（#3b82f6），RO 卡片邊條為橘色（#f97316）。

#### Scenario: RQ/RO 卡片呈現
- **WHEN** 頁面載入完成
- **THEN** RQ1、RQ2、RO1、RO2 各為獨立卡片，左側邊條顏色分別對應規定色；RQ3 與 RO3 維持隱藏

### Requirement: Content sections §1–§9
頁面 SHALL 呈現 §1 背景至 §9 共 9 個章節，每個章節包裹在白色卡片內，左側邊條為綠色（var(--green-600)），章節標題對應原始 `<h2>` 標題。

#### Scenario: 章節完整性
- **WHEN** 頁面載入完成
- **THEN** 9 個章節的所有文字、表格、清單均完整呈現，無內容遺漏

### Requirement: Experiment results table (§4)
§4 章節 SHALL 呈現 30 棵樹的實驗結果表格，表頭底色為淺綠（var(--green-100)），各列依誤差大小套用綠/黃/紅/灰底色，PASS 欄位顯示 ✓ 或 ✗。

#### Scenario: 表格顏色標記
- **WHEN** 頁面載入完成
- **THEN** 誤差 ≤15% 的儲存格底色為綠色，15–30% 為黃色，>30% 為紅色，N/A 或 null 為灰色

### Requirement: Timeline for §3
§3 演進旅程 SHALL 改用 timeline 組件排版：每個演進階段為一張白色卡片，左側顯示綠色圓點與垂直連接線，卡片內容包含階段標題與說明文字。

#### Scenario: Timeline 視覺呈現
- **WHEN** 頁面載入完成
- **THEN** §3 以垂直 timeline 形式呈現 5 個演進階段，每階段有獨立卡片，不使用暗底樣式

### Requirement: Back-to-RQ links
每個章節末尾 SHALL 保留「返回研究問題」的錨點連結，連結目標為 #rq1 與 #rq2。

#### Scenario: 返回連結功能
- **WHEN** 使用者點擊章節末尾的「返回研究問題：RQ1」連結
- **THEN** 頁面捲動至 RQ1 卡片位置
