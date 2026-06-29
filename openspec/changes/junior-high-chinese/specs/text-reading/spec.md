## ADDED Requirements

### Requirement: 課文列表瀏覽
系統 SHALL 顯示依年級（七、八、九年級）分類的課文列表，每篇課文顯示篇名、作者、出處。

#### Scenario: 依年級篩選課文
- **WHEN** 使用者點選年級分頁（七年級/八年級/九年級）
- **THEN** 課文列表 SHALL 只顯示該年級的課文

#### Scenario: 點選課文進入閱讀
- **WHEN** 使用者點選某篇課文標題
- **THEN** 系統 SHALL 導向該課文的閱讀頁面

### Requirement: 課文閱讀與段落導讀
課文閱讀頁 SHALL 顯示課文全文，並提供段落摺疊/展開功能與段落導讀說明。

#### Scenario: 顯示課文全文
- **WHEN** 使用者開啟課文閱讀頁
- **THEN** 系統 SHALL 顯示課文完整內容，段落間有明顯分隔

#### Scenario: 展開段落導讀
- **WHEN** 使用者點擊段落旁的「導讀」按鈕
- **THEN** 系統 SHALL 展開該段落的摘要說明與學習重點

### Requirement: 生字詞注音與解釋
課文中的生字詞 SHALL 以底線標示，點擊後顯示注音與字義解釋。

#### Scenario: 查看生字詞解釋
- **WHEN** 使用者點擊課文中有底線的生字詞
- **THEN** 系統 SHALL 以彈出視窗顯示該詞的注音符號與解釋

#### Scenario: 關閉解釋視窗
- **WHEN** 使用者點擊視窗外區域或關閉按鈕
- **THEN** 系統 SHALL 關閉解釋彈出視窗
