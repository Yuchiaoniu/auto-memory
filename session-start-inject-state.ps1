# session-start-inject-state.ps1
# 觸發時機：SessionStart，matcher = "compact|clear"（壓縮後、或手動 /clear 後都會跑）。
# 這支腳本印到 stdout 的內容，會被注入「接手的 Claude」的 context，
# 讓它一開場就知道這個專案目前的狀態與待辦，不必重新摸索、也不再重複詢問。
#
# 它怎麼知道要載入哪個專案？兩種來源，依序判斷：
#   1) 目前資料夾 cwd 本身就是專案資料夾（裡面有 tasks.md / STATE.md）
#      → 直接用 cwd（適用：直接在專案資料夾裡啟動 claude，例如 open-projects.ps1）。
#   2) cwd 不是專案資料夾（例如在 C:\Users\yuchi 啟動、靠對話「開啟專案 X」切換）
#      → 讀「上次作用中的專案」指標檔 last-active-project.txt，載入它指到的專案。
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 讀取 hook stdin，取得 cwd
$cwd = $null
try {
    $raw = [Console]::In.ReadToEnd()
    if ($raw) { $cwd = ($raw | ConvertFrom-Json).cwd }
} catch {}
if (-not $cwd) { $cwd = (Get-Location).Path }

# ---- 決定要載入哪個專案資料夾 ----
$projPath = $null
if ((Test-Path (Join-Path $cwd "tasks.md")) -or (Test-Path (Join-Path $cwd "STATE.md"))) {
    $projPath = $cwd
} else {
    $pointer = "C:\Users\yuchi\.claude\last-active-project.txt"
    if (Test-Path $pointer) {
        try {
            $p = (Get-Content $pointer -Raw -Encoding UTF8).Trim()
            if ($p -and (Test-Path $p)) { $projPath = $p }
        } catch {}
    }
}
if (-not $projPath) { exit 0 }

$tasksPath  = Join-Path $projPath "tasks.md"
$statePath  = Join-Path $projPath "STATE.md"
$memoryPath = Join-Path $projPath "memory.md"
if (-not (Test-Path $tasksPath) -and -not (Test-Path $statePath) -and -not (Test-Path $memoryPath)) { exit 0 }

$out = [System.Collections.Generic.List[string]]::new()
$out.Add("【系統提示：對話剛被壓縮或清空，以下是先前保存的專案最新狀態，請據此接續工作，不要重新詢問已知資訊。】")
$out.Add("（專案資料夾：$projPath）")

if (Test-Path $statePath) {
    try {
        $s = Get-Content $statePath -Raw -Encoding UTF8
        if ($s.Trim().Length -gt 0) {
            $out.Add("")
            $out.Add("===== STATE.md（目前現況快照：做到哪、手上在處理什麼、下一步）=====")
            $out.Add($s.TrimEnd())
        }
    } catch {}
}

if (Test-Path $memoryPath) {
    try {
        $m = Get-Content $memoryPath -Raw -Encoding UTF8
        if ($m.Trim().Length -gt 0) {
            $out.Add("")
            $out.Add("===== memory.md（長期查詢/對照資料：IP、地址、設定值、指令輸出、決策結論等）=====")
            $out.Add($m.TrimEnd())
        }
    } catch {}
}

if (Test-Path $tasksPath) {
    try {
        $t = Get-Content $tasksPath -Raw -Encoding UTF8
        if ($t.Trim().Length -gt 0) {
            $out.Add("")
            $out.Add("===== tasks.md（任務清單）=====")
            $out.Add($t.TrimEnd())
        }
    } catch {}
}

[Console]::Out.Write(($out -join "`n"))
exit 0
