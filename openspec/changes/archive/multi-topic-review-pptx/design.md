## Context

既有 PPTX 產生器（make_pptx.py、make_unit7_pptx.py、make_unit9_pptx.py）已建立黃色主題配色規範與 python-pptx 寫法慣例。本次新增獨立產生器，不修改既有產生器。

## Goals / Non-Goals

**Goals:**
- 16 頁跨主題複習簡報，一個 .py 產生一個 .pptx
- 字體大（標題 ≥ 40pt、內文 ≥ 28pt）、版面清爽、適合投影
- 配色嚴格沿用黃色主題（THEME amber #FFC107、DARK navy #2C3E50）
- 每頁聚焦單一主題，不混排

**Non-Goals:**
- 不修改既有網頁 JS 或其他 PPTX 產生器
- 不新增動畫或音效（python-pptx 不支援）
- 不部署到 GitHub Pages

## Decisions

**16 頁結構設計：**

| 頁次 | 主題 | 頁型 |
|---|---|---|
| 1 | 封面（Multi-Topic Review） | 封面 |
| 2 | 天氣單字 Weather（6 個：sunny/cloudy/rainy/windy/snowy/cold） | 字卡網格 |
| 3 | 天氣句型 "What's the weather like? It's ___." | 句型框 |
| 4 | 時間單字 Time（6 個：morning/afternoon/evening/night/o'clock/half past） | 字卡網格 |
| 5 | 時間句型 "What time is it? It's ___ o'clock." | 句型框 |
| 6 | 情緒單字 Feelings（8 個：happy/sad/angry/scared/excited/tired/proud/surprised） | 字卡網格 |
| 7 | 情緒句型 "How do you feel? I feel ___." | 句型框 |
| 8 | 教室器具 Classroom Items（8 個：desk/chair/board/window/door/book/pen/ruler） | 字卡網格 |
| 9 | 教室句型 "Where is the ___? It is on/in/at the ___." | 句型框 |
| 10 | 介系詞概念導覽（in/on/at 三格說明） | 概念圖 |
| 11 | AT 點（point）例句（at home / at school / at the bus stop） | 例句卡 |
| 12 | ON 線（line）例句（on the road / on the bus / on the shelf） | 例句卡 |
| 13 | IN 面/空間（area）例句（in the classroom / in the box / in Taiwan） | 例句卡 |
| 14 | 綜合填空練習（in/on/at 選填，4 題） | 練習題 |
| 15 | 複習測驗（選擇題 4 題，涵蓋所有主題） | 測驗 |
| 16 | 結尾（Great Job!） | 結尾 |

**字卡網格版型：** 每頁最多 8 格，2 欄排列，每格白卡（CARD_BD 邊框）＋ emoji ＋ 英文（28pt bold）＋ 中文（20pt）。

**句型框版型：** 黃底大框置中，句型結構 48pt bold，空格用底線標示，中文對照 24pt。

**介系詞概念頁：** 三欄分別說明 AT（紅點 🔴 點狀）、ON（黃線 ━ 線狀）、IN（藍框 🔷 面狀），搭配中英對照與例詞。

## Risks / Trade-offs

- Segoe UI Emoji 在 PowerPoint 中某些 emoji 放大後會空白 → 已知地雷，改用 Segoe UI Symbol 或選擇安全 emoji（測試清單見 memory.md）
- 黃底白字對比不足 → 嚴格遵守 DARK navy 文字規範
