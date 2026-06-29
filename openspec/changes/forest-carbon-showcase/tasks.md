## 1. 建立基礎結構與設計系統

- [x] 1.1 建立 `index.html` 骨架（DOCTYPE、head、meta、Google Fonts Inter）
- [x] 1.2 移植 dashboard02 的 CSS 變數系統（`:root` 綠色色板、--bg、--text、--shadow）
- [x] 1.3 撰寫 header 元件 CSS（深綠漸層背景、tree pattern overlay、sticky 導覽列）
- [x] 1.4 撰寫 KPI 數字卡 CSS（4 欄 grid、白底、上方彩色邊條、hover 效果）
- [x] 1.5 撰寫章節卡片 CSS（白底、圓角、陰影、左側 4px 彩色邊條）
- [x] 1.6 撰寫表格 CSS（border-collapse、淺綠 header、綠/黃/紅/灰行底色）
- [x] 1.7 撰寫 timeline 組件 CSS（垂直連接線、圓點標記、卡片堆疊）

## 2. 撰寫 Header 與 KPI 區塊

- [x] 2.1 撰寫 header HTML（標題「從單一流程到五條流程對照：森林碳測量系統演進」、副標題、pine tree SVG overlay）
- [x] 2.2 撰寫 header 導覽列 HTML（RQ/RO、§1～§9 共 10 個錨點連結）
- [x] 2.3 撰寫 4 個 KPI 數字卡 HTML（樣本數 30、Pipeline 5 條、PASS rate 73.3%、API 成本 ~$1.5 USD）

## 3. 移植 RQ/RO 區塊

- [x] 3.1 移植 RQ1 卡片（藍色左邊條，含 Verra VM0047 §8.4 規定表格、#39～#44 任務表格）
- [x] 3.2 移植 RQ2 卡片（藍色左邊條，含商業模式說明段落）
- [x] 3.3 移植 RO1 卡片（橘色左邊條，含三個動作與章節連結）
- [x] 3.4 移植 RO2 卡片（橘色左邊條，含 UTAUT 與 D&M 兩套框架表格）
- [x] 3.5 確認 RQ3、RO3 維持 `display:none` 隱藏

## 4. 移植 §1～§9 章節內容

- [x] 4.1 §1 背景（段落文字、aside 引言卡片、backtags 連結）
- [x] 4.2 §2 Verra VM0047 碳權標準對齊分析（結論框、三條規定表、P4 計算表、隱藏 Caveat 區塊）
- [x] 4.3 §3 演進旅程（改用 timeline 組件，5 個階段卡片）
- [x] 4.4 §4 30 棵實驗結果（結果表格，含顏色標記與 Google Drive 連結）
- [x] 4.5 §5 五條處理流程設計（兩張表格：流程規格與正交對照）
- [x] 4.6 §6 變數貢獻分析（三張表格：winner 次數、五變數結論、整體重要性）
- [x] 4.7 §7 生產版統計彙整（兩張表格：誤差門檻通過率、Verra §8.4 驗算，加總碳儲量說明）
- [x] 4.8 §8 結論（結論框、四個主要結論清單、7 棵未通過表格、1 棵 N/A 說明）
- [x] 4.9 §9 未解決（IMG_5804 說明段落）

## 5. 細節與收尾

- [x] 5.1 確認每個章節末尾保留「返回研究問題：RQ1 RQ2」backtags 連結，樣式符合設計系統
- [x] 5.2 移植 footer（最後更新時間、dashboard02 連結、Verra 官方文件連結）
- [ ] 5.3 在瀏覽器開啟 index.html，逐章確認內容完整、顏色標記正確、連結可點擊
- [ ] 5.4 確認 sticky header 導覽列在捲動時保持可見，點擊連結跳轉正常
