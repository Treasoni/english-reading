#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  <agent-dir>/scripts/todo-state.sh <workflow-state.md> start P1
  <agent-dir>/scripts/todo-state.sh <workflow-state.md> complete P1
  <agent-dir>/scripts/todo-state.sh <workflow-state.md> skip P3 "reason"
  <agent-dir>/scripts/todo-state.sh <workflow-state.md> block P2 "reason"

Updates the phase status line, YAML recovery metadata, and visible current phase.
USAGE
}

if [ "$#" -lt 3 ]; then
  usage
  exit 2
fi

TODO_FILE="$1"
ACTION="$2"
PHASE="$3"
REASON="${4:-}"

if [ ! -f "$TODO_FILE" ]; then
  echo "todo-state: file not found: $TODO_FILE" >&2
  exit 1
fi

case "$ACTION" in
  start|complete|skip|block) ;;
  *)
    echo "todo-state: unknown action: $ACTION" >&2
    usage
    exit 2
    ;;
esac

case "$PHASE" in
  P[0-9]*) ;;
  *)
    echo "todo-state: phase must look like P0, P1, ..." >&2
    exit 2
    ;;
esac

PHASE_LINE_COUNT="$(grep -cE "^> \[$PHASE\] " "$TODO_FILE" || true)"
if [ "$PHASE_LINE_COUNT" -eq 0 ]; then
  echo "todo-state: phase line not found: $PHASE" >&2
  exit 1
fi
if [ "$PHASE_LINE_COUNT" -ne 1 ]; then
  echo "todo-state: phase line must be unique: $PHASE" >&2
  exit 1
fi

TODAY="$(date +%Y-%m-%d)"
NOW="$(date '+%Y-%m-%d %H:%M')"
PHASE_NUM="${PHASE#P}"

yaml_quote() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  printf '"%s"' "$value"
}

ensure_frontmatter() {
  if [ "$(sed -n '1p' "$TODO_FILE")" = "---" ]; then
    return
  fi

  local tmp
  tmp="$(mktemp "${TODO_FILE}.XXXXXX")"
  {
    printf '%s\n' '---'
    printf '%s\n' 'workflow: unknown'
    printf '%s\n' 'topic: ""'
    printf '%s\n' 'project_slug: ""'
    printf '%s\n' 'created_at: ""'
    printf 'last_updated: "%s"\n' "$TODAY"
    printf 'current_phase: %s\n' "$PHASE"
    printf '%s\n' 'current_status: unknown'
    printf '%s\n' 'mode: standard'
    printf '%s\n' 'blocked_reason: ""'
    printf '%s\n' '---'
    cat "$TODO_FILE"
  } > "$tmp"
  mv "$tmp" "$TODO_FILE"
}

set_frontmatter_key() {
  local key="$1"
  local value="$2"
  local tmp
  tmp="$(mktemp "${TODO_FILE}.XXXXXX")"
  awk -v key="$key" -v value="$value" '
    NR == 1 && $0 == "---" { in_fm = 1; print; next }
    in_fm && $0 == "---" {
      if (!done) print key ": " value
      in_fm = 0
      print
      next
    }
    in_fm && index($0, key ":") == 1 {
      print key ": " value
      done = 1
      next
    }
    { print }
  ' "$TODO_FILE" > "$tmp"
  mv "$tmp" "$TODO_FILE"
}

set_recovery_state() {
  local current_phase="$1"
  local current_status="$2"
  local blocked_reason="${3:-}"

  ensure_frontmatter
  set_frontmatter_key "last_updated" "$(yaml_quote "$TODAY")"
  set_frontmatter_key "current_phase" "$current_phase"
  set_frontmatter_key "current_status" "$current_status"
  set_frontmatter_key "blocked_reason" "$(yaml_quote "$blocked_reason")"
}

set_visible_current_phase() {
  local current_phase="$1"
  local label="$current_phase"

  case "$current_phase" in
    P[0-9]*) label="阶段 ${current_phase#P}" ;;
    done) label="完成" ;;
  esac

  LABEL="$label" perl -0pi -e 's/(^> 当前阶段：).*$/$1$ENV{LABEL}/m' "$TODO_FILE"
}

replace_phase_status() {
  local label="$1"
  PHASE="$PHASE" LABEL="$label" perl -0pi -e '
    my $phase = $ENV{PHASE};
    my $label = $ENV{LABEL};
    my $changed = s/(^> \[\Q$phase\E\] ).*$/$1$label/m;
    die "todo-state: could not update phase line\n" unless $changed;
  ' "$TODO_FILE"
}

phase_has_status() {
  local label="$1"
  grep -qE "^> \\[$PHASE\\] .* \\{$label\\}$" "$TODO_FILE"
}

previous_open_phase_before() {
  PHASE_NUM="$PHASE_NUM" perl -ne '
    if (/^> \[P(\d+)\] .* \{([^}]+)\}$/ && $1 < $ENV{PHASE_NUM}) {
      my $status = $2;
      if ($status ne "complete" && $status ne "skipped") {
        print "P$1\n";
        exit;
      }
    }
  ' "$TODO_FILE"
}

ensure_previous_phases_closed() {
  local open_phase
  open_phase="$(previous_open_phase_before || true)"
  if [ -n "$open_phase" ]; then
    echo "todo-state: previous phase is not complete or skipped: $open_phase" >&2
    exit 1
  fi
}

next_pending_phase_after() {
  PHASE_NUM="$PHASE_NUM" perl -ne '
    if (/^> \[P(\d+)\] .* \{not_started\}$/ && $1 > $ENV{PHASE_NUM}) {
      print "P$1\n";
      exit;
    }
  ' "$TODO_FILE"
}

append_exception_record() {
  local issue="$1"
  local handling="$2"
  issue="${issue//|//}"
  handling="${handling//|//}"
  NOW="$NOW" PHASE="$PHASE" ISSUE="$issue" HANDLING="$handling" perl -0pi -e '
    my $row = "| $ENV{NOW} | $ENV{PHASE} | $ENV{ISSUE} | $ENV{HANDLING} |\n";
    s/(## 异常记录\n\n\|[^\n]*\n\|[^\n]*\n)/$1$row/s;
  ' "$TODO_FILE"
}

ensure_exception_table() {
  if ! grep -qF "## 异常记录" "$TODO_FILE"; then
    echo "todo-state: exception table not found" >&2
    exit 1
  fi
}

case "$ACTION" in
  start)
    ensure_previous_phases_closed
    if phase_has_status "complete" || phase_has_status "skipped"; then
      echo "todo-state: cannot start completed or skipped phase: $PHASE" >&2
      exit 1
    fi
    replace_phase_status "🔲 进行中 {in_progress}"
    set_recovery_state "$PHASE" "in_progress"
    set_visible_current_phase "$PHASE"
    ;;
  complete)
    ensure_previous_phases_closed
    if phase_has_status "skipped"; then
      echo "todo-state: cannot complete skipped phase: $PHASE" >&2
      exit 1
    fi
    if ! phase_has_status "in_progress"; then
      echo "todo-state: phase must be in progress before complete: $PHASE" >&2
      exit 1
    fi
    replace_phase_status "✅ 已完成 {complete}"
    NEXT_PHASE="$(next_pending_phase_after || true)"
    if [ -n "$NEXT_PHASE" ]; then
      set_recovery_state "$NEXT_PHASE" "ready"
      set_visible_current_phase "$NEXT_PHASE"
    else
      set_recovery_state "done" "complete"
      set_visible_current_phase "done"
    fi
    ;;
  skip)
    ensure_previous_phases_closed
    ensure_exception_table
    if phase_has_status "complete"; then
      echo "todo-state: cannot skip completed phase: $PHASE" >&2
      exit 1
    fi
    replace_phase_status "⏭️ 跳过 {skipped}"
    append_exception_record "跳过阶段：${REASON:-未填写原因}" "继续推进到下一未完成阶段"
    NEXT_PHASE="$(next_pending_phase_after || true)"
    if [ -n "$NEXT_PHASE" ]; then
      set_recovery_state "$NEXT_PHASE" "ready"
      set_visible_current_phase "$NEXT_PHASE"
    else
      set_recovery_state "done" "complete"
      set_visible_current_phase "done"
    fi
    ;;
  block)
    ensure_previous_phases_closed
    ensure_exception_table
    if phase_has_status "complete" || phase_has_status "skipped"; then
      echo "todo-state: cannot block completed or skipped phase: $PHASE" >&2
      exit 1
    fi
    replace_phase_status "🔲 进行中 {blocked}"
    set_recovery_state "$PHASE" "blocked" "$REASON"
    set_visible_current_phase "$PHASE"
    append_exception_record "阻塞：${REASON:-未填写原因}" "停在当前阶段，等待用户确认或补充资料"
    ;;
esac
