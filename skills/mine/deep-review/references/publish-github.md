# Publish to GitHub

Recipes for `--publish`. Everything goes through `gh api`; `R` = `owner/repo`, `N` = PR number. Bodies come from files (`-F body=@file`) — never inline shell strings with quoting hazards.

## Reviewer identity

GitHub rejects `APPROVE`/`REQUEST_CHANGES` on a PR the authenticated user authored. Detect first:

```bash
AUTHOR=$(gh api repos/$R/pulls/$N --jq .user.login); ME=$(gh api user --jq .login)
```

Same login → always `event=COMMENT`. Different login (bot/machine user) and the repo config sets `request_changes_workflow: true` → `REQUEST_CHANGES` when Critical/Major findings are open, `COMMENT` otherwise. Approval flips are left to humans.

## 1. Upsert the walkthrough comment

One comment per PR, edited in place, found by its marker:

```bash
CID=$(gh api repos/$R/issues/$N/comments --paginate \
  --jq '[.[] | select(.body | contains("<!-- deep-review:walkthrough -->"))][0].id')
# absent → create; present → edit
gh api repos/$R/issues/$N/comments -F body=@"$OUT/walkthrough.md"
gh api repos/$R/issues/comments/$CID -X PATCH -F body=@"$OUT/walkthrough.md"
```

## 2. Anchor findings to the diff

Inline comments must land on lines the diff touches. The valid new-side ranges are already in the manifest — each selected file's `hunks` array (`{start, lines}`; ranges with `lines > 0`). A finding whose `line` falls inside a range → inline comment. Outside every range (`in_diff: false`, or drifted anchors) → the review body's Outside-diff section. On a 422 from GitHub despite the precheck, move that finding to the body and continue — never drop it.

## 3. Post the review submission

`comments.json` — one entry per anchorable finding, `body` rendered from the finding block template (fingerprint marker included):

```json
[{ "path": "internal/store/queue.go", "line": 42, "side": "RIGHT",
   "start_line": 38, "start_side": "RIGHT", "body": "<rendered finding block>" }]
```

(`start_line`/`start_side` only for multi-line ranges.) Review body = `**Actionable comments posted: <n>**` + collapsed sections (Outside diff range, Duplicates, Nitpicks) + the scope line `Reviewing files that changed between <base> and <head>.`:

```bash
jq -n --rawfile body "$OUT/review-body.md" --slurpfile c "$OUT/comments.json" \
  --arg ev "$EVENT" '{event:$ev, body:$body, comments:$c[0]}' > "$OUT/review-payload.json"
gh api repos/$R/pulls/$N/reviews --input "$OUT/review-payload.json"
```

**Batching:** more than 75 inline comments → split into multiple review submissions of ≤ 75, first one carrying the full body, the rest `**Actionable comments posted (continued): <n>**`.

## 4. Resolve prior-round comments

For each prior finding whose fingerprint this round marked `resolved`, edit the original comment — prepend, keep the rest intact:

```bash
gh api repos/$R/pulls/comments/$COMMENT_ID -X PATCH \
  -F body=@<(printf '✅ Addressed in commit %s\n\n%s' "$SHORT_SHA" "$ORIGINAL_BODY")
```

Unresolved prior findings are **not** re-posted inline; they appear once in the body's Duplicates section.

## 5. Recover state from the PR (no local state — CI, other machine)

```bash
# fingerprints already posted, from inline comments and review bodies
gh api repos/$R/pulls/$N/comments --paginate --jq '.[].body' | grep -o 'deep-review:fp:[a-f0-9]*'
gh api repos/$R/pulls/$N/reviews --paginate --jq '.[].body' | grep -o 'deep-review:fp:[a-f0-9]*'
# last reviewed head: latest "Reviewing files that changed between <base> and <head>." line
```

Rebuild the ledger from those fingerprints (status `open`) and use the recovered head as the incremental base. Resolution detection: a fingerprint absent from this round's findings while its file changed since the prior head → `resolved`.

## Order of operations

1. Verify `gh auth status` and repo access; detect identity (above).
2. Upsert walkthrough.
3. Anchor-check every finding; render comment bodies with fingerprints.
4. Post review submission(s).
5. Apply ✅ edits for resolved prior findings.
6. Cite both URLs (walkthrough comment, review) in the final message.

Idempotency rule: one review submission per round per head SHA — before posting, check the PR's reviews for a body containing `between <base> and <head>` with the same head; if present, editing/adding is a re-run, so stop and report instead of double-posting.
