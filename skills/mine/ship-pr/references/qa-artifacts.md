# QA artifacts in the PR description

## Contents

1. When this section applies
2. Where artifacts live
3. What to extract
4. PR-body `## QA` template
5. Examples
6. Pitfalls

## 1. When this section applies

Include a `## QA` section in the PR description only when the pre-flight detector reports a non-empty `qa_output_paths` array. Those paths are produced by the `qa-report` and `qa-execution` skills (or any equivalent flow). When none are present, **omit the QA section entirely** — do not write "no QA performed", which reads as a red flag to reviewers.

The detector accepts a manual override via the `QA_OUTPUT_PATH` environment variable (point at a single `qa/` directory) for repos that put artifacts somewhere other than `.compozy/tasks/<slug>/qa/`.

## 2. Where artifacts live

The convention in `compozy/agh` and sister repos is:

```
.compozy/tasks/<slug>/
└── qa/
    ├── verification-report.md          # the summary (may not exist for all runs)
    ├── issues/                          # one file per bug filed, BUG-NNN.md
    ├── screenshots/                     # PNGs, named <journey-id>-step<N>.png
    ├── test-cases/                      # TC-NNN.md
    ├── test-plans/                      # charters, journey maps
    └── external-bootstrap/              # tooling bootstrap manifests
```

Not every directory is guaranteed to be present. Probe before reading:

```bash
QA_DIR=".compozy/tasks/<slug>/qa"
test -d "$QA_DIR/screenshots" && ls "$QA_DIR/screenshots"
test -f "$QA_DIR/verification-report.md" && head -40 "$QA_DIR/verification-report.md"
ls "$QA_DIR/issues" 2>/dev/null | wc -l
```

## 3. What to extract

For the PR body, pull these signals:

- **Bug count and severity** — count files in `qa/issues/`. If each file has a frontmatter `severity:` field, tally by severity (Blocker / Critical / Major / Minor). If `verification-report.md` exists, prefer the totals it states explicitly over re-counting.
- **Charter coverage** — list the test-plan charter names (filenames in `qa/test-plans/charters/` or section headings in `verification-report.md`).
- **Screenshot evidence** — pick 2-5 representative PNGs from `qa/screenshots/`. Use repo-relative paths so GitHub renders them inline in the PR description (uploaded screenshots also work, but file paths in the repo are stable).
- **Blocked sessions / coverage gaps** — quote the `verification-report.md` section that lists what could not be tested, if any.

## 4. PR-body `## QA` template

```markdown
## QA

**Coverage:** <one sentence — which personas / journeys ran, e.g. "3 personas across 5 user journeys, Money-Tour + Onboarding-Tour charters">

**Issues filed:** <total> (Blocker: N, Critical: N, Major: N, Minor: N) — see `.compozy/tasks/<slug>/qa/issues/`.

**Evidence:**
- ![onboarding-step3](.compozy/tasks/<slug>/qa/screenshots/onboarding-step3.png)
- ![checkout-step5](.compozy/tasks/<slug>/qa/screenshots/checkout-step5.png)

**Gaps:** <copy the "blocked" or "not tested" paragraph from verification-report.md, or "None">.

**Full report:** [`verification-report.md`](.compozy/tasks/<slug>/qa/verification-report.md)
```

Adjust counts and paths to the real artifacts. If `verification-report.md` is absent, drop that line and the **Gaps** field, then add `> No verification-report.md was produced by this QA run — counts derived from `qa/issues/`.` so reviewers know the source.

## 5. Examples

**With a verification report present:**

```markdown
## QA

**Coverage:** 2 personas (free-tier, paid-pro) across the Money Tour and Onboarding Tour charters.

**Issues filed:** 4 (Blocker: 0, Critical: 1, Major: 2, Minor: 1) — see `.compozy/tasks/checkout-v2/qa/issues/`.

**Evidence:**
- ![money-tour-step3-pricing-plan-selector](.compozy/tasks/checkout-v2/qa/screenshots/money-tour-step3.png)
- ![onboarding-step5-welcome-modal](.compozy/tasks/checkout-v2/qa/screenshots/onboarding-step5.png)

**Gaps:** Stripe webhook handler retried but could not be verified end-to-end because the staging webhook secret was unset.

**Full report:** [`verification-report.md`](.compozy/tasks/checkout-v2/qa/verification-report.md)
```

**Sparse run (issues only, no report):**

```markdown
## QA

**Coverage:** Manual smoke test on Chrome 121 / macOS 14 for the new auth flow.

**Issues filed:** 1 (Minor: 1) — see `.compozy/tasks/auth-fix/qa/issues/BUG-001.md`.

**Evidence:**
- ![login-error-toast](.compozy/tasks/auth-fix/qa/screenshots/login-error-toast.png)

> No verification-report.md was produced by this QA run — counts derived from `qa/issues/`.
```

## 6. Pitfalls

- **Do not stage QA artifacts into the PR commit unless they are intended to ship.** They are reference material for reviewers, not production code. If they live under `.compozy/tasks/`, they may already be `.gitignore`d — verify before committing.
- **Do not paste base64-encoded screenshots into the PR body.** Use repo paths or GitHub-uploaded attachments; base64 dumps make the description unreadable in the GitHub UI.
- **Do not invent severities.** If `qa/issues/` files lack frontmatter severity, report total count only and skip the severity breakdown.
- **Do not link absolute paths** (`/Users/...`). Use repo-relative paths so the links work for everyone.
