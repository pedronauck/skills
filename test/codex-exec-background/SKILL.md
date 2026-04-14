---
name: codex-exec-background
description: Run Codex CLI exec in background without pipe traps. Common pitfalls and patterns.
---

# Codex CLI Background Execution

## Pattern

```bash
cd /path/to/project && codex exec -m gpt-5.4 --full-auto "Your prompt here" 2>&1
```

## CRITICAL: Do NOT pipe output (SIGPIPE trap)

Never pipe `codex exec` output with `| tail`, `| grep`, etc. in background mode.
The pipe closes when there's no output, sending SIGPIPE (exit 143) and killing the process.

```bash
# BAD — pipe kills process when output stalls
codex exec ... 2>&1 | tail -5

# GOOD — no pipe, or redirect to file
codex exec ... 2>&1 > /tmp/codex-output.log
```

**Exception:** Piping via `tee` is safe because tee keeps all FDs open:
```bash
# ✅ SAFE — tee keeps both stdout and file open
codex exec ... 2>&1 | tee /tmp/codex-output.log
```

## CRITICAL: Use `script(1)` wrapper for piped stdin (TTY requirement)

`codex exec` **refuses piped stdin** when it's not a TTY:

```bash
# ❌ FAILS: "Error: stdin is not a terminal"
cat /tmp/prompt.txt | codex exec -m gpt-5.4 --full-auto -

# ✅ WORKS: script(1) fakes a TTY around the pipe
script -q -c "cat /tmp/prompt.txt | codex exec -m gpt-5.4 --full-auto -" /dev/null \
    2>&1 | tee /tmp/codex-output.log
```

**When you need this:**
- Any time you're piping a prompt file into `codex exec`
- When running from a non-TTY context (Hermes cron, background processes, CI)
- The `-` argument tells codex to read from stdin, but stdin must be a TTY

## Reasoning Effort

- `high` (default) — practical for code execution tasks
- `xhigh` — can cause the model to think for 40+ minutes without producing output
- Use `xhigh` only for complex reasoning/planning, NOT for code generation tasks

## Monitoring

- Check git log for new commits: `git log --oneline -5`
- Check for new/modified files: `git status`
- Codex state DB: `~/.codex/state.db` (updated when active)

## Auth

Codex CLI uses OAuth via ChatGPT by default. Check with `codex auth`.
