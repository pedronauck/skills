# Context Pack

How to assemble `<out>/context-pack.md` — the shared context every reviewer and sweep receives. **Keep it lean: target ≤ ~10 KB.** Every agent in the fan-out reads it in full, so each extra kilobyte is paid once per agent; reviewers dig into the code themselves (rg, git, file reads), so the pack carries only what they cannot cheaply rediscover — intent, review law, and what the linters already caught.

## 1. Rubric — the review law

Collect, in precedence order (higher wins on conflict):

1. **Path instructions** — top-level `path_instructions` in `.deep-review.yaml`, else `reviews.path_instructions` in `.coderabbit.yaml` (first file that defines them wins); each entry is a glob + verbatim instructions.
2. **Learnings** — `.deep-review/learnings.md` entries whose scope glob matches selected files.
3. **Guideline files** — discovered at any depth, **directory-scoped** (a guideline governs its directory subtree; nearest file wins): `CLAUDE.md`, `AGENTS.md`, `AGENT.md`, `REVIEW.md`, `DESIGN.md`, `CONTRIBUTING.md`, `.cursorrules`, `.cursor/rules/*`, `.github/copilot-instructions.md`.

For each source, extract only rules that can bind a review verdict (error handling, testing shape, layering, security, naming, tokens/design constraints) — skip build lore and tooling walkthroughs. Register each rule once, in the machine-readable registry `<out>/rules.json`:

```json
{ "rules": [ { "id": "R07", "scope": ["**/*_test.go"],
               "source": ".deep-review.yaml", "guideline": "MUST use t.Run(\"Should...\") pattern for ALL test cases" } ] }
```

`scope` = glob list: the path_instructions glob, the guideline file's directory subtree (`dir/**`), or the learning's scope glob. Keep rule text verbatim — reviewers cite it and findings carry the rule id. The pack itself lists only the rubric *sources* consulted (one line each); `build_jobs.py` injects each cohort's bound rules into its prompt, so the full registry never needs to be re-read by agents.

## 2. Linter lanes — run first, suppress overlaps

Detect what the repo already enforces and run it scoped to selected files; findings a lane reports are suppressed from the review (taxonomy rule 1).

| Signal in repo | Lane command (scope to changed files where supported) |
| --- | --- |
| `Makefile` with `lint`/`check` target | `make lint` (authoritative when present — prefer it over raw tools) |
| `golangci-lint` config / Go modules | `golangci-lint run <changed dirs>` |
| `package.json` scripts `lint`/`typecheck` | the repo's own script via its package manager |
| eslint/biome/oxlint config | corresponding tool on changed files |
| `tsconfig.json` | `tsc --noEmit` (project-wide; cheap signal) |
| `ruff.toml` / pyproject | `ruff check <files>` |
| `Cargo.toml` | `cargo clippy` |

Record per lane: `ran` (attach findings on selected files, trimmed) or `unavailable` (tool missing/failed — overlap suppression is off for that lane and review.md must say so). Never install tools to fill a lane.

## 3. PR intent

With `--pr`: title, description, linked issues (`gh pr view N --json title,body,closingIssuesReferences`), and base/head. Locally: `git log --oneline <base>..<head>` plus the user's stated intent. Reviewers judge the diff against *stated intent* — a change that does more than its description says is itself a finding.

## 4. Spec contract (`--spec`)

Resolve the conformance baseline: a file path is itself the artifact; a directory contributes its contract-bearing documents — `_prd.md`, `_techspec.md`, `_tests.md`, `_examples.md`, `_qa.md`, `_user_stories.md`, parity maps, requirement/UX docs, plus any document the spec's own files name as canonical. List every resolved artifact as `path → one-line role`. These are the baseline the `spec-parity` sweep judges against — do NOT extract rubric rules from them: §1 sources are review law, the spec is the contract under test.

## 5. context-pack.md layout

```markdown
# Context Pack — <target>

## Intent
<title/description/commits digest>

## Rubric
<sources consulted, one line each: path → rule count; canonical machine form: rules.json>

## Linters
<lane → ran(findings digest) | unavailable(reason)>

## Spec contract
<only with --spec: one `- `path`` line per artifact — render_review.py parses these lines for the conformance table>
```
