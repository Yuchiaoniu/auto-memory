# Claude Code Global Rules

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

## 中文寫作規則

中文輸出禁止句子以「的」結尾，改用完整謂語結構。

中文句子必須保留完整的主詞＋動詞＋受詞結構，不可縮略謂語。
錯誤示例：「梯度強度分不清」、「邊緣無法辨別」
正確示例：「無法分清楚梯度強度」、「無法辨別正確的邊緣」

子句同樣不可省略主詞，每個子句都要有自己的主詞。
錯誤示例：「才能確認裡面 frames 指哪一個」
正確示例：「才能確認函式裡面 frames 指哪一個」

提到程式碼名稱（函式、變數、類別等識別字）時，名稱原樣保留、不翻譯成中文，
但每個名稱第一次出現時，我要在名稱後面用括號補一句白話，說明這個名稱代表什麼。
範例：「我得先把 processVideo 這個函式從頭讀到尾，才能確認函式裡面 frames
這個變數代表整支影片的所有畫面（allFrames），還是只有卡片區那幾張畫面（cardFrames）。」

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

### 論文改寫句型規則（每次回覆嚴格遵守）

**規則一：避免「X 是 Y」短句串聯，改用長句形容詞結構**
將「X 是 Y」等號句型改寫為「以〔功能/關係描述〕修飾的〔主體〕，〔動詞片語〕」的長句，
把定義或性質變成形容詞修飾語嵌入句中。
- 反例：「DBH 是林業碳匯估算中最關鍵的單木測量指標。」
- 正例：「透過異速生長方程式可直接轉換為材積的 DBH，定義為距地面 1.3 公尺高度處的胸高樹幹直徑，
  可以是林業碳匯估算中關鍵的單木測量指標。」

**規則二：避免絕對陳述，改用適度語氣**
「最關鍵」→「關鍵」；「是…基礎」→「可以是…基礎」。
學術寫作應保留語氣空間，避免無來源支撐的絕對性主張。

**規則三：資訊排序以功能／機制優先，定義置後**
先說明概念的用途或計算機制，再給出定義，強調應用脈絡而非純粹名詞解釋。

**規則四：技術術語首次出現加英文對照**
重要技術術語第一次出現時，括號內附英文全稱或縮寫，
例如：胸徑（Diameter at Breast Height, DBH）。

**規則五：用詞規範**
- 全文使用「此專案」，不使用「本研究」
- 「閉環」一律改為「循環」

**規則六：長句一氣呵成，說明完畢後才條列**
每次回覆先用長句完整說明主要論點，整段說明盡量一氣呵成，
盡量避免斷斷續續、轉折語氣（但是、然而、不過等）和被動語態——
這三項不是絕對禁止，是盡量避免。完整說明結束後，才進行條列式補充。

**規則七：段落第一句為主句，後續子句以動詞開頭展開**
每一段的第一句必須是包含完整主謂賓結構的主句，這個主句要能概括整段含意，
讓讀者讀完第一句就掌握這段的核心論點。後續的附屬子句負責展開說明，
附屬子句盡量以動詞開頭，而不是以名詞或連接詞開頭。

## 自訂指令

### 「請存檔」指令

當使用者說「請存檔」時，立刻執行以下三個動作（全部用 PowerShell 以 UTF-8 帶 BOM 寫入）：

1. 把這次對話裡值得長期保存的查詢/對照資料併入當前專案的 `memory.md`（去重、更新，不刪仍有效的舊資料）。
2. 重寫當前專案的 `STATE.md`，只留「現況＋進行中＋下一步」，已完成或已搬進 memory.md 的舊資料一律剔除。
3. 確認當前專案路徑已寫進 `C:\Users\yuchi\.claude\last-active-project.txt`。

執行完畢後，回覆以下兩件事：
- 實際寫入的三個檔案完整路徑
- 說明下次開啟此專案時，系統會自動讀取哪些檔案（tasks.md、memory.md、STATE.md）

## 常用腳本指令

當使用者說「請開啟所有未完成的專案」或類似意思，執行：
```powershell
& "C:\Users\yuchi\open-projects.ps1"
```
此腳本會掃描 `C:\Users\yuchi\openspec\changes\` 下所有專案的 tasks.md，
對每個有 `[ ]` 未完成任務的專案，在同一個 Windows Terminal 視窗內以新分頁開啟 claude，
分頁標題與視窗內文字都會顯示專案名稱，並自動通過授權提示（--dangerously-skip-permissions）。

## 對話記憶機制

記憶系統與「壓縮前搶救」機制的完整白話說明，見
`C:\Users\yuchi\.claude\docs\memory-mechanism.md`（需要細節時再讀）。

規則（每次都要遵守）：
- 不要在記憶檔或對話裡使用「Last Session」這種自創英文標籤。
  一律改用白話中文描述，例如「上一次對話的進度」。

## 程式碼與 PPTX 寫入後自動審查

每次用 Write 或 Edit 寫入程式碼（.py/.js/.ts/.ps1/.go 等）或 PPTX 相關檔案後，
必須主動執行或驗證，確認以下三點無問題才回報完成：
1. **邏輯正確**：實際執行腳本、跑測試、或用工具驗證輸出，不只靠視覺檢查
2. **無殘留代碼**：舊版本片段、被取代的邏輯、遺留 TODO/placeholder 已清除
3. **版面正確**：縮排結構正確；PPTX 版面與格式整齊

若這次是多檔任務的一部分，可等所有相關檔案寫完後統一測試一次。

## 回覆原則

說明與敘述時避免使用代名詞，不寫「你怎樣怎樣」，直接描述事實或動作。

## 回答風格

- 預設只提供「一個最佳解法」，不要列一堆選項讓使用者挑。
  只有當選項之間真的有重大衝突、而且我無法替使用者判斷時，才提出選擇。
- 回答盡量簡要，先講結論與重點，細節需要時再展開。
