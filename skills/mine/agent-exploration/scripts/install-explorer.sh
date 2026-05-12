#!/usr/bin/env bash
# install-explorer.sh — bootstrap helper for the agent-exploration skill.
# Role: bootstrap helper (writes one or two files per invocation).
# Installs the bundled explorer subagent definition for Claude Code,
# OpenAI Codex CLI, or both. Refuses to overwrite existing files.
#
# Usage:
#   install-explorer.sh [--target claude|codex|both] [--user|--project]
#
# Defaults: --target both, --project (installs into the nearest project root).
# Pass --user to install into $HOME instead.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SRC_CLAUDE="${SKILL_DIR}/assets/explorer-agent.md"
SRC_CODEX="${SKILL_DIR}/assets/explorer-agent.toml"

TARGET="both"
SCOPE="project"

while [ $# -gt 0 ]; do
  case "$1" in
    --target)
      shift
      case "${1:-}" in
        claude|codex|both) TARGET="$1" ;;
        *) echo "ERROR: --target must be one of: claude, codex, both" >&2; exit 2 ;;
      esac
      ;;
    --target=*)
      VAL="${1#--target=}"
      case "${VAL}" in
        claude|codex|both) TARGET="${VAL}" ;;
        *) echo "ERROR: --target must be one of: claude, codex, both" >&2; exit 2 ;;
      esac
      ;;
    --user)    SCOPE="user" ;;
    --project) SCOPE="project" ;;
    -h|--help)
      sed -n '2,11p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      exit 2
      ;;
  esac
  shift || true
done

find_project_root() {
  local dir
  dir="$(pwd)"
  while [ "${dir}" != "/" ]; do
    if [ -d "${dir}/.claude" ] || [ -d "${dir}/.codex" ] || [ -f "${dir}/CLAUDE.md" ] || [ -f "${dir}/AGENTS.md" ]; then
      printf '%s\n' "${dir}"
      return 0
    fi
    dir="$(dirname "${dir}")"
  done
  printf '%s\n' "$(pwd)"
}

if [ "${SCOPE}" = "user" ]; then
  BASE="${HOME}"
else
  BASE="$(find_project_root)"
fi

install_one() {
  local label="$1" src="$2" dest_dir="$3" dest_file="$4"
  if [ ! -f "${src}" ]; then
    echo "ERROR: bundled ${label} definition not found at ${src}" >&2
    return 2
  fi
  mkdir -p "${dest_dir}"
  if [ -e "${dest_file}" ]; then
    echo "SKIP : ${label} already installed at ${dest_file}. Delete it first to reinstall."
    return 0
  fi
  cp "${src}" "${dest_file}"
  echo "OK   : installed ${label} → ${dest_file}"
}

INSTALLED_ANY=0
case "${TARGET}" in
  claude|both)
    install_one "Claude Code agent" "${SRC_CLAUDE}" "${BASE}/.claude/agents" "${BASE}/.claude/agents/explorer.md"
    INSTALLED_ANY=1
    ;;
esac
case "${TARGET}" in
  codex|both)
    install_one "Codex CLI agent" "${SRC_CODEX}" "${BASE}/.codex/agents" "${BASE}/.codex/agents/explorer.toml"
    INSTALLED_ANY=1
    ;;
esac

if [ "${INSTALLED_ANY}" -eq 0 ]; then
  echo "ERROR: nothing installed (target=${TARGET})" >&2
  exit 2
fi

echo "scope: ${SCOPE}  base: ${BASE}  target: ${TARGET}"
