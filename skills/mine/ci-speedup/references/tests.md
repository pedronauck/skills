# Tests

Use these when a test or E2E job is on the critical path. Find out first whether the job is slow because it is serial, because the runner is small, or because of setup; the fix differs.

## Split by suite before sharding

One job that runs every package's tests back to back becomes one job per independent suite (unit, database integration, browser/component, workflow). Each job starts only the services it needs. This also isolates suites that cannot share ports or databases.

Watch for cross-package test dependencies in `turbo.json` (`site#test` depending on `api#test`): a filter on one package pulls the other in.

## Shard a single long suite

Use the runner's own sharding; it needs no code.

```yaml
test:
  name: test (${{ matrix.shard }}/3)
  strategy:
    fail-fast: false
    matrix:
      shard: [1, 2, 3]
  steps:
    - run: bunx --no-install turbo run test --filter=<pkg> -- --shard=${{ matrix.shard }}/3
```

- Vitest and Playwright both accept `--shard=<i>/<n>`. Through Turborepo the flag goes after `--` and reaches every selected package's script, so filter to the package being sharded and run the small packages in a separate leg.
- Choose the shard count from the baseline: target shard time ≈ the next-slowest job. More shards than that only add setup cost and runner-minutes.
- Shards are split by file count, not duration. When one shard is more than about 1.5× the others, split by project or directory (`--project=desktop` / `--project=mobile`, a spec-file list per leg) or break up the dominant file. A duration-weighted partition from committed timing data is the last resort and needs a job that refreshes the timings.
- Keep check names stable for the gate by depending on the matrix job as a whole.
- Suites with their own selectors (`--categories`, `--items`) shard the same way: one matrix leg per selector group.

## Prove the partition

A green matrix proves each leg passed what it ran, not that the legs together ran everything. A selector that matches nothing, two legs wired to the same shard, or a package whose report went missing all stay green.

- Each leg writes a receipt of what it executed (test file paths, or item identities for selector-driven suites) to `$RUNNER_TEMP` and uploads it. Never write receipts to a tracked path: an `always()` upload after an early failure ships the committed copy.
- The gate, or a job the gate needs, compares the union of receipts with the inventory from the checkout (`git ls-files` patterns, or the suite's own listing). Missing entries, duplicates, unexpected entries and files in which every test was skipped fail the run. Agreed exclusions are an explicit list in that script.
- Compare identities, not counts. Matching totals hide one item run twice and another not at all.

## Workers and pools

- Match workers to the runner: Vitest `maxWorkers` around 75% in a job that owns the runner; Playwright `workers` above 1 only when tests do not share server state. A config comment such as "sized for a 2-core runner" must be revisited when the runner changes.
- Worker pools multiply with Turborepo's task concurrency. Cap one of them (`--concurrency`) when a job runs several test tasks at once, or memory runs out.
- Vitest `pool: "threads"` is faster than the default forks for pure-JS suites (measured about 20% on a large jsdom suite). Keep forks for tests that spawn processes, use native addons or rely on `process.chdir`. Validate by comparing the list of executed tests before and after.
- A Playwright `webServer` that starts a dev server per spec or per worker dominates short suites. Start it once per job, or serve the built output.

## Reports and retries

- With shards, each leg uploads a blob report (`--reporter=list,blob`); a separate job merges them. That job is informational: run it with `if: always()` (or only on failure) and keep the gate depending on the shard job directly, so merging never extends the critical path. It needs only Playwright, not a full install, when the repo allows it.
- Retries are CI-only and at most once (`retries: process.env.CI ? 1 : 0`). They are for known nondeterminism, not a speed-up; never add retries to make a slow or failing lane pass, and never retry whole jobs.
- A suite that skips when a variable, binary or service is missing must fail in CI instead. After moving a suite to its own job, confirm from the job output that it executed the expected number of tests.
