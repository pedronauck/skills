---
name: deps-update
description: Upgrade every dependency of a Bun repo to latest with `bun update --recursive --latest` in an isolated git worktree, research what each upgrade breaks, adapt the code until the checks pass, and open a PR in a fixed format. Use when asked to update or bump all deps to latest in a Bun project; not for a single-package upgrade or other package managers.
---

# Deps update

The upgrade runs in its own worktree and branch, never in the user's checkout. Stop and say so if the repo has no `bun.lock`/`bun.lockb`.

## 1. Worktree

Fetch, then create a branch `chore/deps-latest-<YYYY-MM-DD>` from the up-to-date default branch in a new worktree. Use the harness worktree tool when there is one (CompozyOS `compozy__worktree_create`, Claude Code `EnterWorktree`); otherwise `git worktree add ../<repo>-deps-<date> -b <branch> origin/<default>`. Every later step runs inside it.

## 2. Baseline

Find the project's real checks (typecheck, lint, test, build) from `package.json` scripts and the CI workflow. Run `bun install` and those checks once before upgrading and record failures: they are pre-existing, not caused by the upgrade.

## 3. Upgrade

```bash
bun update --recursive --latest
```

Build the change list from `git diff -- '**/package.json'`: package, workspace, old → new, and bump type. Treat a major bump, and a minor bump of a `0.x` package, as breaking.

## 4. Research what breaks

For every breaking bump, read the release notes or migration guide for the exact range crossed (not only the newest version):

- `npx ctx7@latest library <name> "migration <old> to <new>"` then `npx ctx7@latest docs <id> "<topic>"` (the `context7`/`find-docs` skill);
- fallback: `gh release list/view -R <owner>/<repo>` or the repo's CHANGELOG; Exa/Firecrawl only when those miss.

Then grep the codebase for each removed or changed API, config key, peer dependency, or runtime/Node requirement. Classify each package as **needs adaptation** (our usage is affected) or **no change needed** (with the reason). Patch/minor bumps get researched only when a check fails because of them.

## 5. Adapt and verify

Fix the code at the call sites, following the migration guide and existing repo patterns. Run the checks again and repeat until they match or beat the baseline. Never silence the failure (`@ts-ignore`, skipped or weakened tests, loosened lint rules). If one upgrade can't be done in this PR, pin only that package to its previous version and record why under **Held back**.

When the repo has an app, start it and exercise what the breaking upgrades touch; checks alone don't cover runtime behavior.

## 6. Commit and PR

Commit with the repo's commit convention: first `chore(deps): update all dependencies to latest` (package.json files + lockfile only), then one commit per adaptation (`fix(deps): adapt to <pkg> v<N>`). Push the branch and open the PR against the default branch with `gh pr create --body-file`. Write the PR in the language of the repo's recent PRs (English by default). Omit sections that would be empty.

Title: `chore(deps): update all dependencies to latest (<YYYY-MM-DD>)`

```markdown
## Summary
<N> packages updated across <M> workspaces (<X> breaking). <One sentence on adaptations and check status.>

## Updated packages
| Package | Workspace | From | To | Bump |
|---|---|---|---|---|
<breaking bumps first, then minor, then patch>

## Breaking changes and adaptations
### <pkg> <old> → <new>
- **What changed:** <the change that hit us> ([release notes / migration guide](<url>))
- **Impact here:** <files or features affected>
- **Done:** <what was changed>

## Reviewed, no change needed
- **<pkg> <old> → <new>:** <breaking change and why our usage isn't affected>

## Held back
- **<pkg>** kept at <version>: <reason and what unblocks it>

## Validation
| Check | Before | After |
|---|---|---|
| `<command>` | <pass / N failures> | <pass / N failures> |

<Pre-existing failures, and what was exercised in the running app.>

## Risks and follow-ups
- <runtime behavior the checks don't cover, deprecations to address later>
```

Report to the user the PR URL, the worktree path, and any held-back package.
