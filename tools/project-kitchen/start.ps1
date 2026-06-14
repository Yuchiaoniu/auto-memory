#Requires -Version 5.1
# start.ps1 - 啟動 Project Kitchen 網頁應用

$dir = $PSScriptRoot

# 檢查 Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python 未安裝，請先安裝 Python 3.x"
    exit 1
}

# 安裝依賴（quiet，只在缺少時安裝）
Write-Host "檢查依賴套件..." -ForegroundColor Cyan
python -m pip install -q flask anthropic

# 2 秒後開啟瀏覽器（讓 server 先啟動）
Start-Job -ScriptBlock { Start-Sleep 2; Start-Process "http://localhost:7799" } | Out-Null

Write-Host ""
Write-Host "Project Kitchen 啟動中 → http://localhost:7799" -ForegroundColor Green
Write-Host "按 Ctrl+C 可停止伺服器" -ForegroundColor Gray
Write-Host ""

# 前景執行 server（Ctrl+C 可停止）
$env:PYTHONIOENCODING = 'utf-8'
Set-Location $dir
python server.py
