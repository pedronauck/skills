---
name: outside-to-issue
description: Transform outside-of-diff review files into properly formatted issue files for a given PR. Use when converting review files from ai-docs/reviews-pr-<PR>/outside/ into issue format in ai-docs/reviews-pr-<PR>/issues/. Automatically determines starting issue number and preserves all metadata (file path, date, status) from original review files.
---

# Outside to Issue

Transform outside-of-diff review files into properly formatted issue files for PR review tracking.

## Overview

This skill converts review files from the `outside/` directory into standardized issue files in the `issues/` directory, following the project's issue template format. The transformation preserves all metadata and automatically handles issue numbering.

## Usage

Run the transformation script for a specific PR:

```bash
scripts/transform-outside-to-issues.sh --pr <PR_NUMBER>
```

**Example:**
```bash
scripts/transform-outside-to-issues.sh --pr 90
```

## What It Does

1. **Finds all outside files**: Reads all `.md` files from `ai-docs/reviews-pr-<PR>/outside/` directory
2. **Determines starting issue number**: Automatically finds the highest existing issue number and starts numbering from the next available number
3. **Transforms each file**: Converts outside review files into issue format with:
   - Issue number and title
   - File path from the review
   - Date and status
   - Body section containing the review details
   - Footer indicating it's from outside-of-diff review

## File Structure

The script expects this directory structure:

```
ai-docs/reviews-pr-<PR>/
├── outside/
│   ├── 002-outside_01_<file-path>.md
│   ├── 002-outside_02_<file-path>.md
│   └── ...
└── issues/
    ├── 001-issue.md
    ├── 002-issue.md
    └── ...
```

## Output Format

Each transformed issue file follows this format:

```markdown
# Issue <NUMBER> - Outside-of-diff

**File:** `<file-path>`
**Date:** <date>
**Status:** <status>

## Body

<review-details-content>

---

_Generated from outside-of-diff review_
```

## Example

For PR 90 with 18 outside files:

```bash
scripts/transform-outside-to-issues.sh --pr 90
```

**Output:**
```
Created: issues/026-issue.md
Created: issues/027-issue.md
...
Created: issues/043-issue.md
Transformation complete! Created issues starting from 26
```

## Notes

- The script automatically determines the starting issue number based on existing issues
- Files are processed in sorted order (alphabetically by filename)
- All metadata (file path, date, status) is preserved from the original outside file
- The Details section content becomes the Body section in the issue file
- The script creates the `issues/` directory if it doesn't exist

## Related Commands

- `read_pr_issues.sh` - Read and display PR review issues
- `resolve_pr_issues.sh` - Mark issues as resolved and update GitHub threads
- `pr-fix` command - Fix issues for a given PR
