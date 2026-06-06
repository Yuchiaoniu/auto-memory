# review-reminder.ps1
# 觸發時機：PostToolUse，matcher = "Write|Edit"
# 審查規則已移至 CLAUDE.md，此 hook 靜默退出，不產生任何輸出。
# 保留檔案結構供日後需要時恢復。
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$raw = $null
try { $raw = [Console]::In.ReadToEnd() } catch {}
if (-not $raw) { exit 0 }

$data = $null
try { $data = $raw | ConvertFrom-Json } catch { exit 0 }

$path = $null
try {
    if ($data.tool_input.file_path) { $path = $data.tool_input.file_path }
} catch {}
if (-not $path) { exit 0 }

exit 0