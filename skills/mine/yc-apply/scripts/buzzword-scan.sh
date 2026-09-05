#!/usr/bin/env bash
# buzzword-scan.sh — READ-ONLY
# Scans draft files for forbidden buzzwords / marketing-speak and prints hits
# with file:line. Advisory exit 0 by default; --strict exits 3 on hits. Never modifies anything.
# Usage: buzzword-scan.sh [--strict] <file-or-dir> [<file-or-dir> ...]

set -uo pipefail

STRICT=0
if [ "${1:-}" = "--strict" ]; then STRICT=1; shift; fi

if [ $# -lt 1 ]; then
  echo "ERROR: usage: buzzword-scan.sh [--strict] <file-or-dir> [...]" >&2
  exit 1
fi

# Case-insensitive ERE built from substring STEMS (no empty alternations — some
# greps, e.g. ugrep, reject "(a|b|)"). MUST stay in sync with the seed list in
# references/anti-patterns.md. Terms are contextual — the skill resolves each hit
# by contextual review; this scanner only flags.
PATTERN='revolutioniz|disrupt|leverag|synerg|ecosystem|hyper-|next-generation|cutting-edge|seamless|empower|unlock|end-to-end|democratiz|platform|world-class|game-chang|paradigm|stakeholder|holistic|frictionless|lifeblood|best-in-class|ai-powered|ai-native|transform the relationship|no competitors|no direct competition|in stealth|funding to start|funding to begin|some users|a few customers|a few users|passionate|dedicated|driven'

FILES=()
for arg in "$@"; do
  if [ -d "$arg" ]; then
    while IFS= read -r f; do FILES+=("$f"); done < <(find "$arg" -type f -name '*.md')
  elif [ -f "$arg" ]; then
    FILES+=("$arg")
  fi
done

if [ ${#FILES[@]} -eq 0 ]; then
  echo "OK: no markdown files found to scan."
  exit 0
fi

HITS=0
for f in "${FILES[@]}"; do
  while IFS= read -r line; do
    echo "$f:$line"
    HITS=$((HITS+1))
  done < <(grep -niE -- "$PATTERN" "$f" || true)
done

if [ "$HITS" -eq 0 ]; then
  echo "OK: 0 wording candidates across ${#FILES[@]} file(s)."
  exit 0
fi

echo "---"
echo "FOUND $HITS wording candidate line(s). Inspect context; keep accurate technical terms and improve vague claims."
if [ "$STRICT" = 1 ]; then exit 3; fi
exit 0
