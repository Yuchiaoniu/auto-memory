$SCP = "C:\WINDOWS\System32\OpenSSH\scp.exe"
$KEY = "$env:USERPROFILE\.ssh\google_compute_engine"
$SRC = "C:\Users\yuchi\.claude\.credentials.json"
$DST = "yuchi@35.227.93.38:/home/yuchi/.claude/.credentials.json"

if (Test-Path $SRC) {
    & $SCP -i $KEY -o StrictHostKeyChecking=no -o BatchMode=yes -q $SRC $DST 2>$null
}
