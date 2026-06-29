## ADDED Requirements

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
