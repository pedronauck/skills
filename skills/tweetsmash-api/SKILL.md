---
name: tweetsmash-api
description: Uses the TweetSmash REST API to fetch bookmarks, inspect labels, and add or remove labels from saved tweets. Use when integrating TweetSmash into scripts, agents, workflows, cron jobs, or internal tools that need bookmark retrieval, filtering, pagination, or label management. Do not use for direct browser automation inside TweetSmash, unrelated X or Twitter APIs, or tasks that only need product marketing copy.
---

# TweetSmash API

Use this skill to work directly with the TweetSmash REST API after verifying the current docs. Read `references/api-reference.md` before choosing an endpoint. Read `references/bookmarks-filters.md` only when bookmark filtering is required.

## Procedures

**Step 1: Validate Credentials and Scope**
1. Confirm that a TweetSmash API key is available before making requests. Prefer `TWEETSMASH_API_KEY` in the shell environment.
2. Read `references/api-reference.md` to confirm the current endpoint, required headers, rate limits, and status codes.
3. If the task requires bookmark filtering or pagination, read `references/bookmarks-filters.md`.

**Step 2: Build the Request**
1. Use `Authorization: Bearer $TWEETSMASH_API_KEY` on every request.
2. Use `Content-Type: application/json` for all examples in this skill. Keep the base URL as `https://api.tweetsmash.com/v1`.
3. If the task fetches bookmarks with filters, execute `python3 scripts/build-bookmarks-url.py` with the needed flags to generate a correctly encoded URL.
4. If the task adds labels, start from `assets/add-labels-body.json` and fill in `tweet_ids` plus either `label_id` or `label_name`.
5. If the task removes labels, start from `assets/remove-labels-body.json` and fill in `tweet_ids` plus `label_name`.

**Step 3: Execute the Correct Endpoint**
1. Fetch bookmarks with `GET /bookmarks`. Use the URL from `scripts/build-bookmarks-url.py` when filters, search, or cursors are present.
2. List labels with `GET /labels` when the task needs current label IDs, label names, or usage counts.
3. Add labels with `POST /labels/add` when the task needs to organize one or more bookmarked tweets.
4. Remove labels with `POST /labels/remove` when the task needs to clean up or reclassify bookmarked tweets.
5. Use cURL for quick execution or translate the same request into the caller’s runtime only after the endpoint and payload are confirmed.

**Step 4: Verify the Response**
1. Confirm that the response JSON contains `"status": true` before reporting success.
2. For bookmark reads, inspect `meta.next_cursor`, `meta.limit`, and `meta.total_count` when pagination matters.
3. For label mutations, confirm the success message matches the intended action.
4. If the task depends on label existence, call `GET /labels` again after a mutation to verify the resulting state.

**Step 5: Return a Usable Result**
1. Summarize the request method, endpoint, and effective filters or payload fields that were used.
2. Return the response body or a structured summary, depending on the caller’s requested output format.
3. If follow-up pagination is possible, expose `meta.next_cursor` so the next request can continue from the prior page.

## Error Handling

* If authentication fails with `401`, confirm that the bearer token is present, non-empty, and taken from the correct TweetSmash account.
* If the API returns `402`, stop and report that the current plan does not permit the requested API access.
* If the API returns `429`, stop sending additional requests, note the documented limit of 100 requests per hour per API key, and retry later.
* If a bookmark query becomes hard to assemble by hand, rerun `python3 scripts/build-bookmarks-url.py --help` and rebuild the URL instead of manually concatenating query strings.
* If a label mutation is ambiguous, list labels first with `GET /labels` and then rerun the mutation using the confirmed label identifier or label name.
