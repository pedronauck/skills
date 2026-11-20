#!/usr/bin/env bash
# upload-evidence.sh — host PR screenshots/recordings in the public R2 evidence bucket.
#
# Usage: upload-evidence.sh [--slug <slug>] <file>[#<alt text>] ...
#
# Run from inside the repository whose PR the evidence belongs to. Each file is
# uploaded to <bucket>/<owner>/<repo>/<slug>/<short-sha>-<token>/<NN>-<name>,
# verified with an HTTP HEAD (200 and the expected content type), and printed as
# one Markdown line ready for the PR body. Any failed upload or check exits 1.
#
# Environment overrides:
#   PR_EVIDENCE_BUCKET      default compozy-pr-evidence
#   PR_EVIDENCE_PUBLIC_URL  default the bucket's public r2.dev URL
#   WRANGLER                default `wrangler` on PATH, else `npx --yes wrangler@4`

set -euo pipefail

BUCKET="${PR_EVIDENCE_BUCKET:-compozy-pr-evidence}"
PUBLIC_URL="${PR_EVIDENCE_PUBLIC_URL:-https://pub-6cb601c36b3b4de9bc57fae6b15686d0.r2.dev}"
PUBLIC_URL="${PUBLIC_URL%/}"

die() { printf 'upload-evidence: %s\n' "$*" >&2; exit 1; }
sanitize() { printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9._-]+/-/g; s/^-+|-+$//g'; }

slug=""
files=()
while [ $# -gt 0 ]; do
    case "$1" in
        --slug) [ $# -ge 2 ] || die "--slug needs a value"; slug="$2"; shift 2 ;;
        -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
        *) files+=("$1"); shift ;;
    esac
done
[ "${#files[@]}" -gt 0 ] || die "pass at least one file"

git rev-parse --show-toplevel >/dev/null 2>&1 || die "run inside the PR's git repository"
remote="$(git remote get-url origin 2>/dev/null)" || die "no origin remote"
# Keep only the path: scheme, userinfo (tokens!), host and port never reach the public key.
case "$remote" in
    *://*) owner_repo="${remote#*://}"; owner_repo="${owner_repo#*/}" ;;
    *:*) owner_repo="${remote##*:}" ;;
    *) owner_repo="$remote" ;;
esac
owner_repo="${owner_repo%/}"
owner_repo="${owner_repo%.git}"
case "$owner_repo" in */*/*) owner_repo="${owner_repo#"${owner_repo%/*/*}/"}" ;; esac
case "$owner_repo" in */*) ;; *) die "cannot parse owner/repo from origin" ;; esac
owner_repo="$(sanitize "${owner_repo%%/*}")/$(sanitize "${owner_repo#*/}")"

[ -n "$slug" ] || slug="$(git branch --show-current)"
slug="$(sanitize "$slug")"
[ -n "$slug" ] || die "detached HEAD: pass --slug <slug>"
sha="$(git rev-parse --short=7 HEAD)"
# Unguessable path segment: the bucket is public, so keys must not be enumerable.
token="$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')"
prefix="$owner_repo/$slug/$sha-$token"

if [ -n "${WRANGLER:-}" ]; then
    read -r -a wrangler <<<"$WRANGLER"
elif command -v wrangler >/dev/null 2>&1; then
    wrangler=(wrangler)
else
    wrangler=(npx --yes wrangler@4)
fi

# Run wrangler from an empty directory so a repository's .env or wrangler config
# cannot redirect the upload to another account or bucket.
neutral="$(mktemp -d)"
trap 'rm -rf "$neutral"' EXIT

n=0
for spec in "${files[@]}"; do
    path="${spec%%#*}"
    alt="${spec#*#}"
    [ "$alt" != "$spec" ] || alt=""
    [ -f "$path" ] || die "not a file: $path"
    abs="$(cd "$(dirname "$path")" && pwd)/$(basename "$path")"
    name="$(sanitize "$(basename "$path")")"
    case "$name" in
        *.png) type=image/png ;;
        *.jpg|*.jpeg) type=image/jpeg ;;
        *.gif) type=image/gif ;;
        *.webp) type=image/webp ;;
        *.mp4) type=video/mp4 ;;
        *.webm) type=video/webm ;;
        *) die "unsupported evidence type: $path" ;;
    esac
    n=$((n + 1))
    key="$prefix/$(printf '%02d' "$n")-$name"
    (cd "$neutral" && "${wrangler[@]}" r2 object put "$BUCKET/$key" --file "$abs" --content-type "$type" --remote >/dev/null) \
        || die "upload failed: $path"
    url="$PUBLIC_URL/$key"
    headers=""
    for _ in 1 2 3; do
        headers="$(curl -sSI --connect-timeout 5 --max-time 15 "$url" | tr -d '\r')" || headers=""
        printf '%s\n' "$headers" | head -1 | grep -q ' 200' && break
        sleep 2
    done
    printf '%s\n' "$headers" | head -1 | grep -q ' 200' || die "not publicly readable (expected 200): $url"
    printf '%s\n' "$headers" | grep -qi "^content-type: $type" || die "wrong content type (expected $type): $url"
    [ -n "$alt" ] || alt="${name%.*}"
    case "$type" in
        image/*) printf '![%s](%s)\n' "$alt" "$url" ;;
        *) printf '[%s](%s)\n' "$alt" "$url" ;;
    esac
done
