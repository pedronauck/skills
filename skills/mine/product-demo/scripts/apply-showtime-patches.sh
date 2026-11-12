#!/usr/bin/env bash
# Applies the fluid-motion patch to the installed showtime skill. Safe to re-run.
# Usage: apply-showtime-patches.sh [path-to-showtime-skill]
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd -P)"
patch_file="$here/../patches/showtime-fluid-motion.patch"
target="${1:-$here/../../showtime}"
[ -f "$target/SKILL.md" ] || { echo "showtime skill not found at $target" >&2; exit 2; }
if patch -d "$target" -p1 -R --dry-run -s -f < "$patch_file" >/dev/null 2>&1; then
  echo "already patched: $target"; exit 0
fi
if ! patch -d "$target" -p1 -N --dry-run -s -f < "$patch_file" >/dev/null 2>&1; then
  echo "patch does not apply to $target: showtime changed upstream, port patches/showtime-fluid-motion.patch by hand" >&2
  exit 1
fi
patch -d "$target" -p1 -N -s -f < "$patch_file"
echo "patched: $target"
