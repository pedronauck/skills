#!/usr/bin/env bash
# Scaffold a new topic folder for a Karpathy-style knowledge base.
#
# Usage: bash new-topic.sh <topic-slug> "<Topic Title>" <domain>
# Example: bash new-topic.sh rust-systems "Rust Systems Programming" rust
#
# Run from the vault root. Creates <topic-slug>/ with full subtree and
# template files populated from assets/.

set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: bash new-topic.sh <topic-slug> \"<Topic Title>\" <domain>" >&2
  echo "Example: bash new-topic.sh rust-systems \"Rust Systems Programming\" rust" >&2
  exit 1
fi

SLUG="$1"
TITLE="$2"
DOMAIN="$3"
TODAY="$(date +%Y-%m-%d)"

# Validate slug format
if [[ ! "$SLUG" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "ERROR: topic-slug must be lowercase alphanumerics separated by single hyphens (got: $SLUG)" >&2
  exit 1
fi

# Refuse to overwrite existing folder
if [[ -e "$SLUG" ]]; then
  echo "ERROR: $SLUG/ already exists. Remove it first or choose a different slug." >&2
  exit 1
fi

# Resolve assets directory relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS="$SCRIPT_DIR/../assets"

if [[ ! -d "$ASSETS" ]]; then
  echo "ERROR: assets directory not found at $ASSETS" >&2
  exit 1
fi

echo "Scaffolding topic: $SLUG ($TITLE, domain=$DOMAIN)"

# Create directory tree
mkdir -p "$SLUG/raw/articles" \
         "$SLUG/raw/bookmarks" \
         "$SLUG/raw/github" \
         "$SLUG/wiki/concepts" \
         "$SLUG/wiki/index" \
         "$SLUG/outputs/briefings" \
         "$SLUG/outputs/queries" \
         "$SLUG/outputs/diagrams" \
         "$SLUG/outputs/reports" \
         "$SLUG/bases"

# Substitute placeholders in a template file
render_template() {
  local src="$1"
  local dest="$2"
  sed -e "s/TOPIC_TITLE/$TITLE/g" \
      -e "s/TOPIC_DOMAIN/$DOMAIN/g" \
      -e "s/TOPIC_SLUG/$SLUG/g" \
      -e "s/YYYY-MM-DD/$TODAY/g" \
      "$src" > "$dest"
}

render_template "$ASSETS/dashboard-template.md" "$SLUG/wiki/index/Dashboard.md"
render_template "$ASSETS/concept-index-template.md" "$SLUG/wiki/index/Concept Index.md"
render_template "$ASSETS/source-index-template.md" "$SLUG/wiki/index/Source Index.md"
render_template "$ASSETS/topic-claude-template.md" "$SLUG/CLAUDE.md"
render_template "$ASSETS/log-template.md" "$SLUG/log.md"

# AGENTS.md → symlink to CLAUDE.md for Codex parity
ln -s CLAUDE.md "$SLUG/AGENTS.md"

# Placeholder .gitkeep files so empty dirs commit
touch "$SLUG/raw/articles/.gitkeep" \
      "$SLUG/raw/bookmarks/.gitkeep" \
      "$SLUG/raw/github/.gitkeep" \
      "$SLUG/wiki/concepts/.gitkeep" \
      "$SLUG/outputs/briefings/.gitkeep" \
      "$SLUG/outputs/queries/.gitkeep" \
      "$SLUG/outputs/diagrams/.gitkeep" \
      "$SLUG/outputs/reports/.gitkeep" \
      "$SLUG/bases/.gitkeep"

cat <<EOF

Topic '$SLUG' scaffolded.

Next steps:
  1. Add a row for '$SLUG' to README.md (topic table)
  2. (Optional — recommended at ~20+ sources) Create qmd collection:
       qmd collection add $SLUG/ --name $SLUG && qmd embed
  3. Start ingesting sources (Procedure 2 in karpathy-kb skill)
  4. Append every operation to $SLUG/log.md (Procedure 7)

Layout:
$(find "$SLUG" -type d | sort | sed 's/^/  /')
EOF
