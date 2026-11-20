# Adopting the PR standard in a repository

Four pieces make a repository follow the standard. Each is owned by the repository after adoption; the copies in this skill are canonical, so improve them here first and resync.

## 1. Template: `.github/PULL_REQUEST_TEMPLATE.md`

Start from `assets/PULL_REQUEST_TEMPLATE.md`. Keep the three headings `What & why`, `How you verified it`, and `Impact`, then make the guidance specific to the repository:

- **How you verified it:** the repository's gate (`bun run verify`, CI-only policy, E2E command) and its screenshot requirements (viewports, themes, pages).
- **Impact:** the surfaces this repository can break (schema, public URLs, tokens, MCP tools, tenancy, revenue numbers).
- **Checklist:** the shared three boxes plus repository invariants that a reviewer must confirm.

Write guidance as plain paragraphs, never HTML comments: the check rejects comments, so a leftover comment fails CI instead of hiding in the body. Every `##` heading becomes a required, nonempty section; add one (for example `Observability`) only when every PR must answer it. The title convention belongs in the commit/PR-title tooling, not in the template.

## 2. Check: `.github/scripts/check-pr-body.py` and `.github/workflows/pr-body.yml`

Copy `assets/check-pr-body.py` and `assets/pr-body.yml` unchanged. The script reads the required headings from the template, so it needs no per-repository edits, and the workflow runs its self-test before validating the PR. Release branches `release/v*` and Dependabot/Renovate are exempt.

When the repository has commitlint but no PR-title check, add one in the repository's existing CI style: `printf '%s\n' "$PR_TITLE" | bunx --no-install commitlint` with `PR_TITLE: ${{ github.event.pull_request.title }}` on `pull_request` events.

## 3. Instructions: `CLAUDE.md` / `AGENTS.md`

Replace any existing PR-delivery paragraph with a short routing section, and remove every instruction to use `gh pr create --attach` or GitHub uploads:

```markdown
## Pull Requests

Opening or updating a PR, handling its review or CI, or declaring PR work done: follow
`pr-delivery`. Write the body from `.github/PULL_REQUEST_TEMPLATE.md`; the `PR body` check
enforces it. UI changes ship screenshots of the real page hosted in the R2 evidence bucket
through the skill's upload helper, never `gh --attach` or GitHub uploads.
```

Keep repository-specific screenshot or verification rules in that section when the template alone does not carry them.

## 4. Skill

Install with the repository's existing skills setup, for example `npx skills add pedronauck/skills/skills/mine --skill pr-delivery -y`, and commit the result with `skills-lock.json`. A repository whose published-surface rules forbid `.agents/` keeps only pieces 1–3 and relies on a user-level install.
