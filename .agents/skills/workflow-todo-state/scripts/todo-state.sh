#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="${SCRIPT_DIR}/todo-state.py"

if [ ! -f "$PY_SCRIPT" ]; then
  echo "todo-state: Python implementation not found: $PY_SCRIPT" >&2
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$PY_SCRIPT" "$@"
fi

if command -v python >/dev/null 2>&1; then
  exec python "$PY_SCRIPT" "$@"
fi

if command -v py >/dev/null 2>&1; then
  exec py -3 "$PY_SCRIPT" "$@"
fi

echo "todo-state: Python 3 is required. Install Python 3 or run todo-state.py with a Python 3 interpreter." >&2
exit 127
