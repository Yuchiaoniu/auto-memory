## ADDED Requirements

### Requirement: 產生器腳本存在且可執行
系統 SHALL 在 `C:\Users\yuchi\grade4-english-tutor\make_multi_topic_pptx.py` 提供可直接執行的 Python 產生器。

#### Scenario: 執行產生器
- **WHEN** 在 `C:\Users\yuchi\grade4-english-tutor\` 執行 `python make_multi_topic_pptx.py`
- **THEN** 同目錄產生 `Multi_Topic_Review.pptx`，且不拋出任何錯誤

### Requirement: 簡報共 16 頁
產生的 PPTX SHALL 恰好包含 16 張投影片，依序涵蓋所有指定主題。

#### Scenario: 頁數驗證
- **WHEN** 開啟 `Multi_Topic_Review.pptx`
- **THEN** 投影片數量為 16，第 1 頁為封面，第 16 頁為結尾

### Requirement: 配色符合黃色主題規範
所有投影片 SHALL 使用黃色主題（THEME amber #FFC107），黃底文字 SHALL 使用深 navy #2C3E50，禁止使用粉紅色系。

#### Scenario: 封面配色
- **WHEN** 開啟第 1 頁封面
- **THEN** 背景為 amber 黃色，標題文字為深 navy，無粉紅色元素

### Requirement: 字體大小符合投影規格
標題文字 SHALL 不小於 40pt，內文與單字 SHALL 不小於 28pt，中文對照 SHALL 不小於 20pt。

#### Scenario: 字卡文字大小
- **WHEN** 開啟任一單字字卡頁
- **THEN** 英文單字字體 ≥ 28pt，中文對照字體 ≥ 20pt

### Requirement: 涵蓋五大主題
簡報 SHALL 涵蓋天氣用語（≥6 個單字）、時間用語（≥6 個單字）、情緒感覺（≥6 個單字）、教室桌椅器具（≥6 個單字）、介系詞 in/on/at 點線面概念（含例句）。

#### Scenario: 天氣主題完整性
- **WHEN** 開啟第 2 頁天氣單字頁
- **THEN** 至少顯示 sunny、cloudy、rainy、windy、snowy、cold 六個單字及其中文對照

#### Scenario: 介系詞主題完整性
- **WHEN** 開啟第 10–13 頁
- **THEN** 第 10 頁顯示 in/on/at 三者的點線面概念說明，第 11–13 頁各自列出 at/on/in 的例句

### Requirement: 包含練習與測驗頁
簡報 SHALL 包含至少一頁填空練習（針對 in/on/at）與一頁複習測驗（涵蓋多主題）。

#### Scenario: 練習頁存在
- **WHEN** 開啟第 14 頁
- **THEN** 顯示 4 題 in/on/at 填空練習題
