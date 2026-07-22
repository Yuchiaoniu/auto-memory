# arcus 長期查詢資料

## 論文卡片機制（2026-07-19 探索定案，尚未實作）

### 前提事實（已查證）
- arcus **沒有子代理機制**。隔離靠 `_call_model`（arcus_core.py 第 2390 行）開獨立子行程
  `claude --print --model <模型>`，該行程的內容與對話完全分開，效果等同隔離。
- arcus **一律使用 Opus**（`claude-opus-4-8`）。第 225 行 `OPUS_MODEL` 常數目前無人使用。
- `_call_model` 預設 timeout 為 120 秒，讀六萬字元論文必須拉長到約 600 秒。
- 本機已裝 PyMuPDF、BeautifulSoup、lxml、requests；trafilatura、readability 未裝（用不到）。
- 待解決：PDF 放在 Windows 本機，arcus 跑在 GCP，檔案傳輸路徑尚未決定。

### 實測數據（114年公費留學考試簡章.pdf，74 頁）
- 整份 58,738 字元；抽取工具吐出的原始碎塊 1,847 個。
- 合併到約 1000 字元後為 57 段，平均每段 1030 字元。
- 目錄約 2,394 字元。
- 分段存成 JSON 再讀回接合，與原文一字不差（已驗證為 True）。

### 機制設計
- 一篇論文一個資料夾，名稱取檔案內容雜湊前 16 碼，路徑 `~/.claude/cache/papers/`。
- 三個檔分工：`meta.json`（檔頭）、`card.json`（六欄卡片，約 1500 字元，常讀）、
  `text.json`（切段全文，約 60000 字元，備查才讀）。另有 `index.json` 當總表。
- 卡片固定六欄：研究問題／研究方法／研究流程／研究成果／爭議／未來發展。
  爭議與未來發展拆開存，顯示時可以合併呈現。
- 每一欄除了 `text` 之外帶 `refs` 出處鍵陣列（例如 `p012#03`）。
- 餵給模型的是「每段前面掛著鍵」的全文，模型回傳時必須附上出處鍵。
- 出處鍵由程式回查 `text.json` 驗證，查不到就標記「出處存疑」。
  原則與記憶卡片一致：程式判斷有沒有，模型只負責內容是什麼。
- 去重靠檔案內容雜湊，不靠檔名。改名、換資料夾、重複下載都會命中同一份快取。
- 超過約 15 萬字元改成分批讀再合併；掃描型檔案走文字辨識，辨識失敗就不產卡。
- 卡片經人工修改後在檔頭標記已編修，重跑不覆寫。

### 成本結論
- 第一次讀一篇：對話佔用約 1500 字元，實際付費約 60000（落在一次性行程身上，躲不掉）。
- 第二次以後重看同一篇：約 1500，省下約 97%。
- 回查一處出處：約 2000。
- 十篇論文比較同一欄：約 2000（相對於十篇全文的 587,380）。
- 平衡點：需要全文九成五以上才會虧，超過那條線只虧目錄那 2,394 字元。

<!-- arcus:memory-inbox:begin 機器維護區塊，請勿手動編輯 -->
{"title": "智商矩陣", "kind": "term", "gloss": "用作衡量和测试人在不同情景下认知表现的框架", "subject_hint": "心理学", "ts": "2026-07-22 09:15:32"}
{"title": "認知", "kind": "term", "gloss": "指人的思维能力，强调在不同情景间快速切换的高级认知能力", "subject_hint": "心理学", "ts": "2026-07-22 09:15:32"}
{"title": "動賽局", "kind": "term", "gloss": "描述具有时间维度和变动条件的竞争或博弈情境", "subject_hint": "博弈论", "ts": "2026-07-22 09:15:32"}
{"title": "快取層", "kind": "term", "gloss": "系统设计中的技术组件，用于性能优化", "subject_hint": "计算机科学", "ts": "2026-07-22 09:15:32"}
{"title": "推演", "kind": "term", "gloss": "指前面进行的复杂推理演绎过程", "subject_hint": "逻辑学", "ts": "2026-07-22 09:15:42"}
{"title": "矩陣", "kind": "term", "gloss": "用作分析工具，也是五个待回答问题之一", "subject_hint": "数学", "ts": "2026-07-22 09:15:42"}
{"title": "否決閘", "kind": "term", "gloss": "五个待回答问题之一，涉及否决权或制约机制", "subject_hint": "政治学", "ts": "2026-07-22 09:15:42"}
{"title": "發散", "kind": "term", "gloss": "在'高端會不會發散'问题中被提及，指思维或观点是否散开分化", "subject_hint": "心理学", "ts": "2026-07-22 09:15:42"}
{"title": "快取層", "kind": "term", "gloss": "新机制在升入核心系统前的隔离测试环境，失败机制在此停用不污染主体，成功后才升入core", "subject_hint": "计算机科学", "ts": "2026-07-22 09:20:29"}
{"title": "核心系統", "kind": "term", "gloss": "经过测试和批准的机制最终进入的主系统，代表生产环境的稳定状态", "subject_hint": "软件工程", "ts": "2026-07-22 09:20:29"}
{"title": "認知海拔", "kind": "term", "gloss": "用150/200/250/300四个等级标注回覆中对对话认知水准的自评，让使用者看到AI自我评估的思考水位", "subject_hint": "认知科学", "ts": "2026-07-22 09:20:29"}
{"title": "批准閘門", "kind": "term", "gloss": "测试窗满期后启动的人工检查点，由人工决定是否将测试成功的机制升入核心系统，决定权完全保留给使用者", "subject_hint": "系统工程", "ts": "2026-07-22 09:20:29"}
{"title": "快取層", "kind": "term", "gloss": "討論停用快取層需要驗證層執行程式碼判斷有害性，但驗證層實際不執行", "subject_hint": "計算機科學", "ts": "2026-07-22 09:25:21"}
{"title": "沙盒", "kind": "term", "gloss": "作為執行環境，驗證層缺少沙盒執行能力，導致無法驗證程式碼動作的害處", "subject_hint": "計算機科學", "ts": "2026-07-22 09:25:21"}
{"title": "排程", "kind": "term", "gloss": "實現三天測試窗需要外部排程器數時間、到期觸發，但arcus_do缺少這能力", "subject_hint": "計算機科學", "ts": "2026-07-22 09:25:21"}
{"title": "推播", "kind": "term", "gloss": "網頁批准閘到期後主動推提醒需要伺服器端推播機制，超出arcus_do範圍", "subject_hint": "計算機科學", "ts": "2026-07-22 09:25:21"}
{"title": "排程", "kind": "term", "gloss": "在引擎中實現定時機制，使新機制在測試期滿后自動觸發或標記為待批准", "subject_hint": "軟體工程", "ts": "2026-07-22 09:29:26"}
{"title": "stage → run → promote", "kind": "term", "gloss": "系統的正規流程，通過逐步推進更改來確保完整性，對比『後門』方式", "subject_hint": "軟體工程", "ts": "2026-07-22 09:29:26"}
{"title": "被動檢查", "kind": "term", "gloss": "無需背景進程，每次交互時檢查是否滿足條件的系統設計模式", "subject_hint": "軟體工程", "ts": "2026-07-22 09:29:26"}
{"title": "沙盒", "kind": "term", "gloss": "隔離環境中執行程式碼來判斷其危害性，但被驗證層的設計原則所限制", "subject_hint": "軟體工程", "ts": "2026-07-22 09:29:26"}
{"title": "驗證層", "kind": "term", "gloss": "系統故意不執行程式碼的設計層級，保持驗證的純淨性和安全性", "subject_hint": "軟體工程", "ts": "2026-07-22 09:29:26"}
{"title": "型別檢查", "kind": "term", "gloss": "靜態分析方法，檢查新機制是否破壞編譯或引入不相容", "subject_hint": "軟體工程", "ts": "2026-07-22 09:29:26"}
{"title": "測試窗", "kind": "term", "gloss": "新機制正式部署前的觀察期，通過靜態觀察和人工判斷驗證其有效性", "subject_hint": "軟體工程", "ts": "2026-07-22 09:29:26"}
{"title": "快取層", "kind": "term", "gloss": "系統中可根據觀察結果停用的層級，若發現問題可以禁用其快取功能", "subject_hint": "軟體工程", "ts": "2026-07-22 09:29:26"}
{"title": "快取層", "kind": "term", "gloss": "系統中需要測試的真實機制，判準包括回傳值正確性、命中率、記憶體佔用、過期資料等，可通過引擎每輪自檢來累積判定", "subject_hint": "軟體工程", "ts": "2026-07-22 09:36:42"}
{"title": "命中率", "kind": "term", "gloss": "評估快取效能的指標，命中率過低表示該快取無用應該停用", "subject_hint": "軟體工程", "ts": "2026-07-22 09:36:42"}
{"title": "沙盒", "kind": "term", "gloss": "隔離執行環境的機制，快取層測試不需要沙盒執行任意程式碼，可改而利用引擎內建的自檢路徑", "subject_hint": "軟體工程", "ts": "2026-07-22 09:36:42"}
{"title": "過期資料", "kind": "term", "gloss": "快取可能回傳的有害值，判別方式是對比直算結果和快取結果是否一致", "subject_hint": "軟體工程", "ts": "2026-07-22 09:36:42"}
{"title": "外推", "kind": "term", "gloss": "給超出現有數據的推測掛警語，用戶要求移除以鼓勵不縮手的思考", "subject_hint": "統計學", "ts": "2026-07-22 09:39:49"}
{"title": "自適應", "kind": "term", "gloss": "系統根據判官反饋自動調整提案的特性", "subject_hint": "系統論", "ts": "2026-07-22 09:39:49"}
{"title": "快取層", "kind": "term", "gloss": "新提案先在核心代碼外測試 3 天，判官把關後才進核心", "subject_hint": "計算機科學", "ts": "2026-07-22 09:39:49"}
{"title": "言之有據", "kind": "term", "gloss": "引用論文時必須指出具體出處並附上段落編碼", "subject_hint": "邏輯學", "ts": "2026-07-22 09:39:49"}
{"title": "段落編碼", "kind": "term", "gloss": "給論文段落賦予穩定編號（如 §1、§2），實現精確引用", "subject_hint": "資訊科學", "ts": "2026-07-22 09:39:49"}
{"title": "自適應提案快取層", "kind": "term", "gloss": "提案在核心檔之外的測試環境，判官審核無害後在3天期滿時通知", "subject_hint": "軟體工程", "ts": "2026-07-22 09:41:26"}
{"title": "判官", "kind": "term", "gloss": "負責審核提案，中途判定有害則停用該提案", "subject_hint": "軟體工程", "ts": "2026-07-22 09:41:26"}
{"title": "論文段碼", "kind": "term", "gloss": "為論文段落分配穩定編號，引用時強制帶碼便於反查", "subject_hint": "資訊管理", "ts": "2026-07-22 09:41:26"}
{"title": "粒度", "kind": "term", "gloss": "決定段碼編碼的最小單位是自然段還是每句", "subject_hint": "軟體工程", "ts": "2026-07-22 09:41:26"}
{"title": "智商矩陣", "kind": "term", "gloss": "用四個視角(150/200/250/300字級)同時分析同一問題並展開", "subject_hint": "認知科學", "ts": "2026-07-22 09:41:26"}
{"title": "觀察期", "kind": "term", "gloss": "提案在快取層中的測試週期(3天)，期滿無害則觸發到期通知", "subject_hint": "軟體工程", "ts": "2026-07-22 09:41:26"}
{"title": "有害處置", "kind": "term", "gloss": "在觀察期間若判定提案有害則直接從測試快取層停用", "subject_hint": "軟體工程", "ts": "2026-07-22 09:41:26"}
{"title": "核心檔", "kind": "term", "gloss": "系統的穩定主資料，提案獲批准前不變更任何內容", "subject_hint": "軟體工程", "ts": "2026-07-22 09:41:26"}
{"title": "溯源", "kind": "term", "gloss": "論文卡片每個字段都需帶有溯源資訊，使每條引用都能追蹤到原文來源", "subject_hint": "信息学", "ts": "2026-07-22 10:01:59"}
{"title": "段碼", "kind": "term", "gloss": "用 pXXX#YY 格式標記論文段落位置，作為實現溯源的基礎", "subject_hint": "信息检索", "ts": "2026-07-22 10:01:59"}
{"title": "自然段粒度", "kind": "term", "gloss": "以自然段落作為段碼分割單位，約每千字為一段", "subject_hint": "自然语言处理", "ts": "2026-07-22 10:01:59"}
{"title": "arcus_core.py", "kind": "work", "summary": "", "ref": "runtime/arcus_core.py", "subject_hint": "", "ts": "2026-07-22 10:15:41"}
{"title": "memory.md", "kind": "work", "summary": "", "ref": "memory.md", "subject_hint": "", "ts": "2026-07-22 10:16:03"}
{"title": "arcus_core.py", "kind": "work", "summary": "", "ref": "arcus_core.py", "subject_hint": "", "ts": "2026-07-22 10:17:33"}
{"title": "offset", "kind": "term", "gloss": "用於指檔案中的精確字符位置，定位程式碼片段（如 offset 235855 定位 def cards）", "subject_hint": "計算機科學", "ts": "2026-07-22 10:18:38"}
{"title": "spill handle", "kind": "term", "gloss": "用於處理超過回傳上限的大檔案，分段讀取並重組（spill://fetch_6224bcd2a3.txt）", "subject_hint": "計算機科學", "ts": "2026-07-22 10:18:38"}
{"title": "typecheck", "kind": "term", "gloss": "用於編譯前檢查 Python 檔案的語法正確性（kind=code 執行編譯檢查）", "subject_hint": "編譯原理", "ts": "2026-07-22 10:18:38"}
{"title": "stage", "kind": "term", "gloss": "用於暫存修改內容、分段組合程式碼，最後統一落地（stage_new、stage_run、promote 機制）", "subject_hint": "軟體工程", "ts": "2026-07-22 10:18:38"}
{"title": "segment", "kind": "term", "gloss": "用於表示文本的分段單位，對應段碼查詢原文內容（text.json 的 segments）", "subject_hint": "計算機科學", "ts": "2026-07-22 10:18:38"}
{"title": "JSON", "kind": "term", "gloss": "用於儲存結構化資料，但中文和換行符號會造成解析失敗需改用其他編碼", "subject_hint": "計算機科學", "ts": "2026-07-22 10:18:38"}
{"title": "refs", "kind": "term", "gloss": "用於儲存文本的引用段碼清單，指向原文位置（refs 裡每個段碼對應一個原文段落）", "subject_hint": "計算機科學", "ts": "2026-07-22 10:18:38"}
{"title": "offset", "kind": "term", "gloss": "日誌讀取的偏移量參數，offset=-1 不是合法分段", "subject_hint": "計算機科學", "ts": "2026-07-22 10:29:10"}
{"title": "import", "kind": "term", "gloss": "Python 模組導入機制，在伺服器啟動時將 arcus_core.py 載入到記憶體", "subject_hint": "計算機科學", "ts": "2026-07-22 10:29:10"}
{"title": "記憶體", "kind": "term", "gloss": "程式執行時的運行環境，新程式碼在磁碟但記憶體仍是舊版本，需重啟伺服器才能更新", "subject_hint": "計算機科學", "ts": "2026-07-22 10:29:10"}
{"title": "memory.md", "kind": "work", "summary": "", "ref": "memory.md", "subject_hint": "", "ts": "2026-07-22 10:53:55"}
{"title": "crompvoets_fetch_queue.jsonl", "kind": "work", "summary": "", "ref": "crompvoets_fetch_queue.jsonl", "subject_hint": "", "ts": "2026-07-22 11:07:53"}
{"title": "memory.md", "kind": "work", "summary": "", "ref": "memory.md", "subject_hint": "", "ts": "2026-07-22 11:08:10"}
{"title": "memory.md", "kind": "work", "summary": "", "ref": "memory.md", "subject_hint": "", "ts": "2026-07-22 11:21:15"}
{"title": "memory.md", "kind": "work", "summary": "", "ref": "memory.md", "subject_hint": "", "ts": "2026-07-22 11:42:54"}
{"title": "memory.md", "kind": "work", "summary": "", "ref": "memory.md", "subject_hint": "", "ts": "2026-07-22 12:17:35"}
{"title": "memory.md", "kind": "work", "summary": "", "ref": "memory.md", "subject_hint": "", "ts": "2026-07-22 12:18:14"}
<!-- arcus:memory-inbox:end -->
