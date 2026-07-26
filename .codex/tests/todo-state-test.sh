#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT="$ROOT_DIR/.codex/scripts/todo-state.sh"
PY_SCRIPT="$ROOT_DIR/.codex/scripts/todo-state.py"
PYTHON_BIN="${PYTHON:-python3}"
TEMPLATE="$ROOT_DIR/.codex/workflows/reading-note-generation/state-template.md"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/todo-state-test.XXXXXX")"
STATE_DIR="$TEST_ROOT/workspace/workflow-runs"
INTERMEDIATE_DIR="intermediate/2099-passage1-enforcement"
OUTPUT_PATH="2099阅读/2099-passage1-enforcement-精读笔记.md"
FAILURES=0

mkdir -p "$STATE_DIR"

fail() {
  printf 'not ok - %s\n' "$1" >&2
  FAILURES=$((FAILURES + 1))
}

pass() {
  printf 'ok - %s\n' "$1"
}

assert_success() {
  local description="$1"
  shift
  local output
  if output="$("$@" 2>&1)"; then
    pass "$description"
  else
    fail "$description"
    printf '%s\n' "$output" >&2
  fi
}

assert_failure_contains() {
  local description="$1"
  local expected="$2"
  shift 2
  local output
  if output="$("$@" 2>&1)"; then
    fail "$description"
    printf 'expected failure containing: %s\n' "$expected" >&2
  elif [[ "$output" == *"$expected"* ]]; then
    pass "$description"
  else
    fail "$description"
    printf 'expected failure containing: %s\nactual: %s\n' "$expected" "$output" >&2
  fi
}

assert_file_contains() {
  local description="$1"
  local path="$2"
  local expected="$3"
  if grep -qF "$expected" "$path"; then
    pass "$description"
  else
    fail "$description"
    printf 'expected file to contain: %s\nfile: %s\n' "$expected" "$path" >&2
  fi
}

make_state() {
  local name="$1"
  local state="$STATE_DIR/${name}.workflow.md"
  cp "$TEMPLATE" "$state"
  RUN_ID="$name" \
  TASK="test $name" \
  DATE="2099-01-01" \
  YEAR="2099" \
  PASSAGE="1" \
  TOPIC="enforcement" \
  INTERMEDIATE_DIR="$INTERMEDIATE_DIR" \
  OUTPUT_PATH="$OUTPUT_PATH" \
  perl -0pi -e '
    s/\{run_id\}/$ENV{RUN_ID}/g;
    s/\{task\}/$ENV{TASK}/g;
    s/\{date\}/$ENV{DATE}/g;
    s/\{article_source\}/inline test article/g;
    s/\{year\}/$ENV{YEAR}/g;
    s/\{passage\}/$ENV{PASSAGE}/g;
    s/\{topic\}/$ENV{TOPIC}/g;
    s#intermediate/\{year\}-passage\{passage\}-\{topic\}/#$ENV{INTERMEDIATE_DIR}/#g;
    s/\{output_path\}/$ENV{OUTPUT_PATH}/g;
  ' "$state"
  printf '%s\n' "$state"
}

write_required_artifacts() {
  mkdir -p "$TEST_ROOT/$INTERMEDIATE_DIR" "$TEST_ROOT/2099阅读"
  printf '# Article\n\nA test sentence.\n\n> [!abstract]- 长难句分析\n> **原句**：A test sentence.\n' \
    > "$TEST_ROOT/$INTERMEDIATE_DIR/formatted-article.md"
  printf '# Translation\n\nA test sentence.\n' > "$TEST_ROOT/$INTERMEDIATE_DIR/translation.md"
  printf '# Grammar Notes\n\n- Test grammar point.\n' > "$TEST_ROOT/$INTERMEDIATE_DIR/grammar-notes.md"
  printf -- '---\ntitle: test\n---\n\n# Final Note\n\n## 生词表\n\n| 词 | 义 |\n|---|---|\n| enforce | 强制 |\n\n### 生词练习\n\n1. enforce\n' \
    > "$TEST_ROOT/$OUTPUT_PATH"
}

test_validate_rejects_out_of_order_phase() {
  local state
  state="$(make_state out-of-order)"
  perl -0pi -e 's/> \[P1\] ⬜ 未开始 \{not_started\}/> [P1] ✅ 已完成 {complete}/' "$state"

  assert_failure_contains \
    "validate rejects a completed phase after an open previous phase" \
    "previous phase is not complete or skipped: P0" \
    "$SCRIPT" "$state" validate
}

test_complete_rejects_missing_artifact() {
  local state
  state="$(make_state missing-artifact)"

  assert_success "can start P0" "$SCRIPT" "$state" start P0
  assert_success "can complete P0" "$SCRIPT" "$state" complete P0
  assert_success "can start P1" "$SCRIPT" "$state" start P1
  assert_failure_contains \
    "complete P1 rejects missing formatted article" \
    "required artifact missing" \
    "$SCRIPT" "$state" complete P1
}

test_validate_accepts_complete_single_reading_note_run() {
  local state
  state="$(make_state valid-run)"
  write_required_artifacts

  assert_success "valid run starts P0" "$SCRIPT" "$state" start P0
  assert_success "valid run completes P0" "$SCRIPT" "$state" complete P0
  assert_success "valid run starts P1" "$SCRIPT" "$state" start P1
  assert_success "valid run completes P1" "$SCRIPT" "$state" complete P1
  assert_success "valid run validates" "$SCRIPT" "$state" validate
}

test_python_entry_supports_cross_platform_state_flow() {
  local state
  state="$(make_state python-run)"
  write_required_artifacts

  assert_success "python entry starts P0" "$PYTHON_BIN" "$PY_SCRIPT" --root "$TEST_ROOT" "$state" start P0
  assert_success "python entry completes P0" "$PYTHON_BIN" "$PY_SCRIPT" --root "$TEST_ROOT" "$state" complete P0
  assert_success "python entry starts P1" "$PYTHON_BIN" "$PY_SCRIPT" --root "$TEST_ROOT" "$state" start P1
  assert_success "python entry completes P1" "$PYTHON_BIN" "$PY_SCRIPT" --root "$TEST_ROOT" "$state" complete P1
  assert_success "python entry validates" "$PYTHON_BIN" "$PY_SCRIPT" --root "$TEST_ROOT" "$state" validate
}

test_python_entry_preserves_multi_word_reason() {
  local state
  state="$(make_state python-reason)"

  assert_success "reason run starts P0" "$PYTHON_BIN" "$PY_SCRIPT" --root "$TEST_ROOT" "$state" start P0
  assert_success "reason run completes P0" "$PYTHON_BIN" "$PY_SCRIPT" --root "$TEST_ROOT" "$state" complete P0
  assert_success \
    "python entry skips with multi-word reason" \
    "$PYTHON_BIN" "$PY_SCRIPT" --root "$TEST_ROOT" "$state" skip P1 waiting for Windows confirmation
  assert_file_contains \
    "python entry records full multi-word reason" \
    "$state" \
    "waiting for Windows confirmation"
}

test_validate_rejects_out_of_order_phase
test_complete_rejects_missing_artifact
test_validate_accepts_complete_single_reading_note_run
test_python_entry_supports_cross_platform_state_flow
test_python_entry_preserves_multi_word_reason

if [ "$FAILURES" -gt 0 ]; then
  printf '%s test(s) failed\n' "$FAILURES" >&2
  exit 1
fi
