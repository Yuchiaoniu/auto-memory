## ADDED Requirements

### Requirement: grade4-english-tutor memory.md 包含跨單元複習 PPTX 記錄
合併後，memory.md 的 PPTX 產生器表格必須包含 make_multi_topic_pptx.py → Multi_Topic_Review.pptx 一列。

#### Scenario: memory.md 記錄跨單元 PPTX
WHEN 查看 grade4-english-tutor/memory.md
THEN 能看到 Multi_Topic_Review.pptx 的產生器名稱與投影片數（16 頁）

### Requirement: grade4-english-tutor tasks.md 包含跨單元複習 PPTX 完成記錄
tasks.md 必須有已勾選的 Multi-Topic Review PPTX 完成項目。

#### Scenario: tasks.md 顯示 PPTX 已完成
WHEN 查看 grade4-english-tutor/tasks.md
THEN 能看到 Multi-Topic Review PPTX（16 頁）的已完成勾選任務
