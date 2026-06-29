#Requires -Version 5.1
# spawn-project.ps1 - 在子進程中執行另一個專案的任務
param(
    [Parameter(Mandatory)][string]$ProjectName,
    [Parameter(Mandatory)][string]$Task,
    [switch]$Async
)

$projectPath = Join-Path $HOME ".claude/openspec/changes/$ProjectName"

if (-not (Test-Path $projectPath)) {
    Write-Error "找不到專案資料夾：$projectPath"
    exit 1
}

$statePath  = Join-Path $projectPath "STATE.md"
$tasksPath  = Join-Path $projectPath "tasks.md"

$stateContent = if (Test-Path $statePath)  { Get-Content $statePath  -Raw -Encoding UTF8 } else { "（無 STATE.md）" }
$tasksContent = if (Test-Path $tasksPath)  { Get-Content $tasksPath  -Raw -Encoding UTF8 } else { "（無 tasks.md）" }

# 截斷過長的內容，避免 prompt 過大
if ($stateContent.Length -gt 3000) { $stateContent = $stateContent.Substring(0, 3000) + "`n...（略）" }
if ($tasksContent.Length -gt 3000) { $tasksContent = $tasksContent.Substring(0, 3000) + "`n...（略）" }

$prompt = @"
你正在以子進程模式操作專案 $ProjectName。

專案路徑：$projectPath

## 目前狀態（STATE.md）
$stateContent

## 任務清單（tasks.md）
$tasksContent

## 你現在的任務
$Task

完成後：
1. 更新 $tasksPath，把已完成的任務打勾（[ ] 改為 [x]）
2. 更新 $statePath，反映最新現況（只保留現況＋下一步，不累積歷史）
3. 最後輸出一行摘要：「[完成] <做了什麼>」
"@

# 標記子進程模式，讓 SessionStart hook 靜默退出，避免選單輸出污染 stdout
$env:CLAUDE_SUBPROCESS = "1"

if ($Async) {
    $job = Start-Job -ScriptBlock {
        param($path, $p)
        $env:CLAUDE_SUBPROCESS = "1"
        Set-Location $path
        $p | & claude --print --dangerously-skip-permissions
    } -ArgumentList $projectPath, $prompt

    Write-Host ""
    Write-Host "子進程已在背景啟動（Job ID: $($job.Id)）" -ForegroundColor Green
    Write-Host "專案：$ProjectName"
    Write-Host "任務：$Task"
    Write-Host ""
    Write-Host "查看進度：Receive-Job $($job.Id)"
    Write-Host "等待完成：Wait-Job $($job.Id) | Receive-Job"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "啟動子進程 → $ProjectName" -ForegroundColor Cyan
    Write-Host "任務：$Task"
    Write-Host "────────────────────────────────────────" -ForegroundColor Gray

    Push-Location $projectPath
    try {
        $prompt | & claude --print --dangerously-skip-permissions
    } finally {
        Pop-Location
    }

    Write-Host "────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "子進程完成。STATE.md 已更新。" -ForegroundColor Green
    Write-Host ""
}
