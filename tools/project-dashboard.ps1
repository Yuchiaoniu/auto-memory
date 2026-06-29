#Requires -Version 5.1
# project-dashboard.ps1 - 顯示所有 openspec 專案的狀態總覽
param(
    [switch]$PendingOnly  # 只顯示有未完成任務的專案
)

$changesPath = Join-Path $HOME ".claude/openspec/changes"
$projects = Get-ChildItem $changesPath -Directory | Sort-Object Name

$width = 60
$line  = "═" * $width

Write-Host ""
Write-Host $line -ForegroundColor Cyan
Write-Host "  專案總覽                       $((Get-Date).ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor Cyan
Write-Host $line -ForegroundColor Cyan

foreach ($proj in $projects) {
    $tasksPath = Join-Path $proj.FullName "tasks.md"
    $statePath = Join-Path $proj.FullName "STATE.md"

    $pendingCount = 0
    $doneCount    = 0
    $nextStep     = ""

    if (Test-Path $tasksPath) {
        $lines        = Get-Content $tasksPath -Encoding UTF8
        $pendingLines = $lines | Where-Object { $_ -match '^\s*-\s*\[ \]' }
        $doneLines    = $lines | Where-Object { $_ -match '^\s*-\s*\[x\]' }
        $pendingCount = @($pendingLines).Count
        $doneCount    = @($doneLines).Count
        $firstPending = $pendingLines | Select-Object -First 1
        if ($firstPending) {
            $nextStep = ($firstPending -replace '^\s*-\s*\[ \]\s*', '').Trim()
            if ($nextStep.Length -gt 45) { $nextStep = $nextStep.Substring(0, 45) + "…" }
        }
    }

    if ($PendingOnly -and $pendingCount -eq 0) { continue }

    $statusIcon  = if ($pendingCount -eq 0 -and $doneCount -gt 0) { "✅" }
                   elseif ($pendingCount -gt 0) { "🔄" }
                   else { "❓" }

    $statusColor = if ($pendingCount -eq 0) { "Gray" } else { "Yellow" }

    Write-Host ""
    Write-Host "  $statusIcon  $($proj.Name)" -ForegroundColor $statusColor -NoNewline
    Write-Host "  （待辦 $pendingCount  已完成 $doneCount）" -ForegroundColor DarkGray

    if ($nextStep) {
        Write-Host "     → $nextStep" -ForegroundColor White
    } elseif ($pendingCount -eq 0 -and $doneCount -gt 0) {
        Write-Host "     → 全部完成" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host $line -ForegroundColor Cyan
Write-Host "  用法：spawn-project.ps1 -ProjectName <name> -Task '<task>'" -ForegroundColor DarkGray
Write-Host "        加 -Async 可在背景執行，不卡主視窗" -ForegroundColor DarkGray
Write-Host $line -ForegroundColor Cyan
Write-Host ""
