---
name: kb-yt-channel
description: Creates and maintains Knowledge Base topics from YouTube channels by scaffolding a yt-channels topic, bulk-ingesting transcripts through kb ingest channel, and validating/indexing the result. Use when turning a YouTube channel into a Karpathy KB topic. Do not use for single-video ingestion, general video summaries, or non-YouTube sources.
---

# KB YouTube Channel

This skill is a thin wrapper around the native `kb ingest channel` command. `kb`
owns the ingest *mechanics* — channel resolution, video enumeration,
resume/dedup, bounded concurrency, throttling, adaptive backoff, retries,
native-language captions, and STT. The skill's `scripts/ingest-channel.py` owns
the KB-side *organization*: scaffolding the topic under `yt-channels/`,
maintaining category docs, patching CLAUDE.md, building wiki indexes, writing the
run report, and validating the topic.

## Required Inputs

- Channel or playlist URL, such as https://www.youtube.com/@aiDotEngineer.
- Topic slug, such as ai-dot-engineer.
- Topic title and domain.
- Video selection: either --limit N for the newest uploads or --all for the full uploads list.
- Transcript policy: --transcribe captions, auto, or stt.

Caption language defaults to the **original-language** track (`--sub-langs orig`)
and is handled natively by `kb ingest channel`. Pass a comma list like
`--sub-langs pt,en` only to override it.

## Rate limits and large channels (read before --all or --limit > ~10)

YouTube throttles caption downloads per IP (HTTP 429). `kb ingest channel`
already paces itself with bounded concurrency, inter-request throttling, and
adaptive exponential backoff (configured via `[youtube].bulk_concurrency`,
`[youtube].bulk_throttle`, `[youtube].bulk_retries`, `[youtube].bulk_backoff_max`).
For anything beyond a handful of videos, also give `kb` better network identity
via its config/env — **not** via this script:

1. **Cookies** — set `YOUTUBE_COOKIES_FILE` (or `[youtube].cookies_file`) to a logged-in YouTube session. Prefer a secondary Google account.
2. **Impersonation** — install curl_cffi into the yt-dlp environment so it can present a browser TLS fingerprint. Homebrew yt-dlp: `/opt/homebrew/opt/yt-dlp/libexec/bin/python -m pip install curl_cffi`.
3. **Residential proxy** — set `YOUTUBE_PROXY` to a rotating **residential** proxy (datacenter IPs are blocked). Pin to one country to avoid account-geo flags.
4. **Pacing** — raise `--throttle` (e.g. `5s`) and/or keep `--concurrency` low (1) on a bare IP. `--concurrency N` (>1) is only safe behind a rotating proxy; respect the proxy plan's concurrent-connection cap.

See references/troubleshooting.md for details.

## Procedure

**Step 1: Confirm Prerequisites**
1. Run kb version from the vault root.
2. Run yt-dlp --version from the vault root (kb shells out to it).
3. Run qmd --version when final indexing is required.
4. For channels beyond a handful of videos, configure cookies + proxy + curl_cffi per "Rate limits" above.
5. If --transcribe stt is selected, confirm ffmpeg -version and the configured STT provider credentials.

**Step 2: Preview With --dry-run (recommended)**
Run the Step 3 command with `--dry-run` first to confirm the channel resolves and
see how many videos will be ingested. This scaffolds the empty topic skeleton but
ingests nothing.

**Step 3: Run Channel Ingest**
1. Read references/channel-topic-contract.md when topic metadata or output validation is unclear.
2. Execute python3 scripts/ingest-channel.py from this skill directory, passing:
   - --vault /path/to/vault
   - --channel-url <youtube-channel-url>
   - --topic-slug <slug>
   - --title <title>
   - --domain <domain>
   - either --limit <n> or --all
   - --transcribe captions|auto|stt
   - optionally --sub-langs <langs> to override the native original track
   - optionally --concurrency <n> and/or --throttle <dur> to override the kb config defaults for large channels
   - optionally --no-index to defer indexing, --embed for vector embedding
3. Treat the script's JSON stdout as the run summary (it embeds the `kb ingest channel` summary plus validation and report path). kb's per-video progress and diagnostics stream live to stderr.

Example (small channel, defaults):

    python3 .agents/skills/kb-yt-channel/scripts/ingest-channel.py --vault . --channel-url https://www.youtube.com/@aiDotEngineer --topic-slug ai-dot-engineer --title "AI Engineer Channel" --domain youtube-channel --limit 10 --transcribe captions

Example (large channel behind a residential proxy):

    YOUTUBE_COOKIES_FILE=~/.config/kb/yt-cookies.txt YOUTUBE_PROXY="http://user-CC-rotate:pass@p.webshare.io:80" \
    python3 .agents/skills/kb-yt-channel/scripts/ingest-channel.py --vault . --channel-url https://www.youtube.com/@aiDotEngineer --topic-slug ai-dot-engineer --title "AI Engineer Channel" --domain youtube-channel --all --transcribe captions --concurrency 3 --throttle 3s

**Step 4: Verify The Topic**
1. Confirm kb topic info yt-channels/<slug> returns the expected topic path and source count.
2. Confirm <topic>/outputs/reports/ contains the channel ingest report for the run.
3. Confirm kb search "<channel topic>" --topic yt-channels/<slug> --collection <slug> --lex --format json returns raw transcript or index content after indexing.
4. Leave wiki article compilation to the normal kb compile workflow unless the user explicitly asks for article synthesis.

## Error Handling

- The script's JSON summary lists per-video results under `ingested`, `skipped`, and `failures` (each failure carries the kb `error` string). `kb ingest channel` already retries transient rate-limit/network errors with backoff before reporting a failure.
- If channel resolution fails, read references/troubleshooting.md and retry after updating yt-dlp or YouTube proxy/cookie settings.
- If many videos fail with rate-limit/network errors, raise --throttle, lower --concurrency, or fix cookies/proxy, then rerun. `kb ingest channel` skips videos already present in raw/youtube, so successful ingests are not repeated.
- If a failure is a genuine "no captions available" case, switch --transcribe to auto (captions then STT) or stt.
- If STT fails, read references/troubleshooting.md to check ffmpeg, provider credentials, model, chunk size, and network settings.
- If a partial topic exists after failure, rerun the same command. The script reuses the existing topic and kb skips videos already ingested. To re-fetch a specific video (e.g. to refresh a transcript), delete its file under raw/youtube/ and rerun.
