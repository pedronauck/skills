#!/usr/bin/env bash
# Seeds an isolated Northstar lab for recordings and holds its live states until SIGINT.
# Run through a CompozyOS terminal. Usage: compozy-lab.sh <compozy-checkout> [home] [port]
set -euo pipefail
checkout="${1:?compozy checkout with the demo seed}"
home="${2:-/tmp/demo-lab}"
port="${3:-47393}"
case "$home" in /tmp/*) ;; *) echo "home must live under /tmp" >&2; exit 2 ;; esac
cd "$checkout"
[ -x bin/compozy ] && [ -d web/dist ] || make build web-build
[ -x bin/acpmock-driver ] || go build -o bin/acpmock-driver ./internal/testutil/acpmock/cmd/acpmock-driver
rm -rf "$home"
go run ./scripts/demo-seed --home "$home" --replace
COMPOZY_HOME="$home" ./bin/compozy config set http.port "$port" --scope user >/dev/null
COMPOZY_HOME="$home" ./bin/compozy config set shell.sessions.group_by project --scope user >/dev/null
COMPOZY_HOME="$home" ./bin/compozy config set agents.always_on.max_active_instances 40 --scope user >/dev/null
echo LAB_SEEDED
exec go run ./scripts/demo-seed --home "$home" --live
