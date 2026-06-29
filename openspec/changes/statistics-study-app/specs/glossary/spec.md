# glossary Specification

## Purpose
TBD - created by archiving change expand-foundations. Update Purpose after archive.
## Requirements
### Requirement: 速查頁面

系統 SHALL 提供 `/chapters/glossary.html` 頁面，作為所有講義出現過的統計學專詞與公式的單頁速查工具，使用 HTML5 原生 `<details>/<summary>` 元素做摺疊區塊。

#### Scenario: 進入速查頁

- **WHEN** 使用者點選導覽列「速查」
- **THEN** 系統顯示頁面分上下兩段：「統計學專詞」與「公式速查」，各自含多個摺疊類別

#### Scenario: 摺疊區塊互動

- **WHEN** 使用者點選類別標題（如「離散 vs 連續」）
- **THEN** 該類別內容展開/收合，標題前的箭頭 ▸ 旋轉 90°

#### Scenario: 頁內錨點跳轉

- **WHEN** 使用者點選頁面頂端「📖 統計學專詞」按鈕
- **THEN** 視窗捲動到 `#terms` 段落；點「📐 公式速查」則跳到 `#formulas`

### Requirement: 專詞區段內容

系統 SHALL 將專詞分為 8 個類別摺疊區塊：（1）基礎概念、（2）離散 vs 連續、（3）分配的特徵數、（4）機率公理與運算規則、（5）離散型分配、（6）連續型分配、（7）連續型核心性質、（8）抽樣與推論。

#### Scenario: 不重複、含英文對照

- **WHEN** 使用者瀏覽任一專詞
- **THEN** 每個專詞含中文名 + 英文名（斜體灰色 `.en`）+ 口語化說明

#### Scenario: 涵蓋所有講義專詞

- **WHEN** 學習者查找「無記憶性」「卡方分配」「貝氏定理」「波松近似二項」等任一講義出現過的詞
- **THEN** 在速查頁能找到該詞的解釋

### Requirement: 公式區段內容

系統 SHALL 將公式分為 7 個類別摺疊區塊：（1）通用公式、（2）二項、（3）波松、（4）均勻、（5）常態、（6）指數、（7）抽樣分配/CLT。每個公式以 `.formula-card` 呈現，含公式 + 符號解釋。

#### Scenario: 公式卡片結構

- **WHEN** 使用者展開「常態分配」公式類別
- **THEN** 看到三張卡片（PDF、標準化、68-95-99.7），每張含標題、公式、符號逐項解釋

#### Scenario: 每個符號都被解釋

- **WHEN** 使用者看到 $f(x) = \frac{1}{\sigma\sqrt{2\pi}}\,e^{-(x-\mu)^2/(2\sigma^2)}$
- **THEN** 下方符號解釋區列出 $\mu$, $\sigma$, $\pi$, $e$, $(x-\mu)^2$, $\frac{1}{\sigma\sqrt{2\pi}}$ 等所有出現符號的意義

### Requirement: 導覽列入口

系統 SHALL 在所有頁面的導覽列加入「速查」連結，位於「課程目錄」之後、章節連結之前。

#### Scenario: 從任一頁面進入速查

- **WHEN** 使用者在隨機變數頁或連續型分配頁
- **THEN** 點上方導覽列「速查」即可跳到 glossary 頁

### Requirement: 查表工具 section

系統 SHALL 在 `chapters/glossary.html` 加入新 section（id="lookup"），位於「公式速查」之後，包含 Z 表互動工具與 t 表互動工具兩個元件。

#### Scenario: 從速查頁進入查表工具

- **WHEN** 使用者開啟 glossary 頁
- **THEN** 頁面頂端錨點導覽列加入「📊 查表工具」項，點擊後跳到 #lookup section

### Requirement: t 分配核心專詞補強

系統 SHALL 在 glossary 專詞第 8 段「抽樣與推論」中加入「自由度」「t 分配」「臨界值」「α 與 1-α 信賴水準」四個專詞的詳細解釋。

#### Scenario: 自由度解釋

- **WHEN** 使用者搜尋「自由度」
- **THEN** 在速查頁找到該詞，含中英對照、直觀解釋（樣本中獨立資訊個數）、典型公式（單樣本 ν = n - 1）

### Requirement: t 分配公式卡

系統 SHALL 在 glossary 公式段加入「t 分配對應」公式卡，包含 t 統計量公式、與 Z 對比的關係，並含符號解釋。

#### Scenario: 公式卡內容

- **WHEN** 使用者展開「t 分配對應」公式類別
- **THEN** 看到 $t = \dfrac{\bar X - \mu}{S/\sqrt{n}}$ 公式 + 與 $Z$ 的對比（用 S 取代 σ、自由度 n-1）+ 符號逐項解釋

