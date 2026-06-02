# clear-reminder.ps1
# 觸發時機：Stop（每一輪對話結束）。在 settings.json 必須設為「非 async」，
#   因為 async:true 會讓所有輸出被吞掉（已查證官方文件），提醒就看不到了。
#
# 角色：上下文水位提醒。每輪讀目前累積 token，超過門檻就用 systemMessage 跳一行黃字，
#   建議使用者存檔後 /clear。每個門檻每段對話只提醒一次，不每輪嘮叨。
#
# 顯示原理：Stop hook 的「純文字 stdout」只會進 debug log、使用者看不到；
#   要讓使用者看到，必須輸出 JSON 並用 systemMessage 欄位（官方文件確認）。
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ===== 門檻設定（要調整就改這裡，由低到高）=====
# 累積 token 一旦超過某個 at 值，就跳該則 msg；每個 at 每段對話只提醒一次。
$tiers = @(
    @{ at = 300000; msg = "上下文已累積約 30 萬 token。找個段落『存檔』後 /clear，開乾淨對話會更順。" },
    @{ at = 500000; msg = "上下文已累積約 50 萬 token，回應會明顯變慢。強烈建議現在『存檔』後 /clear。" }
)

# ===== 找最新的對話逐字稿 =====
$projDir = 'C:\Users\yuchi\.claude\projects\C--Users-yuchi'
$f = Get-ChildItem "$projDir\*.jsonl" -ErrorAction SilentlyContinue |
     Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $f) { exit 0 }

# ===== 讀「最新的累積 context 大小」=====
# 只讀檔尾省時間。真正的 context 大小 = input_tokens + 兩種 cache token，
# 因為開了 prompt caching 後，大部分舊內容會算在 cache_read 而不在 input_tokens。
$latest = 0
Get-Content $f.FullName -Tail 200 -Encoding UTF8 | ForEach-Object {
    try {
        $d = $_ | ConvertFrom-Json
        if ($d.type -eq 'assistant' -and $d.message.usage -and $d.message.usage.input_tokens) {
            $t = [int]$d.message.usage.input_tokens
            if ($d.message.usage.cache_read_input_tokens)     { $t += [int]$d.message.usage.cache_read_input_tokens }
            if ($d.message.usage.cache_creation_input_tokens) { $t += [int]$d.message.usage.cache_creation_input_tokens }
            $latest = $t
        }
    } catch {}
}
if ($latest -le 0) { exit 0 }

# ===== 判斷是否跨過「尚未提醒過」的水位 =====
# flag 檔記錄這段對話已提醒到哪個 at 值，避免每輪重複；新逐字稿＝新 flag＝自動歸零。
$flag = Join-Path $projDir (".clearremind-" + $f.BaseName + ".txt")
$firedAt = 0
if (Test-Path $flag) { try { $firedAt = [int](Get-Content $flag -Raw -Encoding UTF8) } catch {} }

# 取目前已超過、且比上次提醒更高的「最高」水位（一次跳兩級時只報最高那則）
$hit = $null
foreach ($tier in $tiers) {
    if ($latest -ge $tier.at -and $tier.at -gt $firedAt) { $hit = $tier }
}
if (-not $hit) { exit 0 }

# ===== 輸出 systemMessage（使用者看得到）並更新 flag =====
$kt = [math]::Round($latest / 1000)
$payload = @{ systemMessage = "[提醒] $($hit.msg)（目前約 $kt 千 token）" } | ConvertTo-Json -Compress

$utf8 = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($flag, "$($hit.at)", $utf8)

# 直接以 UTF-8 位元組寫 stdout，避免 PS 5.1 主控台編碼把中文弄亂
$bytes = [System.Text.Encoding]::UTF8.GetBytes($payload)
$stdout = [Console]::OpenStandardOutput()
$stdout.Write($bytes, 0, $bytes.Length)
$stdout.Flush()
exit 0
