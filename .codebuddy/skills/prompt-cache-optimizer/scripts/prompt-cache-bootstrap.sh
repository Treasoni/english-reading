#!/usr/bin/env bash
# Install and audit prompt-cache conventions for agent projects.

set -euo pipefail

MODE="check"
PLATFORM="both"
TARGET_DIR="."
CUSTOM_AGENTS=()
WITH_SKILL=false
WITH_OBSERVABILITY=false
OVERWRITE=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ASSET_DIR="${PROMPT_CACHE_ASSET_DIR:-$SCRIPT_DIR}"

if [ ! -f "$ASSET_DIR/llm-usage-event.schema.json" ] && [ -d "$SCRIPT_DIR/../assets" ]; then
  ASSET_DIR="$SCRIPT_DIR/../assets"
fi

PROFILE_ROOT="${PROMPT_CACHE_PROFILE_ROOT:-}"

if [ -z "$PROFILE_ROOT" ]; then
  for candidate in "$SKILL_DIR/profiles" "$SCRIPT_DIR/../../profiles" "$SCRIPT_DIR/../../../profiles"; do
    if [ -d "$candidate" ]; then
      PROFILE_ROOT="$(cd "$candidate" && pwd)"
      break
    fi
  done
fi

usage() {
  cat <<'USAGE'
Usage:
  prompt-cache-bootstrap.sh [--check|--apply] [--platform PROFILE|both|all|none] [--target DIR]

Modes:
  --check              Report missing cache configuration and suspicious prompt content (default).
  --apply              Install rules, entry-point references, and selected optional assets.

Options:
  --with-skill         Copy prompt-cache-optimizer into every selected profile's skills directory.
  --overwrite          Replace existing prompt-cache rules, optional assets, and copied skills. Requires --apply.
  --with-observability Install or check `.llm/prompt-cache` contracts. Use only after automatic
                       provider-usage collection has been connected; this script does not collect it.
  --platform PLATFORM  Configure one built-in profile, `both` (codex + claude), `all`, or `none` (default: both).
  --agent SPEC         Add a custom agent profile: name,agent_dir,entry_file[,rule_path].
                       Example: generic,.agent,AGENTS.md
  --target DIR         Target project root (default: current directory).
  --help               Show this help message.

Examples:
  bash prompt-cache-bootstrap.sh --check --target ../my-project
  bash prompt-cache-bootstrap.sh --apply --platform both --with-skill --target ../my-project
  bash prompt-cache-bootstrap.sh --apply --platform both --with-skill --with-observability --target ../my-project
  bash prompt-cache-bootstrap.sh --apply --platform gemini --target ../my-project
  bash prompt-cache-bootstrap.sh --apply --platform none --agent myagent,.agent,AGENTS.md --target ../my-project
USAGE
}

log() {
  printf '%s\n' "prompt-cache: $*"
}

warn() {
  printf '%s\n' "prompt-cache: warning: $*" >&2
}

profile_value() {
  local profile_file="$1"
  local key="$2"
  sed -n "s/^${key}:[[:space:]]*//p" "$profile_file" | head -n 1 | sed "s/^['\"]//; s/['\"]$//"
}

emit_profile_spec() {
  local name="$1"
  local profile_file="${PROFILE_ROOT}/${name}.yaml"
  local agent_dir entry_file rule_path rules_dir skills_dir

  if [ -n "$PROFILE_ROOT" ] && [ -f "$profile_file" ]; then
    agent_dir="$(profile_value "$profile_file" agent_dir)"
    entry_file="$(profile_value "$profile_file" entry_file)"
    rule_path="$(profile_value "$profile_file" prompt_cache_rule)"
    rules_dir="$(profile_value "$profile_file" rules_dir)"
    skills_dir="$(profile_value "$profile_file" skills_dir)"
    rule_path="${rule_path:-${rules_dir}/common/prompt-cache.md}"
    if [ -z "$agent_dir" ] || [ -z "$entry_file" ] || [ -z "$rule_path" ] || [ -z "$skills_dir" ]; then
      warn "invalid profile contract: $profile_file"
      return 1
    fi
    printf '%s\t%s\t%s\t%s\t%s\n' "$name" "$agent_dir" "$entry_file" "$rule_path" "$skills_dir"
    return
  fi

  case "$name" in
    codex) printf '%s\n' $'codex\t.codex\tAGENTS.md\t.codex/rules/common/prompt-cache.md\t.agents/skills' ;;
    claude) printf '%s\n' $'claude\t.claude\tCLAUDE.md\t.claude/rules/common/prompt-cache.md\t.claude/skills' ;;
    generic) printf '%s\n' $'generic\t.agent\tAGENTS.md\t.agent/rules/common/prompt-cache.md\t.agent/skills' ;;
    *)
      warn "unknown profile: $name (profiles directory unavailable: ${PROFILE_ROOT:-none})"
      return 1
      ;;
  esac
}

selected_profile_specs() {
  local profile_file name
  case "$PLATFORM" in
    none)
      return
      ;;
    both)
      emit_profile_spec codex
      emit_profile_spec claude
      ;;
    all)
      if [ -z "$PROFILE_ROOT" ] || [ ! -d "$PROFILE_ROOT" ]; then
        warn "--platform all requires this repository's profiles directory"
        return 1
      fi
      for profile_file in "$PROFILE_ROOT"/*.yaml; do
        [ -f "$profile_file" ] || continue
        name="$(profile_value "$profile_file" name)"
        emit_profile_spec "${name:-$(basename "${profile_file%.yaml}")}"
      done
      ;;
    *)
      emit_profile_spec "$PLATFORM"
      ;;
  esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --check)
      MODE="check"
      ;;
    --apply)
      MODE="apply"
      ;;
    --with-skill)
      WITH_SKILL=true
      ;;
    --with-observability)
      WITH_OBSERVABILITY=true
      ;;
    --overwrite)
      OVERWRITE=true
      ;;
    --platform)
      if [ "$#" -lt 2 ]; then
        warn "--platform requires a profile name, both, all, or none"
        exit 2
      fi
      PLATFORM="$2"
      shift
      ;;
    --agent)
      if [ "$#" -lt 2 ]; then
        warn "--agent requires name,agent_dir,entry_file[,rule_path]"
        exit 2
      fi
      CUSTOM_AGENTS+=("$2")
      shift
      ;;
    --target)
      if [ "$#" -lt 2 ]; then
        warn "--target requires a directory"
        exit 2
      fi
      TARGET_DIR="$2"
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

if [ "$OVERWRITE" = true ] && [ "$MODE" != "apply" ]; then
  warn "--overwrite requires --apply"
  exit 2
fi

if ! selected_profile_specs >/dev/null; then
  exit 2
fi

if [ ! -d "$TARGET_DIR" ]; then
  warn "target directory not found: $TARGET_DIR"
  exit 1
fi

TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

target_path() {
  case "$1" in
    /*) printf '%s\n' "$1" ;;
    *) printf '%s/%s\n' "$TARGET_DIR" "$1" ;;
  esac
}

rule_content() {
  cat <<'RULES'
# Prompt Cache Rules

## Prompt Order

For every high-frequency request, keep this order:

1. Stable role, task boundaries, and safety rules.
2. Stable tool constraints, output format, and quality requirements.
3. Stable examples, only when they materially improve the result.
4. Dynamic parameters: user request, file excerpts, dates, runtime state, and IDs.

Keep stable content at the beginning and dynamic content at the end. Reuse the same stable prefix for the same task type.

## Stability

- Do not put timestamps, random IDs, UUIDs, git status, live TODOs, or user input in the stable prefix.
- Do not casually reorder or reword stable prompt sections, punctuation, or whitespace.
- Keep one authoritative template for each high-frequency task.
- Keep model settings and tool definitions stable when cache reuse matters.
- Keep dynamic parameter names and order stable; use `none` for missing values.

## Context Loading

- Prefer paths, headings, anchors, and summaries before loading full content.
- Load only the file sections needed for the current task.
- Do not preload build output, dependencies, logs, mirrored configuration, or unrelated examples.
- Save reusable long results as structured files and reference them instead of pasting them again.

## Subagents

- Put fixed responsibilities, output format, and prohibitions before the parameter block.
- Put all task-specific values in a final `Parameters` block.
- Return structured summaries, links, citations, and conclusions instead of full source text.

## Standard Template

```text
You are {stable_role}.

Task boundaries:
{stable_boundaries}

Output format:
{stable_output_format}

Quality requirements:
{stable_quality_requirements}

Prohibitions:
{stable_prohibitions}

Parameters:
- Task: {dynamic_task}
- User request: {dynamic_request}
- Input reference: {dynamic_input_reference}
- Current state: {dynamic_state}
- Extra constraints: {dynamic_constraints}
```
RULES
}

install_asset() {
  local source_file="$1"
  local target_file="$2"
  local existed=false

  if [ ! -f "$source_file" ]; then
    warn "template asset is missing: $source_file"
    exit 1
  fi

  if [ -f "$target_file" ] && [ "$OVERWRITE" != true ]; then
    log "kept existing $target_file"
    return
  fi
  if [ -f "$target_file" ]; then
    existed=true
  fi

  mkdir -p "$(dirname "$target_file")"
  cp "$source_file" "$target_file"
  if [ "$existed" = true ]; then
    log "updated $target_file"
  else
    log "created $target_file"
  fi
}

install_observability() {
  local observability_dir="$TARGET_DIR/.llm/prompt-cache"

  install_asset "$ASSET_DIR/llm-usage-event.schema.json" "$observability_dir/llm-usage-event.schema.json"
  install_asset "$ASSET_DIR/prompt-cache-regression-cases.json" "$observability_dir/regression-cases.json"
}

entry_block() {
  local name="$1"
  local rule_path="$2"
  cat <<RULES
<!-- prompt-cache-bootstrap:${name}:begin -->
## Prompt Cache

- Follow \`$rule_path\` for high-frequency prompt design.
- Keep stable instructions and output formats before dynamic user input, file excerpts, dates, IDs, and runtime state.
- Reuse canonical templates and load long context only when needed.
<!-- prompt-cache-bootstrap:${name}:end -->
RULES
}

install_rule() {
  local name="$1"
  local rule_path="$2"
  local entry_file="$3"
  local relative_rule_path="$4"
  local rule_file
  local entry_path
  local start_marker="<!-- prompt-cache-bootstrap:${name}:begin -->"
  local legacy_marker="<!-- prompt-cache-bootstrap:begin -->"

  rule_file="$(target_path "$rule_path")"
  entry_path="$(target_path "$entry_file")"

  if [ ! -f "$rule_file" ]; then
    mkdir -p "$(dirname "$rule_file")"
    rule_content > "$rule_file"
    log "created $rule_file for $name"
  elif [ "$OVERWRITE" = true ]; then
    rule_content > "$rule_file"
    log "updated $rule_file for $name"
  else
    log "kept existing $rule_file for $name"
  fi

  if [ -f "$entry_path" ] && grep -qF "$start_marker" "$entry_path"; then
    log "entry block already present in $entry_path"
    return
  fi
  if { [ "$name" = "codex" ] || [ "$name" = "claude" ]; } && [ -f "$entry_path" ] && grep -qF "$legacy_marker" "$entry_path"; then
    log "legacy entry block already present in $entry_path"
    return
  fi

  if [ ! -f "$entry_path" ]; then
    printf '# Project Instructions\n' > "$entry_path"
  fi

  {
    printf '\n'
    entry_block "$name" "$relative_rule_path"
  } >> "$entry_path"
  log "updated $entry_path"
}

check_rule() {
  local name="$1"
  local rule_path="$2"
  local entry_file="$3"
  local rule_file
  local entry_path
  local start_marker="<!-- prompt-cache-bootstrap:${name}:begin -->"
  local legacy_marker="<!-- prompt-cache-bootstrap:begin -->"

  rule_file="$(target_path "$rule_path")"
  entry_path="$(target_path "$entry_file")"

  if [ -f "$rule_file" ]; then
    log "found $rule_file for $name"
  else
    warn "missing $rule_file for $name"
  fi

  if [ -f "$entry_path" ] && grep -qF "$start_marker" "$entry_path"; then
    log "found cache entry block in $entry_path"
  elif { [ "$name" = "codex" ] || [ "$name" = "claude" ]; } && [ -f "$entry_path" ] && grep -qF "$legacy_marker" "$entry_path"; then
    log "found legacy cache entry block in $entry_path"
  else
    warn "missing cache entry block in $entry_path"
  fi
}

parse_custom_agent() {
  local spec="$1"
  local name agent_dir entry_file rule_path extra
  IFS=',' read -r name agent_dir entry_file rule_path extra <<EOF
$spec
EOF
  if [ -n "${extra:-}" ] || [ -z "${name:-}" ] || [ -z "${agent_dir:-}" ] || [ -z "${entry_file:-}" ]; then
    warn "--agent must look like name,agent_dir,entry_file[,rule_path]: $spec"
    exit 2
  fi
  if [ -z "${rule_path:-}" ]; then
    rule_path="${agent_dir%/}/rules/common/prompt-cache.md"
  fi
  printf '%s\t%s\t%s\t%s\t%s\n' "$name" "$agent_dir" "$entry_file" "$rule_path" "${agent_dir%/}/skills"
}

install_skill() {
  local skills_dir="$1"
  local target_skill

  if [ "$WITH_SKILL" != true ]; then
    return 0
  fi
  target_skill="$(target_path "${skills_dir%/}/prompt-cache-optimizer")"
  if [ -e "$target_skill" ] && [ "$OVERWRITE" != true ]; then
    log "kept existing $target_skill"
    return
  fi
  if [ -e "$target_skill" ]; then
    rm -rf "$target_skill"
  fi
  mkdir -p "$(dirname "$target_skill")"
  cp -R "$SKILL_DIR" "$target_skill"
  if [ -n "$PROFILE_ROOT" ] && [ -d "$PROFILE_ROOT" ]; then
    cp -R "$PROFILE_ROOT" "$target_skill/profiles"
  fi
  chmod +x "$target_skill/scripts/prompt-cache-bootstrap.sh"
  log "installed $target_skill"
}

run_profile() {
  local action="$1"
  local name="$2"
  local agent_dir="$3"
  local entry_file="$4"
  local rule_path="$5"
  local skills_dir="$6"

  if [ "$action" = "apply" ]; then
    install_rule "$name" "$rule_path" "$entry_file" "$rule_path"
    install_skill "$skills_dir"
  else
    check_rule "$name" "$rule_path" "$entry_file"
  fi
}

run_profiles() {
  local action="$1"
  local spec name agent_dir entry_file rule_path skills_dir

  while IFS=$'\t' read -r name agent_dir entry_file rule_path skills_dir; do
    [ -n "${name:-}" ] || continue
    run_profile "$action" "$name" "$agent_dir" "$entry_file" "$rule_path" "$skills_dir"
  done < <(selected_profile_specs)
  if [ "${#CUSTOM_AGENTS[@]}" -gt 0 ]; then
    for spec in "${CUSTOM_AGENTS[@]}"; do
      IFS=$'\t' read -r name agent_dir entry_file rule_path skills_dir <<EOF
$(parse_custom_agent "$spec")
EOF
      run_profile "$action" "$name" "$agent_dir" "$entry_file" "$rule_path" "$skills_dir"
    done
  fi
}

check_observability() {
  local observability_dir="$TARGET_DIR/.llm/prompt-cache"
  local asset

  for asset in "llm-usage-event.schema.json" "regression-cases.json"; do
    if [ -f "$observability_dir/$asset" ]; then
      log "found $observability_dir/$asset"
    else
      warn "missing $observability_dir/$asset"
    fi
  done
}

scan_prompts() {
  local root="$1"
  local prompt_dir
  local found=0
  local prompt_dirs=("$root/prompts")
  local spec name agent_dir entry_file rule_path skills_dir

  while IFS=$'\t' read -r name agent_dir entry_file rule_path skills_dir; do
    [ -n "${name:-}" ] || continue
    prompt_dirs+=("$root/${agent_dir%/}/prompts")
  done < <(selected_profile_specs)
  if [ "${#CUSTOM_AGENTS[@]}" -gt 0 ]; then
    for spec in "${CUSTOM_AGENTS[@]}"; do
      IFS=$'\t' read -r name agent_dir entry_file rule_path skills_dir <<EOF
$(parse_custom_agent "$spec")
EOF
      prompt_dirs+=("$root/${agent_dir%/}/prompts")
    done
  fi

  for prompt_dir in "${prompt_dirs[@]}"; do
    [ -d "$prompt_dir" ] || continue
    found=1
    while IFS= read -r -d '' file; do
      if grep -nEi 'timestamp|uuid|random id|git status|current time|当前时间|任务[[:space:]]*ID|随机[[:space:]]*ID' "$file"; then
        warn "review dynamic value placement in $file (it should be in the final Parameters block)"
      fi
    done < <(find "$prompt_dir" -type f \( -name '*.md' -o -name '*.txt' \) -print0)
  done

  if [ "$found" -eq 0 ]; then
    log "no prompt directories found; skipped dynamic-value scan"
  fi
}

if [ "$MODE" = "apply" ]; then
  run_profiles apply
  if [ "$WITH_OBSERVABILITY" = true ]; then
    install_observability
  else
    log "observability not selected; skipped /.llm/prompt-cache"
  fi
  log "installation complete; run --check to review the project"
else
  run_profiles check
  if [ "$WITH_OBSERVABILITY" = true ]; then
    check_observability
  else
    log "observability not selected; skipped /.llm/prompt-cache check"
  fi
  scan_prompts "$TARGET_DIR"
fi
