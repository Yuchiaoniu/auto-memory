# grade4-english-tutor 長期查詢/對照資料

## 路徑對照

| 用途 | 路徑 |
|---|---|
| OpenSpec 規格目錄（tasks.md / memory.md / STATE.md / CLAUDE.md 在此） | `C:\Users\yuchi\openspec\changes\grade4-english-tutor\` |
| 程式碼與 PPTX 所在 repo | `C:\Users\yuchi\grade4-english-tutor\` |
| 線上靜態網頁 | https://Yuchiaoniu.github.io/english/ |
| GitHub repo | https://github.com/Yuchiaoniu/english.git（branch: `master`） |

## 既有單元清單（8 課）

| 課次 | 標題 | 主色 |
|---|---|---|
| Unit 1 | Hello, Friends! | — |
| Unit 2 | My Family | — |
| Unit 3 | At School | — |
| Unit 4 | I'm Hungry! | — |
| Unit 5 | Animals I Like | — |
| Unit 6 | Dress Up! | — |
| Unit 7 | What Time Is It? | teal `#16A085`（非粉紅系，沿用） |
| Unit 8 | What's the Weather? | — |

額外加課：

| 課次 | 標題 | 主色 | 備註 |
|---|---|---|---|
| Unit 9 | How Do You Feel? | 黃色系（amber 500 `#FFC107`） | 加課單元，9 個情緒單字 |

## 配色規範（與 CLAUDE.md 同步，避免遺忘）

- 禁止粉紅／玫瑰紅／magenta；新單元主色一律黃色系。
- 黃底文字一律用 navy `#2C3E50`，不可用白色（對比不足）。
- 白卡邊框與點綴用深琥珀 `THEME_D` `#B07309`，不可用鮮黃。

```python
THEME    = RGBColor(0xFF, 0xC1, 0x07)  # 主黃 amber 500
THEME_D  = RGBColor(0xB0, 0x73, 0x09)  # 深琥珀
LIGHT    = RGBColor(0xFF, 0xFA, 0xE5)  # 米色背景
CARD_BD  = RGBColor(0xF1, 0xDA, 0x9B)  # 暖棕邊
DARK     = RGBColor(0x2C, 0x3E, 0x50)  # navy slate
```

## PPTX 產生器與成品

| 產生器 | 成品 | 投影片數 |
|---|---|---|
| `make_pptx.py` | `Grade4_English_Vocab.pptx` | 145 |
| `make_unit7_pptx.py` | `Unit7_What_Time_Is_It.pptx` | 17 |
| `make_unit9_pptx.py` | `Unit9_How_Do_You_Feel.pptx` | 15 |
| `make_multi_topic_pptx.py` | `Multi_Topic_Review.pptx` | 16 |

（皆位於 `C:\Users\yuchi\grade4-english-tutor\`，全部已推送至 master）

## PowerPoint emoji 渲染地雷

- **Segoe UI Emoji 對 keycap 1️⃣–🔟 放大會空白**：Unit 7 數字卡改用鐘面 🕐–🕙 才正常。
- 心臟 emoji：💖 屬粉紅系，黃色主題改用 💛。

## Multi_Topic_Review 內容摘要（16 頁，2026-06-11 完成並推送）

- 涵蓋 5 大主題：天氣（sunny/cloudy/rainy/windy/snowy/cold）、時間（morning/afternoon/evening/night/o'clock/half past）、情緒（happy/sad/angry/scared/excited/tired/proud/surprised）、教室用品（chair/board/window/door/book/pen/ruler/bag）、介系詞 in/on/at 點線面。
- 頁面結構：封面 + 單字頁×4（2 欄字卡網格）+ 句型頁×4 + 介系詞概念三欄導覽 + AT/ON/IN 各一頁大例句卡 + 填空練習 + 複習測驗 + 結尾。
- 字體：標題 32pt、單字 22–30pt（依版面）、中文 16–22pt；符合投影需求。
- 配色：全黃色主題，topbar amber，字卡白底暖棕邊，無粉紅。

## Unit 9 內容摘要

- 9 個情緒單字：happy 😄、sad 😢、angry 😠、scared 😨、shocked 😲、sick 🤒、proud 🏆、confident 💪、cool 😎。
- 三種頁面類型：連連看（Matching Game）×2、句型填空（Pattern & Fill-in）×2、會話（Dialogue）×1。
- 主題 emoji：💛（不是 💖）。

## Unit 7 內容摘要

- 16 單字：one~ten + clock、time、morning、afternoon、night、o'clock。
- `o'clock` 注音是 `ㄉㄧㄢˇ ㄓㄨㄥ`（非 `˙ㄉㄧㄢ`）。
- 17 頁結構：封面 + 單字總覽 + 數字/時間字卡 + 句型×2 + 對話 + 測驗×2 + 解答 + 大學伴提示 + 結尾。
- 公開網址加在封面 y=6.35、結尾 y=5.85。

## Git 工作流提醒

- 預設分支：`master`（不是 main）。
- 「Commit or push only when the user asks.」未經請求不主動推送。
- 在 default branch 上工作時，依 CLAUDE.md 規則應先開分支；目前 master 直推為使用者已建立模式，沿用。

## 重要決策

- **Unit 9 為加課**：原始翰林版到 Unit 8。使用者要求把情緒單字編為「第 9 課」（不是第 10 課）。
- **避免粉紅**：使用者偏好黃色，所有新單元配色不可用粉紅系。Unit 9 原本用 rose pink，已重做為黃色。
- **前測 vs 課堂觀察**（教育學討論結論）：前測提供客觀基準、書面記錄與群體輪廓，課堂觀察無法取代。