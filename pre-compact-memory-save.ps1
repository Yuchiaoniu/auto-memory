# pre-compact-memory-save.ps1
# 觸發時機：Stop（每一輪對話結束），在 settings.json 設為 async（背景跑、不卡使用者）。
# 角色：安全網。萬一使用者沒先請我手動存就 clear，這支腳本至少已自動把現況存下。
#
# 三檔分工（使用者定）：
#   tasks.md  ：主要進度（任務清單），本程式不碰。
#   memory.md ：查詢/對照(mapping)資料的長期保存區（IP、地址、餘額、設定值、指令輸出、
#               固定路徑、決策結論等）。只增與修正、去重，不刪仍有效的資料。
#   STATE.md  ：短期現況快照（目前做到哪、手上在處理什麼、下一步）。已完成或已搬進
#               memory.md 的舊資料要從這裡剔除，保持精簡。
#
# 規則全域共用一份放 CLAUDE.md（手動維護，本程式不碰）；記憶各專案各自一份（本程式維護）。
# 不在專案資料夾（沒有 tasks.md）時直接跳過，連 Haiku 都不呼叫。
#
# -Force 可繞過「token 成長 20K 才存」的門檻（例如 /clear 前手動存一次）。
# 測試用環境變數：MEMSYNC_CWD / MEMSYNC_TRANSCRIPT / MEMSYNC_NO_THROTTLE
param([switch]$Force)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ---- 1. 取得「目前專案資料夾」cwd（優先讀 Stop hook 的 stdin JSON）----
$cwd = $null
try {
    if ([Console]::IsInputRedirected) {
        $raw = [Console]::In.ReadToEnd()
        if ($raw) { $cwd = ($raw | ConvertFrom-Json).cwd }
    }
} catch {}
if ($env:MEMSYNC_CWD) { $cwd = $env:MEMSYNC_CWD }
if (-not $cwd) { $cwd = (Get-Location).Path }

# 決定專案資料夾：先看 cwd 有沒有 tasks.md；沒有就改讀 last-active-project.txt 指到的專案
# （在 C:\Users\yuchi 啟動、再用對話選專案時，cwd 不是專案資料夾，靠指標檔定位）
$projectDir = $cwd
if (-not (Test-Path (Join-Path $projectDir "tasks.md"))) {
    $pointer = "C:\Users\yuchi\.claude\last-active-project.txt"
    if (Test-Path $pointer) {
        try {
            $p = (Get-Content $pointer -Raw -Encoding UTF8).Trim()
            if ($p -and (Test-Path (Join-Path $p "tasks.md"))) { $projectDir = $p }
        } catch {}
    }
}
# 仍找不到含 tasks.md 的專案資料夾就結束（也省 Haiku 錢）
$tasksPath = Join-Path $projectDir "tasks.md"
if (-not (Test-Path $tasksPath)) { exit 0 }
$statePath  = Join-Path $projectDir "STATE.md"
$memoryPath = Join-Path $projectDir "memory.md"

# STATE.md 不存在時先建立最小模板，確保 Haiku 有底稿可增修
if (-not (Test-Path $statePath)) {
    $initState = "# STATE.md`r`n`r`n目前沒有進行中的工作。"
    [System.IO.File]::WriteAllText($statePath, $initState, (New-Object System.Text.UTF8Encoding $true))
}

# ---- 2. 找最新的對話逐字稿 ----
$projDir = 'C:\Users\yuchi\.claude\projects\C--Users-yuchi'
$f = $null
if ($env:MEMSYNC_TRANSCRIPT) { $f = Get-Item $env:MEMSYNC_TRANSCRIPT -ErrorAction SilentlyContinue }
else { $f = Get-ChildItem "$projDir\*.jsonl" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1 }
if (-not $f) { exit 0 }

# ---- 3. token 成長節流（每個逐字稿各自記錄，多視窗不互相干擾）----
$latestInputTokens = 0
Get-Content $f.FullName -Encoding UTF8 | ForEach-Object {
    try {
        $d = $_ | ConvertFrom-Json
        if ($d.type -eq 'assistant' -and $d.message.usage -and $d.message.usage.input_tokens) {
            $latestInputTokens = [int]$d.message.usage.input_tokens
        }
    } catch {}
}
$flagFile = Join-Path $projDir (".memsync-" + $f.BaseName + ".txt")
$lastSaved = 0
if (Test-Path $flagFile) { try { $lastSaved = [int](Get-Content $flagFile -Raw -Encoding UTF8) } catch {} }
if ($latestInputTokens -lt $lastSaved) { $lastSaved = 0 }
$skipThrottle = $Force -or ($env:MEMSYNC_NO_THROTTLE -eq '1')
if (-not $skipThrottle -and ($latestInputTokens - $lastSaved) -lt 20000) { exit 0 }

# ---- 4. 取得 API key（環境變數優先，否則用 OAuth token）----
$apiKey = $env:ANTHROPIC_API_KEY
if (-not $apiKey) {
    try {
        $c = Get-Content "$env:USERPROFILE\.claude\.credentials.json" -Raw | ConvertFrom-Json
        $apiKey = $c.claudeAiOauth.accessToken
    } catch { exit 0 }
}
if (-not $apiKey) { exit 0 }

# ---- 5. 抽最近 40 句對話 ----
$messages = [System.Collections.Generic.List[string]]::new()
Get-Content $f.FullName -Encoding UTF8 | ForEach-Object {
    try {
        $d = $_ | ConvertFrom-Json
        if ($d.type -eq 'user' -and $d.message.content) {
            $text = if ($d.message.content -is [string]) { $d.message.content }
                    else { ($d.message.content | Where-Object { $_.type -eq 'text' } | ForEach-Object { $_.text }) -join '' }
            if ($text.Trim().Length -gt 0) { $messages.Add("USER: $($text.Substring(0, [Math]::Min(800, $text.Length)))") }
        } elseif ($d.type -eq 'assistant' -and $d.message.content) {
            $content = $d.message.content
            $text = if ($content -is [string]) { $content }
                    else { ($content | Where-Object { $_.type -eq 'text' } | ForEach-Object { $_.text }) -join '' }
            if ($text.Trim().Length -gt 0) { $messages.Add("ASSISTANT: $($text.Substring(0, [Math]::Min(1500, $text.Length)))") }
        }
    } catch {}
}
$recentConvo = ($messages | Select-Object -Last 40) -join "`n`n"
if ($recentConvo.Length -lt 100) { exit 0 }

# ---- 6. 把既有 memory.md / STATE.md 當底稿，請 Haiku 同時增修兩者 ----
$existingMemory = ""
if (Test-Path $memoryPath) { try { $existingMemory = Get-Content $memoryPath -Raw -Encoding UTF8 } catch {} }
$existingState = ""
if (Test-Path $statePath) { try { $existingState = Get-Content $statePath -Raw -Encoding UTF8 } catch {} }

$prompt = @"
你在維護某個開發專案的兩份筆記。對話很長、隨時可能被清空，請在細節被抹掉前更新它們。

【memory.md】是「查詢/對照資料的長期保存區」。放具體且長期有效的事實與資料：
IP、地址、餘額、設定值、指令輸出、固定路徑、各種對照關係(mapping)、重要決策與結論。
原則：只新增與修正、去重，不要刪掉仍然有效的舊資料。它可以慢慢變長，但每則都要是有用的資料。

【STATE.md】是「短期現況快照」。只放：目前做到哪、手上正在處理什麼、下一步要做什麼。
原則：要精簡。已經完成的、或已經寫進 memory.md 的長期資料，要從 STATE.md 移除，不要累積歷史。

目前的 memory.md（可能為空）：
$existingMemory

目前的 STATE.md（可能為空）：
$existingState

最近的對話（最多 40 句，已截斷）：
$recentConvo

請輸出更新後的「完整」兩份檔案（不是只給差異），格式嚴格如下，兩個標記獨立成行：
===MEMORY===
(這裡放更新後完整的 memory.md markdown 內容)
===STATE===
(這裡放更新後完整的 STATE.md markdown 內容)

只輸出上面格式的內容本身，不要任何解釋、不要 markdown 圍欄。
若這次對話完全沒有值得更新的新事實，只輸出：NO_UPDATE
"@

# ---- 7. 呼叫 Haiku（自行把回應位元組按 UTF-8 解碼，否則 PS 5.1 中文會變亂碼）----
$isOauth = $apiKey.StartsWith("sk-ant-oat")
$headers = @{ "anthropic-version" = "2023-06-01"; "content-type" = "application/json" }
if ($isOauth) { $headers["Authorization"] = "Bearer $apiKey" }
else { $headers["x-api-key"] = $apiKey }

$body = @{
    model      = "claude-haiku-4-5-20251001"
    max_tokens = 4000
    messages   = @(@{ role = "user"; content = $prompt })
} | ConvertTo-Json -Depth 10 -Compress

try {
    $resp = Invoke-WebRequest -Uri "https://api.anthropic.com/v1/messages" `
        -Method POST -Headers $headers `
        -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) `
        -ContentType "application/json; charset=utf-8" -UseBasicParsing
    $json = [System.Text.Encoding]::UTF8.GetString($resp.RawContentStream.ToArray())
    $text = (($json | ConvertFrom-Json).content[0].text).Trim()
} catch { exit 0 }

$utf8    = New-Object System.Text.UTF8Encoding $false
$utf8bom = New-Object System.Text.UTF8Encoding $true

if ($text -eq "NO_UPDATE" -or $text.StartsWith("NO_UPDATE")) {
    [System.IO.File]::WriteAllText($flagFile, "$latestInputTokens", $utf8)
    exit 0
}

# 去掉可能的 markdown 圍欄
$text = ($text -replace '(?s)^```\w*\s*', '' -replace '(?s)\s*```\s*$', '').Trim()

# ---- 8. 依標記切成 memory.md 與 STATE.md，分別寫入（UTF-8 帶 BOM）----
$memOut   = ""
$stateOut = ""
$mIdx = $text.IndexOf("===MEMORY===")
$sIdx = $text.IndexOf("===STATE===")
if ($mIdx -ge 0 -and $sIdx -gt $mIdx) {
    $memOut   = $text.Substring($mIdx + "===MEMORY===".Length, $sIdx - ($mIdx + "===MEMORY===".Length)).Trim()
    $stateOut = $text.Substring($sIdx + "===STATE===".Length).Trim()
} else {
    # 沒有照格式時，整段當 STATE.md，memory.md 不動，避免污染長期資料
    $stateOut = $text
}

try {
    if ($memOut.Length -gt 0)   { [System.IO.File]::WriteAllText($memoryPath, $memOut, $utf8bom) }
    if ($stateOut.Length -gt 0) { [System.IO.File]::WriteAllText($statePath, $stateOut, $utf8bom) }
    [System.IO.File]::WriteAllText($flagFile, "$latestInputTokens", $utf8)
} catch { exit 0 }
