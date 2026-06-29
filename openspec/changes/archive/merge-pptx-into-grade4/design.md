## Context

multi-topic-review-pptx 產生了 `make_multi_topic_pptx.py` 與 `Multi_Topic_Review.pptx`（16 頁），涵蓋 Unit 7–9 的天氣、時間、情緒單字，以及教室物品與介系詞 at/on/in。grade4-english-tutor 的 memory.md 已有完整的 PPTX 產生器記錄表，直接補充一行即可。

## Goals / Non-Goals

**Goals:**
- memory.md PPTX 產生器表格加入 Multi-Topic Review 一列
- tasks.md 加入已完成的跨單元複習任務記錄

**Non-Goals:**
- 不修改程式碼
- 不合併 pptx-builder 的任務（該專案為通用工具，直接封存）

## Decisions

**pptx-builder 直接封存，不合併任務**：pptx-builder 是通用 PPTX 工具專案，與 grade4-english-tutor 無直接內容關聯，不需要保留其任務記錄。

## Risks / Trade-offs

無顯著風險，皆為 Markdown 文字異動。
