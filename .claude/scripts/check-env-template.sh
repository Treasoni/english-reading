#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  .claude/scripts/check-env-template.sh [--env-file .env.example] [--strict]

Checks that .env.example documents environment variables referenced by project
code, scripts, hooks, workflow definitions, and templates. The default mode
fails on missing variables and suspicious secrets. --strict also fails on
template variables that are not referenced by scanned project files.
USAGE
}

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${PROJECT_ROOT}/.env.example"
STRICT=false

while [ "$#" -gt 0 ]; do
  case "$1" in
    --env-file)
      [ "$#" -ge 2 ] || { echo "check-env-template: --env-file requires a value" >&2; exit 2; }
      ENV_FILE="$2"
      shift 2
      ;;
    --strict)
      STRICT=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "check-env-template: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ ! -f "$ENV_FILE" ]; then
  echo "check-env-template: env template not found: $ENV_FILE" >&2
  exit 1
fi

if ! command -v rg >/dev/null 2>&1; then
  echo "check-env-template: ripgrep (rg) is required" >&2
  exit 1
fi

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/check-env-template.XXXXXX")"
trap 'rm -rf "$TMP_DIR"' EXIT

template_vars_file="${TMP_DIR}/template-vars.txt"
referenced_vars_file="${TMP_DIR}/referenced-vars.txt"
missing_vars_file="${TMP_DIR}/missing-vars.txt"
unused_vars_file="${TMP_DIR}/unused-vars.txt"
secret_findings_file="${TMP_DIR}/secret-findings.txt"
ignored_vars_file="${TMP_DIR}/ignored-vars.txt"

cat > "$ignored_vars_file" <<'EOF'
BASH_SOURCE
AGENT_DIR
CUSTOM_AGENTS
END_MARKER
ENTRY_FILE
GENERATED_BLOCK
GENERATED_TABLE
HOME
LABEL
MODE
NOW
OLDPWD
PATH
PHASE
PHASE_NUM
PROJECT_DIR
PROJECT_ROOT
PROJECT_SLUG
PWD
REASON
ROOT
ROUTING_FILE
RUNS_DIR
RUN_ID
RUN_STATE_FILE
SCRIPT_DIR
SHELL
SKILL_DIR
SKILLS_DIR
STAMP
START_MARKER
TARGET_PROJECT
TMPDIR
TMP_DIR
TODO_FILE
TOPIC
TOTAL_CHAPTERS
USER
WORKFLOW_DIR
WORKFLOW_ID
WORKFLOW_STATE_FILE
EOF

awk '
  /^[[:space:]]*#/ || /^[[:space:]]*$/ { next }
  /^[A-Z][A-Z0-9_]*[[:space:]]*=/ {
    key = $0
    sub(/[[:space:]]*=.*/, "", key)
    print key
  }
' "$ENV_FILE" | sort -u > "$template_vars_file"

extract_vars() {
  perl -ne '
    while (/process\.env\.([A-Z][A-Z0-9_]*)/g) { print "$1\n" }
    while (/process\.env\[['\''"]([A-Z][A-Z0-9_]*)['\''"]\]/g) { print "$1\n" }
    while (/import\.meta\.env\.([A-Z][A-Z0-9_]*)/g) { print "$1\n" }
    while (/os\.getenv\(['\''"]([A-Z][A-Z0-9_]*)['\''"]/g) { print "$1\n" }
    while (/os\.environ(?:\.get)?\(['\''"]([A-Z][A-Z0-9_]*)['\''"]/g) { print "$1\n" }
    while (/os\.environ\[['\''"]([A-Z][A-Z0-9_]*)['\''"]\]/g) { print "$1\n" }
    while (/\$\{([A-Z][A-Z0-9_]*)(?::-[^}]*)?\}/g) { print "$1\n" }
    while (/\b([A-Z][A-Z0-9_]*(?:_API_KEY|_TOKEN|_SECRET|_PASSWORD|_DSN|_URL|_PATH|_MODEL|_PROVIDER|_ENABLED|_ENV|_PORT))\b/g) { print "$1\n" }
  '
}

rg -n --hidden --no-heading \
  -g '!.git/**' \
  -g '!.claude/**' \
  -g '!node_modules/**' \
  -g '!dist/**' \
  -g '!build/**' \
  -g '!.next/**' \
  -g '!coverage/**' \
  -g '!workspace/**' \
  -g '!README.md' \
  -g '!.env' \
  -g '!.env.*' \
  -g '!.env.example' \
  -g '!.claude/rules/common/env.md' \
  -g '!templates/env/**' \
  'process\.env|import\.meta\.env|os\.getenv|os\.environ|\$\{[A-Z][A-Z0-9_]*|[A-Z][A-Z0-9_]*(?:_API_KEY|_TOKEN|_SECRET|_PASSWORD|_DSN|_URL|_PATH|_MODEL|_PROVIDER|_ENABLED|_ENV|_PORT)' \
  "$PROJECT_ROOT" \
  | extract_vars \
  | grep -Fvx -f "$ignored_vars_file" \
  | sort -u > "$referenced_vars_file" || true

comm -23 "$referenced_vars_file" "$template_vars_file" > "$missing_vars_file"
comm -13 "$referenced_vars_file" "$template_vars_file" > "$unused_vars_file"

awk -F= '
  /^[[:space:]]*#/ || /^[[:space:]]*$/ { next }
  /^[A-Z][A-Z0-9_]*[[:space:]]*=/ {
    key = $1
    sub(/[[:space:]]+$/, "", key)
    value = substr($0, index($0, "=") + 1)
    sub(/^[[:space:]]+/, "", value)
    sub(/[[:space:]]+$/, "", value)
    gsub(/^["'\'']|["'\'']$/, "", value)
    if (key ~ /(KEY|SECRET|TOKEN|PASSWORD|PRIVATE|DSN)$/ && value != "" && value !~ /^(your-|example-|change-me|placeholder)/) {
      print key
    }
  }
' "$ENV_FILE" > "$secret_findings_file"

status=0

echo "Env template: ${ENV_FILE#$PROJECT_ROOT/}"
echo "Referenced variables: $(wc -l < "$referenced_vars_file" | tr -d ' ')"
echo "Template variables:   $(wc -l < "$template_vars_file" | tr -d ' ')"

if [ -s "$missing_vars_file" ]; then
  echo
  echo "Missing from .env.example:"
  sed 's/^/  - /' "$missing_vars_file"
  status=1
fi

if [ -s "$secret_findings_file" ]; then
  echo
  echo "Sensitive-looking variables have non-placeholder values:"
  sed 's/^/  - /' "$secret_findings_file"
  status=1
fi

if [ -s "$unused_vars_file" ]; then
  echo
  echo "Template variables not referenced by scanned files:"
  sed 's/^/  - /' "$unused_vars_file"
  if [ "$STRICT" = true ]; then
    status=1
  else
    echo "  (Allowed in default mode for documented optional integrations.)"
  fi
fi

if [ -f "${PROJECT_ROOT}/.gitignore" ]; then
  if ! grep -qxF ".env" "${PROJECT_ROOT}/.gitignore"; then
    echo
    echo ".gitignore does not contain a standalone .env entry."
    status=1
  fi
fi

if [ "$status" -eq 0 ]; then
  echo
  echo "Env template check passed."
fi

exit "$status"
