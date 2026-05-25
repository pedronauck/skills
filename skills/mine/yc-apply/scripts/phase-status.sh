#!/usr/bin/env bash
# phase-status.sh — READ-ONLY
# Inspects a workspace and prints the detected phase + a completion checklist.
# Enforces the real per-phase invariants (not just file existence) so the skill
# cannot advance on template-only or partial work. Never modifies anything.
# Usage: phase-status.sh <workspace-path>

set -uo pipefail

if [ $# -lt 1 ]; then
  echo "ERROR: usage: phase-status.sh <workspace-path>" >&2
  exit 1
fi

WS="$1"

if [ ! -f "$WS/00_meta.md" ]; then
  echo "phase: none (no 00_meta.md) — needs Phase 0 bootstrap"
  exit 0
fi

META="$WS/00_meta.md"

check() {  # check <label> <0|1>
  if [ "$2" = "1" ]; then echo "  [x] $1"; else echo "  [ ] $1"; fi
}

has_file() { [ -s "$1" ] && echo 1 || echo 0; }

# Read a meta value: text after the first colon, strip an inline "# comment",
# trim only surrounding whitespace (internal spaces preserved), drop CR,
# lowercase. Returns the value on stdout.
meta_val() {
  grep -iE "^- *$1:" "$META" | head -1 \
    | sed -E "s/^[^:]*: *//; s/#.*$//; s/[[:space:]]+$//" \
    | tr -d '\r' | tr 'A-Z' 'a-z'
}

# 1 if a meta key has a non-empty value with no {{PLACEHOLDER}} left.
meta_real() {
  local v; v="$(meta_val "$1")"
  if [ -n "$v" ] && [ "${v#*\{\{}" = "$v" ]; then echo 1; else echo 0; fi
}

# A template-seeded prose file is "filled" once non-empty and all {{...}} gone.
filled() { [ -s "$1" ] && ! grep -q '{{' "$1" 2>/dev/null && echo 1 || echo 0; }

REAPPLICANT="$([ "$(meta_val reapplicant)" = "true" ] && echo 1 || echo 0)"
INVITED="$([ "$(meta_val interview_invited)" = "true" ] && echo 1 || echo 0)"
DECISION="$(meta_val decision)"

# --- Phase 0: meta has real values AND form spec captured -------------------
META_OK=$([ "$(meta_real batch)" = 1 ] && [ "$(meta_real company_slug)" = 1 ] \
  && [ "$(meta_real target_deadline)" = 1 ] && [ "$(meta_real reapplicant)" = 1 ] \
  && echo 1 || echo 0)
FORM=$(has_file "$WS/01_form-spec.md")
P0=$([ "$META_OK" = 1 ] && [ "$FORM" = 1 ] && echo 1 || echo 0)

# --- Phase 1: founder profile filled with a versioned, named section --------
PROFILE=$([ "$(filled "$WS/02_founder-profile.md")" = 1 ] \
  && grep -qE '— v[0-9]' "$WS/02_founder-profile.md" 2>/dev/null && echo 1 || echo 0)

# --- Phase 2: idea narrative filled with a numeric Idea Quality average ------
IDEA=$([ "$(filled "$WS/03_idea-narrative.md")" = 1 ] \
  && grep -qiE 'average.*[0-9]' "$WS/03_idea-narrative.md" 2>/dev/null && echo 1 || echo 0)

# --- Phase 3: all 5 research slices + summary, each with Findings + a URL ----
research_ok() {
  local d="$WS/04_research" s
  [ -s "$d/summary.md" ] || { echo 0; return; }
  for s in 01_founder-footprint 02_competitive-landscape 03_market-tam \
           04_regulatory-context 05_traction-signals; do
    [ -s "$d/$s.md" ] || { echo 0; return; }
    grep -qiE '^## *Findings' "$d/$s.md" || { echo 0; return; }
    grep -qiE 'https?://' "$d/$s.md" || { echo 0; return; }
  done
  echo 1
}
RESEARCH=$(research_ok)

# --- Phase 4: a draft per high-stakes field (count [HIGH] markers if present) -
DRAFT_COUNT=$(find "$WS/05_drafts" -maxdepth 1 -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
HIGH_COUNT=$(grep -ciE '\[high' "$WS/01_form-spec.md" 2>/dev/null || true)
HIGH_COUNT=${HIGH_COUNT:-0}
if [ "$HIGH_COUNT" -gt 0 ]; then
  DRAFTS=$([ "$DRAFT_COUNT" -ge "$HIGH_COUNT" ] && echo 1 || echo 0)
else
  DRAFTS=$([ "$DRAFT_COUNT" -ge 1 ] && echo 1 || echo 0)
fi

# --- Phase 5: founder video bullet notes ------------------------------------
VIDEO=$(has_file "$WS/06_video/notes.md")

# --- Phase 6: gate artifact with no unchecked boxes and a PASS/FORCE result --
gate_ok() {
  local g="$WS/06_gate.md"
  [ -s "$g" ] || { echo 0; return; }
  grep -q '\[ \]' "$g" && { echo 0; return; }   # any unchecked box → not passed
  grep -qiE 'result: *(pass|force-submit)' "$g" && echo 1 || echo 0
}
GATE=$(gate_ok)

# --- Phase 7: paste-ready submission pack ------------------------------------
FINAL=$(has_file "$WS/08_final/SUBMIT.md")

echo "workspace: $WS"
echo "reapplicant: $REAPPLICANT   interview_invited: $INVITED   decision: ${DECISION:-pending}"
echo "drafts: $DRAFT_COUNT present / $HIGH_COUNT high-stakes fields"
echo "completion:"
check "Phase 0  bootstrap (real meta + form spec)"   "$P0"
check "Phase 1  founder profile (named, versioned)"  "$PROFILE"
check "Phase 2  idea narrative + numeric score"      "$IDEA"
check "Phase 3  research: 5 slices + summary + URLs"  "$RESEARCH"
check "Phase 4  draft per high-stakes field"         "$DRAFTS"
check "Phase 5  founder video notes"                 "$VIDEO"
check "Phase 6  pre-submit gate (06_gate.md PASS)"   "$GATE"
check "Phase 7  submission pack (08_final/SUBMIT)"   "$FINAL"

# Decide the next phase to resume (strict ordering through the gate).
NEXT="0 bootstrap"
[ "$P0" = 1 ]       && NEXT="1 founder-profile"
[ "$PROFILE" = 1 ]  && NEXT="2 idea-stress-test"
[ "$IDEA" = 1 ]     && NEXT="3 external-research"
[ "$RESEARCH" = 1 ] && NEXT="4 drafts"
[ "$DRAFTS" = 1 ]   && NEXT="5 founder-video"
[ "$VIDEO" = 1 ]    && NEXT="6 pre-submit-gate"
[ "$GATE" = 1 ]     && NEXT="7 submission-pack"
[ "$FINAL" = 1 ]    && NEXT="8 interview-prep (set interview_invited: true to unlock)"

if [ "$DECISION" = "rejected" ]; then
  NEXT="9 post-mortem (decision=rejected)"
elif [ "$INVITED" = 1 ] && [ "$FINAL" = 1 ]; then
  NEXT="8 interview-prep"
fi

echo "next_phase: $NEXT"
