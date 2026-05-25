#!/usr/bin/env bash
# bootstrap-workspace.sh — MUTATING
# Creates the YC application workspace tree and seeds templates.
# Usage: bootstrap-workspace.sh <workspace-path>
# Refuses to clobber an existing 00_meta.md (resume instead).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TPL_DIR="$SKILL_DIR/assets"

if [ $# -lt 1 ]; then
  echo "ERROR: usage: bootstrap-workspace.sh <workspace-path>" >&2
  exit 1
fi

WS="$1"

if [ -f "$WS/00_meta.md" ]; then
  echo "ERROR: $WS/00_meta.md already exists. Resume with /yc-apply --resume '$WS' instead of bootstrapping." >&2
  exit 2
fi

mkdir -p "$WS"/{04_research,05_drafts,05_drafts/coding-session,06_video,07_interview,08_final}

CREATED="$(date +%Y-%m-%d)"

# Seed meta, founder-profile, idea-narrative, journal from templates.
sed "s/{{CREATED}}/$CREATED/g" "$TPL_DIR/template-00-meta.md" > "$WS/00_meta.md"
cp "$TPL_DIR/template-02-founder-profile.md" "$WS/02_founder-profile.md"
cp "$TPL_DIR/template-03-idea-narrative.md"  "$WS/03_idea-narrative.md"
sed "s/{{CREATED}}/$CREATED/g" "$TPL_DIR/template-09-journal.md" > "$WS/09_journal.md"

# 01_form-spec.md is intentionally NOT seeded here — Phase 0 copies the chosen
# batch spec or writes the founder's pasted live form.
touch "$WS/01_form-spec.md"

echo "OK: workspace bootstrapped at $WS"
echo "next: Phase 0 — fill 00_meta.md, capture 01_form-spec.md, set reapplicant flag."
