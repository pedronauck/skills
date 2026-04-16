Goal (incl. success criteria):
- Implement the accepted plan to add explicit E2E coverage detection, planning, enforcement, and reporting across `skills/qa-report` and `skills/qa-execution`.
- Success means both skills, their references, shared templates, helper scripts, and discovery output consistently model when E2E is required, blocked, or manual-only.

Constraints/Assumptions:
- Follow `skills/skill-best-practices/SKILL.md` when editing skills.
- Default policy is balanced: require E2E updates for changed P0/P1 or regression-critical flows only when repository support already exists.
- Do not bootstrap a brand-new E2E harness; document blockers instead.
- Do not touch unrelated files or use destructive git commands.

Key decisions:
- `qa-execution` is the enforcement point.
- `qa-report` annotates plans and test cases with automation intent instead of creating a separate automation artifact.
- Shared verification and issue templates must expose automation follow-up explicitly.

State:
- Completed.

Done:
- Explored current skill docs, references, templates, helper scripts, and discovery script.
- Validated existing metadata for `qa-report` and `qa-execution`.
- Persisted the accepted plan under `.codex/plans/`.
- Updated `qa-execution` to discover and enforce E2E support, including a new `references/e2e-coverage.md`, stricter checklist/reporting, and a richer discovery script output.
- Updated `qa-report` to annotate automation intent in plans, test cases, regression guidance, and shared bug templates.
- Updated helper scripts to prompt for automation fields and fixed multiline markdown rendering in generated artifacts.
- Revalidated metadata, shell syntax, Python compile, and smoke-generated artifact output.

Now:
- Final response.

Next:
- None.

Open questions (UNCONFIRMED if needed):
- None.

Working set (files/ids/commands):
- `skills/qa-report/SKILL.md`
- `skills/qa-execution/SKILL.md`
- `skills/qa-execution/scripts/discover-project-contract.py`
- `skills/qa-execution/references/checklist.md`
- `skills/qa-execution/references/project-signals.md`
- `skills/qa-execution/references/web-ui-qa.md`
- `skills/qa-execution/assets/verification-report-template.md`
- `skills/qa-report/references/test_case_templates.md`
- `skills/qa-report/references/regression_testing.md`
- `skills/qa-report/scripts/generate_test_cases.sh`
- `skills/qa-report/scripts/create_bug_report.sh`
- `skills/qa-report/assets/issue-template.md`
- `skills/qa-execution/assets/issue-template.md`
