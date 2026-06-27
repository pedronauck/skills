# Troubleshooting YouTube Channel Ingest

All ingest mechanics run inside `kb ingest channel`; the rate-limit, proxy, and
cookie knobs below are read by `kb` from its config (`[youtube]` in kb.toml) and
environment, not from `scripts/ingest-channel.py`.

## Channel Listing Fails

- Run yt-dlp --version and update yt-dlp if it is stale.
- Retry the channel videos URL directly, for example https://www.youtube.com/@aiDotEngineer/videos.
- Configure YOUTUBE_PROXY, YOUTUBE_COOKIES_FILE, or YOUTUBE_USER_AGENT when YouTube blocks the local network.

## Rate Limiting (HTTP 429) — the main blocker at scale

YouTube throttles caption downloads (`timedtext`) per IP very aggressively. `kb
ingest channel` paces itself with bounded concurrency, inter-request throttle +
jitter, and adaptive exponential backoff (`[youtube].bulk_concurrency`,
`[youtube].bulk_throttle`, `[youtube].bulk_retries`, `[youtube].bulk_backoff_max`),
but on a bare IP that is still not enough. Layered mitigations, strongest first:

1. **Cookies (authenticated session).** Export a logged-in YouTube session to a Netscape cookies.txt and set `YOUTUBE_COOKIES_FILE` (or `[youtube].cookies_file`). Prefer a secondary Google account — bulk caption scraping can get an account temporarily flagged. yt-dlp can export from a browser: `yt-dlp --cookies-from-browser <browser> --cookies cookies.txt --skip-download <url>` (Chromium browsers need Keychain access; Arc is not a supported `--cookies-from-browser` name — extract from its profile or a supported browser).
2. **Impersonation (curl_cffi).** yt-dlp's YouTube extractor wants to impersonate a browser TLS fingerprint; without curl_cffi it warns "no impersonate target available" and is blocked more often. Install it into the yt-dlp environment. Homebrew: `/opt/homebrew/opt/yt-dlp/libexec/bin/python -m pip install curl_cffi`. Verify with `yt-dlp --list-impersonate-targets`.
3. **Residential proxy.** Set `YOUTUBE_PROXY`. **Datacenter IPs are blocked by YouTube** — use a rotating **residential** proxy. Pin to a single country to avoid account-geo flags (e.g. a `<user>-GB-rotate` username on Webshare rotates the IP per request but stays in GB). Plain all-country rotation with a logged-in account risks impossible-travel security flags.
4. **Pacing.** Raise `--throttle` (e.g. `5s`) and keep `--concurrency 1` on a bare IP. `--concurrency N` (>1) is only safe behind a rotating proxy. Cookies alone are not enough at high volume; pacing or a rotating proxy is required.

## Proxy Errors

- **HTTP 402 Payment Required** (or "Tunnel connection failed: 402"): the proxy's bandwidth/credit is exhausted. Top up the plan and rerun — kb skips videos already ingested, so the run resumes.
- **HTTP 400 / "Tunnel connection failed"**: usually too many concurrent connections for the plan, or a malformed/over-long sticky session id. Lower `--concurrency` (plans often cap ~5 concurrent), and prefer a server-side rotate username over many unique client session ids.

## Captions Fail / Wrong Language

- `kb ingest channel` fetches the **original-language** track by default (`--sub-langs orig`). For a non-English video this avoids YouTube's machine-translation endpoint, which is lower quality and throttled far more aggressively. Override with `--sub-langs pt,en` only when you need a specific language.
- A failure whose error indicates no usable captions for the requested language is a real blocker, not a rate limit. Use `--transcribe auto` (captions then STT) or `--transcribe stt`.
- To re-fetch a video whose transcript needs refreshing (e.g. stored before captions were available), delete its file under raw/youtube/ and rerun — kb re-ingests anything not already present.

## STT Fails

- Confirm ffmpeg is installed and on PATH.
- Confirm OPENAI_API_KEY or OPENROUTER_API_KEY is configured for the selected provider.
- Check kb.toml [stt] settings for provider, model, language, audio_format, chunk_duration, max_chunk_bytes, concurrency, and ffmpeg_path.
- Reduce STT concurrency or chunk size if provider requests time out or exceed upload limits.
- Note: audio downloads are also IP-blocked (HTTP 403) without cookies/proxy, like captions.

## Partial Runs

The script writes a report under outputs/reports/ after every run, with per-video
ingested/skipped/failure breakdown. Rerun the same command after fixing the
blocker; kb detects videos already present in raw/youtube and skips them, so
successful ingests are not repeated. For parallel multi-channel runs, pass
`--no-index` and run `kb index` once per topic afterward to avoid concurrent QMD
index conflicts.
