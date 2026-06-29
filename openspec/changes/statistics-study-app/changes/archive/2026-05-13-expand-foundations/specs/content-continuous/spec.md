## ADDED Requirements

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
