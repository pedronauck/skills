#!/usr/bin/env bash
# buzzword-scan.sh — READ-ONLY
# Scans draft files for forbidden buzzwords / marketing-speak and prints hits
# with file:line. Exit 0 = clean, exit 3 = hits found. Never modifies anything.
# Usage: buzzword-scan.sh <file-or-dir> [<file-or-dir> ...]

set -uo pipefail

if [ $# -lt 1 ]; then
  echo "ERROR: usage: buzzword-scan.sh <file-or-dir> [...]" >&2
  exit 1
fi

# Case-insensitive ERE built from substring STEMS (no empty alternations — some
# greps, e.g. ugrep, reject "(a|b|)"). MUST stay in sync with the seed list in
# references/anti-patterns.md. Terms are contextual — the skill resolves each hit
# by rewrite or journaled rationale; this scanner only flags.
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
  echo "OK: 0 lines with banned terms across ${#FILES[@]} file(s)."
  exit 0
fi

echo "---"
echo "FOUND $HITS line(s) containing a banned term (a line may carry several). For each: rewrite with a concrete noun/verb, or journal a rationale in 09_journal.md."
exit 3
