#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PACKAGE_DIR_NAME="kaoyan-english-reading-essential"
VERSION="$(sed -n 's/^version = "\(.*\)"/\1/p' "$ROOT_DIR/pyproject.toml" | head -1)"

if [[ -z "$VERSION" ]]; then
  echo "Could not read version from pyproject.toml" >&2
  exit 1
fi

TMP_BASE="$(mktemp -d "${TMPDIR:-/tmp}/kaoyan-reading-package.XXXXXX")"
STAGING_DIR="$TMP_BASE/$PACKAGE_DIR_NAME"
VERIFY_DIR="$TMP_BASE/verify"
VERIFY_OUTPUT_DIR="$TMP_BASE/verify-output"
DIST_DIR="$ROOT_DIR/dist"
ZIP_PATH="$DIST_DIR/$PACKAGE_DIR_NAME-$VERSION.zip"

cleanup() {
  rm -rf "$TMP_BASE"
}
trap cleanup EXIT

mkdir -p "$STAGING_DIR" "$STAGING_DIR/examples" "$DIST_DIR"
mkdir -p "$STAGING_DIR/.agents/skills"

copy_file() {
  local source="$1"
  if [[ -f "$ROOT_DIR/$source" ]]; then
    cp "$ROOT_DIR/$source" "$STAGING_DIR/$source"
  fi
}

copy_file "README.md"
copy_file "AGENTS.md"
copy_file "CLAUDE.md"
copy_file "pyproject.toml"
copy_file ".gitignore"
cp "$ROOT_DIR/examples/sample-exam.txt" "$STAGING_DIR/examples/sample-exam.txt"
cp -R "$ROOT_DIR/src" "$STAGING_DIR/src"
cp -R "$ROOT_DIR/tests" "$STAGING_DIR/tests"

CORE_SKILLS=(
  "analyze-sentence"
  "compile-note"
  "extract-vocabulary"
  "format-article"
  "obsidian-markdown"
  "organize-grammar"
  "summarize-grammar"
  "translate"
)

for skill in "${CORE_SKILLS[@]}"; do
  cp -R "$ROOT_DIR/.agents/skills/$skill" "$STAGING_DIR/.agents/skills/$skill"
done

find "$STAGING_DIR" -name ".DS_Store" -delete
find "$STAGING_DIR" -name "__pycache__" -type d -prune -exec rm -rf {} +
find "$STAGING_DIR" -name ".pytest_cache" -type d -prune -exec rm -rf {} +

rm -f "$ZIP_PATH"
(cd "$TMP_BASE" && zip -rq "$ZIP_PATH" "$PACKAGE_DIR_NAME")

mkdir -p "$VERIFY_DIR"
unzip -q "$ZIP_PATH" -d "$VERIFY_DIR"

(
  cd "$VERIFY_DIR/$PACKAGE_DIR_NAME"
  PYTHONPYCACHEPREFIX="$TMP_BASE/pycache" python3 -m compileall -q src tests
  PYTHONPATH=src PYTHONPYCACHEPREFIX="$TMP_BASE/pycache" python3 -m kaoyan_reading.cli --help >/dev/null
  PYTHONPATH=src PYTHONPYCACHEPREFIX="$TMP_BASE/pycache" python3 -m kaoyan_reading.cli \
    init-workflow examples/sample-exam.txt \
    --year 2000 \
    --out "$VERIFY_OUTPUT_DIR" \
    --jobs 2 >/dev/null
)

if unzip -l "$ZIP_PATH" | grep -E 'intermediate/|200[0-9]阅读|\.obsidian|\.git/|\.claude/|\.codex/|origin\.pdf|images/' >/dev/null; then
  echo "Package contains excluded personal or bulky files." >&2
  exit 1
fi

echo "Created package:"
echo "$ZIP_PATH"
