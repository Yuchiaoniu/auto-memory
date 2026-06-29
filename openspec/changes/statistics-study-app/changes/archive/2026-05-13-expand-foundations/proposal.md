## Why

`convert-to-static-site` 結束後，網站隨對話持續增補了大量內容與互動元件，但這些增補**沒有被任何 openspec change 涵蓋**。具體未追蹤的工作包括：

1. 新增「課程目錄」頁面（對應 Mendenhall 第 15 版完整章節）
2. 切換到「暖色暗模式」整套色系
3. 為公式加入「符號解釋」區塊（dl/dt/dd 結構）
4. 加入「PDF 不是機率」警告框（避開最常見的誤解）
5. 加入「機率藏在面積裡」互動 Canvas 視覺化（拖 a、b 看陰影面積變化）
6. 在連續型分配頁前面整段補上「基礎觀念」（PDF 三性質、CDF 與 F(b)−F(a) 神級公式、三種陰影、E/Var 積分版、四大支柱速查）
7. 題庫擴充：30 → 56 題（加易題、加連續型基礎題）

沒有 spec 紀錄意味著：
- 未來閱讀 openspec/ 的人（包括未來的自己）看不出網站長什麼樣
- 後續若要新增章節或調整，無從追蹤「現況到哪、下一步要什麼」
- 與既有兩個 change 並存會混亂

本 change 的目的是**回溯地把這段時間的增補打包成一個正式變更**，同時定義後續可追蹤的擴充工作，讓 openspec 目錄與實際內容對齊。

## What Changes

### 內容擴充（已做）
- **加入 `course-syllabus` capability**：純靜態的課程目錄頁，列出 Mendenhall 全 15 章與子章節、含「已收錄 / 部分收錄 / 待補」狀態
- **加入 `dark-theme` capability**：暖色暗模式整套設計系統（CSS 變數、表面層次、強調色、警告色、互動元件樣式）
- **修改 `content-rv` capability**：新增「觀念 4：機率藏在面積裡」（含 Canvas 互動視覺化）、加 PDF/PMF 誤解警告框、每條公式底下加符號解釋
- **修改 `content-continuous` capability**：在具體分配前新增「基礎觀念」整段（① PDF 三性質 ② CDF + F(b)−F(a) ③ 三種陰影 ④ E/Var 積分版 ⑤ 四大支柱）
- **修改 `quiz-engine` capability**：每觀念新增 2-4 道基礎題，新增 `continuous-foundation` 觀念 8 題；題庫 30 → 56
- **修改 `interactive-charts` capability**：新增 `area-viz.js`（標準常態 PDF + a, b 滑桿 + 陰影 + 即時機率）

### 持續擴充（未做、列在 tasks.md 中追蹤）
- 補 Ch 5 離散型專屬內容（二項、波松、超幾何）
- 補 Ch 7 抽樣分配與 CLT
- 補 Ch 4 機率論基礎獨立頁
- 互動圖表加入「離散→連續過渡」動畫
- 圖片資源（images/）整合：把 5 張教科書截圖正式納入頁面

## Capabilities

### New Capabilities

- `course-syllabus`：完整課程目錄頁面，含 Mendenhall 第 15 版四階段 15 章節、子章節列表、收錄狀態
- `dark-theme`：暖色暗模式設計系統（CSS 變數、各元件深色版本、狀態 pill、警告框、強調框等）
- `glossary`：專詞 + 公式單頁速查表，使用 HTML5 details/summary 做摺疊；不重複地涵蓋所有講義出現過的專詞與公式（每個符號都有逐項解釋）

### Modified Capabilities

- `content-rv`：加入「機率藏在面積裡」觀念、誤解警告框、各公式符號解釋
- `content-continuous`：加入「基礎觀念」整段共 5 個子觀念，原有「具體分配」段落不變
- `quiz-engine`：擴充易度較低題目；新增 `continuous-foundation` 題組
- `interactive-charts`：新增 `area-viz` 元件（PDF 陰影互動）

## Impact

- **檔案系統**：新增 `chapters/syllabus.html`、`js/area-viz.js`；大幅修改 `chapters/random-variables.html`、`chapters/continuous-distributions.html`、`css/main.css`、`data/questions.json`
- **無依賴變動**：仍是純靜態，無 npm package
- **與既有 change 的關係**：
  - `build-mvp-rv-continuous` 可在本 change 完成後一併 archive（內容已被取代）
  - `convert-to-static-site` 亦可一併 archive（架構轉換已完成）
- **未來方向**：本 change 留下完整的「持續擴充清單」於 tasks.md，後續每補一章就是更新 capability 而非新建專案
