---
name: "saveclear"
description: Force-save current conversation context to memory before user runs /clear
category: Workflow
tags: [memory, context, clear]
---

Force-run the memory save script so important decisions and context get persisted before the user wipes context with `/clear`.

This is the "pre-clear" workaround since Claude Code has no built-in PreClear hook.

**Steps**

1. **Run the save script with -Force** (bypasses the 80K token / 20K growth gates):
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\yuchi\.claude\pre-compact-memory-save.ps1" -Force
   ```

   The script silently calls Haiku to extract decisions, task status, and user preferences from the last 40 turns, then writes/updates files in `C:\Users\yuchi\.claude\projects\C--Users-yuchi\memory\` and rebuilds `MEMORY.md`.

2. **Report what was saved.** List memory files modified in the last 2 minutes so the user can verify:
   ```powershell
   Get-ChildItem "C:\Users\yuchi\.claude\projects\C--Users-yuchi\memory\*.md" |
     Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-2) } |
     Select-Object Name, LastWriteTime
   ```

3. **Tell the user**: "Memory saved. Now type `/clear` to wipe context safely."

**Important**

- Do NOT attempt to invoke `/clear` yourself — it's a built-in command only the user can trigger.
- If step 1 produces no modified files in step 2, Haiku likely returned `NO_UPDATE` (nothing new worth saving). Report that explicitly rather than implying a save happened.
- Cost per invocation: ~1 Haiku call, max 2000 output tokens (~$0.002).
