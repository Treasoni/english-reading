#!/usr/bin/env bash

# Report locations and rule names only. Matched content must never reach stdout.
set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DETECTOR="$SCRIPT_DIR/detect-secrets.pl"
MODE="working-tree"
MAX_COMMITS=0
FINDINGS=0
FAILURES=0

usage() {
  cat <<'USAGE'
Usage: audit-secrets.sh [--staged | --history | --all] [--max-commits N]

  --staged          Scan files as staged in the Git index.
  --history         Scan each unique file version reachable from Git history.
  --all             Scan working tree, staged files, and history.
  --max-commits N   Limit commits used to collect historical file versions; 0 means all (default).
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --staged)
      MODE="staged"
      ;;
    --history)
      MODE="history"
      ;;
    --all)
      MODE="all"
      ;;
    --max-commits)
      shift
      if [ "$#" -eq 0 ] || ! [[ "$1" =~ ^[0-9]+$ ]]; then
        printf '%s\n' 'error: --max-commits requires a non-negative integer' >&2
        exit 1
      fi
      MAX_COMMITS="$1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'error: unknown option: %s\n' "$1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

if ! command -v perl >/dev/null 2>&1; then
  printf '%s\n' 'error: perl is required for the secret detector' >&2
  exit 1
fi

if [ ! -f "$DETECTOR" ]; then
  printf '%s\n' 'error: bundled detector is missing' >&2
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf '%s\n' 'error: run this command inside a Git working tree' >&2
  exit 1
fi

record_status() {
  local status="$1"
  local label="$2"

  case "$status" in
    0)
      ;;
    2)
      FINDINGS=1
      ;;
    *)
      printf 'error: could not scan %s\n' "$label" >&2
      FAILURES=1
      ;;
  esac
}

scan_file() {
  local path="$1"
  local label="$2"
  local status=0

  [ -f "$path" ] || return 0
  perl "$DETECTOR" --label "$label" --path "$path" < "$path"
  status=$?
  record_status "$status" "$label"
}

scan_index_file() {
  local path="$1"
  local label="index:$path"
  local status=0

  git show ":$path" 2>/dev/null | perl "$DETECTOR" --label "$label" --path "$path"
  status=${PIPESTATUS[1]}
  record_status "$status" "$label"
}

scan_history_blob() {
  local object="$1"
  local path="$2"
  local short_object="${object:0:12}"
  local source_path="${path:-history-blob-$short_object}"
  local label="history:$source_path"
  local status=0

  git cat-file blob "$object" 2>/dev/null | perl "$DETECTOR" --label "$label" --path "$source_path"
  status=${PIPESTATUS[1]}
  record_status "$status" "$label"
}

history_objects() {
  if [ "$MAX_COMMITS" -gt 0 ]; then
    git rev-list --objects --all --max-count="$MAX_COMMITS"
  else
    git rev-list --objects --all
  fi
}

scan_working_tree() {
  local path

  while IFS= read -r -d '' path; do
    scan_file "$path" "worktree:$path"
  done < <(git ls-files -z)

  while IFS= read -r -d '' path; do
    scan_file "$path" "untracked:$path"
  done < <(git ls-files --others --exclude-standard -z)
}

scan_staged() {
  local path

  while IFS= read -r -d '' path; do
    scan_index_file "$path"
  done < <(git diff --cached --name-only --diff-filter=ACMR -z)
}

scan_history() {
  local object
  local type
  local path

  while IFS=' ' read -r object type path; do
    [ "$type" = 'blob' ] || continue
    scan_history_blob "$object" "$path"
  done < <(history_objects | git cat-file --batch-check='%(objectname) %(objecttype) %(rest)' | awk '$2 == "blob"' | sort -u -k1,1)
}

case "$MODE" in
  working-tree)
    scan_working_tree
    ;;
  staged)
    scan_staged
    ;;
  history)
    scan_history
    ;;
  all)
    scan_working_tree
    scan_staged
    scan_history
    ;;
esac

if [ "$FAILURES" -ne 0 ]; then
  printf '%s\n' 'Secret audit did not finish successfully.' >&2
  exit 1
fi

if [ "$FINDINGS" -ne 0 ]; then
  printf '%s\n' 'Potential credentials found. Do not commit or push until they are reviewed.' >&2
  exit 2
fi

printf '%s\n' 'Secret audit passed: no potential credentials found.'
