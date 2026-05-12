#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE_DIR="$ROOT_DIR/skills"

# Surfaces that consume skills. Both Claude Code and OpenAI Codex expect a
# flat directory of skill folders, so we expose the same set to each.
TARGET_DIRS=(
  "$ROOT_DIR/.claude/skills"
  "$ROOT_DIR/.agents/skills"
)

# Categories of skills under skills/ that should be exposed to each surface.
# Externally installed skills (skills-lock.json) land inside one of these
# directories — usually skills/curated — so they are picked up automatically.
CATEGORIES=(
  "community"
  "curated"
  "marketing"
  "mine"
)

if [ ! -d "$SOURCE_DIR" ]; then
  echo "No skills/ directory found at $SOURCE_DIR, skipping skill symlink."
  exit 0
fi

for target_dir in "${TARGET_DIRS[@]}"; do
  mkdir -p "$target_dir"

  # Remove stale symlinks (broken targets) before relinking so we don't keep
  # pointers to skills that have been deleted or renamed.
  removed_stale=0
  for link in "$target_dir"/*; do
    [ -L "$link" ] || continue
    if [ ! -e "$link" ]; then
      rm "$link"
      removed_stale=$((removed_stale + 1))
    fi
  done

  linked=0
  for category in "${CATEGORIES[@]}"; do
    category_dir="$SOURCE_DIR/$category"
    [ -d "$category_dir" ] || continue

    for skill in "$category_dir"/*/; do
      [ -d "$skill" ] || continue
      skill_name="$(basename "$skill")"
      target="$target_dir/$skill_name"

      if [ -L "$target" ] || [ -e "$target" ]; then
        rm -rf "$target"
      fi

      # Use a path relative to the surface dir (both .claude/skills and
      # .agents/skills sit two levels under ROOT_DIR) so the link survives
      # moving the whole repo.
      ln -s "../../skills/$category/$skill_name" "$target"
      linked=$((linked + 1))
    done
  done

  rel_target="${target_dir#$ROOT_DIR/}"
  echo "Linked $linked skills from skills/{${CATEGORIES[*]// /,}} → $rel_target (removed $removed_stale stale link(s))"
done
