# Audit and baseline

Read this before changing any workflow. The audit decides which mechanisms are worth applying; without it the usual result is machinery added to the wrong job.

## 1. Baseline numbers

```bash
scripts/ci-baseline.sh <owner/repo>                 # 3 latest completed runs of every workflow
scripts/ci-baseline.sh <owner/repo> ci.yml 5        # one workflow file, 5 runs
```

The helper is read-only and costs one `gh` call for the run list plus one per run. It prints, per run: event, branch, conclusion, wall clock, summed runner-minutes, and per job the runner labels, queue time, duration and three slowest steps. It never downloads logs; avoid `gh run view --log` too, since log downloads drain the API quota that other pipelines on the same token share.

Sample at least one PR run and one default-branch run of the main workflow, plus a deploy or release run when those exist. Record:

- **Critical path**: the chain of jobs that sets wall clock. Only changes on it reduce wall clock; everything else reduces cost.
- **Fixed per-job cost**: checkout + setup + cache restore + service containers, typically 25–60 s. Splitting a job adds this once per new job; a split is worth it only when the parallel saving is larger.
- **Queue time**: seconds between job creation and start. Long queues on third-party runners mean capacity or a missing app install, not a slow job.
- **Variance** between runs of the same step. A step that swings 2× on the same commit points at an undersized runner or contention, which sharding will not fix.
- **Cancelled and repeated runs**: several runs for one push or one SHA point at trigger types (`edited`, `labeled`) or overlapping workflows.

A repo with no completed runs has no baseline. Say so, apply the structural changes, and use the PR's own runs as the first measurement.

## 2. What already exists

Read every file in `.github/workflows/` and `.github/actions/` on `origin/<default>` and note, per job: `needs`, `if`, `runs-on`, `timeout-minutes`, matrix, services, caches, and the exact commands. Then read the entry points those commands call: `package.json` scripts (root and per workspace), `turbo.json`, `Makefile`, test runner configs (pool, workers, shards, retries, web servers), Dockerfiles.

Check for each mechanism in `SKILL.md`'s table whether it is present, partial or absent. Repos that share an owner tend to share a house pattern (for example a `changes` job calling `scripts/ci-scope.py`, a `.github/actions/setup` composite, a `CI gate` job, `.github/actionlint.yaml`). Extend the pattern that is there rather than introducing a second one.

## 3. Contracts and constraints

Collect these before designing the change; each one is a way to break something outside the CI workflow.

```bash
gh api repos/<owner>/<repo>/branches/<default>/protection   # 404 = no classic protection
gh api repos/<owner>/<repo>/rulesets                        # then /rulesets/<id> for rules
gh repo view <owner>/<repo> --json visibility,squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed
```

- **Required status checks and merge queue.** The exact context names must keep reporting. If nothing is required today, still keep the name the docs call "the required check".
- **`workflow_run` listeners.** `grep -rn "workflow_run" .github/workflows`. They match the triggering workflow's `name:` and usually its `conclusion`, `event` and branch. A cancelled default-branch run means no deploy for that SHA.
- **Commit-subject and title contracts.** Release jobs keyed on prefixes such as `build: release `; commitlint or a PR-title workflow.
- **Generated or synced workflow files.** A repo populated by a sync from another repo deletes files it does not own; a template repo copies its workflow into every generated project. Find the owning list or generator before adding files.
- **Workflow linters.** If CI runs `actionlint` or `zizmor`, new runner labels go in `.github/actionlint.yaml` and new steps must satisfy both.
- **Secrets, variables and environments** referenced by name, and which jobs need them. Fork PRs and Dependabot runs do not receive secrets.
- **Docs that describe CI.** `CONTRIBUTING.md`, `AGENTS.md`/`CLAUDE.md`, `docs/tooling.md` or similar. Update them in the same PR when the described behavior changes.
- **Test environment gates.** Suites that skip silently when a variable or binary is missing (`TEST_DATABASE_URL`, `ffmpeg`, a browser). A split job that forgets the variable goes green while running nothing; add an assertion that the suite ran or that the dependency is present.
- **Local checkout state.** `git status --short` and the current branch. Never base the audit or the change on a dirty or stale checkout.

## 4. Classify the bottleneck

| Shape in the baseline | Meaning | First move |
|---|---|---|
| One job ≫ the rest, one step inside it dominates | Serial chain or an unsharded suite | Split the chain; shard the suite |
| Many jobs, each with a large setup share | Setup cost repeated | Setup composite, caches, install only what the job needs |
| Every PR takes the same time regardless of diff | No scoping | Conservative scope with skips |
| Same step 2× slower on some runs, heavy memory use | Undersized runner | Larger runner before more shards |
| The same build or test appears in several jobs or workflows | Duplicate work | Run once; reuse by artifact or by result |
| Default-branch run repeats the PR run and then deploy rebuilds | Post-merge duplication | Keep the run that seeds caches and triggers deploy; remove the rebuild |
| Wall clock is fine, runner-minutes are high | Cost, not speed | Scope and dedupe; do not add shards |
