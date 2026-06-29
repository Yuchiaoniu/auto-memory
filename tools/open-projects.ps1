# open-projects.ps1
$base   = (Join-Path $HOME ".claude/openspec/changes")
$claude = "C:\Users\yuchi\.local\bin\claude.exe"
$wt     = "C:\Users\yuchi\AppData\Local\Microsoft\WindowsApps\wt.exe"

$incomplete = @()

Get-ChildItem $base -Directory | ForEach-Object {
    $tasksFile = Join-Path $_.FullName "tasks.md"
    if (Test-Path $tasksFile) {
        $content = Get-Content $tasksFile -Raw -Encoding UTF8
        if ($content -match '\[ \]') {
            $incomplete += $_.Name
        }
    }
}

if ($incomplete.Count -eq 0) {
    Write-Host "All projects completed!"
    exit
}

Write-Host "Found $($incomplete.Count) incomplete projects:"
$incomplete | ForEach-Object { Write-Host "  - $_" }
Write-Host ""
Write-Host "Opening tabs..."

$launchDir = "$env:TEMP\openspec-launchers"
New-Item -ItemType Directory -Force $launchDir | Out-Null

foreach ($project in $incomplete) {
    $projectDir = Join-Path $base $project
    $tasksFile  = Join-Path $projectDir "tasks.md"
    $tasksContent = Get-Content $tasksFile -Raw -Encoding UTF8

    # Write tasks content to a temp file to avoid encoding issues in script generation
    $msgFile = Join-Path $launchDir "$project-init.txt"
    $initMsg = "你正在處理 openspec 專案: $project`r`n`r`n--- tasks.md ---`r`n$tasksContent`r`n--- end ---`r`n`r`n請列出所有標記為 [ ] 的未完成任務，然後繼續執行下一個任務。"
    [System.IO.File]::WriteAllText($msgFile, $initMsg, [System.Text.Encoding]::UTF8)

    # Write a per-project launcher script (avoids base64 + quote nesting issues)
    $launcher = Join-Path $launchDir "$project-launch.ps1"
    [System.IO.File]::WriteAllText($launcher, @"
Write-Host ''
Write-Host '  PROJECT: $project' -ForegroundColor Cyan
Write-Host ''
Set-Location "$projectDir"
`$msg = [System.IO.File]::ReadAllText("$msgFile", [System.Text.Encoding]::UTF8)
& "$claude" --name "$project" `$msg
"@, [System.Text.Encoding]::UTF8)

    & $wt -w 0 new-tab --title "$project" powershell -NoExit -File $launcher
    Start-Sleep -Milliseconds 800
}

Write-Host "Done! $($incomplete.Count) tabs opened."
