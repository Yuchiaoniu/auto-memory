# statistics-study-app memory.md

## 網站部署資訊
- GitHub Pages URL：https://yuchiaoniu.github.io/statistics-study-app/
- 本機路徑：C:\Users\yuchi\projects\statistics-study-app
- 主分支：main，push 即上線

## 心智模型架構（M1–M4）
| 模型 | 核心問題 | 對應頁面 |
|------|---------|---------|
| M1 描述與分類 | 怎麼整理眼前的數據？ | descriptive-statistics.html |
| M2 推論與概率 | 看不見母體，但能猜嗎？ | probability-discrete.html, continuous-distributions.html |
| M3 實驗與審判 | 效果是真實的還是巧合？ | hypothesis-testing.html, inference-testing.html, decision-tree.html |
| M4 系統與決策 | 多個變數同時分析怎麼辦？ | advanced-analysis.html |

## 過渡橋接（已補齊）
- M1→M2：continuous-distributions.html 開頭加入「從觀察形狀到建立模型」說明
- M2→M3：sampling-distributions.html（CLT、標準誤）
- M3→M4：advanced-analysis.html 開頭加入多重比較問題說明（1-(1-α)^k 公式）

## ANOVA 解題框架（一般步驟）
- Step 1：建立假設（H0 全組相等，H1 至少一組不同，設 α）
- Step 2：計算各組平均 x̄ⱼ 與總平均 x̄
- Step 3：計算 SSB = Σ nⱼ(x̄ⱼ−x̄)²，dfB = k−1，MSB = SSB/dfB
- Step 4：計算 SSW = ΣSSⱼ（各組組內離差平方和相加），dfW = N−k，MSW = SSW/dfW
- Step 5：F = MSB/MSW，列 ANOVA 彙總表
- Step 6：與 F 臨界值比較，做出決策
- Step 7（若拒絕 H0）：LSD 事後多重比較，LSD = t(α/2,dfW) × √(MSW×2/n)

## 名詞對照
| 縮寫 | 全名 | 白話 |
|------|------|------|
| SSB | Sum of Squares Between | 各組平均離總平均的距離平方和（加權）|
| SSW | Sum of Squares Within | 各組內資料離自己組平均的距離平方和（三組加總）|
| SST | Sum of Squares Total | 所有資料離總平均的距離平方和，SST = SSB + SSW |
| dfB | Degrees of Freedom Between | k−1 |
| dfW | Degrees of Freedom Within | N−k（各組 nⱼ−1 的總和）|
| MSB | Mean Square Between | SSB/dfB，組間差距強度（訊號）|
| MSW | Mean Square Within | SSW/dfW，組內隨機波動強度（雜訊）|
| F   | F 統計量 | MSB/MSW，訊號與雜訊的倍數比值 |

## 練習題解答（20260527）
檔案路徑：C:\Users\yuchi\OneDrive\Desktop\三下課程\統計學\20260527練習題_解答.docx

### 第一題（三種教學方式，不平衡設計）
- 資料：電視教學 n=7（sum=588）、講師講習 n=8（sum=688）、實地觀摩 n=6（sum=468），N=21
- 注意：94 屬於講師講習欄，不是實地觀摩（表格原始排版易誤讀）
- x̄₁=84.00，x̄₂=86.00，x̄₃=78.00，總平均=83.05
- SSB=228.95，MSB=114.48；SSW=818.00，MSW=45.44
- F=2.52 < F臨界(2,18,α=0.05)=3.55 → 不拒絕 H0，無顯著差異

### 第二題（三種戰機速度，平衡設計）
- 資料：IDF/F16/幻象2000 各 n=10，N=30
- x̄(IDF)=2.095，x̄(F16)=2.206，x̄(2000)=2.832，總平均=2.378
- SSB=3.158，MSB=1.579；SSW=0.993，MSW=0.0368
- F=42.94 > F臨界(2,27,α=0.05)=3.35 → 拒絕 H0，有顯著差異
- LSD=0.176：IDF vs F16 無差異；IDF vs 2000 顯著；F16 vs 2000 顯著
- 結論：幻象2000 速度顯著高於 IDF 與 F16
## Case 1~8 決策流程（2026-06-24 整理）

```
① 配對？
   → 是 → Case 8（算差值 d，單母體 t，df = n-1）
   → 否 → ②

② 幾個母體？
   → 1 個 → Case 1/2/3（σ已知→Z；n≥30→Z；否則→t，df=n-1）
   → 2 個 → ③
   → 3個以上 → ANOVA

③ 雙母體：n₁≥30 且 n₂≥30？
   → 是 → Case 5（Z，SE=√(s₁²/n₁+s₂²/n₂)）
   → 否 → F檢定：F₀=s₁²/s₂²（大的放分子）
      → F不顯著（等變異）→ Case 6（pooled t，df=n₁+n₂-2）
      → F顯著（不等變異）→ Case 7（Welch t，Satterthwaite df）
```

## Case 6/7/8 關鍵公式

| Case | 分子 | 分母（SE） | df |
|------|------|-----------|-----|
| 6（pooled t） | x̄₁−x̄₂ | √(sₚ²/n₁+sₚ²/n₂) | n₁+n₂−2 |
| 7（Welch t） | x̄₁−x̄₂ | √(s₁²/n₁+s₂²/n₂) | Satterthwaite |
| 8（配對 t） | d̄ | s_d/√n | n−1 |

Case 6 合併變異數：sₚ² = [(n₁−1)s₁²+(n₂−1)s₂²] / (n₁+n₂−2)

## 常見錯誤與修正（本次對話）

- F₀ 分子分母說反：正確為 MSB/MSW（組間/組內），不是組內/組間
- SSB 乘以總 N：正確為各組自己的 nᵢ，不是 N；有 k 項，不是一項
- SSW 除以組數：SSW 是各組離差平方和直接加總，不需除以組數
- Case 6 SE「各自開根號再相加」：正確為加總後才開根號 √(sₚ²/n₁+sₚ²/n₂)
- 配對 t 分子說成「差值除以根號n」：分子只是 d̄，√n 在分母
- 分子的 0 誤解為「母體/樣本變異數比值」：0 是 H₀ 主張的差值（μ₁−μ₂=0）

## 各檢定在測什麼（本次對話整理）

| 工具 | 在測什麼 | H₀形式 |
|------|---------|--------|
| 單母體 Z/t | x̄ 離 μ₀ 幾個 SE | μ = μ₀ |
| 雙母體 Z/t | 兩組母體平均數是否相等 | μ₁−μ₂=0 |
| 配對 t | 差值的母體平均是否為 0 | μ_d=0 |
| F（Case 6/7 前置） | 兩組母體變異數是否相等 | σ₁²=σ₂² |
| ANOVA | k 組母體平均數是否全部相等 | μ₁=μ₂=…=μₖ |
