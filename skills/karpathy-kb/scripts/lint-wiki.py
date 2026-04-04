#!/usr/bin/env python3
"""
Lint a Karpathy-style knowledge base topic for structural issues.

Usage: python3 lint-wiki.py <topic-dir>
Example: python3 lint-wiki.py ai-harness/

Reports three classes of issues:
  1. Dead wikilinks    — [[Target]] where no matching .md file exists
  2. Orphan articles   — wiki/concepts/*.md with zero incoming wikilinks
  3. Missing sources   — frontmatter sources: entries pointing at nonexistent raw/ files

Exit codes:
  0 — no issues found
  1 — issues found (details on stdout)
  2 — usage or filesystem error
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path


WIKILINK_RE = re.compile(r"\[\[([^\[\]|#]+?)(?:\|[^\[\]]*?)?(?:#[^\[\]]*?)?\]\]")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def find_markdown_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def strip_code(text: str) -> str:
    """Remove fenced code blocks and inline code spans so their contents don't count as links."""
    text = FENCED_CODE_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def extract_wikilinks(text: str) -> list[str]:
    """Return the target portion of every [[wikilink]] in text (outside code).

    [[Name]]          → Name
    [[Name|Display]]  → Name
    [[Name#heading]]  → Name
    [[path/Name]]     → path/Name (kept — cross-topic path links)
    """
    clean = strip_code(text)
    return [m.group(1).strip() for m in WIKILINK_RE.finditer(clean)]


def extract_frontmatter_sources(text: str) -> list[str]:
    """Pull the sources: list entries out of YAML frontmatter. Naive parser."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return []
    fm = m.group(1)
    sources: list[str] = []
    in_sources = False
    for line in fm.splitlines():
        stripped = line.strip()
        if stripped.startswith("sources:"):
            in_sources = True
            continue
        if in_sources:
            if line.startswith(" ") or line.startswith("\t"):
                # list item
                if stripped.startswith("-"):
                    value = stripped.lstrip("-").strip().strip('"').strip("'")
                    # strip wikilink wrapper if present
                    if value.startswith("[[") and value.endswith("]]"):
                        value = value[2:-2]
                        # drop alias/heading
                        value = value.split("|")[0].split("#")[0].strip()
                    sources.append(value)
            else:
                in_sources = False
    return sources


def build_filename_index(files: list[Path]) -> dict[str, list[Path]]:
    """Map stem (filename without .md) → list of paths. Also map lowercase."""
    index: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        index[path.stem].append(path)
    return index


def resolve_wikilink(target: str, index: dict[str, list[Path]], vault_root: Path) -> Path | None:
    """Return the resolved file path for a wikilink target, or None."""
    # Strip any alias/heading fragment already handled, but be defensive
    target = target.split("|")[0].split("#")[0].strip()
    if not target:
        return None

    # Path-style target: resolve relative to vault root
    if "/" in target:
        candidate = vault_root / (target + ".md")
        if candidate.is_file():
            return candidate
        candidate_no_suffix = vault_root / target
        if candidate_no_suffix.is_file():
            return candidate_no_suffix
        return None

    # Bare-name target: match by stem
    if target in index:
        return index[target][0]
    return None


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 lint-wiki.py <topic-dir>", file=sys.stderr)
        return 2

    topic_dir = Path(sys.argv[1]).resolve()
    if not topic_dir.is_dir():
        print(f"ERROR: {topic_dir} is not a directory", file=sys.stderr)
        return 2

    vault_root = topic_dir.parent

    # Gather files inside the topic and across the whole vault (for cross-topic links)
    topic_files = find_markdown_files(topic_dir)
    vault_files = find_markdown_files(vault_root)
    vault_index = build_filename_index(vault_files)

    # Separate wiki concept articles from everything else in the topic
    wiki_concepts_dir = topic_dir / "wiki" / "concepts"
    concept_files = [p for p in topic_files if p.parent == wiki_concepts_dir]

    dead_links: dict[Path, list[str]] = defaultdict(list)
    incoming_links: dict[str, set[Path]] = defaultdict(set)
    missing_sources: dict[Path, list[str]] = defaultdict(list)

    for path in topic_files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"WARNING: could not read {path}: {exc}", file=sys.stderr)
            continue

        # Dead wikilinks
        for target in extract_wikilinks(text):
            resolved = resolve_wikilink(target, vault_index, vault_root)
            if resolved is None:
                dead_links[path].append(target)
            else:
                incoming_links[resolved.stem].add(path)

        # Missing sources (only relevant for wiki articles)
        if path.parent == wiki_concepts_dir:
            for source_ref in extract_frontmatter_sources(text):
                # URLs are acceptable source references; skip file-existence check.
                if URL_RE.match(source_ref):
                    continue
                resolved = resolve_wikilink(source_ref, vault_index, vault_root)
                if resolved is None:
                    missing_sources[path].append(source_ref)

    # Orphan concept articles: zero incoming wikilinks
    orphans = [p for p in concept_files if not incoming_links.get(p.stem)]

    # Report
    topic_rel = topic_dir.relative_to(vault_root)
    print(f"LINT REPORT — {topic_rel}/ — {len(concept_files)} concept articles")
    print()

    def rel(p: Path) -> str:
        try:
            return str(p.relative_to(vault_root))
        except ValueError:
            return str(p)

    total_issues = 0

    print(f"DEAD WIKILINKS ({sum(len(v) for v in dead_links.values())})")
    if dead_links:
        for src, targets in sorted(dead_links.items()):
            for target in targets:
                print(f"  {rel(src)} → [[{target}]]")
                total_issues += 1
    else:
        print("  (none)")
    print()

    print(f"ORPHAN ARTICLES ({len(orphans)})")
    if orphans:
        for path in sorted(orphans):
            print(f"  {rel(path)}")
            total_issues += 1
    else:
        print("  (none)")
    print()

    print(f"MISSING SOURCES ({sum(len(v) for v in missing_sources.values())})")
    if missing_sources:
        for article, refs in sorted(missing_sources.items()):
            for ref in refs:
                print(f"  {rel(article)} → sources: [[{ref}]]")
                total_issues += 1
    else:
        print("  (none)")
    print()

    if total_issues:
        print(f"TOTAL ISSUES: {total_issues}")
        return 1
    print("OK — no issues found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
