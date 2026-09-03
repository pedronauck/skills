---
name: kb-yt-channel
description: Creates and maintains Knowledge Base topics from YouTube channels, playlists, or thematic searches by scaffolding a yt-channels topic, bulk-ingesting transcripts, and validating/indexing the result. Use when turning a YouTube channel, playlist, or topic-filtered video set into a Karpathy KB topic. Do not use for single-video ingestion or non-YouTube sources.
disable-model-invocation: true
---

# KB YouTube Channel

This skill creates and maintains a Karpathy Knowledge Base topic under `yt-channels/` from YouTube channel uploads, playlists, or thematic queries.

The skill's `scripts/ingest-channel.py` coordinates three selection branches:
1. **Whole-channel ingest:** Ingest all channel uploads or the newest N uploads.
2. **Playlist ingest:** Ingest all videos from a named or linked channel playlist.
3. **Thematic ingest:** Ingest videos matching a topic search query or title regex.

## Selection Branches

| Branch | CLI Selector | Resolution | Ingest Engine |
| --- | --- | --- | --- |
| **Whole Channel** | `--limit N` or `--all` | Channel uploads (`/videos`) | `kb ingest channel` |
| **Playlist** | `--playlist "<name_or_url>"` | Resolved via `yt-dlp @channel/playlists` | `kb ingest channel` |
| **Thematic (Query)** | `--query "<term>"` | Resolved via `yt-dlp @channel/search` | Managed `kb ingest youtube` |
| **Thematic (Regex)** | `--title-regex "<pattern>"` | Resolved via `yt-dlp @channel/videos` | Managed `kb ingest youtube` |

Read `references/thematic-ingest.md` when selecting videos by playlist, topic query, or title regex.

## Required Inputs

- Channel URL, such as `https://www.youtube.com/@rodrigobranas`.
- Topic slug, such as `rodrigo-branas-clean-code`.
- Topic title and domain.
- Selection policy:
  - `--limit N` or `--all` for whole-channel ingest.
  - `--playlist "<title_or_url>"` for a playlist.
  - `--query "<term>"` or `--title-regex "<regex>"` for thematic ingest.
- Transcript policy: `--transcribe captions`, `auto`, or `stt`.

Caption language defaults to the **original-language** track (`--sub-langs orig`). Pass a comma list like `--sub-langs pt,en` only to override it.

## Rate limits and large channels (read before --all or --limit > ~10)

YouTube throttles caption downloads per IP (HTTP 429). `kb` already paces itself with bounded concurrency, inter-request throttling, and adaptive exponential backoff.

For large ingest runs, give `kb` better network identity via config/env:
1. **Cookies** — set `YOUTUBE_COOKIES_FILE` to a logged-in YouTube session. Prefer a secondary Google account.
2. **Impersonation** — install `curl_cffi` into the yt-dlp environment to present a browser TLS fingerprint.
3. **Residential proxy** — set `YOUTUBE_PROXY` to a rotating residential proxy.
4. **Pacing** — raise `--throttle` (e.g. `3s` or `5s`) and keep `--concurrency 1` on a bare IP.

See `references/troubleshooting.md` for details.

## Procedure

**Step 1: Confirm Prerequisites**
1. Run `kb version` from the vault root.
2. Run `yt-dlp --version` from the vault root.
3. Run `qmd --version` when final indexing is required.
4. For large channels, configure cookies + proxy + curl_cffi per "Rate limits" above.
5. If `--transcribe stt` is selected, confirm `ffmpeg -version` and STT provider credentials.

*Completion criterion:* Tool versions and environment credentials verified.

**Step 2: Preview With --dry-run**
Execute the ingest command with `--dry-run` to inspect resolved videos without downloading:

```bash
python3 .agents/skills/kb-yt-channel/scripts/ingest-channel.py --vault . \
  --channel-url <channel-url> --topic-slug <slug> --title <title> --domain <domain> \
  [--playlist "<name>" | --query "<query>" | --title-regex "<regex>" | --all | --limit <n>] \
  --dry-run
```

*Completion criterion:* The JSON output lists candidate videos under `videos` and reports `dry_run: true`. Review the list to confirm no unrelated videos are caught in the scope.

**Step 3: Run Channel Ingest**
1. Read `references/channel-topic-contract.md` when topic metadata or output validation is unclear.
2. Execute the script without `--dry-run`:

Example (Channel playlist):

    python3 .agents/skills/kb-yt-channel/scripts/ingest-channel.py --vault . --channel-url https://www.youtube.com/@rodrigobranas --playlist "Clean Code" --topic-slug rodrigo-branas-clean-code --title "Clean Code - Rodrigo Branas" --domain clean-code --transcribe captions

Example (Thematic query with limit):

    python3 .agents/skills/kb-yt-channel/scripts/ingest-channel.py --vault . --channel-url https://www.youtube.com/@rodrigobranas --query "clean code" --limit 10 --topic-slug rodrigo-branas-clean-code --title "Clean Code - Rodrigo Branas" --domain clean-code --transcribe captions

Example (Thematic regex title match):

    python3 .agents/skills/kb-yt-channel/scripts/ingest-channel.py --vault . --channel-url https://www.youtube.com/@rodrigobranas --title-regex "(?i)clean code" --topic-slug rodrigo-branas-clean-code --title "Clean Code - Rodrigo Branas" --domain clean-code --transcribe captions

Example (Whole channel uploads with residential proxy):

    YOUTUBE_COOKIES_FILE=~/.config/kb/yt-cookies.txt YOUTUBE_PROXY="http://user-CC-rotate:pass@p.webshare.io:80" \
    python3 .agents/skills/kb-yt-channel/scripts/ingest-channel.py --vault . --channel-url https://www.youtube.com/@aiDotEngineer --topic-slug ai-dot-engineer --title "AI Engineer Channel" --domain youtube-channel --all --transcribe captions --concurrency 3 --throttle 3s

*Completion criterion:* The JSON output reports `failures: []` (or identified acceptable skips), and emits the report path under `outputs/reports/`.

**Step 4: Verify The Topic**
1. Confirm `kb topic info yt-channels/<slug>` returns the expected source count.
2. Confirm `<topic>/outputs/reports/` contains the run report.
3. Confirm `kb search "<topic>" --topic yt-channels/<slug> --collection <slug> --lex --format json` returns hits.
4. Leave wiki article compilation to the normal `kb compile` workflow.

*Completion criterion:* All verification commands exit with code 0 and `sourceCount` matches ingested/skipped videos.

## Error Handling

- The script's JSON summary lists per-video results under `ingested`, `skipped`, and `failures`.
- If playlist or channel resolution fails, check channel URL format and verify yt-dlp is updated.
- If many videos fail with HTTP 429 rate-limit errors, raise `--throttle` (e.g. `5s`), lower concurrency to 1, or provide `YOUTUBE_PROXY` / `YOUTUBE_COOKIES_FILE`.
- Existing transcripts in `raw/youtube/` are skipped automatically on re-runs. To re-fetch a specific video transcript, delete its file under `raw/youtube/` and re-run.
