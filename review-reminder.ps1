# review-reminder.ps1
# 觸發時機：PostToolUse，matcher = "Write|Edit"
# 每次寫入程式碼或 PPTX 相關檔案後，輸出 systemMessage 提醒 Claude 做審查。
# 純資料/文件檔（.md/.txt/.json/.yaml 等）不觸發。
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

$codeExts = @(
    '.py', '.js', '.ts', '.jsx', '.tsx', '.mjs', '.cjs',
    '.ps1', '.sh', '.bash',
    '.go', '.java', '.cs', '.cpp', '.c', '.h', '.rb', '.php',
    '.html', '.css', '.scss', '.sass', '.vue', '.svelte',
    '.pptx'
)
$ext = [System.IO.Path]::GetExtension($path).ToLower()
if ($codeExts -notcontains $ext) { exit 0 }

$type = if ($ext -eq '.pptx') { 'PPTX' } else { '程式碼' }
$fileName = [System.IO.Path]::GetFileName($path)
$msg = "[review] 已寫入 $type 檔案（$fileName）。請重新讀取並確認：邏輯錯誤、殘留代碼、版面問題。多檔任務可等全部寫完後統一審查。"

$payload = @{ systemMessage = $msg } | ConvertTo-Json -Compress
$bytes = [System.Text.Encoding]::UTF8.GetBytes($payload)
$stdout = [Console]::OpenStandardOutput()
$stdout.Write($bytes, 0, $bytes.Length)
$stdout.Flush()
exit 0