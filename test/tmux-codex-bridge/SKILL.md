---
name: tmux-codex-bridge
description: Control and monitor Codex CLI sessions running inside tmux — send prompts, check progress, and manage background work
---

# TMux Codex Bridge

Control a Codex CLI agent running inside a tmux session remotely.

## Prerequisites

- `tmux` installed (often via Homebrew: `/home/linuxbrew/.linuxbrew/bin/tmux`)
- A tmux session with Codex CLI running inside it

## Usage Pattern

### 1. List tmux sessions

```bash
/home/linuxbrew/.linuxbrew/bin/tmux list-sessions
```

**Important:** Use full path to tmux if running from bash (Homebrew path may not be in bash PATH).

### 2. Send a prompt to Codex in a tmux session

```bash
# Send the prompt text
/home/linuxbrew/.linuxbrew/bin/tmux send-keys -t <session-name> '<your prompt here>'

# CRITICAL: Always send Enter afterwards!
/home/linuxbrew/.linuxbrew/bin/tmux send-keys -t <session-name> Enter
```

⚠️ **Always press Enter after sending the prompt** — `send-keys` only types the text, it doesn't submit it.

### 3. Monitor progress

```bash
# Capture last N lines of the session output
/home/linuxbrew/.linuxbrew/bin/tmux capture-pane -t <session-name> -p -S -100

# For real-time monitoring, capture repeatedly with delays
```

### 4. Check if Codex is working or idle

Look for these indicators in the captured output:
- `Working...` + `background terminal running` = Codex is executing
- `>` prompt alone = Codex is idle, waiting for input
- Fish shell `$` prompt = Codex has exited (need to restart)

### 5. Restart Codex if session died

```bash
/home/linuxbrew/.linuxbrew/bin/tmux send-keys -t <session-name> 'codex --full-auto' Enter
```

Then send your prompt.

## Common Workflow

```bash
SESSION="agh"  # or whatever session name

# 1. Send prompt
tmux send-keys -t $SESSION 'seu prompt aqui' Enter

# 2. Wait a bit (10-30s for context to build)
sleep 15

# 3. Check progress
tmux capture-pane -t $SESSION -p -S -100

# 4. Repeat checking until done
```

## Pitfalls

- **Forgot Enter**: Prompt appears but Codex doesn't execute. Always send `Enter` as separate command.
- **PATH issues**: When using bash, Homebrew-installed tools like `tmux` need full path `/home/linuxbrew/.linuxbrew/bin/tmux`.
- **Codex exited**: If you see fish shell prompt (`$`), Codex has terminated and needs restart.
- **Background processes**: Codex may show "Working..." with "N background terminal(s) running" — this is normal, it's doing work.
- **HTML tags in prompts**: Tags like `<critical>` may cause fish shell errors if Codex isn't running. Make sure Codex is active before sending.
- **Context nearly full → stuck**: When context bar shows near-full (e.g., `[██▉]` or `[███▏]`), Codex may appear stuck after sending a prompt (shows the prompt text but no `Working...`). Send a bare `Enter` to wake it up — this usually triggers execution.
- **Pre-commit hook PATH hell**: Husky pre-commit hooks run with a severely limited PATH (no Homebrew, no bun, no mise). If the project uses `make fmt` (needs `go`) or lint-staged with `oxfmt` (via `bunx`), commits will fail from Hermes/terminal even though both tools are installed. Fix by exporting the full PATH before committing:

```bash
export PATH="$HOME/.bun/bin:/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/Cellar/go/$(ls /home/linuxbrew/.linuxbrew/Cellar/go/ | tail -1)/libexec/bin:$HOME/.hermes/node_modules/.bin:$PATH"
git commit -m "... && git push"
```

Key paths to know:
| Tool | Path |
|------|------|
| tmux | `/home/linuxbrew/.linuxbrew/bin/tmux` |
| go | `/home/linuxbrew/.linuxbrew/Cellar/go/<version>/libexec/bin/go` |
| bun/bunx | `~/.bun/bin/bun`, `~/.bin/bunx` |

If `bun` isn't installed at all, install it first: `curl -fsSL https://bun.sh/install \| bash`
- **Finding the right Go version**: Use `ls /home/linuxbrew/.linuxbrew/Cellar/go/` or `find /home/linuxbrew -name "go" -type f 2>/dev/null` to locate the binary.

## Full Workflow: Prompt → Monitor → Commit

```bash
SESSION="agh"
TMUX="/home/linuxbrew/.linuxbrew/bin/tmux"

# 1. Send prompt to Codex
$TMUX send-keys -t $SESSION 'Fix X and make tests pass' Enter

# 2. Wait, then check progress (repeat until done)
sleep 15 && $TMUX capture-pane -t $SESSION -p | tail -30

# 3. If stuck (context near-full, no Working... indicator)
$TMUX send-keys -t $SESSION Enter
sleep 10 && $TMUX capture-pane -t $SESSION -p | tail -30

# 4. Once done, cd to project and commit WITH full PATH
cd ~/Projects/agh
export PATH="$HOME/.bun/bin:/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/Cellar/go/$(ls /home/linuxbrew/.linuxbrew/Cellar/go/ | tail -1)/libexec/bin:$PATH"
git add -A && git commit -m "description" && git push
```
