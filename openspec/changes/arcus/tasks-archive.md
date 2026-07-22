# 已完成任務封存

<!-- ===== 封存於 2026-07-19 11:16 ===== -->

## 0. 資料結構初始化
- [x] 0.1 建立 `DNA_weights.json` 基準格式（每條規則 ID → weight 0.5，附 meta 欄位：`gamma_base`, `gamma_entropy_threshold`, `gamma_slope`）（14:00）
- [x] 0.2 建立 `error_tensors.json` 初始空陣列，確認追加寫入不覆蓋歷史（14:00）
- [x] 0.3 讀取現行 routing_law.py，列出所有規則 ID（含 openspec_discuss / openspec_implement / arch_design 等），填入 DNA_weights.json 初始值（14:01）
- [x] 0.4 驗證 DNA_weights.json 可被 Python json.load() 讀取，所有 weight 值 ∈ [0.0, 1.0]（14:02）

## 1. Step 1：動態 DNA 空間投影（routing_law.py weight reader）
- [x] 1.1 在 routing_law.py module import 時讀取 DNA_weights.json，失敗時 fallback 為全部 0.5（14:05）
- [x] 1.2 實作序列化協議：weight < 0.3 → 不注入；0.3–0.7 → 正常注入；≥ 0.7 → 前綴加「[強制]」標記（14:06）
- [x] 1.3 在 `run()` 中，按序列化協議篩選規則清單，輸出規則優先序列表（文字，不是向量）（14:07）
- [x] 1.4 驗證：人工把某條規則 weight 設為 0.2，確認下輪該規則確實不出現在 prompt 中（14:08）
- [x] 1.5 驗證：weight 設 0.8 的規則，prompt 中出現「[強制]」前綴（14:09）

## 2. Step 2：幾何場景張量塌縮（場景地圖降維）
- [x] 2.1 在 before_prompt_hook() 中執行 locate（find）掃描，限定近 7 天有修改的路徑（14:12）
- [x] 2.2 按目錄深度與 mtime 加權，截取最多 40 條路徑（降維輸出精簡路徑清單）（14:13）
- [x] 2.3 把路徑清單序列化為純文字（每行一條），附加到 Step 1 的規則清單後（14:14）
- [x] 2.4 驗證：場景地圖在 prompt 中可讀，行數 ≤ 40（14:15）

## 3. Step 3：通用熵能阻尼器（γ 係數計算）
- [x] 3.1 實作語義資訊熵計算：對使用者輸入分詞，計算 Shannon entropy（14:18）
- [x] 3.2 熵值 > `gamma_entropy_threshold`（DNA_weights.json meta 欄位）時，計算 γ = gamma_base + entropy * gamma_slope（14:19）
- [x] 3.3 把 {熵值, γ} 記錄進本輪日誌（verbose_log.md 或 log-YYYY-MM-DD.md），供 baker 學習調整 γ 設定（14:20）
- [x] 3.4 γ 注入到 Step 4 的 prompt context（以 max_loops 上限的連續版本呈現）（14:21）

## 4. Step 4–5：量子式單發快門 + 順流流式釋放
- [x] 4.1 確認 before_prompt_hook() 把（Step1 規則清單 + Step2 路徑清單 + Step3 γ 參數）打包成單次 prompt（14:24）
- [x] 4.2 確認 Claude CLI 呼叫方式為非交互模式 `--print`，不允許多輪追問（14:25）
- [x] 4.3 驗證 stdout 100% 通透輸出（SSE stream），server.py 不攔截不過濾（14:26）

## 5. Step 6：非同步重力波觀測（Exit Code 軌跡向量）
- [x] 5.1 在 after_response_hook() 中捕捉 Claude CLI exit code（14:29）
- [x] 5.2 建立軌跡向量結構：`{exit_code, command_type, timestamp, session_id}`（14:30）
- [x] 5.3 把軌跡向量暫存到 after_response_hook() 的 context，供 Step 7 使用（14:31）

## 6. Step 7：跌倒偏差矩陣沈澱（error_tensors.json 寫入）
- [x] 6.1 在 scan() 中依違規類型計算偏差值 L：路徑錯誤 L=1.0、幻覺寫入 L=0.8、超時 L=0.5、警告型 L=0.3（14:34）
- [x] 6.2 把 `{L, 軌跡向量, 觸發規則 ID, timestamp}` 追加寫入 error_tensors.json（14:35）
- [x] 6.3 觸發規則 ID 必須對應 DNA_weights.json 的 key，讓 baker 能用 ID 索引更新 weight（14:36）
- [x] 6.4 驗證：人工觸發一次違規，確認 error_tensors.json 新增一筆記錄，格式正確（14:37）

## 7. Step 8：非同步空間拓撲補償（correction 欄位）
- [x] 7.1 在 scan() 偵測到路徑錯誤時，執行 find/grep 找出正確路徑（14:40）
- [x] 7.2 把正確路徑座標寫入該筆 error_tensors 記錄的 `correction` 欄位（14:41）
- [x] 7.3 建立計數器（counter.json 或 error_tensors.json meta）：新增 correction 記錄時 +1，達 5 次觸發 Step 9（14:42）
- [x] 7.4 驗證：correction 欄位存在且包含有效路徑字串（14:43）

## 8. Step 9–10：反向傳播基因反思 + 基因矩陣自我修正（weight_baker.py）
- [x] 8.1 建立 `weight_baker.py`，讀取 error_tensors.json，計算每條規則的命中次數與平均 L 值（14:46）
- [x] 8.2 實作 EMA 梯度調整：`new_weight = old_weight * 0.85 + hit_rate * 0.15`，同時根據高熵任務 L 調整 gamma_slope（14:47）
- [x] 8.3 對 correction 有效（correction 欄位非空）的規則，提升 weight；高 L 的規則降低 weight（14:48）
- [x] 8.4 Step 10：驗證所有 weight ∈ [0.1, 0.95]（clamp），無 NaN、無負值；通過後才覆寫 DNA_weights.json（14:49）
- [x] 8.5 封存 error_tensors.json 中 > 30 天的記錄到 error_tensors_archive.json（14:50）
- [x] 8.6 提供雙觸發機制：計數器達 5 次觸發 OR 深夜 Cron（先到先得，不重複執行）（14:51）

## 9. scan() 強化（來自 log 討論的缺口修補）
- [x] 9.1 新增偵測規則：「Write 工具被呼叫，但當輪 tasks.md 無新增 [ ] 條目」→ L=0.8 記入 error_tensors.json（14:54）
- [x] 9.2 把「好」「對」「可以」「沒問題」「那就」加入 `_OPENSPEC_IMPLEMENT_RE`（解決 log 討論記錄的授權語漏洞）（14:55）
- [x] 9.3 驗證 `_OPENSPEC_IMPLEMENT_RE` 的新 pattern 不誤觸非授權語境（14:56）
- [x] 9.4 補強「架構設計類問題強制 deep_research.py」法條的 regex，使技術選型討論必定觸發（14:57）

## 10. 整合驗證與基準快照
- [x] 10.1 把現行 server.py + kitchen_hooks.py + routing_law.py 複製進 `arcus/kitchen-snapshot/` 作為版控基準（15:00）
- [x] 10.2 完整端到端驗證：一輪對話中故意觸發違規 → 確認 error_tensors.json 有新記錄 → 手動執行 weight_baker.py → 確認 DNA_weights.json 更新（15:01）
- [x] 10.3 確認 routing_law.py 讀取更新後的 DNA_weights.json，規則注入行為隨 weight 變化（15:02）
- [x] 10.4 建立 hotfix 程序說明：routing_law.py 凍結後發現 bug 的處理流程（建票 → hotfix commit → 記錄 tasks.md）（15:03）

## 繪圖機制優化（2026-07-13）draw cmd
- [x] D.1 讀通 draw_docx_figure.py 介面：`--spec/--out` 產 SVG+PNG、`--verify` 回文字報告 exit0/3；五原語 rect/line/polygon/ellipse/text ＋ arc_arrow ＋ connect（具名 id 自動接方塊邊）
- [x] D.2 環境驗證：GCP python3 有 matplotlib/fontTools/python-docx，用現成規格跑通 verify＋產圖
- [x] D.3 arcus_core.py 加 `_arcus_draw()`：引擎路徑寫死在 dispatch 層，模型不必也無法自己 bash 找工具
- [x] D.4 紀律焊進工具：一律先 `--verify`，不通過回報告不產圖；通過才產圖；永不回傳 PNG 位元組、只回 URL
- [x] D.5 draw 掛進 `_arcus_do_dispatch`、補進 `_ARCUS_TOOL` enum 與說明（八 cmd → 九 cmd）
- [x] D.6 接線測試：import arcus_core 直接呼叫 `dispatch('draw')`，verify_only 與產圖兩路皆通、產出檔案存在
- [x] D.7 nginx 加 `location /vecfigs/` 靜態服務，繞過會掛的 Node app（順帶修好 learn-thesis 預覽圖）
- [x] D.8 arcus_workspace.md 補 draw cmd、繪圖規格速查（含 connect 用法）、切勿讀回 PNG 的紀律
- [x] D.9 端到端：透過 /arcus/api/chat 叫 arcus 自己畫 arcus_concept 向量圖，計回合、外部驗證 URL
- [x] D.10 更新預覽頁 fig_preview 指向新的向量概念圖

## arcus 內化為手腳（2026-07-13）身分改寫＋禁殘留反射
- [x] D.11 server.py 的 `--disallowedTools` 補上 `ToolSearch Skill`，殺掉每輪多餘反射（實測 `arcus_do` 仍可直接呼叫，不會斷手）
- [x] D.12 arcus_core.py 的 `build_system_prompt` 為 `project=='arcus'` 分岔出原生身分提示（你就是 arcus、唯一的手是 `arcus_do`、天生沒有別的工具、絕不向使用者盤點工具），其他專案的通用提示不動
- [x] D.13 外部 URL 實測（https://forest-carbon.duckdns.org/arcus/api/chat 叫 arcus 跑 map）：0 次 ToolSearch、免責聲明消失、只有單一 `arcus_do map` 呼叫、模式標籤保留；成本 0.38 美元、7.6 秒

## arcus 跟著打開的專案走（2026-07-13）多專案根路徑
- [x] D.14 server.py：env 加 `ARCUS_PROJECT_PATH`（arcus 專案傳 runtime 子資料夾、其餘傳專案資料夾），把當前專案根傳進 MCP 子程序
- [x] D.15 arcus_core.py `_arcus_runtime_dir()`：改先讀 `ARCUS_PROJECT_PATH`，讀不到才退回檔案自身資料夾，讓 read/query 跟著打開的專案走
- [x] D.16 arcus_core.py `map` 指令分兩種：根等於 arcus 自身 runtime → 回函式群地圖（自我維護）；否則 → 回該專案的 `generate_project_map` 檔案結構地圖
- [x] D.17 arcus_core.py `build_system_prompt`：拿掉 `if project == 'arcus'`，改無條件回原生身分提示，讓每個專案都認 arcus 為身分、免責聲明對所有專案消失
- [x] D.18 原生身分提示措辭校準：「runtime 目錄」改「當前專案資料夾」，避免提示誤導模型猜路徑
- [x] D.19 外部實測（公開網址用 auto-memory-sync 專案）：map 回 auto-memory 的檔案地圖、read 讀到它的 tasks.md、免責聲明零命中、只有兩次 arcus_do、模型自我更正「我在 auto-memory 不是 arcus」

## read／stage_new 改批次、鎖死一口氣（2026-07-14）停用單數退路
- [x] E.1 arcus_core `_arcus_do_dispatch` 的 read：改收 `paths=[...]` 一次讀完回 `files` 清單；傳單數 `path` 直接擋下回錯，停用單數退路（2026-07-14）
- [x] E.2 arcus_core `_arcus_do_dispatch` 的 stage_new：改收 `specs=[{basename,code},...]` 一次開好所有空白快取回 `caches` 清單；傳單支 basename/code 直接擋下，停用單數退路
- [x] E.3 系統提示指令清單（build_system_prompt）與 arcus_workspace.md 同步：read payload 標 `{paths:[...]}`、stage_new payload 標 `{specs:[...]}`，並註明不再收單數
- [x] E.4 分派層執行測試：批次讀 2 檔都有內容、單數讀被擋（訊息含「批次」）、批次開 2 支快取、單數開被擋、cleanup 刪 2；py_compile 通過
- [x] E.5 server.py 重啟、外部網址 200 健康確認；思考預算已歸零＋輸出上限 64000，一口氣讀改測寫的流水線就此焊進工具層

## 身分保留＋規則換本機子集＋修 f-string bug（2026-07-14）
- [x] E.6 發現嚴重 bug：`_arcus_system_prompt` 是 f-string，先前批次改動加的 `{paths}`/`{specs}` 大括號被當成替換欄位 → 每輪建提示 NameError（py_compile 沒抓到、外部 200 只驗到 nginx，沒驗到聊天）
- [x] E.7 修法：cmd 清單裡的大括號改雙括號（`{{paths:[...]}}`/`{{specs:[{{basename,code}},...]}}`），f-string 輸出字面 `{paths:[...]}`
- [x] E.8 身分保留、行為規則換成本機 CLAUDE.md 適用子集：留身分＋解剖構造＋沒有的東西＋模式標籤，砍掉舊寫作原則，換入白話寫作紀律（禁縮寫/不省謂語/不受詞前移/分層寫法/≤150字）與自檢驗證（先測假說、stage_run 跑斷言、沒測不說完成），改用 read/stage_run 措辭非 Bash
- [x] E.9 外部端到端驗證（公開網址叫 arcus 說身分＋讀三檔）：建提示不炸、回正常文字、模式標籤在、身分句在、模型自然講「用 paths 陣列一次帶三個檔」，單數反射消失

## 批次常態＋清 kitchen-snapshot（2026-07-14）
- [x] E.10 系統提示加「批次是常態，不是被擋才用」：read 的 paths、stage_new 的 specs 一律當陣列填，只動一個檔也寫成單一元素陣列，一開始就走陣列、省掉單數被擋那一次來回；建提示驗證通過、重啟後外部頁面 200
- [x] E.11 刪除 GCP 專案資料夾殘留的 kitchen-snapshot/（32M），與先前本機 repo＋GitHub 的清理對齊；確認刪除後不存在

## 把 explorer 技能真的還給 arcus（2026-07-14）
- [x] E.12 查出矛盾：先前只把 Skill 從 --disallowedTools 拿掉，但提示層第 1338 行仍寫「你沒有 Skill、絕不呼叫」，且 --print 非互動下未列入 --allowedTools 的工具會被擋 → 技能實際叫不動
- [x] E.13 順帶查出：build_system_prompt 第 1362 行就 return _arcus_system_prompt，底下整段舊通用提示（tasks/memory/STATE 三檔紀律）全是死碼，永不執行；確認生效提示只有 _arcus_system_prompt 33 行
- [x] E.14 三處放行（其餘不動）：server.py --allowedTools 加 Skill；提示層「你沒有」段拿掉 Skill 並 carve 例外；探索模式段明講「呼叫 Skill(openspec-explore) 啟動探索技能」
- [x] E.15 確認 arcus_settings.json 的 permissions.deny 未含 Skill、GCP 上 openspec-explore/SKILL.md 存在
- [x] E.16 外部端到端強迫測試：明確要 arcus 真的叫技能 → token_log 最後一輪 tools=['Skill']、回應自證「探索技能已經真的用起來」，確認叫得動；一般討論輪它仍可選擇直接討論、不強制每輪叫

## 提示詞整併清理（2026-07-14）
- [x] E.17 盤點 arcus 全部提示詞散落點：身分提示(_arcus_system_prompt)、每輪注入(ARCUS_ARCHITECTURE)、集中工作區(arcus_workspace.md)、判官提示(turn_review)、死碼(build_system_prompt 舊通用提示)
- [x] E.18 刪死碼：build_system_prompt 1364 行 return 之後 108 行永不可達的舊通用提示（含 tasks/STATE 三檔紀律、read_pdf/deep_research 腳本指令、與身分提示矛盾的「你是專案X對話助理」），py_compile＋建提示＋重啟＋外部驗證全通
- [x] E.19 刷新 ARCUS_ARCHITECTURE：拿掉過時的「注入 STATE.md/tasks.md」（§78 打底瘦身已停注）與 scan/bake/反向傳播考古字句，改寫為現況（arcus_do 九指令分派、每輪注入 arcus_workspace.md），重啟＋外部驗證通過

### 第一段：每輪都把名詞收進收件匣
- [x] F.1 新增 `_memory_capture_turn(project_path, user_msg, response_text)`：
- [x] F.2 卡片以機器區塊追加寫進各專案 memory.md 檔尾（收件匣），不寫進索引
- [x] F.3 保留 `_memory_cheap_gate` 長度門檻，擋掉寒暄短句
- [x] F.4 `after_response_hook` 改呼叫 `_memory_capture_turn`，
- [x] F.5 收料改為同步或有 join 的執行緒，不再用 `daemon=True` 讓主行程結束時被無聲砍掉

### 第二段：每 6 小時整理一次，把科別收斂
- [x] G.1 在 core 加入專案根目錄常數（core 目前沒有 server.py 那個 `CHANGES` 的對應物）　→ 免做：core 第 49 行早已有 CHANGES 常數
- [x] G.2 新增 `_memory_archive_daily()`：一次讀進整個收件匣，
- [x] G.3 同名卡合併時保留較完整的解釋；整份索引只寫一次，不再每張卡重寫
- [x] G.4 歸檔成功後清空收件匣，並把這次的歸檔時間戳寫進索引裡底線開頭的保留鍵
- [x] G.5 新增 `_memory_should_archive()`：讀保留鍵判斷「距上次歸檔是否已超過 6 小時」
- [x] G.6 用 `O_CREAT|O_EXCL` 佔位檔當鎖，搶不到就跳過；結束刪除鎖檔
- [x] G.7 新增 `start_memory_scheduler(interval_hours=6)`：`while True: check(); sleep(600)` 輪詢，
- [x] G.8 `list_subjects` 與 `recall` 過濾底線開頭的保留鍵，避免被當成抽屜列出來

### 第三段：回覆前自動把相關卡片塞進提示
- [x] H.1 新增 `_memory_keyword_hits(user_msg)`：建立「卡片標題 → 抽屜」對照表，
- [x] H.2 在 `before_prompt_hook` 注入命中的卡片，全程不經模型判斷

### 第四段：讓作品卡真的被產生出來
- [x] I.1 `cmd=draw` 完成時開作品卡（標題、網址、路徑當下都齊全）
- [x] I.2 `cmd=promote` 完成時開作品卡（標題取落地檔名、路徑取落地位置，

### 第五段：實際跑過確認沒壞
- [x] J.1 實測連續三輪對話，確認每輪都有卡片進收件匣（不再是四輪一次）
- [x] J.2 手動觸發一次歸檔，確認抽屜有收斂、收件匣被清空、索引只寫一次
- [x] J.3 兩個行程同時觸發歸檔，確認鎖生效、資料沒有被覆蓋掉
- [x] J.4 重啟常駐服務並把時間戳往前調超過 6 小時，確認重啟後會自動補做這一批歸檔
- [x] J.5 確認 `list_subjects` 沒有把保留鍵當成抽屜列出來

### 第一段：把 PDF 變成帶鍵的段落
- [x] L.1 新增 runtime/paper_cards.py 模組
- [x] L.2 來源支援網址與虛擬機路徑，一律回傳位元組內容
- [x] L.3 用 PyMuPDF 抽出非空白區塊（虛擬環境已安裝 PyMuPDF 1.28.0）
- [x] L.4 碎塊合併至約 1000 字元一段，鍵取起始頁加頁內序號並重新編號
- [x] L.5 整份文字定義為各段用固定接合字串串起，無損靠定義成立
- [x] L.6 切段全文寫進 text.json，附接合字串與整份雜湊值

### 第二段：萃取六欄卡片
- [x] M.1 組出「每段前面掛鍵」的提示詞
- [x] M.2 借用 _call_model 開一次性行程，模型指定 opus、上限 600 秒
- [x] M.3 解析模型回傳的 JSON，容忍前後多餘文字
- [x] M.4 程式回查出處鍵，查不到就標記出處存疑並留下 bad_refs
- [x] M.5 寫入 meta.json 與 card.json，更新 index.json 總表
- [x] M.6 檔案內容雜湊當識別碼，重複收同一篇直接命中快取

### 第三段：接進 arcus 指令
- [x] N.1 paper_ingest：批次收論文
- [x] N.2 paper_cards：批次取卡片，只給欄位就跨論文比較同一欄
- [x] N.3 paper_quote：點名取原文段落核對出處
- [x] N.4 paper_list：總表；paper_verify：還原比對雜湊值
- [x] N.5 抽取套件延後匯入，不拖慢臨時 MCP 行程

### 第四段：實跑確認
- [x] O.1 虛擬機自行下載測試論文，抽段與無損還原驗證通過
- [x] O.2 實際呼叫 Opus 萃取六欄，出處存疑 0 欄
- [x] O.3 快取命中、點名取原文、跨論文取單欄全部驗證通過
- [x] O.4 重啟服務後從全新行程驗證四個指令分派正確
- [x] O.5 外部公開網址回傳 200

<!-- ===== 封存於 2026-07-19 11:26 ===== -->

## 廢除現況快照檔與待辦封存（2026-07-19）
- [x] Q.1 清點 29 份現況快照檔，整份備份到 backup/state_retire_20260719
- [x] Q.2 逐份附加進各專案記憶檔，回查特徵字串確認寫入成功才刪原檔
- [x] Q.3 server.py 專案清單不再讀現況快照檔，欄位留空供舊前端相容
- [x] Q.4 status.sh 改看待辦封存檔
- [x] Q.5 arcus_core.py 新增只搬已勾項目的待辦封存，沿用 log_task.py 那把 flock 鎖
- [x] Q.6 空章節標頭反覆掃到穩定後一併移除
- [x] Q.7 接進記憶卡片排程迴圈，先問一次再依序做兩件事
- [x] Q.8 write_state.py 退役改名，close_round.py 快照步驟改為跳過
- [x] Q.9 假專案驗證 14 項全過
- [x] Q.10 真實資料搬走 1,592 條已勾項目，441 條未勾完整保留
- [x] Q.11 外部公開網址驗證回傳 200，快照欄位全空

<!-- ===== 封存於 2026-07-19 11:38 ===== -->

## §88 讀寫柵欄分家（2026-07-19）
- [x] R.1 新增 _arcus_read_path，讀取上限放寬到 openspec/changes 全體專案
- [x] R.2 讀取端（read、query）改用新函式，寫入端六個呼叫點維持 _arcus_safe_path
- [x] R.3 確認家目錄其他位置（憑證、金鑰、/etc）讀不到
- [x] R.4 專案地圖副檔名白名單改黑名單，只擋二進位雜訊
- [x] R.5 18 項測試通過，服務重啟後外部 HTTPS 200

<!-- ===== 封存於 2026-07-19 18:38 ===== -->

## §89 歸檔改三段式，慢的模型呼叫不再佔住鎖 (2026-07-19)
- [x] S.1 佔用標記加入持有者存活檢查：讀出行程編號後用 `os.kill(pid, 0)`，
- [x] S.2 新增成品區 `_memory_spool`，收料落地與併入索引分離
- [x] S.3 歸檔拆成三段：收料（短鎖）→ 模型分批收斂（不佔鎖）→ 併入索引（短鎖），
- [x] S.4 模型呼叫改分批，每批上限 50 張，逾時放寬到 600 秒
- [x] S.5 收料時為每張卡片補上來源專案名稱（`c.setdefault('project', nm)`）
- [x] S.6 假模型測試 20 項全數通過（分批 50/50/20、模型失效保全、下一輪補回、鎖的死活判斷）
- [x] S.7 重啟 arcus 並從外部網址驗證：`/arcus/` 回 200、`/arcus/api/projects` 回 200
- [x] S.8 真實資料實跑：取走 35 張、1 批、96.5 秒，索引名詞 198 → 217（淨增 19），

## §90 工具全部併入引擎本體，移除臨時修補後門 (2026-07-19)
- [x] T.1 移除 patch_text 臨時分支（46 行），並在姿態檔寫入「絕不自創臨時工具」的禁令
- [x] T.2 三支外部工具併入 arcus_core.py：上網搜尋 816 行、畫圖 1068 行、論文抽取 322 行
- [x] T.3 補齊缺失套件：beautifulsoup4、python-docx、matplotlib、fonttools
- [x] T.4 呼叫端改為同行程呼叫，移除三處 sys.path 借用外部路徑的寫法
- [x] T.5 論文快取區由 ~/.claude/cache/papers 搬回 runtime/_papers
- [x] T.6 新增 publish 指令：把檔案送上公開網頁並回傳可開啟的網址
- [x] T.7 工具清單補齊——先前 enum 只列十個指令，論文相關五個指令雖已接上分派點卻從未被揭露，
- [x] T.8 姿態檔補上新能力，並寫明這些能力是引擎本體的一部分、不是外借工具
- [x] T.9 三支原檔退場到 backup/retired_tools_20260719
- [x] T.10 實測五項能力全通過：畫圖產圖、讀 pdf、發佈網頁、上網抓文、論文清單
- [x] T.11 重啟後從外部網址驗證四個端點皆回 200

<!-- ===== 封存於 2026-07-20 12:48 ===== -->

## §91 論文卡片改造：權威索引庫連接器 + meta 逐字化 (2026-07-20)
- [x] U.1 新增 arXiv 轉接器與 `_journal_lookup`，統一著錄介面，查無或無全文回 None
- [x] U.2 改寫 `_ingest_one` 的 meta 組裝：作者/科別/日期改由著錄逐字填入，棄用 pdf 內部中繼資料
- [x] U.3 加建卡守門：`_journal_lookup` 回 None 或下載失敗一律不建卡（岔路甲留白）
- [x] U.4 `paper_ingest` 加 source 參數，可吃查詢字或論文 id，接上分派點與工具清單 enum
- [x] U.5 姿態檔補一句：科別/作者來自索引庫權威著錄、逐字，非 pdf 內部中繼資料
- [x] U.6 實測晶格／格論一篇（預期命中、科別逐字）
- [x] U.7 實測公共行政系統理論一篇（預期不在 arXiv 則正確觸發留白）
- [x] U.8 py_compile 通過、arcus 重啟、外部端點驗證回 200

<!-- ===== 封存於 2026-07-20 18:52 ===== -->

## §92 網頁抓取型別感知 + 授權層（已完成）
- [x] W.1 抓取函式改為型別感知：JSON/純文字/XML 逐字回傳，HTML 才走去雜訊
- [x] W.2 機器格式超長時明講截斷（原始長度/顯示長度），不靜默丟資料
- [x] W.3 HTML 無正文容器時退回原始文字，不再整份回空
- [x] W.4 新增 _web_auth_headers：依主機查授權標頭，權杖只放 gitignore 憑證檔
- [x] W.5 建立 .web_creds.json（權限 600）並加入 .gitignore，登記 api.apify.com
- [x] W.6 功能測試：Apify 介面逐字回並解析出 5 個 Actor；example.com 對照仍去雜訊
- [x] W.7 服務重啟 active，外部端點 /arcus/ 與 /arcus/api/projects 皆回 200
- [x] R.1 定位真正根因：--print 模式工具清單快照早於 MCP 連上，思考歸零移除了原本的緩衝
- [x] R.2 以 importtime 證實 requests/bs4 佔模組冷啟約 200 毫秒；以 init 事件與 tools_changed 佐證競賽
- [x] R.3 requests/bs4 改延遲載入（_ensure_web_libs），冷啟由約 243 毫秒降到約 93 毫秒
- [x] R.4 複本先測 16/16 第一輪就位，通過才套用正式檔，備份 arcus_core.py.bak_lazyweb
- [x] R.5 正式設定檔 16/16 第一輪就位；服務 active；外部網址端到端工具呼叫成功、無失敗字樣

<!-- ===== 封存於 2026-07-21 19:28 ===== -->

## §90 工具全部併入引擎本體，移除臨時修補後門 (2026-07-19)
- [x] 信封說明對齊實作：工具總說明補回 append、拆清 content/op 欄位、追加不覆寫提醒；stage_new 錯誤訊息同步；閘門偵測 content 型別誤帶 op 鍵時指路 append（2026-07-21 22:59）
