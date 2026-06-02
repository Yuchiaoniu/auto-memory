# post-compact-memory-update.ps1
# 1. Saves memory + generates session snapshot (single Haiku call)
# 2. Writes snapshot to MEMORY.md top — loaded seamlessly in next session
# 3. Outputs SHORT systemMessage (no 29KB injection) to keep baseline low
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$memDir = "$env:USERPROFILE\.claude\projects\C--Users-yuchi\memory"
$snapshot = ""
$tasksSnippet = ""

# ── Step 1: Update memory files + generate session snapshot ──────────────────
try {
    $raw = [Console]::In.ReadToEnd()
    if ($raw -and $raw.Trim().Length -gt 0) {
        $data = $raw | ConvertFrom-Json
        $summary = $data.summary

        if ($summary -and $summary.Length -ge 50) {
            $apiKey = $env:ANTHROPIC_API_KEY
            if (-not $apiKey) {
                try {
                    $c = Get-Content "$env:USERPROFILE\.claude\.credentials.json" -Raw | ConvertFrom-Json
                    $apiKey = $c.claudeAiOauth.accessToken
                } catch {}
            }

            if ($apiKey) {
                $memIndex = ""
                try { $memIndex = Get-Content "$memDir\MEMORY.md" -Raw -Encoding UTF8 } catch {}

                $today = (Get-Date).ToString("yyyy-MM-dd HH:mm")
                $prompt = @"
You update a developer memory system. Analyze the conversation summary and do TWO things.

CURRENT MEMORY INDEX (MEMORY.md):
$memIndex

CONVERSATION SUMMARY:
$summary

MEMORY FILE SCHEMA - each file must start with this exact frontmatter:
---
name: short-kebab-slug
description: one line used to judge future relevance
metadata:
  type: user|feedback|project|reference
---
Then the content body.

RULES for memory files:
- project memories: lead with the fact, then **Why:** line and **How to apply:** line
- feedback memories: lead with the rule, then **Why:** line and **How to apply:** line
- Only save things NOT already in the current index
- Do not duplicate existing entries

OUTPUT FORMAT - respond with ONLY this exact JSON structure (no markdown fences, no extra text):
{
  "snapshot": "3-5 lines of plain text. State: current project, what task/topic, key decisions made, what comes next. Be specific. No markdown headers or bullets.",
  "updates": []
}

Where "updates" is either empty [] or an array of:
{"file":"filename.md","action":"create|update","content":"full markdown with frontmatter"}
"@

                $isOauth = $apiKey.StartsWith("sk-ant-oat")
                $headers = @{ "anthropic-version" = "2023-06-01"; "content-type" = "application/json" }
                if ($isOauth) { $headers["Authorization"] = "Bearer $apiKey" }
                else { $headers["x-api-key"] = $apiKey }

                $body = @{
                    model      = "claude-haiku-4-5-20251001"
                    max_tokens = 2000
                    messages   = @(@{ role = "user"; content = $prompt })
                } | ConvertTo-Json -Depth 10 -Compress

                $resp = Invoke-RestMethod -Uri "https://api.anthropic.com/v1/messages" `
                    -Method POST -Headers $headers `
                    -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) `
                    -ContentType "application/json; charset=utf-8"
                $text = $resp.content[0].text.Trim()
                $text = ($text -replace '(?s)^```json\s*', '' -replace '(?s)\s*```\s*$', '').Trim()

                $result  = $text | ConvertFrom-Json
                $snapshot = $result.snapshot
                $updates  = $result.updates

                $utf8 = New-Object System.Text.UTF8Encoding $false

                # Write updated memory files
                if ($updates -and $updates.Count -gt 0) {
                    foreach ($u in $updates) {
                        $path = Join-Path $memDir $u.file
                        [System.IO.File]::WriteAllText($path, $u.content, $utf8)
                    }
                }

                # Rebuild MEMORY.md: snapshot section at top + index entries
                $entries = Get-ChildItem "$memDir\*.md" |
                    Where-Object { $_.Name -ne "MEMORY.md" } |
                    ForEach-Object {
                        $fc   = Get-Content $_.FullName -Raw -Encoding UTF8
                        $desc = if ($fc -match "description:\s*(.+)") { $Matches[1].Trim() } else { $_.BaseName }
                        $name = if ($fc -match "name:\s*(.+)") { $Matches[1].Trim() } else { $_.BaseName }
                        "- [$name]($($_.Name)) -- $desc"
                    }
                $snapshotSection = if ($snapshot) { "## Last Session ($today)`n$snapshot`n`n" } else { "" }
                $newIndex = "# Memory Index`n`n$snapshotSection" + ($entries -join "`n") + "`n"
                [System.IO.File]::WriteAllText("$memDir\MEMORY.md", $newIndex, $utf8)
            }
        }
    }
} catch {}

# ── Step 2: Detect openspec project tasks.md ─────────────────────────────────
try {
    $openspecBase = "$env:USERPROFILE\openspec\changes"
    $cwd = (Get-Location).Path

    if ($cwd.StartsWith($openspecBase)) {
        $rel      = $cwd.Substring($openspecBase.Length).TrimStart('\')
        $projName = $rel.Split('\')[0]
        if ($projName) {
            $tasksPath = Join-Path (Join-Path $openspecBase $projName) "tasks.md"
            if (Test-Path $tasksPath) {
                $tc = Get-Content $tasksPath -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
                if ($tc) {
                    $tasksSnippet = "`n`n## Current Project: $projName — tasks.md`n``````markdown`n$tc`n``````"
                }
            }
        }
    }
} catch {}

# ── Step 3: Output SHORT systemMessage ───────────────────────────────────────
$snapshotMsg = if ($snapshot) { "`n`n$snapshot" } else { "" }
$msg = "Context was auto-compacted. Memory and session snapshot saved.$snapshotMsg$tasksSnippet"
@{ systemMessage = $msg } | ConvertTo-Json -Compress
