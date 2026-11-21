# Pipeline shape

How the job graph is arranged. Sections are independent; read the ones the audit pointed at.

## Concurrency

Cancel superseded pull-request runs. Never cancel default-branch runs when they seed caches or when a deploy listens for their completion: a cancelled run saves nothing and deploys nothing.

```yaml
on:
  pull_request:
    # Code events only. `edited` restarts and cancels the suite on every title or body change.
    types: [opened, synchronize, reopened]
  push:
    branches: [main]
  workflow_dispatch:
concurrency:
  group: ci-${{ github.event_name == 'pull_request' && github.ref || github.sha }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

- Checks on PR metadata (title, body) go in their own workflow with their own group, triggered on `opened, edited, synchronize, reopened`. Keep it install-free when possible: piping the title to an already-installed commitlint needs a full dependency install, an action such as `amannn/action-semantic-pull-request` does not. Every run in that group validates the current title: a job-level `if:` that skips body-only edits lets a skipped run supersede an in-flight validation and become the PR's latest result.
- Adding `labeled` to the types makes every label change restart the run. Add it only for a label that selects lanes, and read labels live (`gh api`) so re-runs see them.
- If runner-minutes on frequent default-branch pushes matter more than per-SHA results and nothing listens to those runs, cancelling older default-branch runs is acceptable; state the trade.
- Removing default-branch cancellation changes what a `workflow_run` deploy sees: runs for two quick pushes now both complete, in either order. Add the stale-candidate guard from `references/release-deploy.md` §Ordering in the same change.
- Publish and deploy workflows use a group with `cancel-in-progress: false`.

## Scope

A `changes` job decides how much of the pipeline a pull request needs. Keep it conservative: an allowlist of what is provably safe to skip, everything else runs.

```yaml
changes:
  runs-on: ubuntu-latest
  timeout-minutes: 5
  outputs:
    scope: ${{ steps.paths.outputs.scope }}
  steps:
    - uses: actions/checkout@<pin>
      with:
        fetch-depth: 0
        filter: blob:none        # history without file contents: enough for --name-only
        persist-credentials: false
    - run: python3 scripts/ci-scope.py --self-test
    - id: paths
      env:
        EVENT: ${{ github.event_name }}
        BASE: ${{ github.event.pull_request.base.sha }}
        HEAD: ${{ github.event.pull_request.head.sha }}
      run: python3 scripts/ci-scope.py
```

`assets/ci-scope.py` is the starting script: it emits `scope=docs|<area>|all`, narrows only on `pull_request`, and returns `all` on any error. Pushes to the default branch are never narrowed, even in a repo where most commits are docs: that run is the only one that tests the merged result. The `changes` job itself runs on every event; an event-level `if:` on it skips every job downstream (see §Gate). Rules for the table inside it:

- **Docs scope** is only files that no check reads. Markdown that a formatter checks, a catalog a test validates, site content, HTML prototypes and agent instruction files consumed by a build are code. When the format check covers `*.md`, the docs scope still runs the format job.
- **Area scopes** (for example `site`) are worth adding only when the area's dependents are known; pair them with `turbo run <task> --filter=<pkg>...` so dependents still run. Tests in another package that drive the area (an E2E spec that submits the site's form) are dependents too.
- Before allowlisting a file as docs, search the tests and build scripts for its name. A `DESIGN.md` whose frontmatter a test parses is code.
- CI files, lockfiles, root configs, the scope script itself and anything unmatched select `all`.
- Use `git diff --no-renames`, otherwise the deleted side of a rename is invisible.

For a monorepo where most PRs touch one package, try `turbo run <tasks> --affected` (needs the base ref fetched; set `TURBO_SCM_BASE`) before writing a custom workspace mapper. `--affected` only sees files inside packages plus declared `inputs`/`globalDependencies`, so declare root files that change behavior.

**Where to skip.** Two options, with different gate requirements:

- *Step-level* `if:` on each expensive step. The job always runs and reports `success`, so the gate stays "all results are success". Costs one runner start per skipped job. Good default for a few jobs.
- *Job-level* `if:`. Saves the runner entirely, but the job reports `skipped`, jobs that `needs` it are skipped too unless they use `always()`, and the gate must know which skips were expected. Use it when there are many heavy jobs or queue time is significant.

## Gate

One job, always the same name, the only required check.

```yaml
ci:
  name: CI gate
  needs: [changes, quality, tasks, test, e2e]
  if: always()
  runs-on: ubuntu-latest
  timeout-minutes: 5
  steps:
    - name: Require every job the change needs
      env:
        RESULTS: ${{ toJSON(needs) }}
        # Jobs allowed to report `skipped` for this scope. Empty when skips are step-level.
        ALLOWED_SKIPS: ${{ needs.changes.outputs.scope == 'docs' && 'tasks test e2e' || '' }}
      run: |
        python3 - <<'PY'
        import json, os
        results = json.loads(os.environ["RESULTS"])
        allowed = set(os.environ["ALLOWED_SKIPS"].split())
        bad = [f"{name}={job['result']}" for name, job in results.items()
               if job["result"] != "success" and not (job["result"] == "skipped" and name in allowed)]
        if results.get("changes", {}).get("result") != "success":
            bad.append("changes did not succeed")
        if bad:
            raise SystemExit("Unsuccessful jobs: " + ", ".join(bad))
        PY
```

- GitHub treats a skipped required check as passing, so a wrong `if:` passes silently without this contract. `ALLOWED_SKIPS` must use the same condition as the jobs' `if:`.
- `changes` must be `success`; when it fails its outputs are empty and every dependent job is skipped.
- A matrix job's `needs.<job>.result` is `success` only if every leg succeeded, so shard counts can change without changing check names.
- Keep report-merging, flake-collection and other informational jobs out of the critical path: the gate depends on the test job itself, and the report job runs with `if: always()` beside it (or only on failure).
- Every new job goes into `needs`; a job missing from the gate is not gating.
- A job whose `needs` ancestor was skipped is skipped as well, through the whole chain, unless its `if:` starts with `always()` or `!cancelled()`. Walk every event (pull request, default-branch push, release push, dispatch, schedule) through the graph and confirm that publish and deploy jobs still run where they did before.
- A job with side effects (publish, deploy, tag) that used to follow one serial verify job now `needs` the gate, not a subset of the split jobs. The gate never needs that job.
- The skip rule above also reaches jobs behind the gate. When the gate tolerated a skipped need (a PR-title job that never runs on pushes), a job with `needs: gate` and an `if:` without a status function is skipped although the gate is green. Write `if: ${{ !cancelled() && needs.gate.result == 'success' && <event conditions> }}`.
- The gate covers one workflow. Checks that live in another workflow (a template scaffold matrix, a separate E2E workflow) are outside it: call that workflow from the gated one with `workflow_call` and add the call to `needs`, or name both checks as required in the owner follow-ups.

## Parallel jobs

Replace a serial chain (`format && lint && typecheck && test && build`) with jobs that all depend only on `changes`, so wall clock becomes the slowest job instead of the sum.

- Typical split: `quality` (format, lint, other static guards, seconds each: keep them together), `typecheck`, `test` (sharded when long), `build`, plus E2E.
- Keep the local aggregate script (`bun run verify`) working and documented; CI calls its parts. When docs say "CI runs the same command", update them.
- An unfiltered `turbo run test` discovers new packages and test projects by itself; lanes that name packages or projects do not. Add a catch-all lane for whatever no lane claims, or a check that fails when the discovered list and the lane list differ.
- Each job declares only the services it needs. A Postgres container on the typecheck job costs 15–25 s for nothing.
- Suites that share fixed ports, a database name or a dev server cannot run in parallel inside one job; give each its own job and service containers.
- Do not chain `build` before `test` unless tests consume build output. When they do, see "Build once" in `references/caching.md`.
- A check that runs in two places (a linter inside `verify` and again as its own workflow) runs once after the split; delete the duplicate, keep the blocking one.
- Memory-bound tools need their own leg or a concurrency cap (`turbo run typecheck --concurrency=1`, `NODE_OPTIONS=--max-old-space-size=…`) on small runners. A larger runner removes the cap.

## Lanes

Split fast checks (static, typecheck, unit, build) from heavy ones (browser E2E, integration, render, cross-platform) when the heavy lane is the PR critical path and sharding alone does not bring it down.

- Heavy lane triggers: default-branch push, nightly `schedule`, `workflow_dispatch`, a `ci:full` label, and any PR that changes CI itself.
- This moves failures to after the merge unless a merge queue (`merge_group` trigger, same job names) runs the heavy lane before it. Without a queue, post-merge failures land on the default branch with no PR author, so route them to an issue and keep the heavy lane mandatory for risky areas.
- It is a coverage trade and a repo-settings change, so propose it in the PR with numbers instead of applying it, unless the user asked. Prefer sharding and larger runners first: they keep the heavy lane on the PR.
- Noisy measurements (performance censuses, paired benchmarks) are not gates. Run them nightly or on dispatch and report to one tracking issue.

## Hygiene

- `timeout-minutes` on every job, about twice the slowest observed duration (5 for scope and gate jobs). The default is 6 hours.
- `permissions: contents: read` at workflow level; widen per job.
- `persist-credentials: false` on checkouts that do not push. Default shallow checkout everywhere except jobs that diff history.
- `fail-fast: false` on shard and platform matrices, so one red shard does not hide the others and `gh run rerun --failed` stays useful.
- Scheduled runs of the CI workflow must not redeploy: a `workflow_run` listener should require `github.event.workflow_run.event == 'push'`.
- Pin third-party actions the way the repo already does (commit SHA with a `# vX.Y.Z` comment, or tags). Do not mix styles in one PR.
