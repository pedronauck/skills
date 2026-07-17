# Deep-review prompt templates

The single source of truth for every prompt the fan-out dispatches. `build_jobs.py` renders these blocks — edit wording here, nowhere else. Consistency is enforced twice at render time: the build fails if a template lost a mandatory `{{placeholder}}`, and fails again if any placeholder survives unfilled in a rendered prompt.

Placeholders are `{{snake_case}}` tokens. Mandatory sets live in `build_jobs.py` (`REVIEWER_PLACEHOLDERS`, `SWEEP_PLACEHOLDERS`).

<!-- template:reviewer -->
Review cohort "{{cohort_name}}" (risk: {{risk}}) of {{target}}. Read-only: never modify product, test, docs, or generated source — your only write is the output file named in the OUTPUT CONTRACT.

The unit of judgment is the HUNK; whole files are context.

FILES — you own every listed hunk:
{{file_list}}
{{scope_instruction}}

CONTEXT: read `{{context}}` (change intent, linters that already ran, spec contract when present) and `{{taxonomy}}` (category/severity grammar, profile gate, suppression rules) in full before judging.

REPO RULES bound to these files — when a finding violates one, set its `rule_id` and quote the rule verbatim in `guideline`:
{{rules_block}}

REVIEW:
1. Read every cohort file in full — hunks lie without their surroundings. See each change with `{{diff_command}}`. For status A files the whole file is the new-side hunk. For status D read `git show {{base}}:<file>` and judge the old-side hunk plus surviving callers.
2. FIND broadly. For each owned hunk, form concrete failure hypotheses across correctness, security, concurrency, error handling, contract drift, resource leaks, test gaps, rule violations, and sibling paths that should mirror the change. Treat each as a candidate until Step 3. When one pattern may repeat, search the whole cohort and enumerate every occurrence under one finding's `also_applies`.
3. REFUTE each candidate against the checkout: read the changed premise, callers and callees; trace a named input/state through the path; run targeted rg/grep or a focused check. Promote only candidates that survive refutation and have a concrete failure mode (or measurable improvement). `evidence[0]` is the one-line certificate `Premise: <observed fact at file:line> → Path: <named caller/input/control flow> → Verdict: <resulting failure or improvement>`. Record later checks as `command or file:line → what it showed`.
4. REPORT narrowly. Apply every taxonomy suppression rule, then assign severity so impact cannot bias the investigation. Findings a linter lane that ran already reports are void. Set `hunk` on every in-diff finding; outside-diff findings set `in_diff` false and `hunk` null. Fill `suggestion` only with an exact, self-contained replacement.

OUTPUT CONTRACT: write ONLY valid JSON matching this schema to `{{output}}` — no other file, nothing to stdout: `{{schema}}`
Empty findings is a valid result after the full review. Validate the JSON before returning; the final response states only that the artifact was written.
<!-- /template -->

<!-- template:sweep -->
Global sweep "{{sweep_key}}" over {{target}}: {{lens}}. Read-only: never modify product, test, docs, or generated source — your only write is the output file named in the OUTPUT CONTRACT.

Read `{{context}}`, `{{manifest}}`, and `{{taxonomy}}` in full. Work from the manifest's selected files and hunks; read any repository file you need and see changes with `{{diff_command}}`. FIND concrete cross-cohort hypotheses through this lens, enumerate every occurrence, then REFUTE each by tracing callers/callees and running targeted rg/grep or a focused check. REPORT only survivors: `evidence[0]` is the taxonomy's `Premise → Path → Verdict` certificate, later entries record `command or file:line → what it showed`, and repeats go in `also_applies`. Cross-cohort findings are the point of this sweep — cohort reviewers own single-cohort defects. Apply the taxonomy's suppression rules before assigning severity.{{spec_extra}}

OUTPUT CONTRACT: write ONLY valid JSON matching this schema to `{{output}}` — no other file, nothing to stdout: `{{schema}}`
Empty findings is valid only after the full lens. Validate the JSON before returning; the final response states only that the artifact was written.
<!-- /template -->
