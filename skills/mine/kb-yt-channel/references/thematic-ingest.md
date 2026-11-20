# Thematic and Playlist Ingest

Reference guide for resolving and selecting channel videos by playlist or topic.

## Selection Branches

### 1. Playlist Ingest (--playlist)

Target a specific playlist hosted on the channel.

- **Name match:** Pass the playlist name, e.g. `--playlist "Clean Code"`. The script fetches `@channel/playlists` via `yt-dlp` and resolves the matching playlist URL.
- **URL or ID:** Pass a full URL (`https://www.youtube.com/playlist?list=PL...`) or ID (`PL...`).
- **Behavior:** The resolved playlist URL is handed directly to `kb ingest channel`, taking advantage of native deduplication, pacing, and caption handling.
- **Default limit:** Defaults to all videos in the playlist unless `--limit N` is explicitly provided.

### 2. Thematic Search Query (--query)

Query YouTube's search index within the channel scope.

- **Usage:** `--query "clean code"`
- **Resolution:** Targets `https://www.youtube.com/@channel/search?query=<encoded>`.
- **Scope:** Returns videos where the query appears in the title, description, or automatic tags. Also matches live streams (`/streams`) and interviews.
- **Tail filtering:** YouTube search results can degrade into broad channel recommendations after the top hits. Always combine with `--dry-run` to inspect candidate videos, or set `--limit N` (e.g. `--limit 10`) to avoid drifting into unrelated uploads.

### 3. Title Regex Filtering (--title-regex)

Apply strict regular expression matching against video titles.

- **Usage:** `--title-regex "(?i)clean code"`
- **Resolution:** Enumerates videos from `@channel/videos` and keeps only items matching the regular expression.
- **Precision:** 0% false positive rate for known keywords. Ideal when videos follow structured naming conventions (e.g. series, courses, or episode tags).
- **Caveat:** Matches only standard uploads under `/videos`. For lives and streams, prefer `--query` or provide a playlist.

## Ingest Mechanics & Dedup

For thematic ingests (query or regex):
1. **Resolution:** Candidate videos are resolved into `[{"video_id": "...", "title": "...", "url": "..."}]`.
2. **Dedup check:** Before each fetch, the script checks `raw/youtube/` frontmatter for existing `source_url` or video IDs. Already ingested videos are marked `skipped` and not re-downloaded.
3. **Pacing:** Between consecutive single-video ingests, the script enforces a throttle delay (`--throttle 2s` default) to prevent HTTP 429 rate limiting.
4. **Validation:** Post-ingest validation commands (`kb topic info`, `kb lint`, `kb index`, `kb search`) run identically to whole-channel ingests.
