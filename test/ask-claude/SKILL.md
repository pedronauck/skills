---
name: ask-claude
description: Delegate tasks to Claude Code (Anthropic's CLI agent) running inside a detached tmux session with full permissions. Communicates via tmux-bridge CLI for cross-pane messaging. Use when the user wants Claude Code to analyze codebases, write code, refactor, or perform complex multi-file operations autonomously. Supports optional system prompt injection for enforcing specific behaviors (agent mode, output format, constraints). Not for quick single-line queries or when other agents (codex, opencode) are preferred.
---

# Ask Claude (Claude Code via Tmux + tmux-bridge)

## When to Use
- User wants Claude Code to work on a codebase autonomously
- Complex multi-file refactoring, analysis, or documentation tasks
- Need to enforce specific behavior via custom system prompt
- Long-running coding sessions that should survive in background

## Prerequisites
- `claudey` CLI must be available (wrapper around `claude`)
- `tmux` installed and accessible via `/home/linuxbrew/.linuxbrew/bin/tmux`
- `tmux-bridge` CLI installed at `~/.smux/bin/tmux-bridge` (from [smux](https://github.com/ShawnPana/smux) skill)
- Working directory should be set before launching

## tmux-bridge Setup

The agent calling this skill does **not** need to be inside a tmux session. `tmux-bridge` communicates via the tmux socket from any shell. It has been pre-patched to find tmux in `/home/linuxbrew/.linuxbrew/bin/`.

**Raw tmux commands** (session create/kill) still need the full path since they're not routed through `tmux-bridge`:

```bash
TMUX="/home/linuxbrew/.linuxbrew/bin/tmux"
```

**tmux-bridge works directly** (no PATH hack needed):
```bash
tmux-bridge list           # List all panes with IDs and labels
tmux-bridge read <target>  # Read pane content (also satisfies read guard)
tmux-bridge type <target> "text"   # Type text without Enter
tmux-bridge message <target> "text" # Type with sender info
tmux-bridge keys <target> Enter    # Send special keys
tmux-bridge name <target> <label>  # Label a pane for easy reference
```

### Target Format

`tmux-bridge` identifies panes by **pane ID** (e.g., `%16`) or **label** (e.g., `claude`). After creating a session, always get the pane ID from `tmux-bridge list`:

```bash
# Create session (raw tmux with full path)
$TMUX new-session -d -s "my-session" -c /path/to/project

# Get the pane ID from the list output
PANE_ID=$(tmux-bridge list | grep 'my-session' | awk '{print $1}')
# e.g., PANE_ID="%16"

# Now use $PANE_ID as target for ALL tmux-bridge calls
tmux-bridge read "$PANE_ID" 10
tmux-bridge type "$PANE_ID" "command"
```

## Workflow

### 1. Validate environment

```bash
which claudey && echo "claudey ✅" || echo "claudey ❌ MISSING"
tmux-bridge list >/dev/null 2>&1 && echo "tmux-bridge ✅" || echo "tmux-bridge ❌ MISSING"
TMUX="/home/linuxbrew/.linuxbrew/bin/tmux"
```

If `claudey` is missing, fall back to `claude`:
```bash
which claude && echo "claude ✅" || echo "claude ❌ MISSING"
```

### 2. Build the command

The core pattern uses `--dangerously-skip-permissions` and runs inside a detached tmux session:

**Basic form (question only):**
```bash
claudey --dangerously-skip-permissions '<user-prompt>'
```

**With system prompt override:**
```bash
claudey --dangerously-skip-permissions --system-prompt '<system-instruction>' '<user-prompt>'
```

The `--system-prompt` flag injects additional instructions before the user prompt. Use it to:
- Enforce **agent mode**: `"You are a specialized refactoring agent. Focus only on X."`
- Enforce **output format**: `"Always respond in JSON with keys: files_changed, summary."`
- Set **constraints**: `"Do not modify test files. Only touch src/ directory."`
- Define **persona**: `"You are a senior Go code reviewer. Be strict about errors."`

### 3. Launch in tmux session

Use raw `tmux` (with full path) for session management, then `tmux-bridge` for all interaction:

```bash
# Generate unique session name
SESSION_NAME="claude-$(echo '<task-description>' | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | head -c 20)-$(date +%s)"
TMUX="/home/linuxbrew/.linuxbrew/bin/tmux"

# Create detached session with working directory
$TMUX new-session -d -s "${SESSION_NAME}" -c '<working-directory>'

# Get pane ID from tmux-bridge list
PANE_ID=$(tmux-bridge list | grep "${SESSION_NAME}" | awk '{print $1}')
```

**Launch Claude Code TUI using tmux-bridge read-act cycle:**

```bash
# Step 1: READ the pane to satisfy read guard
tmux-bridge read "$PANE_ID" 5

# Step 2: TYPE launch command (no Enter yet)
tmux-bridge type "$PANE_ID" "claudey --dangerously-skip-permissions '<full-prompt>'"

# Step 3: VERIFY text landed, then submit with KEYS
tmux-bridge read "$PANE_ID" 5
tmux-bridge keys "$PANE_ID" Enter

# Label for easy reference
tmux-bridge name "$PANE_ID" claude
### 4. Monitor progress

Poll at regular intervals (every 2-3 minutes recommended) using `tmux-bridge read`:

```bash
# Read the pane output (satisfies read guard for next interaction)
tmux-bridge read "$PANE_ID" 50

# Check if Claude Code finished by looking for idle prompt
tmux-bridge read "$PANE_ID" 30 | grep -q "^❯ $" && echo "idle/done" || echo "working"
```

**Status indicators in Claude Code output:**

| Indicator | Meaning |
|-----------|---------|
| `● Booping…` | Claude is thinking/processing |
| `⎿ Running…` | A tool call is executing |
| `✻ Cooked for Xm Ys` | Task completed, total time shown |
| `❯` (empty prompt) | Waiting for input / done |

### 5. Send follow-up prompts (multi-turn)

After each task completes:

```bash
# READ first (required by read guard)
tmux-bridge read "$PANE_ID" 10

# TYPE the next prompt
tmux-bridge message "$PANE_ID" "Now do X, Y, Z."

# VERIFY and submit
tmux-bridge read "$PANE_ID" 10
tmux-bridge keys "$PANE_ID" Enter

# STOP here — do NOT poll for reply. Check back after delay.
```

### 6. Collect results

When completion detected (`Cooked` or idle prompt):

```bash
# Read final state (larger buffer)
tmux-bridge read "$PANE_ID" 200 > /tmp/claude-output-${SESSION_NAME}.txt
```

Parse the output to extract:
1. **Summary** of what was done
2. **Files modified** (look for Write/Edit tool calls)
3. **Commit hash** if git operations were performed
4. **Errors or warnings** if any

### 7. Cleanup

```bash
# Kill session (raw tmux for session management)
$TMUX kill-session -t "${SESSION_NAME}"

# Or keep open for manual inspection
```

## Complete Example

```bash
TMUX="/home/linuxbrew/.linuxbrew/bin/tmux"
SESSION_NAME="claude-auth-refactor-$(date +%s)"
WORK_DIR="$HOME/Projects/myapp"

# Launch session (raw tmux)
$TMUX new-session -d -s "${SESSION_NAME}" -c "${WORK_DIR}"

# Get pane ID from bridge list
PANE_ID=$(tmux-bridge list | grep "${SESSION_NAME}" | awk '{print $1}')

# READ → TYPE → VERIFY → KEYS (tmux-bridge pattern)
PROMPT="Refactor internal/auth to use middleware pattern."
SYSTEM_PROMPT="You are a Go refactoring specialist. Rules: 1) Do not change public API signatures. 2) Add comments. 3) Run go build. 4) Commit."

tmux-bridge read "$PANE_ID" 5
tmux-bridge type "$PANE_ID" "claudey --dangerously-skip-permissions --system-prompt '${SYSTEM_PROMPT}' '${PROMPT}'"
tmux-bridge read "$PANE_ID" 5
tmux-bridge keys "$PANE_ID" Enter
tmux-bridge name "$PANE_ID" claude

# Monitor every 2 min until done...
```

## System Prompt Recipes

| Goal | System Prompt Snippet |
|------|----------------------|
| Agent mode | `You are a <role>. Only perform <scope>. Ignore all other requests.` |
| Output format | `Respond in this exact JSON format: {"status": "...", "changes": [...]}` |
| Read-only analysis | `DO NOT write or modify any files. Only read and report.` |
| Test-focused | `Run tests after every change. If tests fail, revert and try again.` |
| Commit discipline | `After completing work, stage all changes and commit with conventional commit message.` |

## Tips

- Always use **unique session names** (append timestamp) to avoid collisions
- Set `-c <working-dir>` on `$TMUX new-session` so Claude Code starts in correct project
- `--dangerously-skip-permissions` is intentional — autonomous execution is the goal
- For very long tasks (>15 min), poll less frequently (every 5 min)
- Sessions survive agent restarts — safe for long-running work
- If `claudey` is not available, use `claude` directly (same flags apply)
- **Always follow the read-act-read cycle** — `tmux-bridge` enforces it and will error if you skip read
- **Label your panes** with `tmux-bridge name "$PANE_ID" <label>` — makes `tmux-bridge list` readable
- Session create/kill uses raw `$TMUX` — only pane interaction uses `tmux-bridge`
- Get pane ID from `tmux-bridge list | grep <session> | awk '{print $1}'` after creating session

## Related Skills

- [smux](../../.agents/skills/smux/SKILL.md) — Core tmux-bridge CLI reference and cross-pane communication patterns
- [tmux-background-session](../devops/tmux-background-session/SKILL.md) — Core tmux patterns for session lifecycle
- [claude-code](./claude-code/SKILL.md) — Alternative delegation approach using ACP subprocess transport
