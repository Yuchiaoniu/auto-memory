# §27.9 batch upload 31 videos
$ErrorActionPreference = 'Continue'
$API = 'http://35.227.93.38:3000'
$SRC = 'C:\Users\yuchi\OneDrive\Desktop\' + [char]0x5341 + [char]0x68F5 + [char]0x6372 + [char]0x5C3A + [char]0x6A39 + [char]0x5F91
$LOG = 'C:\Users\yuchi\openspec\changes\forest-carbon-measurement\batch-upload-31.log'

$files = Get-ChildItem -LiteralPath $SRC -File | Where-Object { $_.Extension -match '\.(mp4|mov|MOV|MP4)$' } | Sort-Object Name
$total = $files.Count
Write-Host ('Found ' + $total + ' videos. SRC=' + $SRC)
('=== batch-upload-31 start ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' ===') | Out-File $LOG -Append -Encoding utf8

$ok = 0; $fail = 0; $cached = 0
$idx = 0
foreach ($f in $files) {
    $idx++
    $tStart = Get-Date
    $tag = '[' + $idx + '/' + $total + '] ' + $f.Name + ' (' + [math]::Round($f.Length/1MB,1) + ' MB)'
    Write-Host ''
    Write-Host $tag
    $tag | Out-File $LOG -Append -Encoding utf8

    try {
        $raw = & curl.exe -s -X POST -F ('video=@' + $f.FullName) ($API + '/api/upload') --max-time 600
        if (-not $raw) { throw 'empty response from upload' }
        $resp = $raw | ConvertFrom-Json
        $jobId = $resp.jobId
        if (-not $jobId) { throw 'no jobId in upload response: ' + $raw }
        Write-Host ('  jobId=' + $jobId)

        $deadline = (Get-Date).AddMinutes(10)
        $status = $null
        $lastStep = $null
        while ((Get-Date) -lt $deadline) {
            Start-Sleep -Seconds 8
            try {
                $s = Invoke-RestMethod -Uri ($API + '/api/status/' + $jobId) -Method Get -TimeoutSec 20
                if ($s.step -ne $lastStep) { Write-Host ('  step=' + $s.step); $lastStep = $s.step }
                if ($s.status -eq 'done' -or $s.status -eq 'error') { $status = $s; break }
            } catch { Write-Host ('  poll error: ' + $_.Exception.Message) }
        }

        $elapsed = [math]::Round(((Get-Date) - $tStart).TotalSeconds, 0)
        if ($null -eq $status) {
            $fail++
            $msg = '  TIMEOUT after ' + $elapsed + ' s'
            Write-Host $msg -ForegroundColor Yellow
            $msg | Out-File $LOG -Append -Encoding utf8
        } elseif ($status.status -eq 'error') {
            $fail++
            $msg = '  ERROR (' + $elapsed + ' s): ' + $status.error
            Write-Host $msg -ForegroundColor Red
            $msg | Out-File $LOG -Append -Encoding utf8
        } else {
            $r = $status.result
            $isCached = $status.cached -eq $true
            if ($isCached) { $cached++ } else { $ok++ }
            $msg = '  OK (' + $elapsed + ' s) cached=' + $isCached + ' species=' + $r.species + ' dbh=' + $r.dbhCm + ' tree=' + $r.treeId
            Write-Host $msg -ForegroundColor Green
            $msg | Out-File $LOG -Append -Encoding utf8
        }
    } catch {
        $fail++
        $msg = '  UPLOAD FAILED: ' + $_.Exception.Message
        Write-Host $msg -ForegroundColor Red
        $msg | Out-File $LOG -Append -Encoding utf8
    }
}

$summary = "`n=== done " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' === ok=' + $ok + ' cached=' + $cached + ' fail=' + $fail + ' total=' + $total
Write-Host $summary
$summary | Out-File $LOG -Append -Encoding utf8
