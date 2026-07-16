#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 scripts/verify-vault.py "$@"
python3 .agents/skills/maintain-learnings/scripts/sync_platform_skills.py --root . --strict
.codex/scripts/sync-workflow-routing.sh --check
.claude/scripts/sync-workflow-routing.sh --check
.codex/scripts/check-env-template.sh
.claude/scripts/check-env-template.sh
