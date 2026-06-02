# cache-check.ps1：讀最新一筆 assistant message 的實際 context 大小
# （input_tokens + cache_creation + cache_read = 這輪送給模型的總 token 數）
# 只看最新一筆，不累加，避免跨輪加總導致假警報。
$dir = 'C:\Users\yuchi\.claude\projects\C--Users-yuchi'
$f = Get-ChildItem "$dir\*.jsonl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $f) { exit 0 }
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
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
if ($latest -gt 170000) {
    $k = [math]::Round($latest / 1000)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes(("{0}" -f (@{ systemMessage = "[存檔提醒] Context 已達 ${k}k token，autoCompact 即將啟動。如需保留查詢資料請先說『請存檔』。" } | ConvertTo-Json -Compress)))
    $stdout = [Console]::OpenStandardOutput()
    $stdout.Write($bytes, 0, $bytes.Length)
    $stdout.Flush()
}