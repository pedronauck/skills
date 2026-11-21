# Deploy and release workflows

These are slower to iterate on and riskier to change than CI. Change them only where the audit shows duplicated or serialized work, and keep every contract listed in `references/audit.md` §3.

## Do not repeat what CI proved

- **Publish re-running the full verification.** When the publish job runs on a commit whose CI run is green, gate on that result instead of re-running it: trigger publish from `workflow_run` of CI, or check the commit's check runs/status before publishing. Keep the checks that are specific to the artifact (packing, tarball smoke test). The result must be the whole gate for the exact SHA being published, not a subset of jobs and not the branch's latest run.
- **Packaging or release rehearsal on every pull request.** Scope it to release PRs (title or branch prefix), changes to packaging inputs, or a label. Guard every job of that workflow with the same condition.
- **Deploy rebuilding the application CI built.** Reuse the Turbo cache with the same key family as CI, or have the deploy consume an artifact or image digest. Publish the bytes that were tested where the publish is irreversible (npm, tagged images).
- **Scheduled CI triggering a deploy.** A `workflow_run` listener deploys only when `github.event.workflow_run.event == 'push'`.

## Shorten the deploy path

- Independent steps run as parallel jobs: build the SPA while the API image rolls out, publish after both. Keep ordering only where correctness needs it (migrations before the app, staging before production).
- Image builds use the layer cache and one job per image (`references/caching.md` §Docker).
- Poll loops (rollout status, registry propagation) get explicit timeouts and intervals; they are often the largest step and cannot be sped up, so start them as early as their inputs exist.
- Heavy runners per `references/runners.md`; the rule covers deploy and release jobs in private repos.

## Ordering

A deploy that follows CI completions deploys in completion order, not push order. While default-branch pushes cancelled each other only the newest run could finish; once they all finish, an older commit can go green last and be deployed over a newer one.

- Decide eligibility twice. Before the run joins the deploy concurrency group, a job outside that group compares the candidate SHA with the branch tip and stops stale candidates, so a stale run cannot replace a newer pending one (GitHub keeps one pending run per group). Inside the group, immediately before the first mutation, compare again.
- A stale candidate skips the deploy and every status or marker it would have written. A later stage that trusts that status must not see success for a commit that was not deployed.
- "Re-run failed jobs" reuses the successful jobs of the old attempt. Every mutating job revalidates the candidate itself, including the second half of a split deploy (SPA after API), or a re-run publishes old output over a newer deploy.
- The tip lookup fails visibly. Validate the value against `^[0-9a-f]{40}$` before comparing: an empty or malformed API answer that compares unequal is otherwise classified as "stale" and a valid deploy disappears with a green run. The same applies to cloud lookups read with `--output text`, where an empty result is the literal `None`.
- A job that names an `environment` records a GitHub deployment when it starts and a success status when it ends green, even if its guard skipped every step. Build jobs and guarded jobs that may no-op use `environment: { name: <env>, deployment: false }` (secrets, variables, reviewers and wait timers still apply; custom deployment protection rules do not support it), so the environment history shows only what was published.
- A manual dispatch with an explicit ref stays the way to deploy an older commit on purpose; keep it outside the stale check.

## Concurrency and reruns

```yaml
concurrency:
  group: deploy-${{ github.ref }}       # or release-<channel>
  cancel-in-progress: false
```

- Never cancel a publish or deploy in progress. GitHub keeps one pending run per group, so queued deploys collapse to the latest.
- When one workflow both validates PRs and publishes, give the publish path its own group suffix so a routine push cannot cancel it.
- Design irreversible steps to be re-runnable: probe first (`npm view <pkg>@<version>`, existing tag or release) and exit cleanly when the identical result exists, fail when the state cannot be determined. Then `gh run rerun --failed` resumes instead of restarting.
- `fail-fast: false` on platform matrices, for the same reason.
- Validate required secrets in the first step of a long job, so a missing one fails in seconds instead of after the build.

## Release automation

A bot-maintained release PR (version bump and changelog, merged to publish) keeps release validation off ordinary PRs. It needs a PAT or App token (PRs opened with `GITHUB_TOKEN` do not start workflows), full history with tags, and conventional commits; the release commit prefix becomes a contract. Adopting it is a process change: propose it, do not add it as part of a speed-up PR.
