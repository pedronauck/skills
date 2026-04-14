---
name: ask-codex
description: Delegate tasks to OpenAI Codex CLI running in full-danger mode inside a detached tmux TUI session. Communicates via tmux-bridge CLI for cross-pane messaging. Use when the user wants Codex to analyze codebases, write code, refactor, or perform complex multi-file operations autonomously via the interactive terminal UI. Supports optional system prompt injection via prompt prefixing and config overrides for enforcing specific behaviors. Not for quick single-line queries or when Claude Code (ask-claude) is preferred.
---

# Ask Codex (Codex CLI TUI via Tmux + tmux-bridge)

## When to Use
- User wants OpenAI Codex's TUI to work on a codebase autonomously
- Complex multi-file refactoring, analysis, documentation, or generation tasks
- Long-running coding sessions that should survive in background
- Need the full interactive experience (multi-turn, tool use, self-correction)
- User prefers OpenAI models over Anthropic's Claude

## Prerequisites
- `codex` CLI must be available (installed via npm or Go)
- `tmux` installed and accessible via `/home/linuxbrew/.linuxbrew/bin/tmux`
- `tmux-bridge` CLI installed at `~/.smux/bin/tmux-bridge` (from [smux](https://github.com/ShawnPana/smux) skill)
- Authenticated with `codex login` (or `$OPENAI_API_KEY` set)

## tmux-bridge Setup

The agent calling this skill does **not** need to be inside a tmux session. `tmux-bridge` communicates via the tmux socket from any shell. It has been pre-patched to find tmux in `/home/linuxbrew/.linuxbrew/bin/`.

**Raw tmux commands** (session create/kill) need the full path:
```bash
TMUX="/home/linuxbrew/.linuxbrew/bin/tmux"
```

**tmux-bridge works directly** (no PATH hack needed):
```bash
tmux-bridge list           # List panes with IDs and labels
tmux-bridge read <target>  # Read content + satisfies read guard
tmux-bridge type <target> "text"   # Type without Enter
tmux-bridge message <target> "text" # Type with sender info
tmux-bridge keys <target> Enter    # Send special keys
tmux-bridge name <target> <label>  # Label pane for easy reference
```

### Target Format

Use **pane ID** from `tmux-bridge list` (e.g., `%16`) or **label**. After creating session:

```bash
$TMUX new-session -d -s "my-session" -c /path/to/project
PANE_ID=$(tmux-bridge list | grep 'my-session' | awk '{print $1}')
# e.g., PANE_ID="%16"

# Use $PANE_ID for ALL bridge calls
tmux-bridge read "$PANE_ID" 10
```

## Workflow

### 1. Validate environment

```bash
which codex && echo "codex ✅" || echo "codex ❌ MISSING"
tmux-bridge list >/dev/null 2>&1 && echo "tmux-bridge ✅" || echo "tmux-bridge ❌ MISSING"
TMUX="/home/linuxbrew/.linuxbrew/bin/tmux"
```

### 2. Understand permission modes

Codex has three auto-execution tiers:

| Mode | Flag | Sandbox | Approvals | Use Case |
|------|------|---------|-----------|----------|
| **Full Auto** | `--full-auto` | `workspace-write` | `on-request` | Safe autonomous work |
| **Danger Mode** | `--dangerously-bypass-approvals-and-sandbox` | None | None | Full access |
| **Custom** | `-s <mode> -a <policy>` | Configurable | Configurable | Fine-grained control |

For this skill, **default to `--dangerously-bypass-approvals-and-sandbox`** unless user specifies otherwise.

### 3. Build the launch command

**Default model is always `gpt-5.4` with reasoning effort `xhigh`:**
```bash
codex --dangerously-bypass-approvals-and-sandbox -m 'gpt-5.4' -c 'reasoning_effort="xhigh"'
```

To override model or reasoning effort:
```bash
codex --dangerously-bypass-approvals-and-sandbox -m '<model>' -c 'reasoning_effort="<level>"'
```

**With working directory** (use tmux `-c` flag):
```bash
tmux new-session -d -s <name> -c /path/to/project
```

**With system-prompt-like behavior** (inject instructions before the task):

Codex has no native `--system-prompt` flag. Use prompt prefix or `-c` overrides:

```bash
# Method 1: System instruction prefix in the prompt
"[SYSTEM: You are a specialist Go developer. Only modify files in internal/] Refactor auth"

# Method 2: Config overrides
-c 'features.web_search=true'
-c 'model="o3"'
-c 'reasoning_effort="high"'
```

### 4. Launch in tmux session

Use raw `tmux` (full path) for session management, then `tmux-bridge` for all interaction:

```bash
# Generate unique session name
SESSION_NAME="codex-$(echo '<task-description>' | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | head -c 20)-$(date +%s)"
TMUX="/home/linuxbrew/.linuxbrew/bin/tmux"

# Create detached session with working directory
$TMUX new-session -d -s "${SESSION_NAME}" -c '<working-directory>'

# Get pane ID from tmux-bridge list
PANE_ID=$(tmux-bridge list | grep "${SESSION_NAME}" | awk '{print $1}')
```

**Launch Codex TUI using tmux-bridge read-act cycle:**

```bash
# Step 1: READ to satisfy read guard
tmux-bridge read "$PANE_ID" 5

# Step 2: TYPE launch command (no Enter yet)
CMD="codex --dangerously-bypass-approvals-and-sandbox -m 'gpt-5.4' -c 'reasoning_effort=\"xhigh\"'"
tmux-bridge type "$PANE_ID" "${CMD}"

# Step 3: VERIFY text landed, then submit
tmux-bridge read "$PANE_ID" 5
tmux-bridge keys "$PANE_ID" Enter

# Wait for TUI init
sleep 3

# Label the pane
tmux-bridge name "$PANE_ID" codex
```

The Codex TUI will now be running inside the detached tmux session, ready to receive input.

### 5. Send prompts to the TUI (multi-turn)

After TUI init, send task prompts:

```bash
# READ first (required by read guard)
tmux-bridge read "$PANE_ID" 10

# SEND the main prompt (message prepends sender info)
tmux-bridge message "$PANE_ID" "<your-task-prompt>"

# VERIFY and submit
tmux-bridge read "$PANE_ID" 10
tmux-bridge keys "$PANE_ID" Enter
```

Multi-turn — sequential prompts:

```bash
# Turn 1
tmux-bridge read "$PANE_ID" 10
tmux-bridge message "$PANE_ID" "Analyze the codebase and find all TODO comments"
tmux-bridge read "$PANE_ID" 10
tmux-bridge keys "$PANE_ID" Enter
# ... wait ~3 min ...

# Turn 2: follow up
tmux-bridge read "$PANE_ID" 10
tmux-bridge message "$PANE_ID" "Now fix the top 5 most critical ones"
tmux-bridge read "$PANE_ID" 10
tmux-bridge keys "$PANE_ID" Enter
```

### 6. Monitor progress

Poll at regular intervals (every 2-3 minutes):

```bash
# Read pane output (satisfies read guard)
tmux-bridge read "$PANE_ID" 50

# List all panes to check session status
tmux-bridge list
```

**Status indicators in the Codex TUI output:**

| Indicator | Meaning |
|-----------|---------|
| `• Working (Xs • esc to interrupt)` | Actively processing |
| New `›` prompt appears after `Working` | **Task complete**, awaiting next input |
| Session exits to shell / not in `$TMUX_BRIDGE list` | TUI closed (error or `/exit`) |
| No change between polls | Still processing (gpt-5.4 + xhigh is slow) |

### 7. Collect results

When completion detected (new idle prompt):

```bash
# Read final state
tmux-bridge read "$PANE_ID" 300 > /tmp/codex-output-${SESSION_NAME}.txt
```

### 8. Cleanup

```bash
# Kill session (raw tmux)
$TMUX kill-session -t "${SESSION_NAME}"
```

## Complete Example

```bash
TMUX="/home/linuxbrew/.linuxbrew/bin/tmux"
SESSION_NAME="codex-api-docs-$(date +%s)"
WORK_DIR="$HOME/Projects/myapi"

# Step 1: Create session (raw tmux)
$TMUX new-session -d -s "${SESSION_NAME}" -c "${WORK_DIR}"

# Step 2: Get pane ID
PANE_ID=$(tmux-bridge list | grep "${SESSION_NAME}" | awk '{print $1}')

# Step 3: READ → TYPE → VERIFY → KEYS to launch TUI
tmux-bridge read "$PANE_ID" 5
tmux-bridge type "$PANE_ID" "codex --dangerously-bypass-approvals-and-sandbox -m 'gpt-5.4' -c 'reasoning_effort=\"xhigh\"'"
tmux-bridge read "$PANE_ID" 5
tmux-bridge keys "$PANE_ID" Enter
sleep 3
tmux-bridge name "$PANE_ID" codex

# Step 4: Send task prompt
tmux-bridge read "$PANE_ID" 10
tmux-bridge message "$PANE_ID" "[SYSTEM: You are a technical writer.] Analyze all HTTP handlers in cmd/server/ and write OpenAPI-style doc comments."
tmux-bridge read "$PANE_ID" 10
tmux-bridge keys "$PANE_ID" Enter
```

## Multi-Turn Conversation Pattern

Guide Codex step by step:

```bash
TMUX="/home/linuxbrew/.linuxbrew/bin/tmux"
SESSION_NAME="codex-refactor-$(date +%s)"
$TMUX new-session -d -s "${SESSION_NAME}" -c "$HOME/Projects/myapp"

# Get pane ID
PANE_ID=$(tmux-bridge list | grep "${SESSION_NAME}" | awk '{print $1}')

# Launch
tmux-bridge read "$PANE_ID" 5
tmux-bridge type "$PANE_ID" "codex --dangerously-bypass-approvals-and-sandbox -m 'gpt-5.4' -c 'reasoning_effort=\"xhigh\"'"
tmux-bridge read "$PANE_ID" 5
tmux-bridge keys "$PANE_ID" Enter
sleep 3
tmux-bridge name "$PANE_ID" codex

# Turn 1: Initial analysis
tmux-bridge read "$PANE_ID" 10
tmux-bridge message "$PANE_ID" "Review internal/auth/ package and identify all security issues"
tmux-bridge read "$PANE_ID" 10
tmux-bridge keys "$PANE_ID" Enter
# ... wait ~3 min ...

# Turn 2: Act on findings
tmux-bridge read "$PANE_ID" 10
tmux-bridge message "$PANE_ID" "Fix the top 3 issues you found. Add unit tests for each fix."
tmux-bridge read "$PANE_ID" 10
tmux-bridge keys "$PANE_ID" Enter
# ... wait ~5 min ...

# Turn 3: Verify
tmux-bridge read "$PANE_ID" 10
tmux-bridge message "$PANE_ID" "Run make test and make lint. Fix anything that fails."
tmux-bridge read "$PANE_ID" 10
tmux-bridge keys "$PANE_ID" Enter
# ... wait ~3 min ...

# Turn 4: Commit
tmux-bridge read "$PANE_ID" 10
tmux-bridge message "$PANE_ID" "Stage all changes and commit with conventional commit message."
tmux-bridge read "$PANE_ID" 10
tmux-bridge keys "$PANE_ID" Enter
```

## Model Selection Guide

**Default: `gpt-5.4` with `reasoning_effort="xhigh"`** — always used unless explicitly overridden.

| Flag Override | Model | Reasoning | Best For |
|---------------|-------|-----------|----------|
| *(default)* | **gpt-5.4** | **xhigh** | **Default for all tasks — maximum reasoning** |
| `-c 'reasoning_effort="high"'` | gpt-5.4 | high | Balanced speed/reasoning for large codebases |
| `-c 'reasoning_effort="low"'` | gpt-5.4 | low | Fast tasks where deep reasoning isn't needed |
| `-m o3` | o3 | default | Complex architecture decisions, heavy multi-file refactor |
| `-m gpt-4.1` | GPT-4.1 | default | Legacy fallback, general coding |
| `--oss` | Local (Ollama/LM Studio) | — | Offline, privacy-sensitive work |

## Alternative Mode: `codex exec` (Non-Interactive / Reliable)

### When to Use `exec` Instead of TUI

The TUI mode via `tmux-bridge` has known reliability issues with long/complex prompts. Use `codex exec` as the **primary mode** for:

- **Complex/long prompts** (>10 lines, multi-section design specs)
- **Single-shot tasks** where you don't need interactive multi-turn
- **When TUI gets stuck** (prompt typed but not submitted, session hanging)
- **Background execution** where you want output captured to a file
- **Tasks that write files** — Codex exec can create/write directly

**Use TUI only when:** You genuinely need interactive multi-turn conversation (step-by-step guidance, follow-up questions, real-time course correction).

### How to Use `codex exec` (Recommended for Complex Tasks)

```bash
# Step 1: Write prompt to file first (avoids shell escaping issues)
cat > /tmp/codex-prompt.txt << 'PROMPT'
[SYSTEM: You are a senior analytics engineer...]
## CONTEXT: ...
(full detailed prompt here...)
PROMPT

# Step 2: Run via script wrapper (see ⚠️ TTY GOTCHA below)
# For foreground (quick tasks <3 min):
script -q -c "cat /tmp/codex-prompt.txt | timeout 600 codex \
    --dangerously-bypass-approvals-and-sandbox \
    -m 'gpt-5.4' \
    -c 'reasoning_effort=\"xhigh\"'" /dev/null \
    2>&1 | tee /tmp/codex-exec-output.txt
echo "EXIT CODE: $?"
```

**With Hermes `terminal(background=true)` monitoring** (recommended for >3min tasks):
```bash
# Launch in background with notification (Hermes native pattern)
script -q -c "cat /tmp/codex-prompt.txt | timeout 600 codex \
    --dangerously-bypass-approvals-and-sandbox \
    -m 'gpt-5.4' \
    -c 'reasoning_effort=\"xhigh\"'" /dev/null \
    2>&1 | tee /tmp/codex-exec-output.txt &
echo "PID: $!"
# Then use terminal tool with: background=true, notify_on_complete=true
# Poll with process(action="poll", session_id="proc_...")

# Progress indicators while running:
wc -lc /tmp/codex-exec-output.txt   # file growth = alive
ls -la /tmp/<expected-output-file>  # Codex wrote a file = working
tail -20 /tmp/codex-exec-output.txt # last lines = current activity
```

**Working directory for exec mode:**
```bash
cd /path/to/project && cat /tmp/prompt.txt | codex exec ...
# OR
CODEX_WORK_DIR=/path/to/project cat /tmp/prompt.txt | codex exec ...
```

**Output capture patterns:**

| What Codex Does | Where It Shows Up |
|----------------|-------------------|
| Tool calls (`exec`, file writes) | stdout via `tee` |
| Files written via tool use | On disk at specified path |
| Final response | Last lines of stdout |
| Reasoning/thinking | Interleaved in stdout |

**Key differences from TUI mode:**

| Aspect | TUI (tmux-bridge) | exec (pipe) |
|--------|-------------------|-------------|
| Prompt delivery | Type into buffer (unreliable for long) | Stdin pipe (100% reliable) |
| Multi-turn | Yes, sequential prompts | No, single-shot |
| Output visibility | Requires tmux-bridge read polling | Direct stdout + tee file |
| Background | Survives in tmux session | Use shell `&` or terminal bg |
| File writing | Via tool calls in TUI | Same, via tool calls |
| Trust prompt | Interactive yes/no | Auto-trusts cwd |
| Best for | Interactive pair programming | Design specs, analysis, code gen |

### Decision Tree: TUI vs exec

```
Need multi-turn interactive conversation?
├── YES → Use TUI mode (Sections 4-8 above)
│   (But have exec as fallback if TUI hangs)
│
└── NO → Single-shot task?
    ├── Simple/short (<5 lines)?
    │   └── Either works; TUI is faster to start
    │
    └── Complex/long/design-doc?
        └── USE exec mode (this section)
            → Write prompt to file
            → Pipe to codex exec
            → Capture output with tee
            → Monitor file size / process
```

### Recovering from a Stuck TUI Session

If you launched TUI but it's not processing:

```bash
# 1. Check if prompt is sitting unsubmitted
TMUX="/home/linuxbrew/.linuxbrew/bin/tmux"
$TMUX capture-pane -p -t "$PANE_ID" -S -20 | tail -10

# 2. If you see your prompt text but no "Working..." indicator:
tmux-bridge keys "$PANE_ID" Enter   # Force submit

# 3. If still stuck after 60+ seconds, kill and switch to exec:
$TMUX kill-session -t "$SESSION_NAME"
cat /tmp/prompt.txt | codex exec ...  # Switch to exec mode
```

## Tips

- Always use **unique session names** (append timestamp) to avoid collisions
- Set working dir on `$TMUX new-session -d -s X -c <dir>` (TUI) or `cd` before `exec`
- `--dangerously-bypass-approvals-and-sandbox` is the default for this skill
- **Wait 2-3 seconds after launching** TUI before sending first prompt — TUI init time
- Sessions survive agent restarts — safe for long-running work (>15 min)
- To interrupt Codex mid-task: `tmux-bridge keys "$PANE_ID" Escape` (TUI) or kill process (exec)
- To safely exit TUI: `tmux-bridge message "$PANE_ID" "/exit"` then `tmux-bridge keys "$PANE_ID" Enter`
- **For complex prompts (>10 lines), prefer exec mode** — more reliable, captures all output
- **Write prompt to `/tmp/codex-prompt.txt` first** — avoids shell escaping nightmares
- **Use `tee` to capture exec output** — lets you monitor file size while Codex runs
- **Label your panes** with `tmux-bridge name "$PANE_ID" <label>` (TUI only)
- Session create/kill uses raw `$TMUX` — only pane interaction uses `tmux-bridge`
- **gpt-5.4 + xhigh can take 5-15 min for real work** — plan accordingly, use background mode

## Gotchas Discovered in Testing

### ⚠️ `codex exec` refuses piped stdin (CRITICAL — April 2026)
**This is the #1 gotcha for exec mode.** `codex exec` checks if stdin is a TTY and **refuses piped input**:

```bash
# ❌ THIS FAILS with "Error: stdin is not a terminal"
cat /tmp/prompt.txt | codex exec --dangerously-bypass-approvals-and-sandbox -m 'gpt-5.4' ...

# ✅ USE THIS INSTEAD — script(1) fakes a TTY around the pipe
script -q -c "cat /tmp/prompt.txt | codex exec --dangerously-bypass-approvals-and-sandbox -m 'gpt-5.4' ..." /dev/null
```

**Why this happens:** Codex exec uses a prompt that requires a terminal for its interactive elements (trust prompts, rich output rendering). When stdin is a plain pipe, it detects the missing TTY and exits immediately.

**The `script -q -c "..." /dev/null` pattern:**
- `script` spawns a pseudo-TTY (`/dev/ptmx`) wrapping the command
- `-q` = quiet mode (no "Script started" banner)
- `-c "..."` = command to run inside the pseudo-TTY
- `/dev/null` = discard the typescript log file (we capture via tee instead)

**All exec mode examples in this skill assume this wrapper.** If you see `Error: stdin is not a terminal`, wrap with `script`.

### ⚠️ TUI mode unreliable for long/complex prompts
**Discovered April 2026 during real-world usage with multi-paragraph design prompts:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| `tmux-bridge message` errors: "not running inside a tmux pane ($TMUX_PANE is unset)" | `message` subcommand has stricter guard than `type`/`keys` | Use `type` + separate `keys Enter`, or switch to exec mode |
| Prompt text lands in buffer but Codex never starts processing | `Enter` key press not delivered to TUI properly | Force submit: `tmux-bridge keys "$PANE_ID" Enter` multiple times, or kill and use exec |
| TUI sits at `›` prompt for 10+ minutes with no activity | Trust dialog consumed one Enter; second prompt needed another full cycle | Check if trust prompt (`1. Yes, continue`) is still pending |
| Long prompts get truncated by tmux-bridge type buffer | tmux-bridge has internal buffer limits for typed text | **Use exec mode instead** — no buffer limit via stdin pipe |

**Recommendation:** For any prompt >5 lines or containing markdown/code blocks, **default to `codex exec` mode** (see Alternative Mode section above). Only use TUI for genuinely interactive multi-turn sessions.

### TUI response visibility via capture-pane
The Codex TUI uses rich terminal rendering (alternate screen buffer, custom layout). **Responses may not appear clearly in `tmux-bridge read` output even when Codex has completed.** Use these signals instead:

| Signal | Meaning |
|--------|---------|
| `• Working (Xs • esc to interrupt)` | Actively processing |
| New `›` prompt appears after `Working` | **Task complete**, awaiting next input |
| Session disappears from `$TMUX_BRIDGE list` | TUI closed (error or `/exit`) |
| No change between polls | Still processing (gpt-5.4 + xhigh is slow) |
| Output file created on disk (e.g., `/tmp/codex-analytics-design.md`) | **Codex completed and wrote file** — most reliable signal for exec mode |

### Model availability (ChatGPT account)
If using a **ChatGPT account** (not API key), some models are **not available**:
- ❌ `o4-mini` — `"not supported when using Codex with a ChatGPT account"`
- ✅ `gpt-5.4` — works but slow with xhigh reasoning (~18k tokens even for simple prompts)
- Always verify model compatibility before launching long sessions
- Quick test: `timeout 30 codex exec --dangerously-bypass-approvals-and-sandbox -m '<model>' 'say ok'`

### gpt-5.4 + xhigh is SLOW
With `reasoning_effort="xhigh"`, gpt-5.4 produces massive token counts:
- Simple "say OK" → **~18k tokens**
- Real coding tasks → **5-10+ minutes**
- For faster iterations, override with `-c 'reasoning_effort="low"'`

**Timing calibration from real tasks (gpt-5.4 + xhigh):**

| Task Type | Tokens | Wall Time | Output Size |
|-----------|--------|-----------|-------------|
| Simple ("say OK") | ~18K | ~10s | <1KB |
| Code refactor (single file) | ~50-80K | 3-5 min | 20-40KB |
| Architecture / design spec (multi-file analysis) | ~130K+ | 10-15 min | 100-170KB |
| Full codebase analysis + code generation | ~200K+ | 15-25 min | 200KB+ |

**For Hermes agents**: Use `terminal(background=true, notify_on_complete=true)` for anything over 3 minutes, and monitor progress via `wc -lc` on the tee output file + `process(action="poll")`.

## Comparison: ask-claude vs ask-codex

| Feature | ask-claude | ask-codex |
|---------|-----------|-----------|
| CLI | `claudey` / `claude` (TUI) | `codex` (TUI) |
| Danger flag | `--dangerously-skip-permissions` | `--dangerously-bypass-approvals-and-sandbox` |
| System prompt | `--system-prompt` native | Prompt prefix `[SYSTEM: ...]` or `-c` overrides |
| Default model | (uses Claude's default) | **gpt-5.4 + xhigh reasoning** |
| Model override | `-m` | `-m` + `-c reasoning_effort=` |
| Web search | Built-in | `--search` flag |
| Multi-turn | Yes (TUI) | Yes (TUI) |
| Bridge tool | `tmux-bridge` | `tmux-bridge` |

## Related Skills

- [smux](../../.agents/skills/smux/SKILL.md) — Core tmux-bridge CLI reference and cross-pane communication patterns
- [tmux-background-session](../devops/tmux-background-session/SKILL.md) — Core tmux patterns for session lifecycle
- [ask-claude](./ask-claude/SKILL.md) — Equivalent skill for Claude Code (Anthropic)
- [codex](../codex/codex.SKILL.md) — Codex CLI usage reference
- [codex-exec-background](./codex-exec-background/SKILL.md) — Background execution without pipe traps
