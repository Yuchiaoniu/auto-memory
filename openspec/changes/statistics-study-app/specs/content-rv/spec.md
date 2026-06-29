# content-rv Specification

## Purpose
TBD - created by archiving change build-mvp-rv-continuous. Update Purpose after archive.
## Requirements
### Requirement: 隨機變數章節首頁

系統 SHALL 提供 `/chapters/random-variables` 路由，呈現本章節的學習目錄，列出所有觀念卡片並標示完成狀態。

#### Scenario: 訪客進入隨機變數章節

- **WHEN** 使用者點選導覽列「隨機變數」
- **THEN** 系統顯示包含「機率分配本質」「Σ 與 ∫ 統一性」「PMF/PDF/CDF 對比」「離散→連續過渡」等觀念卡片，每張卡片可進入觀念頁

### Requirement: 機率分配本質觀念頁

系統 SHALL 呈現「分配 = 把總機率 1 分配給各結果的規則」的核心觀念，配合「分餅圖」視覺化說明。

#### Scenario: 閱讀機率分配本質

- **WHEN** 使用者點開「機率分配本質」觀念
- **THEN** 系統顯示分餅比喻圖（一個圓被切成 n 等分）、兩條公理（非負、總和為 1）、離散與連續的差異說明

### Requirement: Σ 與 ∫ 統一性觀念頁

系統 SHALL 解釋積分本質為「無限薄條的加總」，並用動畫呈現直方圖過渡到連續密度的過程。

#### Scenario: 動畫呈現極限過程

- **WHEN** 使用者點開「Σ 與 ∫ 統一性」觀念
- **THEN** 系統顯示一個按鈕「切得更細」，每按一次直方圖的柱數加倍，最終逼近平滑曲線；旁邊以公式 ∫f(x)dx = lim Σf(xᵢ)Δx 對應每一步

### Requirement: PMF、PDF、CDF 對比頁

系統 SHALL 提供左右並排的離散 vs 連續對比：左側顯示階梯函數（CDF）與棒狀圖（PMF），右側顯示平滑曲線（CDF）與密度曲線（PDF）。

#### Scenario: 觀察跳點與平滑

- **WHEN** 使用者進入對比頁
- **THEN** 系統在離散 CDF 圖上標註「跳點」對應 PMF；在連續 CDF 上標註「無跳點」並指出 PDF = F'(x)；同時提供「P(X = x₀) = ?」的即時計算框，離散端可得正值，連續端永遠顯示 0

### Requirement: 觀念 4「機率藏在面積裡」

系統 SHALL 在 `chapters/random-variables.html` 的 Σ/∫ 觀念後加入「觀念 4：機率藏在面積裡」，包含說明文字、互動 Canvas 視覺化、公式、與兩個關鍵口訣。

#### Scenario: 進入隨機變數頁

- **WHEN** 使用者打開隨機變數章節
- **THEN** 在 Σ/∫ 觀念之後可看到「觀念 4」標題，並見到一張可拖 a、b 的 PDF + 陰影 + 即時機率元件

#### Scenario: 拖 a 或 b 觀察陰影

- **WHEN** 使用者把 a 改為 −2、b 改為 2
- **THEN** PDF 陰影區域更新為 [−2, 2]，旁邊「P(a ≤ X ≤ b) = ...」顯示約 0.9545

### Requirement: PDF / PMF 誤解警告框

系統 SHALL 在「PMF / PDF / CDF」觀念內加入紅色警告框，列出 4 種常見對錯情境，並收尾於一句口訣「密度 × 寬度 = 機率」。

#### Scenario: 警告框視覺辨識

- **WHEN** 使用者捲動到 PMF/PDF/CDF 觀念
- **THEN** 顯示 ⚠ 圖示開頭的紅色強調框，內含 4 列對照表（含 ✓ ✗ 符號）

### Requirement: 各公式底下加符號解釋

系統 SHALL 在隨機變數頁的三條主要公式（機率公理、$P(X=x_0)=F(x_0)-F(x_0^-)$、黎曼和）底下各加一個 `.symbol-legend` 區塊，逐項說明每個符號。

#### Scenario: 符號逐一說明

- **WHEN** 使用者看完黎曼和公式
- **THEN** 緊接著的符號解釋區塊用 dl/dt/dd 結構列出 $\int_a^b$、$f(x_i)$、$\Delta x$、$\sum_{i=1}^n$、$\lim_{n\to\infty}$ 等每個符號的意義

