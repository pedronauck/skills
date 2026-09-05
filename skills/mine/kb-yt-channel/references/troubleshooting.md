# Troubleshooting YouTube Channel Ingest

Apply remedies only to an observed failure. Start with the current tool/network configuration and native backoff; cookies, optional impersonation packages, and proxies are not bulk-ingest prerequisites. Respect access restrictions and rate limits. Resolve the actual tool environment rather than copying a machine-specific Python path.

All ingest mechanics run inside `kb ingest channel`; the rate-limit, proxy, and
cookie knobs below are read by `kb` from its config (`[youtube]` in kb.toml) and
environment, not from `scripts/ingest-channel.py`.

## Channel Listing Fails

- Run yt-dlp --version and update yt-dlp if it is stale.
- Retry the channel videos URL directly, for example https://www.youtube.com/@aiDotEngineer/videos.
- Configure YOUTUBE_PROXY, YOUTUBE_COOKIES_FILE, or YOUTUBE_USER_AGENT when YouTube blocks the local network.

## Rate Limiting (HTTP 429)

Honor retry/backoff guidance and reduce request rate or concurrency before changing network infrastructure. `kb ingest channel` exposes bounded pacing through `[youtube].bulk_concurrency`, `bulk_throttle`, `bulk_retries`, and `bulk_backoff_max`; inspect the installed tool's options for the failing request.

- Let the rate-limit window clear and resume with lower concurrency or higher throttle. A particular concurrency value does not guarantee success.
- Use cookies only when the authorized content needs that session. Do not export unrelated browser sessions or treat authentication as a rate-limit bypass.
- If yt-dlp reports a missing impersonation capability relevant to the failure, inspect its actual environment and supported targets before installing an optional package.
- An existing, authorized proxy may be relevant to a diagnosed connectivity restriction. Rotating residential proxies are not a prerequisite for bulk work and do not guarantee that throttling disappears.

## Proxy Errors

- **HTTP 402 / tunnel credit errors:** inspect the configured provider's status and quota. Use an already-authorized route or report the provider boundary; do not purchase capacity automatically. Resume ingestion after the boundary is resolved.
- **HTTP 400 / tunnel connection failed:** inspect the returned error, endpoint, credentials, and connection limits. Lower concurrency only when the error supports that diagnosis.

## Captions Fail / Wrong Language

- `kb ingest channel` fetches the **original-language** track by default (`--sub-langs orig`). For a non-English video this avoids YouTube's machine-translation endpoint, which is lower quality and throttled far more aggressively. Override with `--sub-langs pt,en` only when you need a specific language.
- A failure whose error indicates no usable captions for the requested language is a real blocker, not a rate limit. Use `--transcribe auto` (captions then STT) or `--transcribe stt`.
- To re-fetch a video whose transcript needs refreshing (e.g. stored before captions were available), delete its file under raw/youtube/ and rerun — kb re-ingests anything not already present.

## STT Fails

- Confirm ffmpeg is installed and on PATH.
- Confirm OPENAI_API_KEY or OPENROUTER_API_KEY is configured for the selected provider.
- Check kb.toml [stt] settings for provider, model, language, audio_format, chunk_duration, max_chunk_bytes, concurrency, and ffmpeg_path.
- Reduce STT concurrency or chunk size if provider requests time out or exceed upload limits.
- For an audio HTTP 403, inspect the actual access/network error; the status alone does not establish that cookies or a proxy are required.

## Partial Runs

The script writes a report under outputs/reports/ after every run, with per-video
ingested/skipped/failure breakdown. Rerun the same command after fixing the
blocker; kb detects videos already present in raw/youtube and skips them, so
successful ingests are not repeated. For parallel multi-channel runs, pass
`--no-index` and run `kb index` once per topic afterward to avoid concurrent QMD
index conflicts.
