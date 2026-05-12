# BUG-<num>: <short-title>

**Severity:** Critical | High | Medium | Low
**Priority:** P0 | P1 | P2 | P3
**Type:** Functional | UI | Performance | Security | Data | Crash
**Status:** pending | resolved | invalid | flaky-suspect | quarantined
**Reopens task:** <task_NN.md path or "none">

> Status values (aligned with cy-codex-loop `issue_NNN.md` frontmatter):
> - `pending` — issue is open and unresolved
> - `resolved` — fixed during this QA run and verified by re-run
> - `invalid` — triaged as non-actionable (not a defect, duplicate, environmental)
> - `flaky-suspect` — one run failed, retry passed; awaiting confirmation runs per `references/flaky-triage.md`
> - `quarantined` — confirmed flaky after diagnosis; isolated from merge gate but still monitored (requires named owner and fix-by date)

## Environment

- **Build:** <version or commit>
- **OS:** <operating system if relevant>
- **Browser:** <browser and version if Web UI>
- **URL:** <page or endpoint where bug occurs>

## Summary

<Describe the observable failure in one short paragraph.>

## Reproduction

```bash
<exact command or sequence>
```

Observed before the fix:

- <observable result>

## Expected

<Describe the correct behavior.>

## Root cause

<Describe the actual source of the failure, not the symptom.>

## Fix

<Describe the production change that fixed the root cause.>

## Verification

- <narrow reproduction rerun>
- <broader regression or full gate rerun>

## Impact

- **Users Affected:** <all / subset / specific role>
- **Frequency:** <always / sometimes / rarely>
- **Workaround:** <describe or "none">

## Automation Follow-up

- **Required:** Yes | No
- **Status:** Added | Pending | Blocked | N/A
- **Spec / Command:** <path, suite, or command>
- **Notes:** <rationale or blocker>

## Flake Evidence (when Status is `flaky-suspect` or `quarantined`)

- **Failure Pattern:** consistent | intermittent | order-dependent | env-only
- **Reproducibility Rate:** <e.g. 3/10 runs>
- **Suspected Category:** async-wait | concurrency | order-dep | external | non-determinism | other
- **Owner:** <named person, not team>
- **Fix-by Date:** <YYYY-MM-DD>

## Related

- Test Case: <TC-ID if applicable>
- Figma Design: <URL if UI bug>
