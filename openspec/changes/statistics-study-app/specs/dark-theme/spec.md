# dark-theme Specification

## Purpose
TBD - created by archiving change expand-foundations. Update Purpose after archive.
## Requirements
### Requirement: 暖色暗模式色彩變數

系統 SHALL 在 `css/main.css` 的 `:root` 定義一套暖色暗模式色彩變數，包含背景、表面、文字、互動色、狀態色、圖表色。

#### Scenario: 載入頁面為暗色

- **WHEN** 使用者開啟任一頁面
- **THEN** 整體背景為深炭咖啡色 `#1c1917`、表面為 `#292524`、主強調為暖橘 `#fb923c`

#### Scenario: 系統識別為深色配色

- **WHEN** 系統檢查 `<html>` 的 `color-scheme` 屬性
- **THEN** 該值為 `dark`（讓表單元素自動使用深色版本）

### Requirement: 表面層次設計

系統 SHALL 提供三層表面深度（從深到淺）：
- `--bg`（最深）：頁面背景
- `--surface`：卡片、區塊外框
- `--surface-2`：嵌套元素（公式、輸入框、選項等）

#### Scenario: 嵌套層次正確

- **WHEN** 選擇題的選項位於問題卡片內
- **THEN** 選項背景比卡片背景更深（surface-2 vs surface），形成視覺層次

### Requirement: 狀態顏色與背景搭配

系統 SHALL 提供四組狀態色（success / danger / warning / primary）並各搭配「色 + 深色背景」組合，避免高飽和色直接套在深色底上刺眼。

#### Scenario: 答對顯示

- **WHEN** 使用者選擇正確答案
- **THEN** 選項變為 `success-bg` 深綠底 + `success` 暖萊姆綠文字，對比清晰但不刺眼

#### Scenario: 警告框

- **WHEN** 頁面顯示「PDF 不是機率」警告
- **THEN** 警告框使用 `--danger-bg` 深紅底 + 珊瑚紅左邊框

### Requirement: 互動元件深色適配

系統 SHALL 為所有互動元件提供深色版本：
- 選擇題選項（surface-2 底、hover 變橘色背景）
- 滑桿（`accent-color: var(--primary)`）
- 數字輸入框（bg 深底、白色文字）
- Canvas 繪圖（座標軸用 `#78716c`、文字用 `#a8a29e`、PDF 曲線用 `#fb923c`）

#### Scenario: 圖表在深色背景上可讀

- **WHEN** 查看互動圖表
- **THEN** 座標軸刻度、曲線、陰影都在深色背景上有足夠對比度

### Requirement: 公式區塊與符號解釋

系統 SHALL 提供 `.formula` 與 `.symbol-legend` 兩種樣式：
- `.formula`：嵌套深色底，含 MathJax 公式
- `.symbol-legend`：左側金色邊框 + 深琥珀底，含 dl/dt/dd 結構的符號逐項解釋

#### Scenario: 公式底下出現符號解釋

- **WHEN** 觀念頁顯示一條公式
- **THEN** 公式區塊正下方出現符號解釋區塊，左邊框為金色（`--legend-border`）、標題為金黃色（`--legend-title`）

