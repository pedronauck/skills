#!/usr/bin/env bash
# journal-append.sh — MUTATING
# Appends a timestamped milestone entry to <workspace>/09_journal.md.
# Usage: journal-append.sh <workspace-path> "<entry text>" ["<detail line>"]

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "ERROR: usage: journal-append.sh <workspace-path> \"<entry>\" [\"<detail>\"]" >&2
  exit 1
fi

WS="$1"
ENTRY="$2"
DETAIL="${3:-}"
JOURNAL="$WS/09_journal.md"

if [ ! -f "$JOURNAL" ]; then
  echo "ERROR: $JOURNAL not found. Bootstrap the workspace first." >&2
  exit 2
fi

TS="$(date +%Y-%m-%dT%H:%M)"
{
  printf '\n## %s — %s\n' "$TS" "$ENTRY"
  if [ -n "$DETAIL" ]; then
    printf '  %s\n' "$DETAIL"
  fi
} >> "$JOURNAL"

echo "OK: journal entry appended to $JOURNAL"
