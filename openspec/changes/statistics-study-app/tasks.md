# statistics-study-app — 新內容擴充

## 目標
依照課程目錄分類，將使用者提供的教材資料整合進現有統計學教學網站。

## 已完成

- [x] 靜態網站建立並部署至 GitHub Pages
- [x] Dark theme CSS 設計（`css/main.css`）
- [x] 課程目錄頁面（`chapters/syllabus.html`）— Mendenhall 15th Ed Ch 1–15 完整列表
- [x] 隨機變數章節（`chapters/random-variables.html`）— PMF / CDF / 期望值 / 變異數
- [x] 連續型分配章節（`chapters/continuous-distributions.html`）— 常態 / 均勻 / 指數 / 近似二項
- [x] 互動圖表（Chart.js）— PDF/CDF 視覺化、參數調整
- [x] 專詞速查頁面（`chapters/glossary.html`）— 71 個詞條，9 個分組
- [x] Z 表與 t 表互動查詢工具（即時計算，4 種查詢模式）
- [x] 假設檢定核心詞彙 16 個 + 公式卡 5 張
- [x] 所有詞條加入「白話速覽」說明（先白話，再精準）
- [x] 新增 4 個詞條：μ 母體平均數、標準差 vs 標準誤、母體常態假設、Z 公式邏輯
- [x] 變異數詞條加入計算流程表（原始資料 → 偏差 → 平方 → 變異數 → 標準差 → 標準誤）
- [x] 建立六階段線性學習心智模型（Stage 1–6 + 進階工具）
- [x] `js/terms-data.js` 詞條資料庫（78 個詞條，7 個 stage，STAGES + ADVANCED + TERMS）
- [x] `chapters/stages.html` 六階段地圖主頁（彩色 stage 卡片、詞條 chip、章節 badge）
- [x] `chapters/term.html` 個別詞條模板（白話速覽、公式 MathJax、上下頁導覽）
- [x] 全站 nav bar 加入「六階段地圖」連結
- [x] Stage 7 進階工具加入 STAGES 陣列（ANOVA / 迴歸 / 卡方 / 無母數）

## 待完成（原有）

- [ ] 將 Stage 7 詞條（ANOVA、迴歸、卡方等）補充 easyDef 與公式
- [ ] 公式符號說明：每個公式加入 `symbols` 陣列，term.html 渲染符號表或連結至對應詞條
- [ ] 題庫整合：將現有 72 題（`data/questions.json`）連結至六階段地圖對應詞條
- [ ] 題庫擴充：依各章節新增練習題（目前集中在連續型分配，缺 Stage 1–5 題目）
- [ ] Push 本機變更至 GitHub Pages

---

## 心智模型導向重構

### 設計理念

把「章節目錄」改成「心智模型目錄」：
學生進站時看到的不是 Ch 1、Ch 2，而是四個心智模型的演化路徑。
每個模型回答一個問題：「人類當時面對什麼困境，才逼出這個工具？」

```
M1 描述與分類  →  M2 推論與概率  →  M3 實驗與審判  →  M4 系統與決策
   (直覺時代)        (賭徒天文家)       (費雪農學)         (大數據AI)
```

### 四大心智模型與章節對應

| 模型 | 核心問題 | 歷史背景 | 對應章節 | 核心工具 |
|------|---------|---------|---------|---------|
| M1 描述與分類 | 我怎麼整理眼前的數據？ | 人類天生找規律 | Ch 1–3 敘述統計 | 平均數、標準差、直方圖 |
| M2 推論與概率 | 我看不見母體，但能猜嗎？ | 17–18c 天文誤差分析 | Ch 4–6 機率、連續分配 | 常態分配、Z 分數 |
| M3 實驗與審判 | 效果是真實的，還是巧合？ | 1900–1920s 農學/藥學 | Ch 7–10 抽樣、推論 | Z/t/F/χ² 檢定 |
| M4 系統與決策 | 多個變數同時分析怎麼辦？ | 20c 大科學、資訊爆炸 | Ch 11–15 ANOVA/迴歸 | ANOVA、迴歸、卡方 |

### 檢定工具演化時間軸（M3 的核心敘事）

```
1800s  Z 統計量  ── 高斯/拉普拉斯  ── 大樣本理想，假設已知 σ
1900   χ² 檢定   ── Karl Pearson   ── 突破「只能比數字」，進入類別比較
1908   t 檢定    ── Gosset(Student) ── 啤酒廠小樣本問題，分配尾巴變胖
1920s  F 檢定    ── Ronald Fisher  ── 農學多組比較，ANOVA 架構誕生
```

### 統計決策樹（M3 的導覽邏輯）

```
問題一：數據是什麼型態？
  ├─ 連續（量測出來的）──→ 問題二
  └─ 類別（數出來的）──→ χ² 檢定

問題二：要比什麼？
  ├─ 比平均數 ──→ 問題三
  ├─ 比變異程度 ──→ F 檢定（等變異假設）
  └─ 比整體分配 ──→ χ² 適合度檢定

問題三：樣本大不大？母體 σ 知不知道？
  ├─ 大樣本（n≥30）或已知 σ ──→ Z 檢定
  └─ 小樣本且 σ 未知 ──→ t 檢定
     └─ 兩組比較前先 F 檢定確認等變異
```

---

### 實作任務

#### Phase A — 重構導覽入口

- [x] **A1** 新增 `chapters/mental-models.html`：四模型首頁，每個模型一張卡片，顯示時代背景 + 核心問題 + 進入按鈕
- [x] **A2** `index.html` nav bar 新增「心智模型」連結，或以心智模型取代現有「七階段地圖」入口
- [x] **A3** 在 `chapters/stages.html` 頂部加入「心智模型框架」橫幅，說明現有 Stage 1–7 屬於哪個 Mx 模型

#### Phase B — M3 實驗與審判模型（優先，與課程最直接相關）

- [x] **B1** 新增 `chapters/hypothesis-testing.html`：假設檢定總覽頁
  - 法庭審判隱喻（H₀ = 無罪推定）
  - α 防線視覺化（拒絕域互動圖）
  - 型 I / 型 II 錯誤對照表
- [x] **B2** 新增 `chapters/test-evolution.html`：Z → χ² → t → F 歷史時間軸頁面
  - 每個工具：人物卡（誰發明）＋困境卡（面對什麼問題）＋公式卡
- [x] **B3** 新增 `chapters/decision-tree.html`：統計決策樹互動頁
  - 點選問題節點自動導向對應檢定方法
  - 連結至對應詞條與章節

#### Phase C — 補齊 M1、M2 內容頁

- [x] **C1** `chapters/descriptive-statistics.html`（M1）— 平均/中位/眾數/全距/變異數/標準差/IQR/Z分數，8概念56題
- [x] **C2** `chapters/probability-discrete.html`（M2）— 基本機率/互補/加法/條件/獨立/二項/波松，7概念49題
- [x] **C3** `chapters/sampling-distributions.html`（M2→M3）— 抽樣分配/CLT/標準誤，3概念18題

#### Phase D — M4 進階分析

- [x] **D1** `chapters/inference-testing.html`（M3）— Z/t信賴區間、單樣本Z/t、兩樣本t，5概念38題
- [x] **D2** `chapters/advanced-analysis.html`（M4）— ANOVA/迴歸/卡方，3概念21題
- [x] **D3** Stage 7 詞條補齊 easyDef 與公式（anova formula 已補入 terms-data.js）

#### Phase E — 整合收尾

- [x] **E1** 公式符號說明：每個公式加入 `symbols` 陣列
- [x] **E2** 題庫整合：共 254 題（含新增 182 題），全部連結至心智模型各章節
- [x] **E3** Push 本機變更至 GitHub Pages

#### Phase F — 補齊缺口

- [x] **F1** `chapters/inference-testing.html` 加入觀念 6：配對 t 檢定（Paired t-test）
- [x] **F2** 新增 `chapters/distribution-selection.html`：分配情形選擇決策頁
- [x] **F3** `chapters/decision-tree.html` 加入配對 t 分支
- [x] **F4** 全站 nav bar 加入「分配選擇」連結

#### Phase G — 雙母體四種 Case 補齊

- [x] **G1** `chapters/inference-testing.html` 觀念 5 擴充：補齊 Case 1（σ已知→Z）、Case 2（大樣本→Z近似）、Case 4 Welch t 完整公式（含 Satterthwaite df）；加入四種 Case 決策框架表與決策流程說明
- [x] **G2** `data/questions.json` 補入 8 題（0513×4、0520×2、0527×2）：inftest-0513-q1~q4、twosamp-0520-q1~q2、anova-0527-q1~q2，題庫共 273 題
- [x] **G3** 新增 `chapters/correlation.html`：關聯分析完整教學頁（觀念 1 三種變數組合、觀念 2 Pearson r 公式與解讀、觀念 3 計算範例、觀念 4 顯著性檢定、觀念 5 相關≠因果），補入 6 題（corr-001~006，concept=pearson-r），mental-models.html M4 卡片加入「Pearson 相關」chip 與關聯分析連結，題庫共 279 題
- [x] **G4** 新增 `chapters/estimation.html`：估計理論教學頁（觀念 1 點估計vs區間估計、觀念 2 三大性質不偏/一致/有效、觀念 3 MLE最大概似估計、觀念 4 信賴區間寬度與n的關係），補入 6 題（est-001~006，concept=estimation），mental-models.html M3 卡片加入「點估計/MLE」chip 與估計理論連結，題庫共 285 題：關聯分析完整教學頁（觀念 1 三種變數組合、觀念 2 Pearson r 公式與解讀、觀念 3 計算範例、觀念 4 顯著性檢定、觀念 5 相關≠因果），補入 6 題（corr-001~006，concept=pearson-r），mental-models.html M4 卡片加入「Pearson 相關」chip 與關聯分析連結，題庫共 279 題
- [x] **G5** `chapters/hypothesis-testing.html` 擴充三大補充區塊：① 三種決策方法對照表（臨界值法/p值法/信賴區間法）；② p值法完整說明（定義、三尾公式、決策規則、計算範例）；③ 信賴區間法（Case1/Case3公式、計算範例、等價性說明）；④ 型II誤差β深入說明（定義、四因素影響表、α-β拉扯機制）；⑤ 檢定力Power說明（定義、四個等級表、提高Power四種方法）。補入 11 題（pval-001~004、ci-001~003、beta-001~004，三個 concept）。題庫共 296 題。建立 Word 練習題文件「假設檢定補充練習題（p值法_信賴區間法_型II誤差_檢定力）.docx」共 20 題存至統計學資料夾。
