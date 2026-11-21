# Runners

## The rule

- **Private or internal repository:** heavy jobs run on Ubicloud managed runners. Heavy means anything that installs dependencies, compiles, tests, renders, builds images or deploys. Jobs that finish in seconds without an install (scope, gate, PR-title lint) may stay on `ubuntu-latest`; follow what the repo already does.
- **Public repository:** GitHub-hosted runners, which are free there. Do not add Ubicloud labels.

Check visibility with `gh repo view <owner>/<repo> --json visibility` (`INTERNAL` counts as private).

## Prerequisite: the app must cover the repository

A job whose label no runner serves stays `queued` until it times out. Before switching labels:

```bash
gh api orgs/<org>/installations --jq '.installations[] | select(.app_slug=="ubicloud-managed-runners") | .repository_selection'
```

- No output: the app is not installed on the organization. `selected`: it is installed for chosen repositories, and the API does not say which ones without an app token.
- Evidence that a repository is covered: an existing workflow there already runs on a `ubicloud-*` label, or the first PR run gets picked up within a minute.
- When the app is missing or the PR's jobs stay queued, report it as an owner follow-up (connect the organization in the Ubicloud console under GitHub Runners and select the repository). Do not revert to GitHub-hosted labels to get a green run: that hides the unmet rule.

## Labels

`ubicloud-standard-<vcpu>` for x64 and `ubicloud-standard-<vcpu>-arm` for arm64, with vCPU in 2, 4, 8, 16, 30; append `-ubuntu-2204` or `-ubuntu-2404` to pin the OS (24.04 is the default).

| Label | vCPU | Memory |
|---|---|---|
| `ubicloud-standard-2` | 2 | 8 GB |
| `ubicloud-standard-4` | 4 | 16 GB |
| `ubicloud-standard-8` | 8 | 32 GB |
| `ubicloud-standard-16` | 16 | 64 GB |
| `ubicloud-standard-30` | 30 | 120 GB |
| `ubicloud-standard-<n>-arm` | n | 3 GB per vCPU |

Label names and limits change; confirm against https://www.ubicloud.com/docs/github-actions-integration/runner-types when in doubt.

## Sizing

Price scales linearly with vCPU, so a job that uses the cores costs the same on a larger runner and finishes sooner; a job that does not use them just costs more.

- `ubicloud-standard-2`: format, lint, short static checks, Terraform validation, anything I/O-bound.
- `ubicloud-standard-4`: default for typecheck, unit tests, builds. Removes memory workarounds written for 7–8 GB runners (serialized `tsc`, reduced heaps); delete the workaround only after a run proves it.
- `ubicloud-standard-8` and up: suites that parallelize across cores (many test files, browser workers, render farms, large image builds). Raise the tool's worker count in the same change, or the extra cores sit idle.
- arm labels: native arm64 image builds and deploys.
- Size from the baseline: a step whose duration swings between runs or that sits at the memory limit wants a larger runner before it wants more shards. Sharding and a bigger runner multiply cost together, so pick the cheaper one that reaches the target.

## Wiring

- If the repo lints workflows with actionlint, declare every label in `.github/actionlint.yaml`:

  ```yaml
  self-hosted-runner:
    labels:
      - ubicloud-standard-2
      - ubicloud-standard-4
  ```

- Ubicloud's transparent cache serves `actions/cache`, `actions/setup-*` caching and Buildx `type=gha` without workflow changes, so the same YAML works on both runner types.
- The images track GitHub's Ubuntu images, but do not assume a tool is present: confirm on the first run that Chrome, ffmpeg, Docker, Python or whatever the job shells out to is there, and that Docker service containers start.
- Deploy and release workflows in private repos follow the same rule. A documented exception (for example a deploy that must use GitHub-hosted runners for an OIDC or network reason) stays, and the PR says so.
- Leave a short comment at the first Ubicloud job saying the labels need the Ubicloud GitHub App on the organization; it is the first thing the next reader needs when jobs queue.
