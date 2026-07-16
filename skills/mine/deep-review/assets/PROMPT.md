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
2. Judge each owned hunk: correctness, security, concurrency, error handling, contract drift, resource leaks, test gaps, rule violations, and sibling paths that should mirror this change. Set `hunk` on every in-diff finding; outside-diff findings set `in_diff` false and `hunk` null.
3. Verify every finding against the checkout before recording it: read callers/callees, run targeted rg/grep, trace the failing input. Record each check in `evidence[]` as "command or file:line → what it showed". No concrete failure mode (or concrete improvement) → not a finding.
4. Apply the taxonomy suppression rules; findings a linter lane that ran already reports are void. Severity per the taxonomy — when torn, pick lower. Fill `suggestion` only with an exact, self-contained replacement.

OUTPUT CONTRACT: write ONLY valid JSON matching this schema to `{{output}}` — no other file, nothing to stdout: `{{schema}}`
Empty findings is a valid result after the full review. Validate the JSON before returning; the final response states only that the artifact was written.
<!-- /template -->

<!-- template:sweep -->
Global sweep "{{sweep_key}}" over {{target}}: {{lens}}. Read-only: never modify product, test, docs, or generated source — your only write is the output file named in the OUTPUT CONTRACT.

Read `{{context}}`, `{{manifest}}`, and `{{taxonomy}}` in full. Work from the manifest's selected files and hunks; read any repository file you need, see changes with `{{diff_command}}`, and run targeted rg/grep to confirm every suspicion. Cross-cohort findings are the point of this sweep — cohort reviewers own single-cohort defects. Record verification commands in `evidence[]`; apply the taxonomy's severity and suppression rules.{{spec_extra}}

OUTPUT CONTRACT: write ONLY valid JSON matching this schema to `{{output}}` — no other file, nothing to stdout: `{{schema}}`
Empty findings is valid only after the full lens. Validate the JSON before returning; the final response states only that the artifact was written.
<!-- /template -->
