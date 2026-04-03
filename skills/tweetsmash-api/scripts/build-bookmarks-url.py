#!/usr/bin/env python3
"""Build a TweetSmash bookmarks URL with properly encoded query parameters."""

from __future__ import annotations

import argparse
import sys
from urllib.parse import urlencode


BASE_URL = "https://api.tweetsmash.com/v1/bookmarks"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a TweetSmash /bookmarks URL with encoded filters."
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument("--cursor")
    parser.add_argument("--is-unread-only", choices=("true", "false"))
    parser.add_argument("--hide-archived", choices=("true", "false"))
    parser.add_argument("--media-type")
    parser.add_argument("--author")
    parser.add_argument("--tag")
    parser.add_argument("--posted-from")
    parser.add_argument("--posted-to")
    parser.add_argument("--bookmarked-from")
    parser.add_argument("--bookmarked-to")
    parser.add_argument("--sort-by")
    parser.add_argument("--sort-cursor")
    parser.add_argument("--q")
    parser.add_argument("--vector-search-term")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    params = {
        "limit": args.limit,
        "cursor": args.cursor,
        "is_unread_only": args.is_unread_only,
        "hide_archived": args.hide_archived,
        "media_type": args.media_type,
        "author": args.author,
        "tag": args.tag,
        "posted_from": args.posted_from,
        "posted_to": args.posted_to,
        "bookmarked_from": args.bookmarked_from,
        "bookmarked_to": args.bookmarked_to,
        "sort_by": args.sort_by,
        "sort_cursor": args.sort_cursor,
        "q": args.q,
        "vector_search_term": args.vector_search_term,
    }
    filtered = {key: value for key, value in params.items() if value is not None}

    if not filtered:
        print(BASE_URL)
        return 0

    query = urlencode(filtered, doseq=False)
    print(f"{BASE_URL}?{query}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        sys.stderr.close()
        raise SystemExit(1)
