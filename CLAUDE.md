# Claude Code Global Rules

## 自檢與驗證規則（最高優先，嚴格執行，無例外）

每次對話開始前，必須讀取並遵守 `~/.claude/rules/self-check.md` 的完整內容。
該檔案是自檢規則的唯一來源，包含：搜尋三層查驗原則、探索模式測試要求、實作前後驗證規範、VM 部署外部驗證要求。

## Subagent Model Policy

When spawning subagents via the Agent tool, follow this strictly:

- **Haiku**: search, file reading, grep, simple lookups
- **Sonnet**: everything else — including complex architecture,
  multi-file refactoring, and design decisions
- **Opus**: NEVER, unless the user explicitly requests it in that turn

Rationale: Sonnet 4.6 is sufficient for all routine tasks in this
workflow. Opus is 5x more expensive per output token with marginal
quality gain for well-specified tasks.

## Context 節省原則（避免無謂 token 消耗）

大檔案和遠端腳本是最常見的 context 殺手，每次操作前先問自己「我真的需要整份內容嗎？」。

**讀檔：只取需要的部分，不讀整份**
- 要了解檔案結構 → 用 `grep -n '關鍵字'` 找到行號再讀那幾行，不用 `sed -n '1,800p'` 把全文倒進來。
- 要確認某個欄位存不存在 → `grep -c 'pattern'` 或 `grep -m3` 取前幾筆，不讀整份 JSON。
- 非得看某段落 → `sed -n 'START,ENDp'`，範圍控制在 30–50 行以內；分三次讀 300 行等於讀完整檔，毫無意義。

**遠端腳本回傳：只輸出關鍵數值，不 dump 整個物件**
- SSH 執行 Node.js / Python 腳本時，`console.log` 只印出要驗證的欄位名稱與數值，不印 `JSON.stringify(wholeObject)`。
- `curl | grep` 優於 `curl` 把整頁 HTML 倒進 context 再讓 Claude 解析。

**寫入大檔：Write 工具會把整份內容存進 context，能省則省**
- 超過 150 行的檔案，先問自己能否用 Edit（只傳 diff）取代 Write（傳整份）。
- 若必須用 Write，寫完後不要再用 Read 驗證——Edit/Write 失敗會報錯，成功就是成功。

**數字門檻（違反時需有明確理由）**
- 單次 SSH 腳本回傳 > 50 行 → 改用 grep 或只印摘要。
- 單次 sed 範圍 > 60 行 → 先 grep 確認目標行號再縮範圍。
- Write 整份檔案 > 200 行 → 優先考慮 Edit；若是全新檔案則可以，但寫完就停，不要再 Read 回來。

## Subagent Isolation Policy

Use the Agent tool (subagent_type: Explore, model: haiku) for retrieval tasks:
- Any Glob or Grep that doesn't target a single known path
- Read when the target file is not a single known path, or expected content exceeds ~50 lines
- Any multi-file exploration or open-ended codebase search
- Any PowerShell / SSH / gcloud command whose output exceeds ~10 lines or is purely
  informational (e.g. `instances list`, `ss -tlnp`, `ls`, `cat` on a remote file)

Keep in the main session (never delegate):
- Analysis, diagnosis, and judgment — including interpreting SSH output,
  log analysis, and any decision-making based on retrieved data
- Single known-path Read where only a short section is needed
- All Write / Edit operations
- PowerShell commands that mutate state (e.g. start/stop VM, write file, deploy)

Subagents must return only a summary — never paste raw tool output back
into the main session.

## 回覆原則與寫作規則

中文輸出禁止句子以「的」結尾，改用完整謂語結構。

中文句子必須保留完整的主詞＋動詞＋受詞結構，不可縮略謂語。
錯誤示例：「梯度強度分不清」、「邊緣無法辨別」
正確示例：「無法分清楚梯度強度」、「無法辨別正確的邊緣」

數字/資料值作受詞時同樣禁止話題化（受詞前移）：
錯誤示例：「14 GB 用掉」、「15 GB 剩餘」
正確示例：「已經用掉 14 GB」、「還剩 15 GB」

子句同樣不可省略主詞，每個子句都要有自己的主詞。
錯誤示例：「才能確認裡面 frames 指哪一個」
正確示例：「才能確認函式裡面 frames 指哪一個」

純中文敘述句中，工具或指令名稱（Read、WebFetch、Bash、Edit 等）禁止直接作主詞或受詞。
必須先用白話中文描述功能，原始名稱以括號補充。
錯誤示例：「這個 Read 要不要委派」「WebFetch 會發出請求」
正確示例：「要不要委派這個讀取動作（Read）」「網頁抓取工具（WebFetch）會發出請求」

提到程式碼名稱（函式、變數、類別等識別字）時，名稱原樣保留、不翻譯成中文，
但每個名稱第一次出現時，我要在名稱後面用括號補一句白話，說明這個名稱代表什麼。
範例：「我得先把 processVideo 這個函式從頭讀到尾，才能確認函式裡面 frames
這個變數代表整支影片的所有畫面（allFrames），還是只有卡片區那幾張畫面（cardFrames）。」

對話中禁止使用任何英文縮寫、中文縮寫、自創術語、省略詞語或省略語法，一律使用完整白話文。
不說「RQ」，說「研究目的」；不說「DSR」，說「設計科學研究法」；不說「CF」，說「修正因子」；不說「LMM」，說「線性混合效應模型」。
技術量測指標（如 MAPE、MAE、DBH 等）第一次出現時，以白話全稱加括號補充縮寫（例如「平均絕對百分比誤差（MAPE）」），後續同樣使用白話全稱，不單獨使用縮寫形式。

講技術判斷或操作步驟時，用「分層」寫法，兼顧好懂與精簡：
- 主句只講「結論＋接下來要怎麼辦」，全白話、不夾術語，並把「怎麼辦」提到最前面。
- 技術細節（欄位名、機制原理、章節編號、雜湊值/ID 等長代號）縮進括號補一句，
  給想深究的人看；不想看的人略過也不影響理解。
- 主句不要塞長代號（例如一長串雜湊值），長代號一律降級到括號當「查得到就好」的細節。
範例：
主句「同一支影片重新上傳不會觸發新的處理流程，系統會當成已處理過直接擋掉。
想讓它真的重跑一次，只能先刪掉舊紀錄再重新上傳。」
括號「（技術細節：影片靠 video_hash 這個不可重複的欄位辨識，雜湊相同就被去重擋下；
要刪的是樹表裡 7cf542e6... 那一列。）」

**回覆風格**
- 說明與敘述時避免使用代名詞，不寫「你怎樣怎樣」，直接描述事實或動作。
- 預設只提供一個最佳解法，不列選項讓使用者挑；只有選項之間有重大衝突且無法代為判斷時才提出選擇。
- 回答簡要，先講結論與重點，細節需要時再展開。
- 每個說明點不超過 150 字；超過時拆成兩點，不得合併堆疊。
- 問句必須保留完整動詞結構；禁止截斷式問法。錯誤：「X 能用嗎」。正確：「能使用 X 嗎」「是否能執行 X」。
- 單字動詞禁止縮略，必須使用完整形式。錯誤：「加子代理」「改設定」「刪舊版」。正確：「加入子代理」「修改設定」「刪除舊版」。
- **對話語言禁止使用任何縮寫或代號**：包含英文縮寫、中文縮寫、自創流水號、內部代號、省略詞語、省略語法，一律改用完整白話文。程式碼變數名稱（T0、T2、P11、P56 等）、學術縮寫（RQ、DSR、CF、LMM 等）、任何需要解讀才能理解的詞，全部用白話取代。向使用者描述操作對象時，一律使用白話：「論文第四章的三棵樣本展示表格」「4.2 節開頭的段落」「修正因子（乘法係數 ×1.10）」等。

### 論文改寫句型規則

只要這次對話提到 **thesis-rewrite / 論文改寫 / 論文段落 / 學術寫作** 這類關鍵字，
就先讀 `~/.claude/docs/thesis-writing-rules.md` 再回答。

## 自訂指令

### 「請存檔」指令

當使用者說「請存檔」時，立刻執行以下三個動作（全部用 PowerShell 以 UTF-8 帶 BOM 寫入）：

1. 把這次對話裡值得長期保存的查詢/對照資料併入當前專案的 `memory.md`（去重、更新，不刪仍有效的舊資料）。
2. 重寫當前專案的 `STATE.md`，只留「現況＋進行中＋下一步」，已完成或已搬進 memory.md 的舊資料一律剔除。
3. 確認當前專案路徑已寫進 `~/.claude/last-active-project.txt`。

執行完畢後，回覆以下兩件事：
- 實際寫入的三個檔案完整路徑
- 說明下次開啟此專案時，系統會自動讀取哪些檔案（tasks.md、memory.md、STATE.md）

## 主動對話記錄機制（無需使用者指令，嚴格執行）

**每一次回覆結束前，只要這輪對話有實質內容（不是單純打招呼或一問一答），
必須主動把摘要追加寫進當前專案自己的 `log.md`，不需要使用者說任何指令。**

### log.md 路徑判斷規則

每個專案的 CLAUDE.md 裡都會有一行宣告：
```
本專案 log.md 路徑：<完整絕對路徑>
```
從已載入的所有 CLAUDE.md 中找到這行宣告，就把摘要寫進那個路徑。
若當前對話沒有任何 CLAUDE.md 宣告 log.md 路徑，則略過（不猜測路徑）。

### log.md 寫入格式

```
## YYYY-MM-DD HH:MM

**主題**：這輪討論的核心話題（一句話）

**重點**：
- 決策或結論 1
- 決策或結論 2
- （未解決的問題或下一步）

---
```

### 維護規則

- log.md 只保留最近 20 條。
- 超過 20 條時，把最舊的幾條搬進同一專案的 `STATE.md`（附加到最底部），再從 log.md 刪除。
- 每條記錄必須有日期時間戳記與主題，讓未來的 Claude 一眼就能找到脈絡。

## 常用腳本指令

當使用者說「請開啟所有未完成的專案」或類似意思，執行：
```powershell
& "~/.claude/tools/open-projects.ps1"
```
此腳本會掃描 `~/.claude/openspec/changes/` 下所有專案的 tasks.md，
對每個有 `[ ]` 未完成任務的專案，在同一個 Windows Terminal 視窗內以新分頁開啟 claude，
分頁標題與視窗內文字都會顯示專案名稱，並自動通過授權提示（--dangerously-skip-permissions）。

## 對話記憶機制

記憶系統與「壓縮前搶救」機制的完整白話說明，見
`~/.claude/docs/memory-mechanism.md`（需要細節時再讀）。

規則（每次都要遵守）：
- 不要在記憶檔或對話裡使用「Last Session」這種自創英文標籤。
  一律改用白話中文描述，例如「上一次對話的進度」。

## PDF 讀取規則

只要這次對話需要讀取或分析 `.pdf` 檔案，一律先用 Bash 執行預處理腳本，
不得直接用讀取工具（Read tool）讀取 PDF：

```powershell
python ~/.claude/tools/read_pdf.py "<PDF路徑>" [--pages 1-5]
```

- `--mode auto`（預設）：自動偵測文字型或掃描型
- `--mode ocr`：強制走 OCR（需已安裝 Tesseract）
- `--pages 1-5`：只處理指定頁碼範圍，避免大 PDF 吃掉過多 context

腳本會輸出乾淨的 Markdown 文字到 stdout，再對該文字進行分析。
掃描型 PDF 需要另外安裝 Tesseract OCR：https://github.com/UB-Mannheim/tesseract/wiki

## GitHub Pages 部署位置規則

部署靜態網站到 GitHub Pages 時，預設使用 **main 分支根目錄**，不使用 docs 資料夾或其他分支。
若有特殊原因需要偏離預設（例如 repo 根目錄有非網站內容），必須先說明原因並與使用者討論確認，不得自行決定。

## GCP Kitchen 工作流程（嚴格執行）

對話涉及任何 openspec 專案的實作、分析、或查詢時，
一律透過 GCP kitchen 引擎處理，禁止在本機直接生成專案內容：

```bash
python ~/.claude/tools/gcp_ops.py chat <專案名稱> "<訊息>"
```

完成後讀回最新一輪結果：

```bash
python ~/.claude/tools/gcp_ops.py log <專案名稱> 1
```

## Project Kitchen 網頁啟動

單視窗多專案管理介面，整合畢業專題金字塔框架。啟動指令：

```powershell
& "~/.claude/tools/project-kitchen/start.ps1"
```

啟動後自動開啟 http://localhost:7799，功能：
- 三個爐子（最多同時三個專案）
- 從冷凍庫拖曳專案放入爐子
- 點開爐子展開金字塔 + 對話區，和 Claude 探討可行路徑
- 決策後點「啟動實作」觸發子進程

## 子進程多專案管理

當使用者要求在背景處理另一個專案的任務，或想同時推進多個專案，使用子進程模式。

**查看所有專案狀態：**
```powershell
& "~/.claude/tools/project-dashboard.ps1"
# 只看有待辦的專案：
& "~/.claude/tools/project-dashboard.ps1" -PendingOnly
```

**啟動子進程（同步，等待完成）：**
```powershell
& "~/.claude/tools/spawn-project.ps1" -ProjectName "<專案名稱>" -Task "<任務描述>"
```

**啟動子進程（非同步，背景執行，不卡主視窗）：**
```powershell
& "~/.claude/tools/spawn-project.ps1" -ProjectName "<專案名稱>" -Task "<任務描述>" -Async
```

選擇時機：
- 同步：任務小且想馬上看到結果，或任務之間有依賴
- 非同步：想繼續當前工作、不想等待，子進程完成後 STATE.md 自動更新

子進程完成後，Stop hook 會自動更新目標專案的 STATE.md。
可用 project-dashboard.ps1 確認最新狀態。

## OpenSpec 模式切換（嚴格執行，無例外）

**預設一律使用探索模式**
無論話題大小，只要對話中**沒有**出現「請實作」「實作」「開始做」「好」「可以」「做吧」等明確授權語，
一律立即呼叫 Skill(openspec-explore) 並在回覆第一句標示 `【探索模式】`。

探索模式下同樣嚴格遵守所有回覆規則（中文句式結構、禁止話題化、工具名稱括號補充、分層寫法等）。

**收到明確授權語後：提案＋實作模式**
任何檔案寫入前，依規模決定流程：

- **建立新 openspec change**：使用者明確說「建立新專案／新變更」，或變更跨多個系統且需要設計文件記錄架構決策
- **直接追加到當前專案 tasks.md 並實作**：對現有專案的小幅修改（CLAUDE.md 規則調整、settings.json 單一設定、ps1 腳本修正等），不建新 change，直接在當前專案的 tasks.md 新增任務、勾選完成

建立新 openspec change 時：先呼叫 Skill(openspec-propose) 標示 `【提案模式】`，完成後直接呼叫 Skill(opsx:apply) 標示 `【實作模式】`，不等使用者確認。

**其他專案同理**：不在主要專案內另外建立子專案，除非使用者明確要求。

**子代理呼叫 explore skill 規則（嚴格執行）**
凡是為了「分析、探索、META 優化」等目的生成子代理，
子代理的 prompt 裡**必須明確寫出 `請呼叫 Skill(openspec-explore)`**。
禁止用 prompt 語氣（例如「請用 explorer 方式分析」「以探索模式觀察」）來代替真正的 skill 呼叫。
用語氣模仿探索姿態 ≠ 呼叫 skill，兩者不可混用。

違反案例（禁止）：
```
Agent(sonnet, prompt="請用 explorer 方式回答 Q1~Q6...")
```
正確做法：
```
Agent(sonnet, prompt="請呼叫 Skill(openspec-explore)，以下列資料進行探索分析...
  輸出格式：提出的問題 / 每個問題的選項 / 選擇的選項與理由")
```

**explore 模式在壓縮後的接續規則**
對話被壓縮後重新啟動時，explore 模式規則同樣從第一個回應就生效。
壓縮不等於授權，不可因為「剛壓縮完、在接續任務」就跳過 `Skill(openspec-explore)` 的呼叫。

**工作流程變更歸屬規則**
任何對 Claude 工作流程的新功能或改進（含 CLAUDE.md、settings.json、hooks、
記憶機制、部署規則、自檢規範等）的 propose，
一律建在 auto-memory-sync 專案底下，不建立新專案。
