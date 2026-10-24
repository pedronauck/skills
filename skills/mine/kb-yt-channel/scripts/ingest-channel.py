#!/usr/bin/env python3
"""Create or update a KB topic from a YouTube channel.

Thin orchestrator over ``kb ingest channel`` and ``kb ingest youtube``.
This script owns the KB-side *organization* of a channel topic; ``kb`` owns the
ingest *mechanics*.

Supported selection branches:
  1. Full channel uploads or newest N uploads: ``--all`` or ``--limit N``
  2. Channel playlist: ``--playlist <name_or_url>``
  3. Thematic query: ``--query <query>`` (YouTube channel search)
  4. Thematic regex: ``--title-regex <pattern>`` (filter uploads by title)

Delegated to ``kb``:
  - resume/dedup against existing files in raw/youtube/
  - bounded concurrency, throttling, adaptive backoff, and per-video retries
  - native-language caption selection (``--sub-langs orig``)
  - transcription policy (captions | auto | stt) and STT
  - per-video frontmatter and raw/youtube/*.md generation

Owned by this script:
  - playlist discovery and name-to-URL resolution
  - thematic video discovery and candidate filtering
  - scaffolding the topic under ``yt-channels/<slug>/`` with topic.yaml
  - maintaining the ``yt-channels/`` category docs
  - patching the topic CLAUDE.md with channel metadata
  - wiki index dashboards (Dashboard.md, Source Index.md)
  - the run report under outputs/reports/
  - post-ingest validation (topic info, lint, index, search)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class CommandError(RuntimeError):
    def __init__(self, args: list[str], returncode: int, stdout: str, stderr: str) -> None:
        self.args_list = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(f"command failed ({returncode}): {' '.join(args)}")


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def run(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    eprint("$ " + " ".join(args))
    cmd = list(args)
    if cmd and not Path(cmd[0]).is_file():
        resolved = shutil.which(cmd[0])
        if resolved:
            cmd[0] = resolved
    completed = subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        env=os.environ.copy(),
        errors="replace",
    )
    if check and completed.returncode != 0:
        raise CommandError(args, completed.returncode, completed.stdout, completed.stderr)
    return completed


def validate_inputs(args: argparse.Namespace) -> None:
    if not SLUG_RE.match(args.topic_slug):
        raise ValueError("topic slug must use lowercase alphanumerics separated by single hyphens")
    if not args.title.strip():
        raise ValueError("title is required")
    if not args.domain.strip():
        raise ValueError("domain is required")
    if args.playlist and args.query:
        raise ValueError("cannot combine --playlist and --query")
    if args.playlist and args.title_regex:
        raise ValueError("cannot combine --playlist and --title-regex")


def topic_paths(vault: Path, slug: str) -> tuple[Path, Path]:
    return vault / slug, vault / "yt-channels" / slug


def scaffold_topic(vault: Path, slug: str, title: str, domain: str, kb_path: str) -> Path:
    root_topic, category_topic = topic_paths(vault, slug)
    category_root = vault / "yt-channels"
    category_root.mkdir(parents=True, exist_ok=True)
    if category_topic.exists():
        if not (category_topic / "CLAUDE.md").exists():
            raise RuntimeError(f"existing topic is missing CLAUDE.md: {category_topic}")
        eprint(f"reusing existing topic {category_topic}")
        return category_topic
    if root_topic.exists():
        raise RuntimeError(f"cannot scaffold {slug}: root topic already exists at {root_topic}")
    run([kb_path, "topic", "new", slug, title, domain], cwd=vault)
    shutil.move(str(root_topic), str(category_topic))
    return category_topic


def write_topic_metadata(topic_dir: Path, slug: str, title: str, domain: str) -> None:
    content = "\n".join(
        [
            f"slug: {slug}",
            f"title: {title}",
            f"domain: {domain}",
            "category: yt-channels",
            f"path: yt-channels/{slug}",
            f"qmd_collection: {slug}",
            "",
        ]
    )
    (topic_dir / "topic.yaml").write_text(content, encoding="utf-8")


def ensure_agents_symlink(topic_dir: Path) -> None:
    agents_path = topic_dir / "AGENTS.md"
    if agents_path.exists() or agents_path.is_symlink():
        return
    try:
        agents_path.symlink_to("CLAUDE.md")
    except OSError:
        agents_path.write_text((topic_dir / "CLAUDE.md").read_text(encoding="utf-8"), encoding="utf-8")


def read_simple_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def category_topics(category_root: Path) -> list[dict[str, str]]:
    topics: list[dict[str, str]] = []
    if not category_root.exists():
        return topics
    for child in sorted(category_root.iterdir()):
        if not child.is_dir():
            continue
        metadata = read_simple_yaml(child / "topic.yaml")
        if not metadata:
            continue
        slug = metadata.get("slug", child.name)
        title = metadata.get("title", slug)
        collection = metadata.get("qmd_collection", slug)
        topics.append(
            {
                "folder": child.name,
                "slug": slug,
                "title": title,
                "collection": collection,
            }
        )
    return topics


def update_category_docs(vault: Path) -> None:
    category_root = vault / "yt-channels"
    topics = category_topics(category_root)
    if topics:
        table_rows = [
            f"| [{topic['folder']}/]({topic['folder']}/) | {topic['title']} | {topic['slug']} | {topic['collection']} |"
            for topic in topics
        ]
        topic_lines = [
            f"- yt-channels/{topic['folder']}/ - {topic['title']} (collection: {topic['collection']})"
            for topic in topics
        ]
    else:
        table_rows = ["| _None yet._ | Use the kb-yt-channel skill to create a channel topic. | - | - |"]
        topic_lines = ["- None yet. Use the kb-yt-channel skill to create channel topics."]
    readme = "\n".join(
        [
            "# YouTube Channels",
            "",
            "Knowledge bases generated from YouTube channel uploads.",
            "",
            "| Folder | Topic | Slug | Collection |",
            "|--------|-------|------|------------|",
            *table_rows,
            "",
        ]
    )
    (category_root / "README.md").write_text(readme, encoding="utf-8")
    for name in ("CLAUDE.md", "AGENTS.md"):
        path = category_root / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        replacement = "## Current topics\n\n" + "\n".join(topic_lines) + "\n"
        text = re.sub(r"## Current topics\n\n.*\Z", replacement, text, flags=re.DOTALL)
        path.write_text(text, encoding="utf-8")


def patch_topic_claude(
    topic_dir: Path,
    slug: str,
    title: str,
    domain: str,
    channel_url: str,
    selection: str,
    transcribe: str,
    command_line: str,
) -> None:
    claude_path = topic_dir / "CLAUDE.md"
    text = claude_path.read_text(encoding="utf-8")
    text = text.replace("[root CLAUDE.md](../CLAUDE.md)", "[root CLAUDE.md](../../CLAUDE.md)")
    text = text.replace("../.claude/skills/karpathy-kb/SKILL.md", "../../.claude/skills/kb/SKILL.md")
    text = text.replace("the [karpathy-kb skill]", "the [kb skill]")
    scope = (
        f"**Topic scope:** Transcripts and source material from the YouTube channel {channel_url}. "
        "This topic starts as an immutable transcript corpus and can later be compiled into wiki articles about recurring themes, speakers, demos, and technical patterns."
    )
    text = re.sub(r"^\*\*Topic scope:\*\*.*$", scope, text, count=1, flags=re.MULTILINE)
    domain_line = f"**Domain:** {domain} - all notes in this topic use domain: {domain} in frontmatter."
    text = re.sub(r"^\*\*Domain:\*\*.*$", domain_line, text, count=1, flags=re.MULTILINE)
    marker_start = "<!-- kb-yt-channel:start -->"
    marker_end = "<!-- kb-yt-channel:end -->"
    section = f"""
{marker_start}
## YouTube channel ingest

- Channel URL: {channel_url}
- Topic id: yt-channels/{slug}
- QMD collection: {slug}
- Selection policy: {selection}
- Transcript policy: {transcribe}
- Last ingest command: {command_line}

Raw transcripts live in raw/youtube/. Ingest reports live in outputs/reports/. This topic is functional after kb topic info, kb lint --save, and kb index --name {slug} pass for yt-channels/{slug}.
{marker_end}
""".strip()
    if marker_start in text and marker_end in text:
        pattern = re.compile(re.escape(marker_start) + r".*?" + re.escape(marker_end), re.DOTALL)
        text = pattern.sub(section, text)
    else:
        text = text.rstrip() + "\n\n" + section + "\n"
    if not text.startswith(f"# {title}"):
        text = re.sub(r"^# .+$", f"# {title}", text, count=1, flags=re.MULTILINE)
    claude_path.write_text(text, encoding="utf-8")


def table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def extract_video_id(url_or_id: str) -> str:
    m = re.search(r"(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})", url_or_id)
    if m:
        return m.group(1)
    if len(url_or_id) == 11 and " " not in url_or_id:
        return url_or_id
    return url_or_id


def youtube_sources(topic_dir: Path) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    raw_youtube = topic_dir / "raw" / "youtube"
    if not raw_youtube.exists():
        return sources
    for path in sorted(raw_youtube.glob("*.md")):
        metadata = read_frontmatter(path)
        title = metadata.get("title") or path.stem.replace("-", " ").title()
        sources.append(
            {
                "path": path.relative_to(topic_dir).as_posix(),
                "title": title,
                "scraped": metadata.get("scraped", ""),
                "source_url": metadata.get("source_url", ""),
                "transcript_source": metadata.get("transcript_source", ""),
            }
        )
    return sources


def update_topic_inventory(topic_dir: Path, source_count: int) -> None:
    claude_path = topic_dir / "CLAUDE.md"
    text = claude_path.read_text(encoding="utf-8")
    line = f"- `raw/youtube/` - {source_count} transcript sources"
    if "`raw/youtube/`" in text:
        text = re.sub(r"^- `raw/youtube/` .*$", line, text, count=1, flags=re.MULTILINE)
    else:
        text = re.sub(r"^- `raw/github/` .*$", lambda match: match.group(0) + "\n" + line, text, count=1, flags=re.MULTILINE)
    claude_path.write_text(text, encoding="utf-8")


def write_channel_indexes(topic_dir: Path, title: str, domain: str, source_count: int) -> None:
    today = dt.date.today().isoformat()
    index_dir = topic_dir / "wiki" / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    dashboard = "\n".join(
        [
            "---",
            f"domain: {domain}",
            "title: Dashboard",
            "type: index",
            f"updated: \"{today}\"",
            "---",
            "",
            f"# {title} - Dashboard",
            "",
            f"Landing page for the {title} knowledge base.",
            "",
            "## At a glance",
            "",
            "- **Articles:** 0",
            "- **Total words:** 0",
            f"- **Raw sources:** {source_count} YouTube transcript sources",
            f"- **Last updated:** {today}",
            "",
            "## Topic scope",
            "",
            "YouTube transcript corpus for recurring themes, speakers, demos, and technical patterns from this channel.",
            "",
            "## Featured articles",
            "",
            "_No featured articles yet._",
            "",
            "## Recent additions",
            "",
            "See [[Source Index]] for the current transcript corpus.",
            "",
            "## Coverage map",
            "",
            "_Compile wiki concepts after the transcript corpus has been reviewed._",
            "",
            "## Research gaps",
            "",
            "- Identify recurring agent-engineering practices across talks",
            "- Map speakers, projects, and demos to technical themes",
            "",
            "## Related topics",
            "",
            "_No related topics linked yet._",
            "",
            "## Navigation",
            "",
            "- [[Concept Index]] - alphabetical listing of all articles",
            "- [[Source Index]] - all sources and which articles cite them",
            "",
        ]
    )
    (index_dir / "Dashboard.md").write_text(dashboard, encoding="utf-8")
    source_lines = [
        "---",
        f"domain: {domain}",
        "title: Source Index",
        "type: index",
        f"updated: \"{today}\"",
        "---",
        "",
        f"# {title} - Source Index",
        "",
        "All raw sources that inform this topic's wiki, with the articles that cite them.",
        "",
        "## YouTube transcripts",
        "",
        "| Source | Scraped | Transcript | URL | Cited by |",
        "|--------|---------|------------|-----|----------|",
    ]
    sources = youtube_sources(topic_dir)
    if sources:
        for source in sources:
            source_lines.append(
                "| "
                + f"[[{source['path']}|{table_cell(source['title'])}]]"
                + f" | {table_cell(source['scraped'] or 'unknown')}"
                + f" | {table_cell(source['transcript_source'] or 'unknown')}"
                + f" | {table_cell(source['source_url'] or 'n/a')}"
                + " | _Uncited_ |"
            )
    else:
        source_lines.append("| _None yet._ | - | - | - | - |")
    source_lines.extend(
        [
            "",
            "## Articles (raw/articles/)",
            "",
            "| Source | Scraped | Cited by |",
            "|--------|---------|----------|",
            "| _None yet._ | - | - |",
            "",
            "## GitHub (raw/github/)",
            "",
            "| Source | Scraped | Cited by |",
            "|--------|---------|----------|",
            "| _None yet._ | - | - |",
            "",
            "## Bookmark clusters (raw/bookmarks/)",
            "",
            "| Cluster | Updated | Cited by |",
            "|---------|---------|----------|",
            "| _None yet._ | - | - |",
            "",
            "## Orphan sources",
            "",
            "All YouTube transcripts are uncited until wiki articles are compiled from this corpus.",
            "",
        ]
    )
    (index_dir / "Source Index.md").write_text("\n".join(source_lines), encoding="utf-8")


def parse_json_output(text: str) -> Any:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return None


def parse_duration_seconds(dur_str: str | None, default: float = 2.0) -> float:
    if not dur_str:
        return default
    s = dur_str.strip().lower()
    if s.endswith("ms"):
        try:
            return float(s[:-2]) / 1000.0
        except ValueError:
            return default
    if s.endswith("s"):
        try:
            return float(s[:-1])
        except ValueError:
            return default
    if s.endswith("m"):
        try:
            return float(s[:-1]) * 60.0
        except ValueError:
            return default
    try:
        return float(s)
    except ValueError:
        return default


def build_command_line(args: argparse.Namespace) -> str:
    extras = ""
    if args.playlist:
        extras += f" --playlist {json.dumps(args.playlist)}"
    if args.query:
        extras += f" --query {json.dumps(args.query)}"
    if args.title_regex:
        extras += f" --title-regex {json.dumps(args.title_regex)}"
    if args.all:
        extras += " --all"
    elif args.limit is not None:
        extras += f" --limit {args.limit}"
    if args.sub_langs:
        extras += f" --sub-langs {args.sub_langs}"
    if args.concurrency is not None:
        extras += f" --concurrency {args.concurrency}"
    if args.throttle is not None:
        extras += f" --throttle {args.throttle}"
    if args.embed:
        extras += " --embed"
    if args.no_index:
        extras += " --no-index"
    return (
        "python3 .agents/skills/kb-yt-channel/scripts/ingest-channel.py "
        f"--vault {args.vault} --channel-url {args.channel_url} --topic-slug {args.topic_slug} "
        f"--title {json.dumps(args.title)} --domain {args.domain} --transcribe {args.transcribe}{extras}"
    )


def resolve_playlist(channel_url: str, playlist_input: str, yt_dlp_cmd: str = "yt-dlp") -> tuple[str, str]:
    if "list=" in playlist_input:
        return playlist_input, playlist_input
    if playlist_input.startswith("PL") and len(playlist_input) >= 15 and " " not in playlist_input:
        return f"https://www.youtube.com/playlist?list={playlist_input}", playlist_input

    channel_base = channel_url.rstrip("/")
    for suffix in ("/videos", "/featured", "/streams", "/playlists", "/search"):
        if channel_base.endswith(suffix):
            channel_base = channel_base[: -len(suffix)]
            break
    playlists_url = f"{channel_base}/playlists"

    eprint(f"resolving playlist {playlist_input!r} from {playlists_url}")
    result = subprocess.run(
        [yt_dlp_cmd, "--flat-playlist", "--print", "%(id)s\t%(title)s\t%(url)s", playlists_url],
        capture_output=True,
        text=True,
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(f"failed to fetch playlists from {playlists_url}: {result.stderr.strip()}")

    matches: list[tuple[str, str, str]] = []
    all_playlists: list[str] = []
    target = playlist_input.lower().strip()
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3:
            pid, title, url = parts[0].strip(), parts[1].strip(), parts[2].strip()
            all_playlists.append(f"- {title} ({pid})")
            if target == title.lower():
                return url, title
            if target in title.lower():
                matches.append((pid, title, url))

    if len(matches) == 1:
        return matches[0][2], matches[0][1]
    if len(matches) > 1:
        options = "\n".join(f"  - {m[1]} ({m[2]})" for m in matches)
        raise RuntimeError(f"ambiguous playlist name {playlist_input!r}, multiple matched:\n{options}")

    available = "\n".join(all_playlists[:20])
    raise RuntimeError(
        f"playlist {playlist_input!r} not found on channel {channel_url}.\nAvailable playlists:\n{available}"
    )


def resolve_thematic_videos(
    channel_url: str,
    query: str | None,
    title_regex: str | None,
    limit: int | None,
    yt_dlp_cmd: str = "yt-dlp",
) -> list[dict[str, str]]:
    channel_base = channel_url.rstrip("/")
    for suffix in ("/videos", "/featured", "/streams", "/playlists", "/search"):
        if channel_base.endswith(suffix):
            channel_base = channel_base[: -len(suffix)]
            break

    cmd = [yt_dlp_cmd, "--flat-playlist", "--print", "%(id)s\t%(title)s\t%(url)s"]
    if query:
        encoded_query = urllib.parse.quote_plus(query)
        target_url = f"{channel_base}/search?query={encoded_query}"
    else:
        target_url = f"{channel_base}/videos"
        if title_regex:
            cmd.extend(["--match-title", title_regex])

    cmd.append(target_url)
    eprint(f"resolving thematic videos from {target_url}...")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(f"failed to resolve thematic videos: {result.stderr.strip()}")

    videos: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    regex_matcher = re.compile(title_regex) if (query and title_regex) else None

    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3:
            vid, title, url = parts[0].strip(), parts[1].strip(), parts[2].strip()
            if vid.startswith("PL") or "playlist?list=" in url:
                continue
            if vid in seen_ids:
                continue
            if regex_matcher and not regex_matcher.search(title):
                continue
            seen_ids.add(vid)
            video_url = url if url.startswith("http") else f"https://www.youtube.com/watch?v={vid}"
            videos.append({"video_id": vid, "title": title, "url": video_url})
            if limit and len(videos) >= limit:
                break

    return videos


def ingest_thematic(
    args: argparse.Namespace,
    vault: Path,
    topic_dir: Path,
    videos: list[dict[str, str]],
    selection_desc: str,
    dry_run: bool,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "topic": f"yt-channels/{args.topic_slug}",
        "channel_url": args.channel_url,
        "normalized_channel_url": args.channel_url,
        "selection": selection_desc,
        "transcribe": args.transcribe,
        "caption_languages": [args.sub_langs or "orig"],
        "resolved": len(videos),
        "dry_run": dry_run,
        "videos": videos,
        "ingested": [],
        "skipped": [],
        "failures": [],
    }
    if dry_run:
        return summary

    existing_sources = youtube_sources(topic_dir)
    existing_ids = {extract_video_id(s["source_url"]) for s in existing_sources if s.get("source_url")}
    throttle_sec = parse_duration_seconds(args.throttle, default=2.0)

    total = len(videos)
    for idx, video in enumerate(videos, start=1):
        vid = video["video_id"]
        title = video["title"]
        url = video["url"]

        if vid in existing_ids:
            eprint(f"[{idx}/{total}] skipping already ingested video: {title} ({vid})")
            summary["skipped"].append(video)
            continue

        eprint(f"[{idx}/{total}] ingesting: {title} ({vid})")
        command = [
            args.kb_path,
            "ingest",
            "youtube",
            url,
            "--topic",
            f"yt-channels/{args.topic_slug}",
            "--transcribe",
            args.transcribe,
        ]
        if args.sub_langs:
            command.extend(["--sub-langs", args.sub_langs])

        proc = run(command, cwd=vault, check=False)
        if proc.returncode == 0:
            summary["ingested"].append(video)
            existing_ids.add(vid)
        else:
            summary["failures"].append(
                {
                    "video_id": vid,
                    "title": title,
                    "url": url,
                    "error": f"kb ingest youtube failed with exit code {proc.returncode}",
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                }
            )

        if idx < total and throttle_sec > 0:
            time.sleep(throttle_sec)

    return summary


def ingest_channel(args: argparse.Namespace, vault: Path, dry_run: bool) -> dict[str, Any]:
    """Delegate channel or playlist ingest to ``kb ingest channel`` and return summary."""
    command = [
        args.kb_path,
        "ingest",
        "channel",
        args.channel_url,
        "--topic",
        f"yt-channels/{args.topic_slug}",
        "--transcribe",
        args.transcribe,
    ]
    if args.all:
        command.append("--all")
    elif args.limit is not None:
        command.extend(["--limit", str(args.limit)])
    if args.sub_langs:
        command.extend(["--sub-langs", args.sub_langs])
    if args.concurrency is not None:
        command.extend(["--concurrency", str(args.concurrency)])
    if args.throttle is not None:
        command.extend(["--throttle", args.throttle])
    if dry_run:
        command.append("--dry-run")
    eprint("$ " + " ".join(command))
    cmd = list(command)
    if cmd and not Path(cmd[0]).is_file():
        resolved = shutil.which(cmd[0])
        if resolved:
            cmd[0] = resolved
    completed = subprocess.run(
        cmd,
        cwd=str(vault),
        text=True,
        stdout=subprocess.PIPE,
        stderr=None,
        env=os.environ.copy(),
        errors="replace",
    )
    summary = parse_json_output(completed.stdout)
    if not isinstance(summary, dict):
        raise CommandError(command, completed.returncode, completed.stdout or "", "")
    return summary


def validation_command(label: str, args: list[str], vault: Path) -> dict[str, Any]:
    completed = run(args, cwd=vault, check=False)
    return {
        "command": label,
        "args": args,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "json": parse_json_output(completed.stdout),
    }


def run_validation(args: argparse.Namespace, vault: Path, summary: dict[str, Any]) -> None:
    slug = args.topic_slug
    topic_id = f"yt-channels/{slug}"
    specs: list[tuple[str, list[str]]] = [
        ("topic info", [args.kb_path, "topic", "info", topic_id]),
        ("lint", [args.kb_path, "lint", topic_id, "--save"]),
    ]
    if not args.no_index:
        index_command = [args.kb_path, "index", "--topic", topic_id, "--name", slug]
        if not args.embed:
            index_command.append("--embed=false")
        specs.append(("index", index_command))
    specs.append(
        (
            "search",
            [
                args.kb_path,
                "search",
                slug,
                "--topic",
                topic_id,
                "--collection",
                slug,
                "--lex",
                "--format",
                "json",
            ],
        )
    )
    for label, command in specs:
        result = validation_command(label, command, vault)
        summary["validation"].append(result)
        if result["exit_code"] != 0:
            summary["failures"].append(
                {
                    "video_id": "validation",
                    "title": label,
                    "url": "",
                    "error": f"validation command failed: {label}",
                    "stdout": result["stdout"],
                    "stderr": result["stderr"],
                }
            )
            break
    topic_info = next(
        (item.get("json") for item in summary["validation"] if item["command"] == "topic info"),
        None,
    )
    if isinstance(topic_info, dict):
        source_count = int(topic_info.get("sourceCount", 0))
        successful = len(summary.get("ingested", [])) + len(summary.get("skipped", []))
        if source_count < successful:
            summary["failures"].append(
                {
                    "video_id": "validation",
                    "title": "source count",
                    "url": "",
                    "error": f"sourceCount {source_count} is lower than successful/skipped video count {successful}",
                    "stdout": "",
                    "stderr": "",
                }
            )


def write_report(topic_dir: Path, summary: dict[str, Any]) -> Path:
    reports = topic_dir / "outputs" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now()
    stamp = now.strftime("%Y-%m-%d-%H%M%S")
    path = reports / f"{stamp}-youtube-channel-ingest.md"
    videos = summary.get("videos", [])
    ingested = summary.get("ingested", [])
    skipped = summary.get("skipped", [])
    failures = summary.get("failures", [])
    lines = [
        "---",
        f"title: YouTube Channel Ingest Report - {summary.get('topic', '')}",
        "type: output",
        "stage: lint-report",
        f"domain: {summary.get('domain', 'youtube-channel')}",
        f"created: {now.strftime('%Y-%m-%d')}",
        f"issues_found: {len(failures)}",
        "issues_fixed: 0",
        "tags:",
        "  - youtube-channel",
        "  - ingest",
        "---",
        "",
        "# YouTube Channel Ingest Report",
        "",
        f"- Channel URL: {summary.get('channel_url', '')}",
        f"- Normalized channel URL: {summary.get('normalized_channel_url', '')}",
        f"- Topic: {summary.get('topic', '')}",
        f"- Transcript policy: {summary.get('transcribe', '')}",
        f"- Caption languages: {', '.join(summary.get('caption_languages', []) or ['default'])}",
        f"- Selection: {summary.get('selection', '')}",
        f"- Resolved videos: {len(videos)}",
        f"- Successful ingests: {len(ingested)}",
        f"- Skipped existing videos: {len(skipped)}",
        f"- Failures: {len(failures)}",
        "",
        "## Videos",
        "",
    ]
    for video in videos:
        lines.append(f"- {video.get('video_id', '')} - {video.get('title', '')} - {video.get('url', '')}")
    lines.extend(["", "## Ingested", ""])
    for item in ingested:
        lines.append(f"- {item.get('video_id', '')} - {item.get('title', '')}")
    lines.extend(["", "## Skipped", ""])
    for item in skipped:
        lines.append(f"- {item.get('video_id', '')} - {item.get('title', '')}")
    lines.extend(["", "## Failures", ""])
    if failures:
        for item in failures:
            lines.extend(
                [
                    f"### {item.get('video_id', '')} - {item.get('title', '')}",
                    "",
                    f"- URL: {item.get('url', '') or 'n/a'}",
                    f"- Error: {item.get('error', '')}",
                ]
            )
            for stream_name in ("stderr", "stdout"):
                stream = str(item.get(stream_name, "")).strip()
                if stream:
                    lines.extend(["", f"{stream_name}:", "", "```text", stream, "```"])
            lines.append("")
    else:
        lines.append("- None")
    lines.extend(["", "## Validation", ""])
    for item in summary.get("validation", []):
        lines.append(f"- {item['command']}: exit {item['exit_code']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_ingest(args: argparse.Namespace) -> dict[str, Any]:
    validate_inputs(args)
    vault = Path(args.vault).expanduser().resolve()
    if not vault.exists():
        raise RuntimeError(f"vault does not exist: {vault}")

    # The native `kb ingest channel` requires the topic to already exist, so the
    # topic is scaffolded first even for a dry run.
    topic_dir = scaffold_topic(vault, args.topic_slug, args.title, args.domain, args.kb_path)
    write_topic_metadata(topic_dir, args.topic_slug, args.title, args.domain)
    ensure_agents_symlink(topic_dir)
    update_category_docs(vault)

    if args.query or args.title_regex:
        selection_desc = f"thematic: query={args.query!r}" if args.query else f"thematic: regex={args.title_regex!r}"
        videos = resolve_thematic_videos(
            args.channel_url,
            args.query,
            args.title_regex,
            args.limit,
            args.yt_dlp_path,
        )
        channel = ingest_thematic(args, vault, topic_dir, videos, selection_desc, args.dry_run)
    elif args.playlist:
        playlist_url, playlist_title = resolve_playlist(args.channel_url, args.playlist, args.yt_dlp_path)
        args.channel_url = playlist_url
        channel = ingest_channel(args, vault, args.dry_run)
        channel["selection"] = f"playlist: {playlist_title} ({playlist_url})"
    else:
        channel = ingest_channel(args, vault, args.dry_run)

    summary: dict[str, Any] = dict(channel)
    summary["topic"] = f"yt-channels/{args.topic_slug}"
    summary["topic_path"] = str(topic_dir)
    summary["domain"] = args.domain
    summary.setdefault("ingested", [])
    summary.setdefault("skipped", [])
    summary.setdefault("failures", [])
    summary.setdefault("videos", [])
    summary["validation"] = []

    if args.dry_run:
        summary["dry_run"] = True
        return summary

    patch_topic_claude(
        topic_dir,
        args.topic_slug,
        args.title,
        args.domain,
        channel.get("normalized_channel_url") or args.channel_url,
        channel.get("selection", ""),
        args.transcribe,
        build_command_line(args),
    )
    source_count = len(youtube_sources(topic_dir))
    update_topic_inventory(topic_dir, source_count)
    write_channel_indexes(topic_dir, args.title, args.domain, source_count)

    run_validation(args, vault, summary)

    report_path = write_report(topic_dir, summary)
    summary["report_path"] = str(report_path)
    summary["dry_run"] = False
    return summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or update a KB topic from a YouTube channel.")
    parser.add_argument("--vault", default=".", help="Vault root path")
    parser.add_argument("--channel-url", required=True, help="YouTube channel or playlist URL")
    parser.add_argument("--topic-slug", required=True, help="Topic slug under yt-channels/")
    parser.add_argument("--title", required=True, help="Topic title")
    parser.add_argument("--domain", required=True, help="Topic domain")

    parser.add_argument("--playlist", help="Playlist title, ID, or URL to ingest from the channel")
    parser.add_argument("--query", help="Search query to find thematic videos on the channel")
    parser.add_argument("--title-regex", help="Regex pattern to filter video titles on the channel")

    selector = parser.add_mutually_exclusive_group(required=False)
    selector.add_argument("--limit", type=int, help="Maximum videos to ingest")
    selector.add_argument("--all", action="store_true", help="Ingest all matching/channel uploads")

    parser.add_argument("--transcribe", choices=["captions", "auto", "stt"], default="captions")
    parser.add_argument(
        "--sub-langs",
        default="orig",
        help="Caption language preference passed to kb (default 'orig' = native original track; "
        "or a comma list like 'pt,en').",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=None,
        help="Concurrent transcript fetches for kb (default from [youtube].bulk_concurrency).",
    )
    parser.add_argument(
        "--throttle",
        default=None,
        help="Delay between transcript fetches, e.g. 2s (default from [youtube].bulk_throttle).",
    )
    parser.add_argument("--kb-path", default="kb")
    parser.add_argument("--yt-dlp-path", default="yt-dlp", help="yt-dlp executable path")
    parser.add_argument("--embed", action="store_true", help="Run vector embedding during the index validation step")
    parser.add_argument(
        "--no-index",
        dest="no_index",
        action="store_true",
        help="Skip the kb index validation step (defer indexing; useful for parallel multi-channel runs).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scaffold the topic skeleton and list the videos kb would ingest, without ingesting any.",
    )
    args = parser.parse_args(argv)

    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be greater than zero")
    if args.concurrency is not None and args.concurrency < 1:
        parser.error("--concurrency must be at least 1")

    is_specialized = bool(args.playlist or args.query or args.title_regex)
    if not is_specialized and not (args.limit or args.all):
        parser.error("one of --limit N or --all is required for whole-channel ingest")

    if is_specialized and not args.limit:
        args.all = True

    return args


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        summary = run_ingest(args)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 1 if summary.get("failures") else 0
    except (CommandError, RuntimeError, ValueError) as err:
        print(json.dumps({"error": str(err)}, indent=2), file=sys.stdout)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
