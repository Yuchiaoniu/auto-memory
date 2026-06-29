## ADDED Requirements

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
