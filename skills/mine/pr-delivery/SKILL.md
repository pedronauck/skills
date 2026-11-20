---
name: pr-delivery
description: "Open, update, and deliver pull requests to Pedro's house standard: body from the repository template, R2-hosted screenshots for UI changes, green CI on the current head, and every review thread answered. Use when opening or updating a PR, attaching UI evidence, handling PR review or CI, declaring PR work done, or adopting this PR standard in a repository."
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---

# PR Delivery

A PR is how Pedro reviews and approves agent work, often without the conversation that produced it. The body must let him judge the result alone: what changed and why, how it was verified, what it affects, and, for UI, what it looks like.

Repository instructions (`CLAUDE.md`/`AGENTS.md`) win where they are more specific: verification commands, whether checks run locally or only in CI, language, extra checklist items, and merge policy.

Done means an open, ready PR on its final head with the body current, every required CI check green on that head, and every actionable review finding fixed or answered. A draft PR or a first push is a checkpoint, not delivery.

## Pull request

Write the body from `.github/PULL_REQUEST_TEMPLATE.md`. Keep its exact `##` headings and checklist, replace every guidance paragraph with real content, and fill every section. The `PR body` CI check (`.github/scripts/check-pr-body.py`) fails a missing or empty template section, an HTML comment, a host path, a GitHub-hosted image, or a body with no issue link. Without a template, use `assets/PULL_REQUEST_TEMPLATE.md`.

- **Title:** the repository's commit convention, usually `<type>: <description>` with `feat|fix|refactor|perf|docs|test|build|ci` and no scope. It becomes the squash commit and release-note line, so describe the result, not the activity.
- **Issue link:** `Closes #<n>`, or `Refs #<n>` when closing needs a check you cannot make. Work without an issue carries an explicit `No issue: <reason>` line.
- **What & why:** the trigger, root cause, observable before and after, and tradeoffs, for a reader without this conversation.
- **How you verified it:** commands, CI runs, and scenarios with their actual results, plus the screenshots below. Never list a check that did not run; explain missing tests.
- **Impact:** public routes and APIs, schema and migrations, config and environment variables, docs, and anything else the template names. Say what is not affected only after checking.
- Name the agent that wrote or co-wrote the change. Tick a checklist box only with evidence.
- Omit host paths (`/Users/...`), credentials, tokens, and private identifiers.
- Pass the body with `gh pr create --body-file <file>` / `gh pr edit --body-file <file>`. Keep it current as later rounds change the work.

## Screenshots

Every user-visible UI change ships screenshots of the real running app in **How you verified it**, so Pedro can see the result before approving. The template states the required viewports and themes; default to desktop `1440×900`, plus mobile `390×844` and the dark theme when the app has them. A visual fix also shows the before state. An interaction is better as a short `mp4`/`webm` recording.

Host evidence only in the public R2 bucket through the bundled helper. Never use `gh pr create --attach`, drag-and-drop, or GitHub uploads: those URLs expire or need a GitHub session, and the `PR body` check rejects them.

1. Capture with the repository's own screenshot tooling when it has one (a screenshot skill, Playwright config, or an examples verifier). Otherwise use the Playwright CLI against the running dev server:
   `npx --yes playwright@latest screenshot --viewport-size=1440,900 --wait-for-timeout=2000 [--color-scheme=dark] [--full-page] <url> <abs-out.png>`
   Authenticated pages need the repository's seeded/dev login; script it with Playwright when the CLI cannot reach the state.
2. Open every image and confirm it shows the intended screen, state, theme, and loaded fonts. A blank, error, or loading frame is not evidence.
3. The bucket is public: capture seeded or demo data only, never real customer data, secrets, or tokens.
4. From inside the repository, run `bash <pr-delivery-dir>/scripts/upload-evidence.sh '<file.png>#<alt text>' ...`, resolving the path from this skill's directory. It uploads each file under `<owner>/<repo>/<branch>/<sha>-<random>/`, verifies HTTP 200 and the content type, and prints Markdown lines. Paste those lines into the body; a non-zero exit means no usable URL.

The helper needs `wrangler` authenticated to the Cloudflare account that owns the bucket (`wrangler whoami`). `PR_EVIDENCE_BUCKET` and `PR_EVIDENCE_PUBLIC_URL` override the defaults.

## CI and review

Read every check on the current head; pending, cancelled, missing, or green on an earlier head is not green. Diagnose a finished failure while other jobs run, and read the real conclusion with `gh run view` / `gh pr checks`.

Work in rounds: fold in every failed check and every posted finding, then push once, because each push restarts CI and reviewers. Collect all reviews, inline threads, and PR comments, including bot summaries and outdated threads.

1. Validate each finding against the current code.
2. Fix every valid in-scope finding and failed check, then push one commit for the round. A failed commit hook is repaired in a new commit, not an amend or `--no-verify`.
3. Reply to each thread with the fixing commit or a concrete rationale, then resolve it. Escalate a disputed or out-of-scope finding to Pedro and leave it open until settled.

Repeat on the new head until nothing actionable remains, then report the PR URL, head SHA, and check results.

## Adopting the standard in a repository

Read `references/repo-setup.md` when a repository lacks the template, the `PR body` check, or the `CLAUDE.md` routing to this skill.
