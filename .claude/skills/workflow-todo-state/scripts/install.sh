#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  install.sh <target-project> [--with-skill] [--init-layout] [--update-agents] [--profile NAME] [--agent-dir DIR] [--skills-dir DIR] [--entry-file FILE] [--force]

Options:
  --with-skill      Copy the whole workflow-todo-state skill into the target project.
  --init-layout     Create agent workflows, workspace/workflow-runs, and workflow-routing.md.
  --update-agents   Add an idempotent Workflow Todo State block to the entry file.
  --profile NAME    Use a built-in profile from profiles/*.yaml when available.
  --agent-dir DIR   Agent configuration directory in the target project (default: .claude).
  --skills-dir DIR  Skill installation directory (default: <agent-dir>/skills; Codex profile: .agents/skills).
  --entry-file FILE Project instruction file to update (default: CLAUDE.md for the historical .claude profile).
  --force           Replace existing installed files by moving them to timestamped backups.

Examples:
  skills/workflow-todo-state/scripts/install.sh ../other-project
  skills/workflow-todo-state/scripts/install.sh ../other-project --with-skill --init-layout --update-agents
  skills/workflow-todo-state/scripts/install.sh ../other-project --agent-dir .agent --with-skill --init-layout --update-agents
USAGE
}

if [ "$#" -lt 1 ]; then
  usage
  exit 2
fi

TARGET_PROJECT="$1"
shift

WITH_SKILL=false
INIT_LAYOUT=false
UPDATE_AGENTS=false
FORCE=false
AGENT_DIR=".claude"
SKILLS_DIR=".claude/skills"
RULES_DIR=".claude/rules"
SCRIPTS_DIR=".claude/scripts"
WORKFLOWS_DIR=".claude/workflows"
ENTRY_FILE="CLAUDE.md"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROFILE_ROOT="${WORKFLOW_PROFILE_ROOT:-}"

if [ -z "$PROFILE_ROOT" ]; then
  for candidate in "$SKILL_DIR/profiles" "$SCRIPT_DIR/../../profiles" "$SCRIPT_DIR/../../../profiles" "$SCRIPT_DIR/../../../../profiles"; do
    if [ -d "$candidate" ]; then
      PROFILE_ROOT="$(cd "$candidate" && pwd)"
      break
    fi
  done
fi

profile_value() {
  local profile_file="$1"
  local key="$2"
  sed -n "s/^${key}:[[:space:]]*//p" "$profile_file" | head -n 1 | sed "s/^['\"]//; s/['\"]$//"
}

set_agent_dir_defaults() {
  AGENT_DIR="${1%/}"
  SKILLS_DIR="${AGENT_DIR}/skills"
  RULES_DIR="${AGENT_DIR}/rules"
  SCRIPTS_DIR="${AGENT_DIR}/scripts"
  WORKFLOWS_DIR="${AGENT_DIR}/workflows"
}

load_profile() {
  local name="$1"
  local profile_file="${PROFILE_ROOT}/${name}.yaml"

  if [ -f "$profile_file" ]; then
    AGENT_DIR="$(profile_value "$profile_file" agent_dir)"
    SKILLS_DIR="$(profile_value "$profile_file" skills_dir)"
    RULES_DIR="$(profile_value "$profile_file" rules_dir)"
    SCRIPTS_DIR="$(profile_value "$profile_file" scripts_dir)"
    ENTRY_FILE="$(profile_value "$profile_file" entry_file)"
    if [ -z "$AGENT_DIR" ] || [ -z "$SKILLS_DIR" ] || [ -z "$RULES_DIR" ] || [ -z "$ENTRY_FILE" ]; then
      echo "install: invalid profile contract: $profile_file" >&2
      exit 2
    fi
    SCRIPTS_DIR="${SCRIPTS_DIR:-${AGENT_DIR}/scripts}"
    WORKFLOWS_DIR="${AGENT_DIR}/workflows"
    return
  fi

  case "$name" in
    codex)
      AGENT_DIR=".codex"; SKILLS_DIR=".agents/skills"; RULES_DIR=".codex/rules"; SCRIPTS_DIR=".codex/scripts"; WORKFLOWS_DIR=".codex/workflows"; ENTRY_FILE="AGENTS.md"
      ;;
    claude)
      AGENT_DIR=".claude"; SKILLS_DIR=".claude/skills"; RULES_DIR=".claude/rules"; SCRIPTS_DIR=".claude/scripts"; WORKFLOWS_DIR=".claude/workflows"; ENTRY_FILE="CLAUDE.md"
      ;;
    generic)
      AGENT_DIR=".agent"; SKILLS_DIR=".agent/skills"; RULES_DIR=".agent/rules"; SCRIPTS_DIR=".agent/scripts"; WORKFLOWS_DIR=".agent/workflows"; ENTRY_FILE="AGENTS.md"
      ;;
    *)
      echo "install: unknown profile: $name (expected a profiles/<name>.yaml contract)" >&2
      exit 2
      ;;
  esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --with-skill) WITH_SKILL=true ;;
    --init-layout) INIT_LAYOUT=true ;;
    --update-agents) UPDATE_AGENTS=true ;;
    --profile)
      if [ "$#" -lt 2 ]; then
        echo "install: --profile requires a profile name" >&2
        exit 2
      fi
      load_profile "$2"
      shift
      ;;
    --agent-dir)
      if [ "$#" -lt 2 ]; then
        echo "install: --agent-dir requires a directory" >&2
        exit 2
      fi
      set_agent_dir_defaults "$2"
      shift
      ;;
    --skills-dir)
      if [ "$#" -lt 2 ]; then
        echo "install: --skills-dir requires a directory" >&2
        exit 2
      fi
      SKILLS_DIR="${2%/}"
      shift
      ;;
    --entry-file)
      if [ "$#" -lt 2 ]; then
        echo "install: --entry-file requires a file path" >&2
        exit 2
      fi
      ENTRY_FILE="$2"
      shift
      ;;
    --force) FORCE=true ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "install: unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
  shift
done

STAMP="$(date +%Y%m%d%H%M%S)"

if [ ! -d "$TARGET_PROJECT" ]; then
  echo "install: target project does not exist: $TARGET_PROJECT" >&2
  exit 1
fi

TARGET_PROJECT="$(cd "$TARGET_PROJECT" && pwd)"

backup_existing_file() {
  local path="$1"
  local source="$2"
  if [ -e "$path" ]; then
    if [ -f "$path" ] && cmp -s "$source" "$path"; then
      echo "skipped: unchanged ${path}"
      return 2
    fi
    if [ "$FORCE" != true ]; then
      echo "install: already exists, use --force to replace: $path" >&2
      exit 1
    fi
    mv "$path" "${path}.bak.${STAMP}"
  fi
  return 0
}

backup_existing_path() {
  local path="$1"
  local source="${2:-}"
  if [ -e "$path" ]; then
    if [ -n "$source" ] && [ -d "$path" ] && [ -d "$source" ] && diff -qr "$source" "$path" >/dev/null 2>&1; then
      echo "skipped: unchanged ${path}"
      return 2
    fi
    if [ "$FORCE" != true ]; then
      echo "install: already exists, use --force to replace: $path" >&2
      exit 1
    fi
    mv "$path" "${path}.bak.${STAMP}"
  fi
  return 0
}

install_state_script() {
  local target_dir="${TARGET_PROJECT}/${SCRIPTS_DIR}"
  local target_script="${target_dir}/todo-state.sh"

  mkdir -p "$target_dir"
  if ! backup_existing_file "$target_script" "${SCRIPT_DIR}/todo-state.sh"; then
    return
  fi
  cp "${SCRIPT_DIR}/todo-state.sh" "$target_script"
  chmod +x "$target_script"
  echo "installed: ${target_script}"
}

install_routing_sync_script() {
  local target_dir="${TARGET_PROJECT}/${SCRIPTS_DIR}"
  local target_script="${target_dir}/sync-workflow-routing.sh"
  local source_script="${SCRIPT_DIR}/sync-workflow-routing.sh"
  local rendered_script

  mkdir -p "$target_dir"
  rendered_script="$(mktemp "${TMPDIR:-/tmp}/sync-workflow-routing.XXXXXX")"
  sed \
    -e "s#^DEFAULT_WORKFLOWS_DIR=\"__DEFAULT_WORKFLOWS_DIR__\"#DEFAULT_WORKFLOWS_DIR=\"${WORKFLOWS_DIR}\"#" \
    -e "s#^DEFAULT_RULES_DIR=\"__DEFAULT_RULES_DIR__\"#DEFAULT_RULES_DIR=\"${RULES_DIR}\"#" \
    "$source_script" > "$rendered_script"
  if ! backup_existing_file "$target_script" "$rendered_script"; then
    rm -f "$rendered_script"
    return
  fi
  mv "$rendered_script" "$target_script"
  chmod +x "$target_script"
  echo "installed: ${target_script}"
}

install_skill() {
  local target_skills="${TARGET_PROJECT}/${SKILLS_DIR}"
  local target_skill="${target_skills}/workflow-todo-state"

  mkdir -p "$target_skills"
  if [ -e "$target_skill" ]; then
    if diff -qr -x profiles "$SKILL_DIR" "$target_skill" >/dev/null 2>&1 \
      && { [ -z "$PROFILE_ROOT" ] || { [ -d "$target_skill/profiles" ] && diff -qr "$PROFILE_ROOT" "$target_skill/profiles" >/dev/null 2>&1; }; }; then
      echo "skipped: unchanged ${target_skill}"
      return
    fi
    if [ "$FORCE" != true ]; then
      echo "install: already exists, use --force to replace: $target_skill" >&2
      exit 1
    fi
    mv "$target_skill" "${target_skill}.bak.${STAMP}"
  fi
  cp -R "$SKILL_DIR" "$target_skill"
  if [ -n "$PROFILE_ROOT" ] && [ -d "$PROFILE_ROOT" ]; then
    cp -R "$PROFILE_ROOT" "$target_skill/profiles"
  fi
  chmod +x "${target_skill}/scripts/todo-state.sh" "${target_skill}/scripts/install.sh"
  echo "installed: ${target_skill}"
}

init_layout() {
  local workflows_dir="${TARGET_PROJECT}/${WORKFLOWS_DIR}"
  local rules_dir="${TARGET_PROJECT}/${RULES_DIR}"
  local runs_dir="${TARGET_PROJECT}/workspace/workflow-runs"
  local routing_file="${rules_dir}/workflow-routing.md"
  local routing_template="${SKILL_DIR}/references/workflow-routing-template.md"
  local rendered_template

  mkdir -p "$workflows_dir" "$rules_dir" "$runs_dir"

  rendered_template="$(mktemp "${TMPDIR:-/tmp}/workflow-routing.XXXXXX")"
  sed \
    -e "s#__WORKFLOWS_DIR__#${WORKFLOWS_DIR}#g" \
    -e "s#__SCRIPTS_DIR__#${SCRIPTS_DIR}#g" \
    "$routing_template" > "$rendered_template"

  if ! backup_existing_file "$routing_file" "$rendered_template"; then
    rm -f "$rendered_template"
    echo "initialized: ${workflows_dir}"
    echo "initialized: ${runs_dir}"
    return
  fi

  mv "$rendered_template" "$routing_file"
  echo "initialized: ${workflows_dir}"
  echo "initialized: ${runs_dir}"
  echo "installed: ${routing_file}"
}

workflow_agents_block() {
  sed \
    -e "s#__WORKFLOWS_DIR__#${WORKFLOWS_DIR}#g" \
    -e "s#__RULES_DIR__#${RULES_DIR}#g" \
    -e "s#__SCRIPTS_DIR__#${SCRIPTS_DIR}#g" <<'AGENTS_BLOCK'
<!-- workflow-todo-state:start -->
## Workflow Todo State

Named workflow state files are the source of truth for every routed workflow.

- Workflow definitions live under `__WORKFLOWS_DIR__/{workflow-id}/`.
- Workflow state files live under `workspace/workflow-runs/` and should be named after the task, for example `payment-refactor.workflow.md`.
- Before any action that changes project files, runs project commands, or calls external services, read `__RULES_DIR__/workflow-routing.md` and match the user's original request against its triggers and exclusions.
- When a `Required: yes` workflow matches, read its `workflow.md`, create or resume its state file, and start the current phase before doing the work. Do not take the ordinary execution path instead.
- If the route is ambiguous, ask the user before acting.
- Read the active workflow state file before starting any phase; do not skip prerequisite phases.
- Change phase state only through `__SCRIPTS_DIR__/todo-state.sh`.
- Use one unique phase status line per phase, for example `> [P0] ⬜ 未开始`.
- On resume after interruption, inspect the YAML frontmatter and current phase before acting.
- Each workflow directory must contain a `routing.yaml`. After creating, changing, renaming, or deleting a workflow, run `__SCRIPTS_DIR__/sync-workflow-routing.sh`; the update is incomplete until `__SCRIPTS_DIR__/sync-workflow-routing.sh --check` passes.
<!-- workflow-todo-state:end -->
AGENTS_BLOCK
}

update_agents() {
  local agents_file="${TARGET_PROJECT}/${ENTRY_FILE}"
  local start_marker="<!-- workflow-todo-state:start -->"
  local end_marker="<!-- workflow-todo-state:end -->"

  if [ ! -f "$agents_file" ]; then
    printf '# Project Instructions\n' > "$agents_file"
  fi

  local block
  block="$(workflow_agents_block)"

  if grep -qF "$start_marker" "$agents_file"; then
    if ! grep -qF "$end_marker" "$agents_file"; then
      echo "install: workflow-todo-state block has no end marker: $agents_file" >&2
      exit 1
    fi
    BLOCK="$block" START_MARKER="$start_marker" END_MARKER="$end_marker" perl -0pi -e '
      my $start = quotemeta($ENV{START_MARKER});
      my $end = quotemeta($ENV{END_MARKER});
      my $block = $ENV{BLOCK};
      my $count = s/$start.*?$end/$block/s;
      die "install: could not replace workflow-todo-state block\n" unless $count == 1;
    ' "$agents_file"
    echo "updated: ${agents_file}"
    return
  fi

  printf '\n%s\n' "$block" >> "$agents_file"

  echo "updated: ${agents_file}"
}

install_state_script
install_routing_sync_script

if [ "$WITH_SKILL" = true ]; then
  install_skill
fi

if [ "$INIT_LAYOUT" = true ]; then
  init_layout
fi

if [ "$UPDATE_AGENTS" = true ]; then
  update_agents
fi

cat <<EOF

Done.

Next:
  1. Create a workflow definition under ${WORKFLOWS_DIR}/{workflow-id}/.
  2. Add routing metadata at ${WORKFLOWS_DIR}/{workflow-id}/routing.yaml.
  3. Run ${SCRIPTS_DIR}/sync-workflow-routing.sh.
  4. Create a named state file under workspace/workflow-runs/{task}.workflow.md.
  5. Test: ${SCRIPTS_DIR}/todo-state.sh workspace/workflow-runs/{task}.workflow.md start P0
EOF
