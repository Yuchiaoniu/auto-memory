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

## Subagent Isolation Policy

Use the Agent tool (subagent_type: Explore, model: haiku) instead of
direct tools when searching across more than 3 files or when expected
results exceed ~100 lines. Direct Read is fine for a single known path.

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

## 回答風格

- 預設只提供「一個最佳解法」，不要列一堆選項讓使用者挑。
  只有當選項之間真的有重大衝突、而且我無法替使用者判斷時，才提出選擇。
- 回答盡量簡要，先講結論與重點，細節需要時再展開。
