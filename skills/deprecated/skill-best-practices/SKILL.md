---
name: skill-best-practices
description: Authors and structures professional-grade agent skills following the agentskills.io spec. Use when creating new skill directories, drafting procedural instructions, or optimizing metadata for discoverability. Don't use for general documentation, non-agentic library code, or README files.
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---
# Skill Authoring Procedure

Follow these steps to generate a skill that adheres to the agentskills.io specification and progressive disclosure principles.

## Bundled Path Rule

Resolve bundled paths relative to the directory that contains this `SKILL.md`. When invoking a helper from another working directory, expand `<skill-best-practices-dir>` to that directory first so the command is unambiguous.

## Step 1: Initialize and Validate Metadata
1.  Define a unique `name`: 1-64 characters, lowercase, numbers, and single hyphens only.
2.  Draft a `description`: Max 1,024 characters, written in the third person, including negative triggers.
3.  **Execute Validation Script (read-only helper):** Run the validation script to ensure compliance before proceeding:
    `python3 <skill-best-practices-dir>/scripts/validate-metadata.py --name "[name]" --description "[description]"`
4.  If the script returns an error, self-correct the metadata based on the `stderr` output and re-run until successful.

## Step 2: Structure the Directory
1.  Create the root directory using the validated `name`.
2.  Initialize the following subdirectories:
    *   `scripts/`: For tiny CLI tools and deterministic logic.
    *   `references/`: For flat (one-level deep) context like schemas or API docs.
    *   `assets/`: For output templates, JSON schemas, or static files.
3.  Ensure no human-centric files (README.md, INSTALLATION.md) are created.

## Step 3: Draft Core Logic (SKILL.md)
1.  Use the template in `assets/SKILL.template.md` as the starting point.
2.  Write all instructions in the **third-person imperative** (e.g., "Extract the text," "Run the build").
3.  **Enforce Progressive Disclosure:**
    *   Keep the main logic under 500 lines.
    *   If a procedure requires a large schema or complex rule set, move it to `references/`.
    *   Command the agent to read the specific file only when needed: *"Read references/api-spec.md to identify the correct endpoint."*

## Step 4: Identify and Bundle Scripts
1.  Identify "fragile" tasks (regex, complex parsing, or repetitive boilerplate).
2.  Outline a single-purpose script for the `scripts/` directory.
3.  Ensure the script uses standard output (stdout/stderr) to communicate success or failure to the agent.
4.  In `SKILL.md`, reference bundled helpers by a path that is unambiguous from the agent's working directory (the same path the agent will type to invoke them), rather than bare `scripts/helper.py` snippets that silently depend on CWD.
5.  Label each helper as **read-only**, **bootstrap**, or **mutating** so downstream agents know whether the helper only inspects state or changes it.

## Step 5: Final Logic Validation
1.  Review the `SKILL.md` for "hallucination gaps" (points where the agent is forced to guess).
2.  Verify all file paths are **relative** and use forward slashes (`/`).
3.  Verify every referenced helper path is unambiguous from the agent's working directory and that the helper's role (`read-only`, `bootstrap`, or `mutating`) is stated.
4.  Read `references/checklist.md` and cross-reference every checklist item against the final output.

## Error Handling
*   **Metadata Failure:** If `scripts/validate-metadata.py` fails, identify the specific error (e.g., "STYLE ERROR") and rewrite the field to remove first/second person pronouns.
*   **Context Bloat:** If the draft exceeds 500 lines, extract the largest procedural block and move it to a file in `references/`.
