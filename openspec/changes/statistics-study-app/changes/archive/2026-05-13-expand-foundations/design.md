## Context

`convert-to-static-site` 完成後到本 change 之間，網站累積了七大類增補（見 proposal）。這些增補本來是「邊看教科書講義邊補」的對話式工作，沒有走 propose/apply 流程，因此 openspec/ 目錄與實際網站狀態脫節。

本 change 的本質是「**追溯記錄**」：把已經完成的工作補進 spec 系統，同時為後續工作預留可追蹤的入口。

## Goals / Non-Goals

**Goals:**
- 把所有未追蹤的內容增補整理為正式 capability（新增或修改）
- 把所有已完成的工作在 tasks.md 中以 `[x]` 標示（含完成日期或情境註記）
- 列出明確的後續擴充項目，每項都對應一個可被未來 `/opsx:apply` 推進的任務
- spec 文件應該足夠完整，使「只看 openspec/changes/expand-foundations/」就能還原網站結構

**Non-Goals:**
- 不重新審視已做的設計決策（例如「為何用 vanilla JS」這種已經在 `convert-to-static-site` 討論過的）
- 不一次把所有未補章節都做完——只把基礎觀念與連續型完成，其他列為 future tasks
- 不引入新的技術依賴（仍是純靜態）

## Decisions

### 決策 1：用一個 change 涵蓋多項增補，而非每項一個 change

**選擇**：把 7 類增補都納入 `expand-foundations` 一個 change。

**理由**：
- 這些增補的「主題」一致——都是強化連續型分配章節的學習體驗
- 增補之間有依賴（暗色主題影響所有元件的視覺、警告框 CSS 沿用 misconception 樣式、四大支柱用了既有的 pillar 元素），分散到多個 change 會難以驗收
- 對個人專案來說，每改一處就開 change 太繁瑣，反而會打消使用 opsx 的意願

**替代方案**：
- 7 個小 change：spec 上更精細，但實際維護成本不成比例
- 0 個 change（永遠不追蹤）：失去 openspec 的價值，未來迷失

### 決策 2：新增 `course-syllabus` capability 而非塞進現有

**選擇**：獨立 capability，因為「教科書全章節目錄」是一個跨章節的元功能。

**理由**：
- 不屬於任何單一章節
- 未來會持續變動（每補一章就要更新狀態 pill）
- 若塞進 content-rv 或 content-continuous 都不對稱

### 決策 3：新增 `dark-theme` capability 而非塞進 static-site

**選擇**：把「色彩 / 元件視覺系統」獨立為一個 capability。

**理由**：
- 暗色主題是跨頁面、跨元件的設計系統決策
- 未來若想做「亮色切換」、「色弱模式」、「列印樣式」都會修改這個 capability
- 與 static-site（檔案結構與部署）職責分離

### 決策 4：interactive-charts 採用「漸進擴充」

**選擇**：把 `area-viz.js` 視為 interactive-charts capability 下的新元件，不另建 capability。

**理由**：
- 都是「Canvas-based PDF 互動圖表」這類東西
- 未來若加「離散→連續動畫」、「常態 vs 二項近似比較」也會放這裡
- 共用底層繪圖邏輯（雖然目前是各自寫的，未來可重構共享）

### 決策 5：tasks.md 同時包含「已完成回溯」與「未來待辦」

**選擇**：tasks.md 分兩大段：「Done (回溯)」與「Future Expansion」。

**理由**：
- Done 段讓人理解這個 change 涵蓋什麼
- Future 段讓人知道下一步在哪
- 這也符合 opsx 設計：tasks 是 actionable 但完成了打勾即可

## Risks / Trade-offs

- **風險：spec 與實際程式碼仍可能不同步**（畢竟是手動寫的）→ 緩解：寫 spec 時對著實際檔案逐項對照
- **風險：tasks.md 變得過長**（同時有歷史與未來）→ 接受：分段標題清楚，掃讀仍快
- **權衡：本 change 同時是「歸檔」也是「規劃」** → 接受：對個人專案是合理折衷

## Migration Plan

無遷移。內容已上線、檔案已存在，本 change 純粹是回溯記錄與規劃。

完成本 change 後建議的 archive 順序：
1. archive `build-mvp-rv-continuous`（已被全面取代）
2. archive `convert-to-static-site`（架構轉換已穩定）
3. `expand-foundations` 作為「現況快照」保留，未來新增功能再開新 change

## Open Questions

- Future tasks 中的「離散→連續動畫」是否獨立成 change？建議：是。它需要新的設計決策（動畫機制、互動模式），值得自己一個 propose 循環
- 是否要建立 `course-syllabus` 的 JSON 資料源（讓狀態 pill 由 JSON 驅動）？目前是寫死 HTML，未來擴充可考慮
- 圖片資源管理：使用 `images/` 資料夾的命名與引用約定，本 change 暫不正式化，等實際引用第一張圖時再決定
