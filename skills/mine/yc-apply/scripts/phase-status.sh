#!/usr/bin/env bash
# Read-only inventory. --submission validates recorded readiness, not claim truth.
set -euo pipefail
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Usage: phase-status.sh <workspace> [--submission]" >&2
    exit 1
fi
yc_workspace=$1
yc_mode=${2:-}
if [ -n "$yc_mode" ] && [ "$yc_mode" != "--submission" ]; then
    echo "Unknown mode: $yc_mode" >&2
    exit 1
fi
if [ ! -d "$yc_workspace" ]; then
    echo "Workspace does not exist: $yc_workspace" >&2
    exit 1
fi
printf 'workspace: %s\n' "$yc_workspace"
for yc_path in 00_meta.md 01_form-spec.md 05_drafts 06_video 06_gate.md 08_final/SUBMIT.md; do
    if [ -e "$yc_workspace/$yc_path" ]; then
        printf 'present: %s (content still requires review)\n' "$yc_path"
    else
        printf 'missing: %s (required only for its requested task)\n' "$yc_path"
    fi
done
for yc_path in 02_founder-profile.md 03_idea-narrative.md 04_research/summary.md 07_interview 09_journal.md; do
    if [ -e "$yc_workspace/$yc_path" ]; then
        printf 'optional: %s — available\n' "$yc_path"
    else
        printf 'optional: %s — not recorded; may be skipped\n' "$yc_path"
    fi
done
if [ "$yc_mode" != "--submission" ]; then
    echo "next_phase: requested task; no sequential coaching gate"
    exit 0
fi
yc_missing=0
for yc_path in 01_form-spec.md 08_final/SUBMIT.md; do
    if [ ! -s "$yc_workspace/$yc_path" ] || grep -q '{{' "$yc_workspace/$yc_path"; then
        printf 'required: %s — missing or template-only\n' "$yc_path"
        yc_missing=1
    fi
done
yc_record="$yc_workspace/06_gate.md"
for yc_key in form_current required_fields_complete claims_verified founder_reviewed; do
    if [ ! -f "$yc_record" ] || ! grep -qiE "^[[:space:]]*$yc_key:[[:space:]]*pass[[:space:]]*$" "$yc_record"; then
        printf 'required: %s — not confirmed in 06_gate.md\n' "$yc_key"
        yc_missing=1
    fi
done
if [ ! -f "$yc_record" ] || ! grep -qiE '^[[:space:]]*video_conforms:[[:space:]]*(pass|not_required)[[:space:]]*$' "$yc_record"; then
    echo "required: video_conforms — not confirmed against the current form"
    yc_missing=1
fi
if [ "$yc_missing" = 1 ]; then
    echo "submission_readiness: incomplete"
    exit 1
fi
echo "submission_readiness: recorded; verify the underlying facts before actual submission"
