#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  <agent-dir>/scripts/todo-state.sh <workflow-state.md> validate
  <agent-dir>/scripts/todo-state.sh <workflow-state.md> start P1
  <agent-dir>/scripts/todo-state.sh <workflow-state.md> complete P1
  <agent-dir>/scripts/todo-state.sh <workflow-state.md> skip P3 "reason"
  <agent-dir>/scripts/todo-state.sh <workflow-state.md> block P2 "reason"

Updates the phase status line, YAML recovery metadata, and visible current phase.
USAGE
}

if [ "$#" -lt 2 ]; then
  usage
  exit 2
fi

TODO_FILE="$1"
ACTION="$2"
PHASE="${3:-}"
REASON="${4:-}"

if [ ! -f "$TODO_FILE" ]; then
  echo "todo-state: file not found: $TODO_FILE" >&2
  exit 1
fi

case "$ACTION" in
  validate|start|complete|skip|block) ;;
  *)
    echo "todo-state: unknown action: $ACTION" >&2
    usage
    exit 2
    ;;
esac

if [ "$ACTION" != "validate" ]; then
  if [ -z "$PHASE" ]; then
    echo "todo-state: missing phase for action: $ACTION" >&2
    usage
    exit 2
  fi

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
fi

TODAY="$(date +%Y-%m-%d)"
NOW="$(date '+%Y-%m-%d %H:%M')"
PHASE_NUM="${PHASE#P}"

infer_project_root() {
  local todo_abs="$TODO_FILE"

  case "$todo_abs" in
    /*) ;;
    *) todo_abs="$(pwd)/$todo_abs" ;;
  esac

  case "$todo_abs" in
    */workspace/workflow-runs/*)
      printf '%s\n' "${todo_abs%%/workspace/workflow-runs/*}"
      return
      ;;
  esac

  printf '%s\n' "$(pwd)"
}

PROJECT_ROOT="$(infer_project_root)"

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

phase_status_for() {
  local phase="$1"
  PHASE_LOOKUP="$phase" perl -ne '
    if (/^> \[\Q$ENV{PHASE_LOOKUP}\E\] .* \{([^}]+)\}$/) {
      print "$1\n";
      exit;
    }
  ' "$TODO_FILE"
}

frontmatter_value() {
  local key="$1"
  awk -v key="$key" '
    NR == 1 && $0 == "---" { in_fm = 1; next }
    in_fm && $0 == "---" { exit }
    in_fm && index($0, key ":") == 1 {
      value = substr($0, length(key) + 2)
      sub(/^[[:space:]]*/, "", value)
      sub(/[[:space:]]*$/, "", value)
      if (value ~ /^".*"$/) {
        sub(/^"/, "", value)
        sub(/"$/, "", value)
      }
      print value
      exit
    }
  ' "$TODO_FILE"
}

frontmatter_has_key() {
  local key="$1"
  awk -v key="$key" '
    NR == 1 && $0 == "---" { in_fm = 1; next }
    in_fm && $0 == "---" { exit }
    in_fm && index($0, key ":") == 1 { found = 1; exit }
    END { exit found ? 0 : 1 }
  ' "$TODO_FILE"
}

workflow_path() {
  local path="$1"
  case "$path" in
    ""|*\{*) return 1 ;;
    /*) printf '%s\n' "$path" ;;
    *) printf '%s/%s\n' "$PROJECT_ROOT" "$path" ;;
  esac
}

validation_error() {
  echo "todo-state: $*" >&2
  exit 1
}

require_shape() {
  local current_phase_count
  local key

  if [ "$(sed -n '1p' "$TODO_FILE")" != "---" ]; then
    validation_error "frontmatter not found"
  fi

  for key in workflow_id workflow_name workflow_version state_file_type run_id task created_from current_phase current_status mode blocked_reason; do
    if ! frontmatter_has_key "$key"; then
      validation_error "frontmatter key missing: $key"
    fi
  done

  current_phase_count="$(grep -cE '^> 当前阶段：' "$TODO_FILE" || true)"
  if [ "$current_phase_count" -ne 1 ]; then
    validation_error "visible current phase line must be unique"
  fi
}

validate_phase_order() {
  perl -ne '
    if (/^> \[(P(\d+))\] (.*)$/) {
      my ($phase, $num, $rest) = ($1, $2 + 0, $3);
      if ($seen{$phase}++) {
        print STDERR "todo-state: phase line must be unique: $phase\n";
        exit 1;
      }
      if ($rest !~ /\{([^}]+)\}$/) {
        print STDERR "todo-state: phase line missing machine status: $phase\n";
        exit 1;
      }
      my $status = $1;
      if ($status !~ /^(not_started|in_progress|blocked|complete|skipped)$/) {
        print STDERR "todo-state: unknown phase status for $phase: $status\n";
        exit 1;
      }
      push @phases, [$num, $phase, $status];
    }
    END {
      if (!@phases) {
        print STDERR "todo-state: phase line not found\n";
        exit 1;
      }
      for my $i (0 .. $#phases) {
        my ($num, $phase, $status) = @{$phases[$i]};
        if ($num != $i) {
          print STDERR "todo-state: phase sequence must be contiguous from P0: expected P$i, found $phase\n";
          exit 1;
        }
        next if $status eq "not_started";
        for my $j (0 .. $i - 1) {
          my ($prev_num, $prev_phase, $prev_status) = @{$phases[$j]};
          if ($prev_status ne "complete" && $prev_status ne "skipped") {
            print STDERR "todo-state: previous phase is not complete or skipped: $prev_phase\n";
            exit 1;
          }
        }
      }
      my @active = grep { $_->[2] eq "in_progress" || $_->[2] eq "blocked" } @phases;
      if (@active > 1) {
        print STDERR "todo-state: multiple active phases found\n";
        exit 1;
      }
    }
  ' "$TODO_FILE"
}

validate_recovery_state() {
  local current_phase
  local current_status
  local status

  current_phase="$(frontmatter_value current_phase)"
  current_status="$(frontmatter_value current_status)"

  case "$current_status" in
    not_started|ready|in_progress|blocked|complete) ;;
    *) validation_error "unknown current_status: $current_status" ;;
  esac

  if [ "$current_phase" = "done" ]; then
    if [ "$current_status" != "complete" ]; then
      validation_error "current_phase done requires current_status complete"
    fi
    if perl -ne 'exit 1 if /^> \[P\d+\] .* \{(not_started|in_progress|blocked)\}$/;' "$TODO_FILE"; then
      return
    fi
    validation_error "current_phase done requires every phase to be complete or skipped"
  fi

  case "$current_phase" in
    P[0-9]*) ;;
    *) validation_error "current_phase must be Pn or done: $current_phase" ;;
  esac

  status="$(phase_status_for "$current_phase")"
  if [ -z "$status" ]; then
    validation_error "current_phase line not found: $current_phase"
  fi

  case "$current_status" in
    not_started|ready)
      if [ "$status" != "not_started" ]; then
        validation_error "current_status $current_status requires $current_phase to be not_started"
      fi
      ;;
    in_progress|blocked)
      if [ "$status" != "$current_status" ]; then
        validation_error "current_status $current_status does not match $current_phase status $status"
      fi
      ;;
    complete)
      validation_error "current_status complete requires current_phase done"
      ;;
  esac
}

require_file() {
  local phase="$1"
  local path="$2"

  if [ -z "$path" ] || [ ! -f "$path" ]; then
    validation_error "required artifact missing for $phase: ${path:-unknown path}"
  fi
}

require_file_contains() {
  local phase="$1"
  local path="$2"
  local pattern="$3"

  require_file "$phase" "$path"
  if ! grep -qF "$pattern" "$path"; then
    validation_error "required artifact content missing for $phase: $pattern in $path"
  fi
}

require_file_not_contains() {
  local phase="$1"
  local path="$2"
  local pattern="$3"

  require_file "$phase" "$path"
  if grep -qF "$pattern" "$path"; then
    validation_error "artifact still contains forbidden marker for $phase: $pattern in $path"
  fi
}

validate_reading_note_artifacts() {
  local intermediate_dir
  local output_path
  local formatted_article
  local translation
  local grammar_notes
  local final_note

  intermediate_dir="$(frontmatter_value intermediate_dir)"
  output_path="$(frontmatter_value output_path)"

  formatted_article="$(workflow_path "${intermediate_dir%/}/formatted-article.md" || true)"
  translation="$(workflow_path "${intermediate_dir%/}/translation.md" || true)"
  grammar_notes="$(workflow_path "${intermediate_dir%/}/grammar-notes.md" || true)"
  final_note="$(workflow_path "$output_path" || true)"

  if [ "$(phase_status_for P1)" = "complete" ]; then
    require_file P1 "$formatted_article"
  fi
  if [ "$(phase_status_for P2)" = "complete" ]; then
    require_file P2 "$translation"
  fi
  if [ "$(phase_status_for P3)" = "complete" ]; then
    require_file P3 "$grammar_notes"
  fi
  if [ "$(phase_status_for P5)" = "complete" ]; then
    require_file_contains P5 "$formatted_article" "> [!abstract]- 长难句分析"
  fi
  if [ "$(phase_status_for P6)" = "complete" ]; then
    require_file_contains P6 "$final_note" "<!-- VOCABULARY_SLOT -->"
  fi
  if [ "$(phase_status_for P7)" = "complete" ]; then
    require_file_not_contains P7 "$final_note" "<!-- VOCABULARY_SLOT -->"
    require_file_contains P7 "$final_note" "## 生词表"
    require_file_contains P7 "$final_note" "### 生词练习"
  fi
  if [ "$(phase_status_for P8)" = "complete" ] || [ "$(frontmatter_value current_phase)" = "done" ]; then
    require_file P8 "$formatted_article"
    require_file P8 "$translation"
    require_file P8 "$grammar_notes"
    require_file_not_contains P8 "$final_note" "<!-- VOCABULARY_SLOT -->"
    require_file_contains P8 "$final_note" "## 生词表"
    require_file_contains P8 "$final_note" "### 生词练习"
  fi
}

validate_workflow_artifacts() {
  case "$(frontmatter_value workflow_id)" in
    reading-note-generation) validate_reading_note_artifacts ;;
  esac
}

validate_phase_completion_requirements() {
  local workflow_id
  local intermediate_dir
  local output_path
  local formatted_article
  local translation
  local grammar_notes
  local final_note

  workflow_id="$(frontmatter_value workflow_id)"
  if [ "$workflow_id" != "reading-note-generation" ]; then
    return
  fi

  intermediate_dir="$(frontmatter_value intermediate_dir)"
  output_path="$(frontmatter_value output_path)"
  formatted_article="$(workflow_path "${intermediate_dir%/}/formatted-article.md" || true)"
  translation="$(workflow_path "${intermediate_dir%/}/translation.md" || true)"
  grammar_notes="$(workflow_path "${intermediate_dir%/}/grammar-notes.md" || true)"
  final_note="$(workflow_path "$output_path" || true)"

  case "$PHASE" in
    P1) require_file P1 "$formatted_article" ;;
    P2) require_file P2 "$translation" ;;
    P3) require_file P3 "$grammar_notes" ;;
    P5) require_file_contains P5 "$formatted_article" "> [!abstract]- 长难句分析" ;;
    P6) require_file_contains P6 "$final_note" "<!-- VOCABULARY_SLOT -->" ;;
    P7)
      require_file_not_contains P7 "$final_note" "<!-- VOCABULARY_SLOT -->"
      require_file_contains P7 "$final_note" "## 生词表"
      require_file_contains P7 "$final_note" "### 生词练习"
      ;;
    P8)
      require_file P8 "$formatted_article"
      require_file P8 "$translation"
      require_file P8 "$grammar_notes"
      require_file_not_contains P8 "$final_note" "<!-- VOCABULARY_SLOT -->"
      require_file_contains P8 "$final_note" "## 生词表"
      require_file_contains P8 "$final_note" "### 生词练习"
      ;;
  esac
}

validate_state() {
  require_shape
  validate_phase_order
  validate_recovery_state
  validate_workflow_artifacts
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
  validate)
    validate_state
    ;;
  start)
    ensure_previous_phases_closed
    if phase_has_status "complete" || phase_has_status "skipped"; then
      echo "todo-state: cannot start completed or skipped phase: $PHASE" >&2
      exit 1
    fi
    replace_phase_status "🔲 进行中 {in_progress}"
    set_recovery_state "$PHASE" "in_progress"
    set_visible_current_phase "$PHASE"
    validate_state
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
    validate_phase_completion_requirements
    replace_phase_status "✅ 已完成 {complete}"
    NEXT_PHASE="$(next_pending_phase_after || true)"
    if [ -n "$NEXT_PHASE" ]; then
      set_recovery_state "$NEXT_PHASE" "ready"
      set_visible_current_phase "$NEXT_PHASE"
    else
      set_recovery_state "done" "complete"
      set_visible_current_phase "done"
    fi
    validate_state
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
    validate_state
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
    validate_state
    ;;
esac
