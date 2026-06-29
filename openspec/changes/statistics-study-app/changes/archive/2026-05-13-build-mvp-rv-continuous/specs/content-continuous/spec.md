## ADDED Requirements

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
