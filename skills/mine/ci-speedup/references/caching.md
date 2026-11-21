# Setup and caching

## Setup composite

Every job that installs dependencies calls one composite action (`.github/actions/setup/action.yml`; start from `assets/setup-action.yml`). It pins runtimes from version files, restores caches, installs with a frozen lockfile, and exposes inputs for what only some jobs need (Turbo cache writer, browsers). A job that needs no dependencies (scope, gate, Terraform, workflow lint) does not call it.

- Version sources are files (`.bun-version`, `.node-version`, `packageManager`), read by the setup actions. Grep for the version hardcoded elsewhere (other workflows, Dockerfiles) and leave those in sync.
- `bun install --frozen-lockfile` with `HUSKY=0`. Skip lifecycle scripts only when the repo does not rely on `postinstall` output.
- Cache the package manager's download cache (`~/.bun/install/cache`), not `node_modules`: restoring a large `node_modules` tree often costs as much as the linked install it replaces.

## Cache policy

Every cache restores everywhere and **saves only on default-branch pushes**. A cache saved from a pull request is scoped to that PR's merge ref, so no other PR can read it; it only fills the repository budget, evicts the default branch's entries and adds upload time. Pull requests read their own branch and the default branch, so the default branch is the only writer worth having.

- **Content-addressed keys** (lockfile hash, tool version): an exact hit is always correct. A PR that changes the lockfile runs cold until it merges; that is the accepted cost.
- **Run-scoped keys** (`…-${{ github.sha }}` with `restore-keys` prefixes: Turborepo, compiler and build caches): one entry per default-branch push.

```yaml
- if: github.event_name == 'push' && github.ref_name == github.event.repository.default_branch
  uses: actions/cache@<pin>            # restore now, save in the post step
  with: { path: .turbo/cache, key: "<key>-${{ github.sha }}", restore-keys: "<key>-" }
- if: ${{ !(github.event_name == 'push' && github.ref_name == github.event.repository.default_branch) }}
  uses: actions/cache/restore@<pin>
  with: { path: .turbo/cache, key: "<key>-${{ github.sha }}", restore-keys: "<key>-" }
```

- The same split applies to every writer, including the implicit ones: `oven-sh/setup-bun` saves the Bun executable in its post step unless `no-cache: true`, `actions/setup-node` with `cache:` saves on a miss, and Buildx `cache-to` writes whenever it is set. Gate each on the default-branch condition. After the first PR run, `gh api repos/<owner>/<repo>/actions/caches --jq '.actions_caches[] | [.ref, .key] | @tsv'` must list no `refs/pull/` entry.
- The default-branch run must finish for the save to happen, which is one reason not to cancel it (see `references/pipeline.md` §Concurrency).
- One entry per job or shard: put the job or task name in the key so parallel writers do not overwrite each other. End every `restore-keys` prefix with `-` so `test-1` does not match `test-10`.
- Budget: GitHub keeps 10 GB per repository and evicts least-recently-used entries; Ubicloud's transparent cache keeps 30 GB (100 GB with premium runners). Check with `gh api repos/<owner>/<repo>/actions/cache/usage` when jobs go cold at random.
- A cache that is saved but never restored by any job, or restored by a job whose task has `cache: false`, is pure cost. Remove it.

## Browsers

```yaml
- id: pw
  shell: bash
  run: echo "version=$(bunx --no-install playwright --version | sed 's/^Version //')" >> "$GITHUB_OUTPUT"
- id: pw-cache
  uses: actions/cache/restore@<pin>     # plus an `actions/cache/save` step gated on default-branch pushes
  with:
    path: ~/.cache/ms-playwright
    key: playwright-${{ runner.os }}-${{ runner.arch }}-chromium-${{ steps.pw.outputs.version }}
- shell: bash
  run: |
    if [ "${{ steps.pw-cache.outputs.cache-hit }}" = true ]; then
      bunx --no-install playwright install-deps chromium
    else
      bunx --no-install playwright install --with-deps chromium
    fi
```

- Key by the installed Playwright version, not the whole lockfile, so unrelated dependency bumps do not re-download browsers. Run the commands from the workspace that owns Playwright.
- The cache holds browser binaries, not the OS libraries; `install-deps` still runs. Install only the browsers each job launches (`chromium` alone when WebKit and Firefox suites live in another job).
- Only jobs that launch a browser install one. Keep `--no-install` so a missing dependency fails loudly instead of fetching `latest`.
- System tools installed with `apt-get` on every run (ffmpeg, Chrome) are the same shape: confirm the job needs the tool, then use a preinstalled binary, a cached static build, or move the install to the one job that needs it. If a suite skips silently without the tool, assert its presence.
- An install started in the background to overlap with dependency setup must hand its exit status to the step that joins it: the background command writes a success marker only after every command succeeded, and the join waits, requires the marker, then checks the tool. Checking only `<tool> --version` passes on a partial install.

## Turborepo

Fix correctness of the task graph before persisting any cache; a cache over a wrong hash replays stale green results.

- `outputs` declared for every task that produces files (nothing is restored otherwise); `outputs: []` for check tasks.
- `env` lists only variables that change the result. Secrets, CI flags and connection strings needed at runtime go in `passThroughEnv`, which is not hashed. A test task whose result depends on a service reached through a pass-through variable must stay `cache: false`.
- Files outside the package that change the result are declared as `inputs` (`"$TURBO_DEFAULT$", "$TURBO_ROOT$/shared/**"`) or `globalDependencies`. Keep lint-only configs out of `globalDependencies`: they invalidate every task.
- Dependencies linked from outside the repository are invisible to the hash; put their revision in the cache key or do not cache tasks that consume them.
- `typecheck` and `test` depend on a `transit` task (`"transit": {"dependsOn": ["^transit"]}`) instead of `^build` when packages are consumed from source: they invalidate on upstream source changes without waiting for upstream builds. Keep `^build` when consumers import built output.
- Tests that use real browsers, real time or external services stay `cache: false` unless every such input is in the hash. Caching `lint` and `build` is the safe majority of the gain.
- `typecheck` is safe to cache only when everything `tsc` reads is in the hash. A `tsconfig` whose `include` covers tests that import another workspace's sources (not a declared dependency), or a root config such as `vitest.shared.ts`, replays a stale green result. Declare those inputs or leave the task uncached.
- Exclusions in `inputs` (`!**/*.md`) are a claim that no task reads those files. Check shipped directories (`public/`) and tests that parse Markdown before excluding.

Then persist `.turbo/cache` (not `.turbo/runs`) with a run-scoped key per job, using the policy above. In shard matrices pass shard arguments after `--` so each shard hashes separately.

A remote cache (`TURBO_TEAM` plus a token or OIDC exchange, `TURBO_CACHE=local:rw,remote:r` on pull requests, signed artifacts) shares hits across branches and runners. It needs a backend and credentials the owner must provide, so list it as a follow-up; do not add secrets-dependent steps that fail or no-op without it.

## Build once

When several jobs each rebuild the same application (render suites, E2E shards, packaging), add one `build` job that uploads the output and let consumers download it.

```yaml
- uses: actions/upload-artifact@<pin>
  with: { name: app-build, path: <output dir>, retention-days: 1, if-no-files-found: error }
```

- Worth it when rebuild time × consumers exceeds upload + downloads. Hundreds of megabytes with many small files can be slower to move than to rebuild; archive to a single tarball first, or keep the rebuild and rely on the Turbo cache instead.
- Consumers `needs: build`, which puts the build on the critical path: the saving has to exceed that serialization.
- Name artifacts uniquely per variant and shard; short retention for intermediates.
- Consumers must test what the build produced from the event's commit. If the artifact omits files that consumers restore from their checkout, verify the two agree against the committed tree, not against the build job's working directory, which the build may have modified.

## Docker

```yaml
- uses: docker/setup-buildx-action@<pin>
- uses: docker/build-push-action@<pin>
  with:
    context: .
    file: <Dockerfile>
    push: false
    cache-from: type=gha,scope=<image>
    cache-to: type=gha,scope=<image>,mode=max
```

- One `scope` per image; `mode=max` caches intermediate stages. `type=gha` works unchanged on Ubicloud's transparent cache.
- Several images build as a matrix, not sequentially in one job. Build arm64 images on arm runners rather than under QEMU.
- On pull requests build images only when image inputs changed (Dockerfile, lockfile, the app's sources); default-branch runs always build.
- A Dockerfile stage that copies the whole repository before installing dependencies invalidates every layer on every commit. Copy manifests and lockfile, install, then copy sources.
