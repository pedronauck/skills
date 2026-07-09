---
name: skill-load-tips
description: >-
  Diagnoses and refactors existing SKILL.md files whose references or assets
  are ignored by agents. Applies Required Reading Routers, hard STOP directives,
  gist-tripwire trimming, and flat one-level reference structures so bundled
  context is loaded deliberately. Use when auditing or rewriting long skills
  that feel shallow despite deep reference files. Do not use for authoring new
  skills from scratch, non-skill Markdown, or documentation without SKILL.md
  front matter.
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---
# Skill Load Tips

Refactor pattern for SKILL.md files where the body is the only thing the agent ever reads. The references/ folder might as well not exist.

## The Failure Mode

Large skills frequently ship with rich reference files (`references/*.md`) that contain the load-bearing detail — full ARIA patterns, banned-vocab lists, before/after examples, archetypes — and a SKILL.md body that summarizes them. The agent reads the body, feels it has "enough," and never fans out. The reference files become dead weight.

This is the **inline-substitutes-for-reference antipattern**. It is the single most common reason a well-organized skill underperforms.

## Symptoms (how to spot it)

A SKILL.md likely has this problem if **two or more** apply:

- Body is over 250 lines and inlines checklists, tables, or banned-word lists that also live in a referenced file.
- The "Reference Index" / "Files" section is at the bottom, after the operating loop.
- References are introduced with hedged phrases: *"For depth, read X"*, *"see X for details"*, *"X has more"*.
- No upfront "router" mapping task → mandatory file.
- Reference files are linked from other reference files (deep nesting), not directly from SKILL.md.
- Reference files over 100 lines have no table of contents at the top.

## The Four Fixes (apply in order)

### Fix 1 — Add a Required Reading Router at the top

Insert a table immediately after the skill's opening paragraph (before any "Operating Loop" / "Steps" section). The table maps task type → file(s) that **MUST** be read for that task.

**Template:**

```markdown
## Required Reading Router

Match your task to the row. Read the listed files **in full before** producing output. They are not appendices — they are load-bearing. Inline content in this SKILL.md is a pointer, not a substitute.

| Task                                          | MUST read                                                    |
| --------------------------------------------- | ------------------------------------------------------------ |
| [Task type A]                                 | `references/file-a.md`                                       |
| [Task type B]                                 | `references/file-b.md` + `references/file-c.md`              |
| [Task type C]                                 | `references/file-d.md`                                       |
```

Pair the router with a **Reference Index** directly below it: one-line descriptions of *what each file contains*, so the router tells the agent *when* to load and the index tells *what they get*.

### Fix 2 — Use hard STOP directives in operating steps

Every step that has a corresponding reference file gets a forced-read directive at the end. Replace soft phrasing with imperative.

**Before:**
```markdown
For ARIA component patterns and verification recipes, read `references/accessibility-floor.md`.
```

**After:**
```markdown
**STOP. Read `references/accessibility-floor.md` in full before implementing or reviewing any interactive widget.** That file contains the complete ARIA patterns (dialog, combobox, menu, tabs, slider, listbox) and the verification recipes. The inline summary above is a tripwire, not the contract.
```

Three rules for STOP directives:

1. Bold the word **STOP**. It is a visual interrupt.
2. Name the trigger condition ("when implementing an interactive widget", "when extending tokens"). Not just "if you want depth."
3. State that the inline content is a tripwire, not the source of truth.

### Fix 3 — Trim duplicated inline content to gist tripwires

When a SKILL.md step contains a 10-bullet checklist that is also in a reference file, the agent reads the checklist and skips the reference. Cut the inline to a 2-3 line "tripwire" — enough for the agent to detect violations during scanning, but obviously incomplete.

**Before** (inline 10-bullet WCAG checklist):
```markdown
- Text contrast ≥ 4.5:1 (≥ 3:1 for large text)
- Non-text indicators contrast ≥ 3:1
- Focus visible (2px minimum)
- Keyboard reachable
- Target size ≥ 24×24
- prefers-reduced-motion honored
- Semantic landmarks
- Headings in order
- Form controls labeled
- Errors associated via aria-describedby
```

**After** (3-line tripwire + forced read):
```markdown
Gist tripwires — the floor items that catch most slop:

- Text contrast ≥ 4.5:1; focus-visible ≥ 2px on every interactive element.
- Full keyboard reachability; `prefers-reduced-motion` honored.
- Semantic landmarks + heading order; form controls programmatically labeled.

**STOP. Read `references/accessibility-floor.md` in full before implementing or reviewing any interactive widget.** The three bullets above are tripwires, not the contract.
```

Trim aggressively. If the inline list and the reference cover the same ground, the reference always wins.

### Fix 4 — Flatten reference depth to one level

Per Anthropic's docs: when references link to references, the agent uses partial reads (`head -100`) and misses content. All `references/*.md` files must be linked directly from SKILL.md, not from each other.

**Bad:**
```
SKILL.md → references/advanced.md → references/details.md
```

**Good:**
```
SKILL.md → references/advanced.md
SKILL.md → references/details.md
```

Also: any reference file over 100 lines needs a `## Contents` section at the top, so partial reads still surface the scope.

## Anti-Patterns

Things that look like fixes but aren't:

- **Adding "(important)" or emoji to existing trigger lines.** The agent reads tone, not decoration. Mandatory phrasing requires verbs (`STOP. Read…`), not adjectives.
- **Making references shorter so the body can stay inline.** The opposite of the goal. References should grow as the body shrinks.
- **Adding a "TL;DR" at the top of every reference file.** The agent reads the TL;DR and skips the body. Use a Contents TOC instead — names of sections, not summaries.
- **Renaming references to suggest urgency** (`URGENT-read-this.md`, `MUST-READ.md`). The filename does not change the read decision; the trigger phrasing in SKILL.md does.
- **Splitting SKILL.md into many small files at the same level.** SKILL.md is the single entry point. Multiple top-level skill files break discovery.

## Refactor Checklist

Before declaring a refactor done, verify against the rewritten SKILL.md:

- [ ] Required Reading Router exists in the first 50 lines (after intro/philosophy).
- [ ] Reference Index sits next to the Router.
- [ ] Every operating step that has a corresponding reference file ends with a `**STOP. Read references/X.md …**` directive.
- [ ] Inline checklists that duplicate reference content have been trimmed to ≤ 3 bullets, labeled as "tripwires" or "gist."
- [ ] No reference file links to another reference file (one level deep only).
- [ ] Reference files > 100 lines have a `## Contents` TOC at the top.
- [ ] SKILL.md body is under 500 lines (Anthropic's recommended ceiling).
- [ ] No `For depth, see X` or `Read X for more` phrasing remains — every reference mention is either router/index (descriptive) or a STOP directive (mandatory).

## How To Run a Refactor Pass

1. Open SKILL.md and the `references/` directory side by side.
2. Inventory: list every reference file and what it covers.
3. Diagnose: walk the Symptoms list above; mark each hit.
4. Apply Fix 1 (Router + Index), then Fix 2 (STOPs), then Fix 3 (trim inline), then Fix 4 (flatten depth + add TOCs).
5. Run the checklist. If any item is unchecked, the refactor is not done.
6. Test by asking a fresh agent instance to perform a task that requires a reference file. Observe whether it actually reads the file. If it doesn't, the STOP directive for that file is too weak — strengthen the trigger condition.

## When NOT To Use

- Authoring a new skill from scratch — use `skill-best-practices`.
- Editing reference files themselves without touching SKILL.md.
- Skills under 150 lines with no reference files (nothing to route).
- AGENTS.md / CLAUDE.md refactors — those follow different rules; use `agent-md-refactor`.

## Bottom Line

```
A reference file the agent never loads is a reference file that does not exist.
The body of SKILL.md is a dispatcher, not an encyclopedia.
Trim the inline. Force the load. Flatten the depth.
```
