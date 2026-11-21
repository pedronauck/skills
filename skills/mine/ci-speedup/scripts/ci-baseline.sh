#!/usr/bin/env bash
# Read-only CI baseline: per-job and slowest-step durations for recent workflow runs.
#
#   ci-baseline.sh <owner/repo> [workflow-file-or-name] [runs]
#
# Uses one `gh` call for the run list and one per run. Never downloads logs.
# Requires: gh (authenticated), jq.
set -euo pipefail

if [ $# -lt 1 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
fi

repo="$1"
workflow="${2:-}"
limit="${3:-3}"

for tool in gh jq; do
  command -v "$tool" >/dev/null 2>&1 || { echo "ci-baseline: $tool is required" >&2; exit 1; }
done
case "$limit" in
  '' | *[!0-9]*) echo "ci-baseline: runs must be a positive integer" >&2; exit 2 ;;
esac

list_args=(run list --repo "$repo" --status completed --limit 40
  --json "databaseId,workflowName,event,conclusion,headBranch,createdAt,updatedAt,url")
if [ -n "$workflow" ]; then
  list_args+=(--workflow "$workflow")
fi

# Prefer runs that actually ran to the end; cancelled runs say nothing about duration.
runs="$(gh "${list_args[@]}" | jq -c --argjson limit "$limit" \
  '[.[] | select(.conclusion == "success" or .conclusion == "failure")] | .[:$limit] | .[]')"

if [ -z "$runs" ]; then
  echo "No completed (success or failure) runs found for $repo${workflow:+ workflow $workflow}."
  exit 0
fi

while IFS= read -r run; do
  id="$(jq -r '.databaseId' <<<"$run")"
  jq -r '"\n## \(.workflowName) #\(.databaseId): \(.event) on \(.headBranch), \(.conclusion)\n\(.url)"' <<<"$run"

  gh api "repos/$repo/actions/runs/$id/jobs?per_page=100" | jq -r '
    def ts: sub("\\.[0-9]+Z$"; "Z") | fromdateiso8601;
    def secs(a; b): if (a and b) then ((b | ts) - (a | ts)) else null end;
    def fmt: if . == null then "-" else "\(.)s" end;
    [.jobs[] | select(.started_at and .completed_at)] as $jobs
    | if ($jobs | length) == 0 then "No jobs with timing data." else
        ([$jobs[].created_at | ts] | min) as $first
        | ([$jobs[].completed_at | ts] | max) as $last
        | "Wall clock: \($last - $first)s. Runner time: \([$jobs[] | secs(.started_at; .completed_at)] | add)s across \($jobs | length) jobs.",
          "",
          "| Job | Runner | Result | Queue | Duration | Slowest steps |",
          "|---|---|---|---|---|---|",
          ($jobs | sort_by(-secs(.started_at; .completed_at))[]
            | "| \(.name) | \(.labels | join(", ")) | \(.conclusion) | \(secs(.created_at; .started_at) | fmt) | \(secs(.started_at; .completed_at) | fmt) | \(
                [.steps[]? | select(.started_at and .completed_at)
                  | {name, s: secs(.started_at; .completed_at)}]
                | sort_by(-.s) | .[:3] | map("\(.name) \(.s)s") | join("; ")) |")
      end'
done <<<"$runs"
