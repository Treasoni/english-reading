#!/usr/bin/env bash
set -euo pipefail

MODE="apply"
ROOT_DIR=""
AGENT_DIR=""
WORKFLOWS_DIR=""
RULES_DIR=""
DEFAULT_WORKFLOWS_DIR="__DEFAULT_WORKFLOWS_DIR__"
DEFAULT_RULES_DIR="__DEFAULT_RULES_DIR__"
START_MARKER="<!-- workflow-routing:generated:start -->"
END_MARKER="<!-- workflow-routing:generated:end -->"

usage() {
  cat <<'USAGE'
Usage:
  sync-workflow-routing.sh [--check] [--root DIR] [--agent-dir DIR] [--workflows-dir DIR] [--rules-dir DIR]

Options:
  --check          Fail if workflow-routing.md is stale instead of updating it.
  --root DIR       Project root. Defaults to the parent of the installed agent dir.
  --agent-dir DIR  Agent configuration directory (default: inferred from script path).
  --workflows-dir DIR  Workflow definition directory, relative to the project root.
  --rules-dir DIR  Rule directory containing workflow-routing.md, relative to the project root.
  --help           Show this help message.
USAGE
}

warn() {
  printf '%s\n' "sync-workflow-routing: $*" >&2
}

is_python3() {
  "$1" -c 'import sys; raise SystemExit(0 if sys.version_info[0] == 3 else 1)' >/dev/null 2>&1
}

find_python() {
  if [ -n "${PYTHON:-}" ] && is_python3 "$PYTHON"; then
    printf '%s\n' "$PYTHON"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1 && is_python3 python3; then
    printf '%s\n' python3
    return 0
  fi
  if command -v python >/dev/null 2>&1 && is_python3 python; then
    printf '%s\n' python
    return 0
  fi
  return 1
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --check)
      MODE="check"
      ;;
    --root)
      if [ "$#" -lt 2 ]; then
        warn "--root requires a directory"
        exit 2
      fi
      ROOT_DIR="$2"
      shift
      ;;
    --agent-dir)
      if [ "$#" -lt 2 ]; then
        warn "--agent-dir requires a directory"
        exit 2
      fi
      AGENT_DIR="${2%/}"
      shift
      ;;
    --workflows-dir)
      if [ "$#" -lt 2 ]; then
        warn "--workflows-dir requires a directory"
        exit 2
      fi
      WORKFLOWS_DIR="${2%/}"
      shift
      ;;
    --rules-dir)
      if [ "$#" -lt 2 ]; then
        warn "--rules-dir requires a directory"
        exit 2
      fi
      RULES_DIR="${2%/}"
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      warn "unknown option: $1"
      usage >&2
      exit 2
      ;;
  esac
  shift
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "$ROOT_DIR" ] || [ -z "$AGENT_DIR" ]; then
  AGENT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
  INFERRED_ROOT="$(cd "$AGENT_ROOT/.." && pwd)"
  if [ -z "$ROOT_DIR" ]; then
    ROOT_DIR="$INFERRED_ROOT"
  fi
  if [ -z "$AGENT_DIR" ]; then
    AGENT_DIR="${AGENT_ROOT#"$INFERRED_ROOT"/}"
  fi
fi

if [ ! -d "$ROOT_DIR" ]; then
  warn "project root not found: $ROOT_DIR"
  exit 1
fi

ROOT_DIR="$(cd "$ROOT_DIR" && pwd)"
AGENT_DIR="${AGENT_DIR%/}"
if [ "$DEFAULT_WORKFLOWS_DIR" = "__DEFAULT_WORKFLOWS_DIR__" ]; then
  DEFAULT_WORKFLOWS_DIR=""
fi
if [ "$DEFAULT_RULES_DIR" = "__DEFAULT_RULES_DIR__" ]; then
  DEFAULT_RULES_DIR=""
fi
WORKFLOWS_DIR="${WORKFLOWS_DIR:-${DEFAULT_WORKFLOWS_DIR:-${AGENT_DIR}/workflows}}"
RULES_DIR="${RULES_DIR:-${DEFAULT_RULES_DIR:-${AGENT_DIR}/rules}}"
WORKFLOWS_PATH="$ROOT_DIR/$WORKFLOWS_DIR"
ROUTING_FILE="$ROOT_DIR/$RULES_DIR/workflow-routing.md"

if [ ! -f "$ROUTING_FILE" ]; then
  warn "routing file not found: $ROUTING_FILE"
  exit 1
fi

PYTHON_BIN="$(find_python)" || {
  warn "Python 3 is required (python3 or python)"
  exit 1
}

yaml_value() {
  local file="$1"
  local key="$2"
  awk -v key="$key" '
    $0 ~ "^[[:space:]]*" key "[[:space:]]*:" {
      sub("^[[:space:]]*" key "[[:space:]]*:[[:space:]]*", "")
      gsub(/^[\"\047]|[\"\047]$/, "")
      print
      exit
    }
  ' "$file"
}

escape_md() {
  local value="$1"
  value="${value//|/\\|}"
  printf '%s' "$value"
}

normalize_required() {
  case "$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')" in
    true|yes|y|1|required) printf 'yes' ;;
    *) printf 'no' ;;
  esac
}

generate_table() {
  local workflow_dir routing_file workflow_id required when_to_use triggers excludes state_file_pattern definition

  printf '%s\n' '| Workflow ID | Required | When To Use | Positive Triggers | Excludes | Definition | State File Pattern |'
  printf '%s\n' '| --- | --- | --- | --- | --- | --- | --- |'

  if [ ! -d "$WORKFLOWS_PATH" ]; then
    return
  fi

  for workflow_dir in "$WORKFLOWS_PATH"/*; do
    [ -d "$workflow_dir" ] || continue
    routing_file="$workflow_dir/routing.yaml"
    [ -f "$routing_file" ] || continue

    workflow_id="$(yaml_value "$routing_file" "workflow_id")"
    if [ -z "$workflow_id" ]; then
      workflow_id="$(basename "$workflow_dir")"
    fi
    required="$(normalize_required "$(yaml_value "$routing_file" "required")")"
    when_to_use="$(yaml_value "$routing_file" "when_to_use")"
    triggers="$(yaml_value "$routing_file" "triggers")"
    excludes="$(yaml_value "$routing_file" "excludes")"
    state_file_pattern="$(yaml_value "$routing_file" "state_file_pattern")"
    definition="${WORKFLOWS_DIR}/${workflow_id}/workflow.md"

    printf '| `%s` | %s | %s | %s | %s | `%s` | `%s` |\n' \
      "$(escape_md "$workflow_id")" \
      "$(escape_md "$required")" \
      "$(escape_md "$when_to_use")" \
      "$(escape_md "$triggers")" \
      "$(escape_md "$excludes")" \
      "$(escape_md "$definition")" \
      "$(escape_md "$state_file_pattern")"
  done
}

GENERATED_TABLE="$(generate_table)"
export MODE ROUTING_FILE START_MARKER END_MARKER GENERATED_TABLE

"$PYTHON_BIN" - <<'PY'
from __future__ import annotations

import os
import sys
from pathlib import Path

mode = os.environ["MODE"]
routing_file = Path(os.environ["ROUTING_FILE"])
start = os.environ["START_MARKER"]
end = os.environ["END_MARKER"]
generated_table = os.environ["GENERATED_TABLE"]

text = routing_file.read_text(encoding="utf-8")
if start not in text or end not in text:
    print(f"sync-workflow-routing: missing generated markers in {routing_file}", file=sys.stderr)
    sys.exit(1)

before, rest = text.split(start, 1)
_, after = rest.split(end, 1)
replacement = f"{start}\n{generated_table}\n{end}"
new_text = before + replacement + after

if mode == "check":
    if new_text != text:
        print(f"sync-workflow-routing: stale routing table: {routing_file}", file=sys.stderr)
        sys.exit(1)
    print(f"sync-workflow-routing: up to date: {routing_file}")
else:
    routing_file.write_text(new_text, encoding="utf-8")
    print(f"sync-workflow-routing: updated: {routing_file}")
PY
