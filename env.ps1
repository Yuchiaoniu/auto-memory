# ~/.claude/env.ps1 — OS 自動偵測工具路徑
# 在其他腳本裡用 . ~/.claude/env.ps1 載入，之後可用 $SSH、$SCP、$GCLOUD 等變數

if ($IsWindows) {
    $script:GCLOUD   = "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
    $script:GSUTIL   = "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin\gsutil.cmd"
    $script:SSH_BIN  = "$env:SystemRoot\System32\OpenSSH\ssh.exe"
    $script:SCP_BIN  = "$env:SystemRoot\System32\OpenSSH\scp.exe"
} else {
    # Linux / GCP
    $script:GCLOUD   = "gcloud"
    $script:GSUTIL   = "gsutil"
    $script:SSH_BIN  = "ssh"
    $script:SCP_BIN  = "scp"
}

$script:SSH_KEY     = Join-Path $HOME ".ssh/google_compute_engine"
$script:SSH_USER    = "yuchi"
$script:GCP_PROJECT = "level-up-374308"
$script:GCP_EMAIL   = "yuchiao.niu@gmail.com"
$script:OPENSPEC    = Join-Path $HOME ".claude/openspec/changes"
