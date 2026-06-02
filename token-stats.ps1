# token-stats.ps1
$dir = "$env:USERPROFILE\.claude\projects\C--Users-yuchi"
$rate = if ($env:CLAUDE_NTD_RATE) { [double]$env:CLAUDE_NTD_RATE } else { 32 }
$files = Get-ChildItem "$dir\*.jsonl" | Sort-Object LastWriteTime -Descending | Select-Object -First 5
if (-not $files) { Write-Host "No session files."; exit 0 }

function Get-Stats($path) {
    $r = @{ turns=0; input=0; output=0; cr=0; cc=0 }
    Get-Content $path -Encoding UTF8 | ForEach-Object {
        try {
            $d = $_ | ConvertFrom-Json
            if ($d.type -eq "assistant" -and $d.message.usage) {
                $u = $d.message.usage; $r.turns++
                $r.input  += $u.input_tokens
                $r.output += $u.output_tokens
                if ($u.cache_read_input_tokens)     { $r.cr += $u.cache_read_input_tokens }
                if ($u.cache_creation_input_tokens) { $r.cc += $u.cache_creation_input_tokens }
            }
        } catch {}
    }; return $r
}

Write-Host "`n=== Claude Code Token Stats (rate: NT`$$rate/USD) ===" -ForegroundColor Cyan

$todayCr = 0; $todayOut = 0
$today = (Get-Date).Date
$i = 0
foreach ($f in $files) {
    $s = Get-Stats $f.FullName
    $age = [math]::Round(((Get-Date) - $f.LastWriteTime).TotalMinutes)
    $label = if ($i -eq 0) { "[Current]" } else { "[Recent $i]" }
    $in_cost  = [math]::Round($s.input  / 1000000 * 3.00  * $rate, 0)
    $cc_cost  = [math]::Round($s.cc     / 1000000 * 3.75  * $rate, 0)
    $cr_cost  = [math]::Round($s.cr     / 1000000 * 0.30  * $rate, 0)
    $out_cost = [math]::Round($s.output / 1000000 * 15.00 * $rate, 0)
    $total_cost = $in_cost + $cc_cost + $cr_cost + $out_cost
    $color = if ($i -eq 0) { "Yellow" } else { "Gray" }
    Write-Host "`n$label $($f.Name.Substring(0,8))... ($age min ago)" -ForegroundColor $color
    Write-Host ("  Turns        : {0,6}"                         -f $s.turns)
    Write-Host ("  Input        : {0,12:N0}  (~NT`${1})"        -f $s.input,  $in_cost)
    Write-Host ("  Cache Create : {0,12:N0}  (~NT`${1})"        -f $s.cc,     $cc_cost)
    Write-Host ("  Cache Read   : {0,12:N0}  (~NT`${1})"        -f $s.cr,     $cr_cost)
    Write-Host ("  Output       : {0,12:N0}  (~NT`${1})"        -f $s.output, $out_cost)
    Write-Host ("  Session Est. :               ~NT`$$total_cost") -ForegroundColor $(if ($total_cost -gt 100) { "Red" } else { "White" })
    if ($s.cr -gt 5000000) {
        Write-Host "  >> High cache -- consider /compact" -ForegroundColor Red
    }
    if ($f.LastWriteTime.Date -eq $today) { $todayCr += $s.cr; $todayOut += $s.output }
    $i++
}

# Today Total (all sessions, not just top 5)
$allToday = Get-ChildItem "$dir\*.jsonl" | Where-Object { $_.LastWriteTime.Date -eq $today }
if ($allToday.Count -gt 5) {
    $todayCr = 0; $todayOut = 0
    foreach ($f in $allToday) { $s = Get-Stats $f.FullName; $todayCr += $s.cr; $todayOut += $s.output }
}
$todayIn = 0; $todayCc = 0
foreach ($f in $allToday) {
    $s = Get-Stats $f.FullName
    $todayIn  += $s.input
    $todayCc  += $s.cc
    $todayCr  += $s.cr
    $todayOut += $s.output
}
$today_in_cost  = [math]::Round($todayIn  / 1000000 * 3.00  * $rate, 0)
$today_cc_cost  = [math]::Round($todayCc  / 1000000 * 3.75  * $rate, 0)
$today_cr_cost  = [math]::Round($todayCr  / 1000000 * 0.30  * $rate, 0)
$today_out_cost = [math]::Round($todayOut / 1000000 * 15.00 * $rate, 0)
$today_total    = $today_in_cost + $today_cc_cost + $today_cr_cost + $today_out_cost
Write-Host "`n--- Today Total ($($allToday.Count) sessions) ---" -ForegroundColor Cyan
Write-Host ("  Input        : {0,12:N0}  (~NT`${1})" -f $todayIn,  $today_in_cost)
Write-Host ("  Cache Create : {0,12:N0}  (~NT`${1})" -f $todayCc,  $today_cc_cost)
Write-Host ("  Cache Read   : {0,12:N0}  (~NT`${1})" -f $todayCr,  $today_cr_cost)
Write-Host ("  Output       : {0,12:N0}  (~NT`${1})" -f $todayOut, $today_out_cost)
Write-Host ("  Est. Total   :               ~NT`$$today_total") -ForegroundColor White
Write-Host ""
