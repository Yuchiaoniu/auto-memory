# content-continuous Specification

## Purpose
TBD - created by archiving change build-mvp-rv-continuous. Update Purpose after archive.
## Requirements
### Requirement: 連續型分配章節首頁

系統 SHALL 提供 `/chapters/continuous-distributions` 路由，列出本章涵蓋的三個分配（均勻、常態、指數）的卡片入口。

#### Scenario: 進入連續型分配章節

- **WHEN** 使用者點選「連續型機率分配」
- **THEN** 系統顯示均勻分配 U(a,b)、常態分配 N(μ,σ²)、指數分配 Exp(λ) 三張卡片，每張卡片附 PDF 縮圖預覽

### Requirement: 均勻分配 U(a, b) 觀念頁

系統 SHALL 呈現均勻分配的 PDF f(x)=1/(b-a)、CDF、E(X)=(a+b)/2、Var(X)=(b-a)²/12，並提供互動圖表（在 `interactive-charts` capability 中實作）。

#### Scenario: 閱讀均勻分配公式

- **WHEN** 使用者進入均勻分配頁
- **THEN** 系統用 MathJax 渲染顯示 PDF、CDF、E、Var 公式，並提供「等公車範例」說明使用情境

### Requirement: 常態分配 N(μ, σ²) 觀念頁

系統 SHALL 呈現常態分配的 PDF 公式、標準化 Z=(X-μ)/σ、68-95-99.7 經驗法則，並提供標準常態表查詢工具。

#### Scenario: 查標準常態表

- **WHEN** 使用者輸入 z = 1.5
- **THEN** 系統顯示 P(Z ≤ 1.5) ≈ 0.9332，並在圖上以陰影標示對應區域

#### Scenario: 反查 Z 值

- **WHEN** 使用者切換到反查模式並輸入機率 0.95
- **THEN** 系統回傳 z ≈ 1.645（單尾），並提示「常見臨界值」列表

### Requirement: 指數分配 Exp(λ) 觀念頁

系統 SHALL 呈現指數分配的 PDF f(x)=λe^(-λx)、CDF、E(X)=1/λ、Var(X)=1/λ²，並專門闢一節說明「無記憶性」P(X>s+t|X>s)=P(X>t)。

#### Scenario: 驗證無記憶性

- **WHEN** 使用者輸入 s=300, t=500, λ=1/1000
- **THEN** 系統並列顯示 P(X>800|X>300) 與 P(X>500) 兩個計算結果，並標示兩者相等

### Requirement: 連續型「基礎觀念」整段

系統 SHALL 在 `chapters/continuous-distributions.html` 的「均勻分配」段落之前加入「基礎觀念」section，含 5 個子觀念區塊：① PDF 三大性質、② CDF 與 F(b)−F(a) 神級公式、③ 三種陰影區域、④ 期望值與變異數（積分版）、⑤ 四大支柱速查。

#### Scenario: 進入連續型分配頁的順序

- **WHEN** 使用者開啟連續型分配頁
- **THEN** 先看到「基礎觀念」section 標題與 5 個觀念區塊，再看到「具體分配」section 與三個分配

### Requirement: PDF 三大性質正式列舉

系統 SHALL 在觀念 ① 中以編號列表呈現三條性質，每條包含粗體標題、公式、說明，並收尾於符號解釋。

#### Scenario: 三條性質完整呈現

- **WHEN** 使用者捲動到觀念 ①
- **THEN** 看到「非負性 / 規範性 / 區間機率」三條，每條附獨立公式與解說

### Requirement: F(b) − F(a) 神級公式強調

系統 SHALL 在觀念 ② 中以金色強調框（`.punchline-box`）呈現 $P(a \le X \le b) = F(b) - F(a)$ 公式，並明示「不用真的積分」與「≤ 與 < 等價」兩個威力。

#### Scenario: 強調框內容

- **WHEN** 使用者看到觀念 ②
- **THEN** 強調框內含公式 + 兩條 bullet 說明（避免積分 / ≤ < 等價）

### Requirement: 三種陰影對照表

系統 SHALL 在觀念 ③ 中以表格呈現中段、左尾、右尾三種機率的「陰影位置」與「CDF 公式」對照。

#### Scenario: 表格清楚對照

- **WHEN** 使用者進入觀念 ③
- **THEN** 看到三列表格：中段（$F(b)-F(a)$）、左尾（$F(b)$）、右尾（$1-F(b)$）

### Requirement: 期望值與變異數積分版本

系統 SHALL 在觀念 ④ 中呈現連續型 $E(X)$、$\mathrm{Var}(X)$ 的積分公式，並用金色強調框列出實戰計算神器 $\mathrm{Var}(X) = E(X^2) - [E(X)]^2$。

#### Scenario: 強調 Σ → ∫ 對應

- **WHEN** 使用者看到觀念 ④ 開頭
- **THEN** 看到一句「punchline-mini」說明「把 Σ 換成 ∫、把 P(X=x) 換成 f(x)dx，就是連續型版本」

### Requirement: 四大支柱速查卡片

系統 SHALL 在觀念 ⑤ 中以四張卡片並排呈現四大支柱（總面積=1、單點機率=0、積分萬用、CDF累積積分），每張卡片有編號圖示、粗體標題、簡短說明。

#### Scenario: 四張卡片版面

- **WHEN** 使用者捲動到觀念 ⑤
- **THEN** 在足夠寬的螢幕上看到 4 張卡片並排（窄螢幕自動換行為 2x2 或單欄）

