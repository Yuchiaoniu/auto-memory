
## 2026-07-19 00:00

**主題**：記憶卡片三段式機制實作完成並上線

**重點**：
- 三段流程全部寫進 arcus_core.py：每輪收料進收件匣、每 6 小時歸檔收斂科別、回覆前關鍵字注入
- 排程器寫在 core 而非 server.py，用 --mcp 自檢擋掉臨時行程；server.py 一行未改
- 驗證 31 項通過 30 項，唯一失敗是測試行程自己搶走鎖造成的假失敗，已於乾淨行程重測正確
- 真實歸檔實測：5 張卡片、耗時 9.1 秒、抽屜 11→12，收斂有效
- arcus.service 已重啟，排程執行緒在常駐行程內確實運作（重啟 26 秒內完成補歸檔）
- 外部網址 /arcus/ 回 200，服務正常
- 未完成：J.6 需連續觀察 24 小時確認每天恰好歸檔四次；K.1 STATE.md 歸檔留待第二階段

---

## 2026-07-19 01:30

**主題**：論文卡片機制設計、實作、上線與實測

**重點**：
- 釐清 arcus 沒有子代理，隔離改用一次性模型行程（claude --print 子行程），一律 Opus
- 新增 runtime/paper_cards.py，接上五個指令：ingest／cards／quote／list／verify
- 虛擬機自行下載 arXiv 論文測試，18 項驗證全數通過
- 卡片 2139 字元對全文 40035 字元，省約 95%；跨論文取單欄僅 474 字元
- 萃取耗時 57.3 秒，出處存疑 0 欄；快取二次命中 0.2 秒
- 未做：專書分批讀、掃描型文字辨識、卡片人工編修保護

---

## 2026-07-20 11:14

**主題**：論文卡片改造落地——權威索引庫連接器 + meta 逐字化（§91）

**重點**：
- 在 arcus_core.py 核心新增 arXiv 連接器（`_arxiv_lookup`/`_journal_lookup`/`_resolve_source`），作者/科別/日期改由索引庫官方著錄逐字填入，零模型、不用 pdf 內部中繼資料
- 建卡入口改吃精確識別碼（arXiv id）或直接 pdf；裸關鍵字不建卡、導向 discover，擋掉關鍵字模糊比對張冠李戴
- 作者解析加固，濾掉舊著錄混入的 Keywords 等假人名
- 實測晶格論文 arXiv 1911.08248v2 完整建卡成功：作者 Ankudinov/Galenko、科別 cond-mat.mtrl-sci、日期逐字；六格分析卡照長為附加層，meta 欄已從卡片清乾淨
- 公共行政系統理論以裸關鍵字測試，正確觸發留白（arXiv 不涵蓋，待 Semantic Scholar/Crossref 轉接器補上）
- py_compile 通過、arcus.service 重啟 active、外部端點 /arcus/ 與 /arcus/api/projects 皆回 200
- 備份保留於 arcus_core.py.bak_pre91

---

## 2026-07-20 14:02

**主題**：網頁抓取改為型別感知 + 授權層，讓 arcus 能讀 JSON 介面（§92）

**重點**：
- 根因：舊 fetch_and_prune 一律當 HTML 剖析，只取 <body>/<main>/<article> 容器內文字，JSON 無此容器故整份回空——不是權杖或連線問題
- 修法一（剖析層）：抓完先看 Content-Type 或嗅探首字元，JSON/純文字/XML 逐字回傳、超長明講截斷；HTML 才走原本去雜訊；HTML 無容器時退回原始文字不再回空
- 修法二（授權層）：新增 _web_auth_headers，依主機從 gitignore 的 .web_creds.json 帶授權標頭；權杖不進程式碼、不進版控
- 通用不特例化：任何 JSON 介面、任何需權杖的介面都適用，read 與 discover 兩路共用同一抓取函式
- 驗證：直接載入模組對 Apify 介面呼叫，逐字回 2202 字、解析出 5 個 Actor（授權生效）；example.com 對照仍去雜訊；py_compile 通過；服務 active；外部 /arcus/ 與 /arcus/api/projects 皆 200
- 備份保留於 arcus_core.py.bak_prewebjson

---

## 2026-07-21 修好「第一輪 No such tool available」的真正根因

**根因（已證實，非圍堵）**：`claude --print` 模式在啟動當下就把工具清單快照進第一次推論請求，
此時 stdio 版工具伺服器（python3 arcus_core.py --mcp）還在 status=pending 尚未連上。
arcus_core.py 在模組層即時載入 requests 與 bs4，光這兩個套件就吃掉約 200 毫秒冷啟。
2026-07-14 把思考預算設為 0 之後，模型第一個工具呼叫瞬間送出、搶在工具登記之前，
於是第一輪工具不在清單裡，模型只好退回裸名 arcus_do，被系統回「No such tool available」。
（以前會正常，是因為思考時間剛好替工具伺服器爭取到連上的時間；思考歸零後這段緩衝消失。）

**證據**：init 事件顯示 mcp_servers status=pending 且 tools 陣列缺 mcp__arcus__arcus_do；
第二輪出現 cache_miss_reason type=tools_changed，代表工具集在同一輪中途才變動。

**修法（縮短冷啟、贏得第一輪競賽，不重開思考預算、不做重試牆）**：
把 requests 與 bs4 從模組層即時載入改為延遲載入，新增 _ensure_web_libs()，
只有第一次真正抓網頁時才載入；search_searxng 與 fetch_and_prune 進入時各呼叫一次。
模組載入時間從約 243 毫秒降到約 93 毫秒。

**驗證**：正式設定檔 arcus_mcp.json 連跑 16 次，第一輪工具全部就位、狀態 connected（16/16）；
服務重啟後 active；外部公開網址對 grad-cert-tuijian 連發需要立刻用工具的訊息，
arcus 真的動用工具讀取目錄與檔案、原樣回列表，三次皆無「No such tool available」或「暫時性斷線」字樣。
備份保留於 arcus_core.py.bak_lazyweb。

---
## 2026-07-21 常駐 HTTP MCP 端點上線

**主題**：把每輪臨時 stdio MCP 行程改為常駐 HTTP 路由，根除「工具第一輪還在 pending 就被拍照」的登記競速。

**重點**：
- server.py 新增 /arcus/mcp（POST/GET/DELETE）三方法路由，工具原樣派進 arcus_core._arcus_mcp_handle（真 arcus_do 分派）；零官方套件、純標準庫＋既有 Flask。備份 server.py.bak_httpmcp。
- arcus_mcp.json 由 stdio（python3 arcus_core.py --mcp）改為 {"type":"http","url":"http://127.0.0.1:7800/arcus/mcp"}；伺服器鍵名維持 arcus，工具全名 mcp__arcus__arcus_do 不變。備份 arcus_mcp.json.bak_stdio。
- 驗證：直打路由 N=12 → connected 12/12、tool_present 12/12（第一輪推論即登記）。公開網址 /arcus/api/chat 外部實測 3 輪 → No such tool 0/3；2 輪實際呼叫 arcus_do 成功。競速消除。
- 待辦：Risk 3 併發——server.py threaded=True，多個並行對話共用同一常駐引擎，需稽核 _arcus_do_dispatch 及其處理器的共享狀態執行緒安全（舊 stdio 版每輪獨立行程、天然隔離，此為常駐化新增風險）。
- 回滾：把 arcus_mcp.json 換回 .bak_stdio 即恢復舊行為，server.py 路由留著不影響。

---

## 2026-07-21 08:22

**主題**：工具說明就地化——把每個 cmd 的機械用法收回工具自己的結構定義，姿態檔只留精神與跨工具政策

**重點**：
- 加厚工具結構定義（_ARCUS_TOOL.description）的記憶那段：明講讀記憶卡片一律走 recall、禁止改用 read 去讀 memory.md 或任何卡片原始檔（原始檔含未整理內容、直接讀會拿到雜訊）。修掉先前 arcus 讀卡片時退回讀原始檔的錯誤。
- 移除姿態檔（_arcus_system_prompt）裡與 schema 重複的逐條 cmd 列表，改成一行指標，指向工具自己的說明欄；全名規則、身分、工作紀律、log.jsonl 時區換算等跨工具政策全部保留。用意是去重、讓機械用法跟著 arcus_core.py 程式碼走，避免兩邊各記一份、日久漂移。
- 兩處都在 arcus_core.py，屬常駐記憶體，已 sudo systemctl restart arcus.service 生效；備份 arcus_core.py.bak_tooldoc，py_compile 通過。
- 外部驗證（公開網址 /arcus/api/chat 發真實一輪，請 arcus 讀「心理學」卡片）：無「No such tool available」；串流文字自述走 recall；伺服器端 log.jsonl 只見 recall、不見 read、無 memory.md 原始檔讀取。修正確認生效。

---

## 2026-07-21 20:14 三響互審腳本上線

**主題**：新增分離腳本 three_voices.py，一則訊息三響（主回應 arcus／openrouter 405B 獨立答／判官盲讀裁決）

**重點**：
- 不動 arcus_core.py，獨立成檔放 runtime/；金鑰只從 gitignore 的 .web_creds.json 讀
- 只用 405B 同級：付費 Nemotron Ultra 550B 為主、Super 120B 備援（models 陣列自動 fallback），避開免費版 429
- 判官盲讀 A/B（不知誰寫）後裁異同、判可信、給綜合；判官目前=Nemotron，判到自己那份答案 B 有自偏風險，待議換異血統判官
- 冒煙測試通過：三響齊回，付費端點正常無 429，成本約幾釐美元

---
## 2026-07-21 20:33 卡片子系統補上 paper_delete + 清殘卡

**主題**：為 paper 卡片子系統新增刪除指令 paper_delete，並清掉殘卡 3d777f8f3d4dae7f

**重點**：
- 查核發現 arcus 先前兩處說法錯：卡庫真實路徑在 openspec/changes/arcus/runtime/_papers（非 ~/.claude/tools/_papers），且就在其刪除權限範圍內，「碰不到」不成立；但「工具原本沒有刪除指令」這點屬實
- arcus_core.py 五處改動：新增 delete_paper()（先剪 index.json 那筆、再刪卡片目錄，內建路徑安全上限，只准刪 _papers 直接子目錄）＋接進指令分派＋加進 cmd enum＋補說明欄。備份 .bak_paperdel，py_compile 通過
- 重啟 arcus.service 後引擎已對外露出 paper_delete（tools/list 可見）
- 殘卡已清：卡片數 17→16、目錄消失、index 殘卡歸零、正卡 a9474 完好；安全上限測試擋下越界 id（../evil）與不存在卡號

---
## 2026-07-21 21:20 第三響接進網頁(只動 server.py,不碰 core)

**主題**：把 OpenRouter 第三響接到 arcus 網頁,主回應＋判官＋第三響三則泡泡一起出

**重點**：
- 查證澄清:網頁原本兩則(主回應＋判官)是引擎內建「一回二」機制,three_voices.py 是獨立指令列腳本、從未接網頁,所以網頁看不到 openrouter 那響
- 也查出「繞道讀 PDF」根本不存在:read 指令只讀純文字、VM 無 read_pdf 腳本、arcus 只有 arcus_do 一隻手;先前它自述「read_pdf 讀進來、已建卡、五欄位」全屬憑空捏造(卡數維持 16、無 Van de Walle 卡)
- 改動只在 server.py:檔頭加安全金鑰讀取＋_third_voice()(只借 three_voices 的 ask_openrouter/OR_MODELS,自寫金鑰讀取避開其 load_key 的 sys.exit 打斷串流);判官落地後多送一則 report 泡泡=第三響。借判官泡泡樣式、前端零改動。備份 .bak_thirdvoice,py_compile 通過
- 端到端驗證:本機與公開 HTTPS(HTTP 200)各打一輪,皆收到兩則 report(判官+第三響),第三響走付費端點 nvidia/nemotron-3-ultra-550b-a55b、未撞 429

---
## 2026-07-21 21:56

**主題**:論文卡片空白標題的根源查明與修復(標題回退鏈)

**重點**:
- 事實查核:上傳的兩篇 PDF 其實已成功建卡(卡庫 16→18,今天 13:31/13:33 建成,六個關鍵字全中);arcus 自稱「沒建成卡、絕對路徑讀不到」為誤判,絕對路徑實際可用。
- 根源:arcus_core.py 第 5937 行標題只從權威索引著錄(_r)取,直接上傳的 PDF 無索引比對→標題永遠空白;PDF 內建標題其實已抓進 pdf_meta 但未用。
- 修法:新增模組級 _direct_title(),PDF 內建標題與來源檔名字幹評分擇優(排版副檔名.indd、頁碼範圍891..913、數字多於字母者扣負分)。v1「內建優先」誤把 cd4a011d 標成垃圾「PAD120019352 891..913」,v2 評分版修正為「Public service performance and trust in government」。
- 重新著錄 16 張空標題卡,0 空白;兩顆釘子皆可辨識。服務已重啟,本機/外部 HTTPS 皆 200。
- 備份:arcus_core.py.bak_titlefb、.bak_titlev2。

---
## 2026-07-21 22:12

**主題**：讀論文工具書目欄救回（作者／年份／科別回退鏈）

**重點**：
- 根因：_ingest_one 在 card.pop 前把模型從標題頁抽出的 標題/作者/年份/科別 整批丟棄，只在有權威索引時可用；直接上傳的 PDF 兩頭落空，作者與年份永遠空白。
- 修法（arcus_core.py 三處）：新增 _salvage_biblio() 把模型書目欄正規化（作者／科別轉清單、年份查無留空）；meta 四欄改為「索引 → 模型抽取 →（標題再退檔名）」；建卡提示詞新增「科別」欄讓模型一併抽取。
- 分隔符修正：作者依提示詞以頓號分隔，西文逗號屬「姓, 名縮寫」不可當分隔，分隔集合由 [、,，;；/] 改為 [、；;／/]。
- 驗證：抽取原始碼單測 _salvage_biblio 四案全過；py_compile 通過；重啟 arcus active；本機 /arcus/ 200、外部 HTTPS 200。備份 arcus_core.py.bak_biblio。
- 未做（待授權）：對既有那兩篇論文卡（cd4a011d、197a4f9d）force 重建以回填作者／年份，因舊資料已丟無法救回，需重跑約兩次模型呼叫。

---
## 2026-07-21 22:22

**主題**：對最近上傳五篇論文強制重建，補回作者／年份／科別

**重點**：
- 承接上一條書目救回修正，對五篇直接上傳的論文以 ingest(force=True) 重跑，讓新回退鏈實際補上欄位。
- 五篇結果（皆 cached=False、無錯誤）：Increasing Role of Digital Technologies（Veiko Lember／2017／公共行政‧公共治理‧科技治理）；Blockchain governance（Tan‧Mahula‧Crompvoets／2022／公共行政‧公共管理‧資訊科學）；Translating between PA and the digital（十位作者／2026／公共行政‧數位治理‧資訊系統）；Public Service Performance and Trust（Van de Walle‧Bouckaert／2003／公共行政）；Comparing measures of citizen trust（Bouckaert‧Van de Walle／2003／公共行政‧公共管理）。
- 驗證：五篇 meta 與 index.json 三欄（作者／日期／科別）皆到位；索引空標題數 0、總卡數 18（沿用內容雜湊，不新增卡）。
- 小差異：Translating 那篇檔名寫 2025，模型讀標題頁著錄為 2026（線上早發或年份標示差異），非錯誤。

---
## 2026-07-21 22:59

**主題**：修正信封說明與實作不一致，消除 append 反覆踩坑

**重點**：
- 工具總說明(3295 行)原漏列 append、用 content|op 混寫，已補為 code/content/append/op 並拆清欄位、加「content 會整檔覆寫」提醒
- stage_new 錯誤訊息同步拆欄位
- 閘門(draft_validate_schema)新增：content/code 型別卻帶 op 鍵時，直接提示改用 kind=append
- 已 py_compile、重啟 arcus、本機與外部皆 200；實測誤用信封被擋且指向 append、正確 append 通過

---
