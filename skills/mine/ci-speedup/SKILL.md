---
name: ci-speedup
description: Speed up a repository's GitHub Actions CI, deploy and release workflows. Measures a per-job baseline, then applies change scoping, parallel jobs, caching, test sharding, a stable gate job and Ubicloud runners for private repos, delivered as one PR with before/after timings. Use when CI is slow or when asked to audit, optimize or port CI speed-ups to a repo; not for a first CI from scratch, one failing check, or non-GitHub CI.
---

# CI speedup

Make an existing GitHub Actions pipeline faster without reducing what it verifies. The deliverable is one pull request whose own CI runs prove the gain.

Most of the gain comes from the job graph (what runs, in parallel, on which diff), then from caches, then from runner size. Apply in that order and stop when the measured critical path is short: a pipeline that already finishes in about 3 minutes gets hygiene only (concurrency, timeouts), not machinery.

## Invariants

These hold for every change. They exist because each one has broken a real pipeline.

- **Same coverage.** Every check that gated a merge still gates it, or the PR names where it moved (default-branch push, nightly, label opt-in) and why. Never delete or weaken a test, loosen a lint rule, or add blanket retries to buy time.
- **Fail closed.** Scope selection runs everything on an unknown path, a failed diff, a malformed input, and every non-PR event.
- **No trigger-level `paths`/`paths-ignore`** on a workflow that provides a required check or that a deploy listens to: the check stays pending forever and the deploy never fires. Skip inside the workflow instead.
- **Keep contracts by name.** Before renaming anything, find who consumes it: required status checks, `workflow_run` listeners (they match the workflow `name:`), commit-subject prefixes used by release jobs, OIDC trusted-publisher configs (they match the workflow filename), files generated or synced from another repo.
- **One stable gate job** with `if: always()` is the only check to require. It must reject `failure`, `cancelled`, and any skip the scope did not ask for.
- **Side effects wait for the whole gate.** A job that publishes, deploys or tags depends on the gate for the exact commit, never on a subset of the split jobs. Letting default-branch runs finish instead of cancelling must not let an older commit deploy last (`references/release-deploy.md` §Ordering).
- **A split proves its own coverage.** Shards and lanes are checked against the inventory of what should have run; a green matrix alone does not show that (`references/tests.md` §Prove the partition).
- **Only the default branch writes caches.** Pull requests restore. This includes implicit writers such as setup actions and Buildx `cache-to`.
- **Runner rule.** In private or internal repos the heavy jobs run on Ubicloud; public repos stay on GitHub-hosted runners. Read `references/runners.md` before touching `runs-on`.
- **Repo settings are the owner's.** Branch protection, required checks, merge queue, GitHub App installs, secrets and variables are listed in the PR as follow-ups, not changed, unless the user asked for them.

## Procedure

1. **Isolate.** Work in a new worktree and branch from the up-to-date default branch (`origin/<default>`, not the local checkout, which may be dirty or behind). Use the harness worktree tool when there is one.
2. **Audit and measure.** Follow `references/audit.md`. Run `scripts/ci-baseline.sh <owner/repo>` (read-only, a few `gh` calls) to get per-job and per-step durations. Write down the critical path, the fixed per-job setup cost, the required check names, and every contract from the invariants. Do not run the project's test or build suites locally to measure; CI numbers are the evidence.
3. **Pick by payoff.** Use the table below against the measured numbers. Estimate each saving from the baseline and skip any change whose saving is smaller than the per-job setup cost it adds.
4. **Apply.** Follow the repo's existing conventions first (action pinning style, job naming, setup composite, lint of workflow files, commit format). `assets/` holds starting points for a repo that has none of the structure yet; adapt them, do not paste them over a working pipeline.
5. **Verify on the PR.** Push, open the PR, and read each job's result and duration on the pushed head. A job stuck `queued` on an Ubicloud label means the app is not installed for that repo: report it, do not switch the label back silently. Caches saved only on the default branch are cold on the PR, so say which numbers are cold. Deploy, publish and release paths do not run on a pull request: walk each event (pull request, default-branch push, release push, dispatch, re-run of failed jobs) through the changed job graph and write the result under Risks.
6. **Report** in the PR body using the format at the end.

## What to apply

| Measured symptom | Change | Read |
|---|---|---|
| New pushes pile up runs; title edits restart CI | PR-only cancel-in-progress; drop `edited` from PR types; title lint in its own tiny workflow | `references/pipeline.md` §Concurrency |
| Docs-only or single-area PRs pay the full pipeline | `changes` job with a conservative scope script, skips inside the workflow, gate that knows the expected skips | `references/pipeline.md` §Scope, §Gate |
| One serial `verify`/`check` chain dominates | Split into parallel jobs that depend only on `changes`; keep the local script intact | `references/pipeline.md` §Parallel jobs |
| A single test or E2E job is the critical path | Framework-native shards, per-suite jobs, worker settings matched to the runner | `references/tests.md` |
| Install, browser download or toolchain setup repeats in every job | One setup composite, content-addressed dependency cache, version-keyed browser cache, install only what the job needs | `references/caching.md` |
| Turborepo recomputes identical work on every run | Persist `.turbo/cache`, fix task `inputs`/`env`/`outputs` first; remote cache only if the owner provides one | `references/caching.md` §Turborepo |
| The same build runs in several jobs | Build once and pass an artifact, when the artifact is cheaper to move than to rebuild | `references/caching.md` §Build once |
| Docker builds from scratch | Buildx layer cache, one job per image, build only when image inputs changed | `references/caching.md` §Docker |
| Heavy suites gate every PR push | Fast lane on PRs, heavy lane on default-branch push/nightly/label; needs an owner decision | `references/pipeline.md` §Lanes |
| Private repo on 2-vCPU GitHub runners | Ubicloud labels sized to the job | `references/runners.md` |
| Deploy or release redoes CI work, or CI redeploys on cron | Reuse CI results, scope release packaging, non-cancelling publish group | `references/release-deploy.md` |
| Hung jobs hold runners | `timeout-minutes` at about twice the slowest observed duration | `references/pipeline.md` §Hygiene |

Bundled files:

- `scripts/ci-baseline.sh` (read-only): per-job and slowest-step durations for recent runs.
- `assets/ci-scope.py`: fail-closed PR scope selection with a built-in self-test.
- `assets/setup-action.yml`: Bun setup composite with dependency, Turbo and Playwright caches.
- `assets/ci.workflow.yml`: workflow skeleton with `changes`, parallel lanes, shards and `CI gate`.

## PR format

Title follows the repo's commit convention (commonly `ci: speed up CI with <main changes>`). Omit sections that would be empty.

```markdown
## Summary
<What was slow, what changed, and the measured result in one or two sentences.>

## Before / after
| Run | Wall clock | Critical path | Runner-minutes |
|---|---|---|---|
| Before (<run link>) | | | |
| After, cold caches (<run link>) | | | |

## Changes
- <mechanism>: <what and why, with the measured or expected saving>

## Coverage
<Checks that moved, were merged or were skipped by scope, and where each still runs. "Unchanged" when nothing moved.>

## Follow-ups for the owner
- <setting, secret, app install or decision the PR depends on or recommends>

## Risks
- <what could regress and how the gate or a later run catches it>
```
