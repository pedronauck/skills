---
name: sync-provider
description: >
  Sync provider changes from cloned repositories in the providers/ folder. Use when syncing upstream changes from external provider repositories (claude-code, gemini, codex) while preserving local customizations. Includes multi-step workflow: checking for new commits via GitHub CLI, generating diffs, deep analysis, Pal MCP refactor planning, and applying changes incrementally. Never use for opencode provider (created locally, not cloned).
---

# Sync Provider

Sync changes from cloned provider repositories while preserving local customizations.

## Overview

Most providers (except `opencode`) are cloned from external repositories and need to be kept in sync with upstream changes. This skill guides the complete workflow from checking for updates to applying changes safely.

## Prerequisites

1. **GitHub CLI (`gh`)**: Must be installed and authenticated
   ```bash
   gh --version
   gh auth login
   gh auth status
   ```

2. **GitHub Token**: Add `GITHUB_TOKEN` to root `.env` file
   ```bash
   GITHUB_TOKEN=your_token_here
   ```

3. **Repository Info**: Each provider's `package.json` contains `repository.url` field (format: `https://github.com/owner/repo-name`)

## Workflow

### Step 1: Identify Provider and Repository

Check the provider's `package.json` for repository URL:

```bash
cat providers/<provider>/package.json | grep -A 2 repository
```

Extract owner/repo format: `https://github.com/owner/repo-name` → `owner/repo-name`

### Step 2: Check for New Commits

Use `check-provider-commit.sh` to automatically check for new commits:

```bash
COMMIT_HASH=$(scripts/check-provider-commit.sh <provider> 2>/dev/null)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ] && [ -n "$COMMIT_HASH" ]; then
  echo "Proceeding with sync from commit: $COMMIT_HASH"
elif [ $EXIT_CODE -eq 0 ]; then
  echo "Already up to date - no sync needed"
  exit 0
else
  echo "No state file found - need to determine initial commit hash manually"
  exit 1
fi
```

**Script Behavior:**
- **Up to date**: Exits with code 0, shows "Already up to date"
- **New commits**: Outputs commit hash (last synced), exits with code 0
- **No state file**: Exits with code 1, shows latest commit (requires manual determination for first sync)

**Important:** Redirect stderr (`2>/dev/null`) when capturing commit hash to avoid mixing informational messages.

### Step 3: Run Git Diff Script

Execute the sync script with appropriate parameters:

```bash
REPO=$(cat providers/<provider>/package.json | grep -A 2 repository | grep url | cut -d'"' -f4 | sed 's|https://github.com/||')

pnpm exec tsx scripts/git-diff.ts \
  -r $REPO \
  -c "$COMMIT_HASH" \
  -i "src/**/*" \
  -i "docs/**/*" \
  -i "examples/**/*" \
  --state-file-path ./providers/<provider>/diff_last_commit.txt
```

**Parameters:**
- `-r, --repo`: GitHub repository in `owner/repo` format (required)
- `-c, --commit`: Commit hash to compare from (required) - use last synced commit from state file
- `-i, --include`: Glob pattern(s) to filter files (can specify multiple times)
  - **Always use these three default patterns:**
    - `src/**/*` - All source files
    - `docs/**/*` - Documentation files
    - `examples/**/*` - Example files
- `--state-file-path`: Path to store last synced commit hash

### Step 4: Deep Research and Analysis

**MANDATORY**: Before applying any changes, perform deep research:

```bash
# List all generated diff files
ls -R .diffs/<commit_hash>/

# Review all diffs to understand scope
find .diffs/<commit_hash>/ -name "*.txt" -exec echo "=== {} ===" \; -exec cat {} \;

# Get list of affected files
find .diffs/<commit_hash>/ -name "*.txt" | sed "s|\.diffs/<commit_hash>/||" | sed 's|\.txt$||'
```

**Research Steps:**

1. **Analyze All Diffs**: Review every diff file to understand:
   - Files being modified, added, or removed
   - Nature of changes (bug fixes, features, refactoring, breaking changes)
   - Impact on existing local customizations
   - Dependencies between changes

2. **Check Local Customizations**: Review current local files to identify:
   - Custom modifications that might conflict
   - Local additions that should be preserved
   - Configuration differences

3. **Review Project Rules**: **MANDATORY STEP** - Check `.cursor/rules` to understand:
   - Which rules apply to this provider (TypeScript, React, etc.)
   - Project standards and patterns
   - Best practices for the technologies involved

### Step 5: Create Refactoring Plan Using Pal MCP

**MANDATORY**: Use Pal MCP refactor tool with Gemini 3.0 Pro to create comprehensive plan.

<critical>
- **TASK INVALIDATION**: **THE TASK WILL BE INVALIDATED** if you make ANY edits to files before completing ALL steps of the Pal Refactor tool
- **NO EXCEPTIONS**: You MUST complete the entire Pal Refactor workflow (all steps until `next_step_required: false`) before touching ANY files
- **VERIFICATION**: Only proceed to Step 7 after receiving confirmation that all Pal Refactor steps are complete
</critical>

**Refactor Tool Usage:**

1. **Identify Relevant Files**: Collect all files that will be affected:
   - Files from `.diffs/<commit_hash>/` that have changes
   - Current local files in `providers/<provider>/` that correspond to changed files
   - Use **FULL absolute paths** for all files

2. **Run Pal Refactor Analysis**:
   ```typescript
   // Use mcp_zen_refactor with:
   // - model: "gemini-3.0-pro" or "anthropic/claude-opus-4.6"
   // - relevant_files: Array of absolute paths to affected files
   // - refactor_type: "modernize" or "organization" (as appropriate)
   // - focus_areas: ["sync-upstream-changes", "preserve-local-customizations"]
   ```

3. **Complete ALL Steps**: **MANDATORY** - Finalize ALL steps until `next_step_required: false`
   - Continue calling the refactor tool until you receive confirmation that all steps are complete
   - Do NOT proceed to any file edits until this is confirmed
   - **TASK WILL BE INVALIDATED** if you skip this step

4. **Review Refactoring Recommendations**: The tool will provide:
   - Best approach for applying changes
   - How to preserve local customizations
   - Potential conflicts and how to resolve them
   - Code quality improvements
   - Architecture considerations

**Refactor Tool Requirements:**
- **Model**: Must use `gemini-3.0-pro` or `anthropic/claude-opus-4.6`
- **Multi-step**: Complete ALL steps until `next_step_required: false` - **NO EXCEPTIONS**
- **File Paths**: Use FULL absolute paths (e.g., `/Users/pedronauck/Dev/compozy/compozy-code/providers/claude-code/src/index.ts`)
- **Focus Areas**: Include context about syncing upstream changes while preserving local customizations
- **Completion Verification**: Only proceed when the tool confirms all steps are complete

### Step 6: Create Implementation Plan

Based on the Pal refactor analysis, create detailed implementation plan:

1. **Prioritize Changes**: Order by dependencies (apply dependencies first), risk level (low-risk first), impact (critical files first)

2. **Identify Conflicts**: Document files with local customizations that conflict with upstream changes, strategy for resolving each conflict, decisions on what to preserve vs. update

3. **Plan Testing Strategy**: Define which tests to run after each change, how to verify local customizations are preserved, integration points to test

4. **Document Decisions**: Record why certain changes are applied or skipped, how local customizations are preserved, any architectural decisions made

### Step 7: Apply Changes According to Plan

<critical>
- **VERIFICATION REQUIRED**: Before proceeding, verify that:
  1. All Pal Refactor steps are complete (`next_step_required: false`)
  2. You have received the complete refactoring analysis and recommendations
  3. You have created a detailed implementation plan (Step 6)
- **TASK INVALIDATION**: **THE TASK WILL BE INVALIDATED** if you start editing files before completing ALL Pal Refactor steps
- **NO EXCEPTIONS**: Even if you think you understand the changes, you MUST complete the full Pal Refactor workflow first
</critical>

**Only after completing steps 4-6 AND verifying Pal Refactor completion**, apply changes:

1. **For Modified Files**: Apply changes according to refactor plan, preserving local customizations
2. **For Added Files**: Add new files following project standards
3. **For Removed Files**: Evaluate if removal should be applied locally (may need to preserve)
4. **For Renamed Files**: Handle rename and content changes according to plan

**Best Practices:**
- Apply changes incrementally, following the prioritized plan
- Test after each significant change
- Preserve local customizations as identified in the plan
- Document any deviations from the plan

### Step 8: Update State File

After successfully applying changes, verify state file was updated:

```bash
cat providers/<provider>/diff_last_commit.txt
# Should contain the latest commit hash that was synced
```

## Example Workflow

### Syncing claude-code Provider

```bash
# 1. Check repository info
cat providers/claude-code/package.json | grep repository

# 2. Check for new commits
COMMIT_HASH=$(scripts/check-provider-commit.sh claude-code 2>/dev/null)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo "⚠️  No state file found - need to determine initial commit hash manually"
  exit 1
elif [ -z "$COMMIT_HASH" ]; then
  echo "✅ Already up to date - no sync needed"
  exit 0
fi

# 3. Extract repository name
REPO=$(cat providers/claude-code/package.json | grep -A 2 repository | grep url | cut -d'"' -f4 | sed 's|https://github.com/||')

# 4. Run sync script
pnpm exec tsx scripts/git-diff.ts \
  -r $REPO \
  -c "$COMMIT_HASH" \
  -i "src/**/*" \
  -i "docs/**/*" \
  -i "examples/**/*" \
  --state-file-path ./providers/claude-code/diff_last_commit.txt

# 5. Deep research and analysis
find .diffs/$COMMIT_HASH/ -name "*.txt" -exec echo "=== {} ===" \; -exec cat {} \;

# 6. Use Pal MCP refactor tool (complete all steps)
# 7. Create implementation plan
# 8. Apply changes according to plan
# 9. Verify state file updated
cat providers/claude-code/diff_last_commit.txt
```

## Available Providers

| Provider      | Repository                               | Notes                                |
| ------------- | ---------------------------------------- | ------------------------------------ |
| `claude-code` | `ben-vargas/ai-sdk-provider-claude-code` | Cloned                               |
| `gemini`      | `ben-vargas/ai-sdk-provider-gemini-cli`  | Cloned                               |
| `codex`       | `ben-vargas/ai-sdk-provider-codex-cli`   | Cloned                               |
| `opencode`    | N/A                                      | **Created locally** - no sync needed |

## Critical Requirements

<critical>
- **YOU MUST** use `gh` CLI to automatically check for new commits before syncing
- **YOU MUST** verify the repository URL from `package.json` before running the script
- **YOU MUST** always use the three default include patterns: `src/**/*`, `docs/**/*`, `examples/**/*`
- **YOU MUST** use the commit hash from the state file (last synced commit) as the `-c` parameter
- **YOU MUST** perform deep research and analysis of all diffs before creating a plan
- **YOU MUST** review `.cursor/rules` files to understand which rules apply (MANDATORY STEP)
- **YOU MUST NEED** to use the Pal MCP refactor tool with Gemini 3.0 Pro to find out the best way to apply changes
- **YOU MUST** complete ALL steps of the Pal refactor tool - don't stop the process in the middle
- **YOU MUST** verify Pal Refactor completion (`next_step_required: false`) before proceeding to any file edits
- **YOU MUST** create a detailed implementation plan based on the refactor analysis before applying changes
- **YOU MUST** use FULL absolute paths when using Pal MCP tools (never relative paths)
- **YOU MUST** preserve local customizations when applying upstream changes
- **YOU MUST** test the provider after applying changes (`pnpm test` in provider directory)
- **YOU MUST** run lint and typecheck after applying changes (`pnpm run lint && pnpm run typecheck`)
- **YOU MUST** update the state file path to match the provider directory structure
- **NEVER** sync `opencode` provider (it's created locally, not cloned)
- **NEVER** apply changes directly without deep research and planning first
- **NEVER** start editing files before completing ALL Pal Refactor steps
- **NEVER** use workarounds - always prefer good and well-designed solutions
- **ALWAYS** use the exact repository format: `owner/repo-name` (no `https://github.com/` prefix)
- **ALWAYS** check `.diffs/<commit_hash>/` folder exists and contains expected files before planning
- **ALWAYS** verify that `gh` CLI is authenticated (`gh auth status`)
- **ALWAYS** follow greenfield approach - don't care about backwards compatibility, prioritize quality
- **ALWAYS** double check which rules from `.cursor/rules` apply for the task before starting (MANDATORY STEP)
</critical>

## Troubleshooting

### No files matching glob pattern

- Check if the commit hash is correct
- Verify the repository name format
- Use broader patterns like `**/*` to see all changes

### State file not found

- **First sync**: Use the initial commit hash from when you cloned
- **Subsequent syncs**: The script creates the state file automatically

### Binary files detected

Binary files are noted in `.diffs/<commit_hash>/<file-path>.txt` but not diffed. Handle these manually:
- Images: Review in GitHub or download directly
- Other binaries: Decide if update is needed

### GitHub API rate limits

- Wait before retrying
- Use a GitHub token with higher rate limits
- Consider syncing in smaller batches

## After Syncing

- **MUST TEST**: Run tests in the provider directory:
  ```bash
  cd providers/<provider>
  pnpm test
  pnpm run lint
  pnpm run typecheck
  ```

- **MUST VERIFY**: Ensure all changes are correctly applied and no local customizations are lost

- **MUST DOCUMENT**: Record any decisions made during the sync process, especially:
  - Conflicts resolved
  - Local customizations preserved
  - Deviations from upstream changes
  - Architectural decisions
