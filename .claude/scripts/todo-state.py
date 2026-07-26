#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cross-platform workflow phase state transitions."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import tempfile
from pathlib import Path


VALID_ACTIONS = {"validate", "start", "complete", "skip", "block"}
VALID_PHASE_RE = re.compile(r"^P[0-9]+$")
PHASE_LINE_RE = re.compile(r"^> \[(P([0-9]+))\] .* \{([^}]+)\}$")
VALID_PHASE_STATUSES = {"not_started", "in_progress", "blocked", "complete", "skipped"}
VALID_CURRENT_STATUSES = {"not_started", "ready", "in_progress", "blocked", "complete"}
REQUIRED_FRONTMATTER_KEYS = (
    "workflow_id",
    "workflow_name",
    "workflow_version",
    "state_file_type",
    "run_id",
    "task",
    "created_from",
    "current_phase",
    "current_status",
    "mode",
    "blocked_reason",
)


class TodoStateError(Exception):
    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def usage() -> str:
    return """Usage:
  <agent-dir>/scripts/todo-state.py [--root DIR] <workflow-state.md> validate
  <agent-dir>/scripts/todo-state.py [--root DIR] <workflow-state.md> start P1
  <agent-dir>/scripts/todo-state.py [--root DIR] <workflow-state.md> complete P1
  <agent-dir>/scripts/todo-state.py [--root DIR] <workflow-state.md> skip P3 "reason"
  <agent-dir>/scripts/todo-state.py [--root DIR] <workflow-state.md> block P2 "reason"

Updates the phase status line, YAML recovery metadata, and visible current phase."""


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def unquote_frontmatter_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
    return value


class WorkflowState:
    def __init__(self, todo_file: str, project_root: str | None = None) -> None:
        self.path = Path(todo_file)
        if not self.path.is_absolute():
            self.path = Path.cwd() / self.path
        self.path = self.path.resolve()
        if not self.path.is_file():
            raise TodoStateError(f"todo-state: file not found: {todo_file}")

        if project_root:
            self.project_root = Path(project_root).resolve()
        else:
            self.project_root = self._infer_project_root()

        self.today = dt.date.today().isoformat()
        self.now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    def _infer_project_root(self) -> Path:
        parts = self.path.parts
        for index in range(len(parts) - 1):
            if parts[index] == "workspace" and parts[index + 1] == "workflow-runs":
                return Path(*parts[:index])
        return Path.cwd().resolve()

    def read_text(self) -> str:
        return self.path.read_text(encoding="utf-8")

    def write_text(self, text: str) -> None:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            delete=False,
            dir=str(self.path.parent),
            prefix=f"{self.path.name}.",
        ) as handle:
            handle.write(text)
            temp_path = Path(handle.name)
        temp_path.replace(self.path)

    def lines(self) -> list[str]:
        return self.read_text().splitlines()

    def frontmatter_lines(self) -> tuple[list[str], int, int] | None:
        lines = self.lines()
        if not lines or lines[0] != "---":
            return None
        for index in range(1, len(lines)):
            if lines[index] == "---":
                return lines[1:index], 0, index
        return None

    def frontmatter_has_key(self, key: str) -> bool:
        frontmatter = self.frontmatter_lines()
        if not frontmatter:
            return False
        lines, _, _ = frontmatter
        return any(line.startswith(f"{key}:") for line in lines)

    def frontmatter_value(self, key: str) -> str:
        frontmatter = self.frontmatter_lines()
        if not frontmatter:
            return ""
        lines, _, _ = frontmatter
        for line in lines:
            if line.startswith(f"{key}:"):
                return unquote_frontmatter_value(line.split(":", 1)[1])
        return ""

    def ensure_frontmatter(self, phase: str) -> None:
        lines = self.lines()
        if lines and lines[0] == "---":
            return
        prefix = [
            "---",
            "workflow: unknown",
            'topic: ""',
            'project_slug: ""',
            'created_at: ""',
            f"last_updated: {yaml_quote(self.today)}",
            f"current_phase: {phase}",
            "current_status: unknown",
            "mode: standard",
            'blocked_reason: ""',
            "---",
        ]
        self.write_text("\n".join(prefix + lines) + "\n")

    def set_frontmatter_key(self, key: str, value: str) -> None:
        lines = self.lines()
        if not lines or lines[0] != "---":
            raise TodoStateError("todo-state: frontmatter not found")

        done = False
        in_frontmatter = False
        output: list[str] = []
        for line in lines:
            if not output and line == "---":
                in_frontmatter = True
                output.append(line)
                continue
            if in_frontmatter and line == "---":
                if not done:
                    output.append(f"{key}: {value}")
                in_frontmatter = False
                output.append(line)
                continue
            if in_frontmatter and line.startswith(f"{key}:"):
                output.append(f"{key}: {value}")
                done = True
                continue
            output.append(line)

        self.write_text("\n".join(output) + "\n")

    def set_recovery_state(
        self, current_phase: str, current_status: str, blocked_reason: str = ""
    ) -> None:
        self.ensure_frontmatter(current_phase)
        self.set_frontmatter_key("last_updated", yaml_quote(self.today))
        self.set_frontmatter_key("current_phase", current_phase)
        self.set_frontmatter_key("current_status", current_status)
        self.set_frontmatter_key("blocked_reason", yaml_quote(blocked_reason))

    def set_visible_current_phase(self, current_phase: str) -> None:
        label = current_phase
        if VALID_PHASE_RE.match(current_phase):
            label = f"阶段 {current_phase[1:]}"
        elif current_phase == "done":
            label = "完成"

        lines = self.lines()
        for index, line in enumerate(lines):
            if line.startswith("> 当前阶段："):
                lines[index] = f"> 当前阶段：{label}"
                break
        self.write_text("\n".join(lines) + "\n")

    def phase_lines(self) -> list[tuple[int, str, int, str]]:
        result: list[tuple[int, str, int, str]] = []
        for line_index, line in enumerate(self.lines()):
            match = PHASE_LINE_RE.match(line)
            if match:
                phase = match.group(1)
                result.append((line_index, phase, int(match.group(2)), match.group(3)))
        return result

    def phase_line_count(self, phase: str) -> int:
        prefix = f"> [{phase}] "
        return sum(1 for line in self.lines() if line.startswith(prefix))

    def require_phase_line(self, phase: str) -> None:
        count = self.phase_line_count(phase)
        if count == 0:
            raise TodoStateError(f"todo-state: phase line not found: {phase}")
        if count != 1:
            raise TodoStateError(f"todo-state: phase line must be unique: {phase}")

    def phase_status_for(self, phase: str) -> str:
        for _, current_phase, _, status in self.phase_lines():
            if current_phase == phase:
                return status
        return ""

    def phase_has_status(self, phase: str, status: str) -> bool:
        return self.phase_status_for(phase) == status

    def replace_phase_status(self, phase: str, label: str) -> None:
        lines = self.lines()
        prefix = f"> [{phase}] "
        for index, line in enumerate(lines):
            if line.startswith(prefix):
                lines[index] = f"{prefix}{label}"
                self.write_text("\n".join(lines) + "\n")
                return
        raise TodoStateError("todo-state: could not update phase line")

    def previous_open_phase_before(self, phase: str) -> str:
        phase_num = int(phase[1:])
        for _, previous_phase, previous_num, status in self.phase_lines():
            if previous_num < phase_num and status not in {"complete", "skipped"}:
                return previous_phase
        return ""

    def ensure_previous_phases_closed(self, phase: str) -> None:
        open_phase = self.previous_open_phase_before(phase)
        if open_phase:
            raise TodoStateError(
                f"todo-state: previous phase is not complete or skipped: {open_phase}"
            )

    def next_pending_phase_after(self, phase: str) -> str:
        phase_num = int(phase[1:])
        for _, next_phase, next_num, status in self.phase_lines():
            if next_num > phase_num and status == "not_started":
                return next_phase
        return ""

    def ensure_exception_table(self) -> None:
        if "## 异常记录" not in self.read_text():
            raise TodoStateError("todo-state: exception table not found")

    def append_exception_record(self, phase: str, issue: str, handling: str) -> None:
        issue = issue.replace("|", "")
        handling = handling.replace("|", "")
        row = f"| {self.now} | {phase} | {issue} | {handling} |"
        lines = self.lines()

        for index, line in enumerate(lines):
            if line == "## 异常记录":
                table_lines_seen = 0
                for table_index in range(index + 1, len(lines)):
                    if lines[table_index].startswith("|"):
                        table_lines_seen += 1
                        if table_lines_seen == 2:
                            lines.insert(table_index + 1, row)
                            self.write_text("\n".join(lines) + "\n")
                            return
                break
        raise TodoStateError("todo-state: exception table rows not found")

    def workflow_path(self, raw_path: str) -> Path | None:
        if not raw_path or "{" in raw_path:
            return None
        path = Path(raw_path)
        if path.is_absolute():
            return path
        return self.project_root / path

    def require_shape(self) -> None:
        lines = self.lines()
        if not lines or lines[0] != "---":
            raise TodoStateError("todo-state: frontmatter not found")

        for key in REQUIRED_FRONTMATTER_KEYS:
            if not self.frontmatter_has_key(key):
                raise TodoStateError(f"todo-state: frontmatter key missing: {key}")

        current_phase_count = sum(1 for line in lines if line.startswith("> 当前阶段："))
        if current_phase_count != 1:
            raise TodoStateError("todo-state: visible current phase line must be unique")

    def validate_phase_order(self) -> None:
        phases: list[tuple[int, str, str]] = []
        seen: set[str] = set()
        for line in self.lines():
            if not line.startswith("> [P"):
                continue
            match = PHASE_LINE_RE.match(line)
            if not match:
                phase_match = re.match(r"^> \[(P[0-9]+)\] ", line)
                phase = phase_match.group(1) if phase_match else "unknown"
                raise TodoStateError(
                    f"todo-state: phase line missing machine status: {phase}"
                )
            phase = match.group(1)
            if phase in seen:
                raise TodoStateError(f"todo-state: phase line must be unique: {phase}")
            seen.add(phase)
            status = match.group(3)
            if status not in VALID_PHASE_STATUSES:
                raise TodoStateError(
                    f"todo-state: unknown phase status for {phase}: {status}"
                )
            phases.append((int(match.group(2)), phase, status))

        if not phases:
            raise TodoStateError("todo-state: phase line not found")

        for index, (phase_num, phase, status) in enumerate(phases):
            if phase_num != index:
                raise TodoStateError(
                    "todo-state: phase sequence must be contiguous from P0: "
                    f"expected P{index}, found {phase}"
                )
            if status == "not_started":
                continue
            for _, previous_phase, previous_status in phases[:index]:
                if previous_status not in {"complete", "skipped"}:
                    raise TodoStateError(
                        "todo-state: previous phase is not complete or skipped: "
                        f"{previous_phase}"
                    )

        active = [
            phase
            for _, phase, status in phases
            if status in {"in_progress", "blocked"}
        ]
        if len(active) > 1:
            raise TodoStateError("todo-state: multiple active phases found")

    def validate_recovery_state(self) -> None:
        current_phase = self.frontmatter_value("current_phase")
        current_status = self.frontmatter_value("current_status")

        if current_status not in VALID_CURRENT_STATUSES:
            raise TodoStateError(f"todo-state: unknown current_status: {current_status}")

        if current_phase == "done":
            if current_status != "complete":
                raise TodoStateError(
                    "todo-state: current_phase done requires current_status complete"
                )
            for _, _, _, status in self.phase_lines():
                if status in {"not_started", "in_progress", "blocked"}:
                    raise TodoStateError(
                        "todo-state: current_phase done requires every phase "
                        "to be complete or skipped"
                    )
            return

        if not VALID_PHASE_RE.match(current_phase):
            raise TodoStateError(
                f"todo-state: current_phase must be Pn or done: {current_phase}"
            )

        phase_status = self.phase_status_for(current_phase)
        if not phase_status:
            raise TodoStateError(f"todo-state: current_phase line not found: {current_phase}")

        if current_status in {"not_started", "ready"}:
            if phase_status != "not_started":
                raise TodoStateError(
                    f"todo-state: current_status {current_status} requires "
                    f"{current_phase} to be not_started"
                )
            return

        if current_status in {"in_progress", "blocked"}:
            if phase_status != current_status:
                raise TodoStateError(
                    f"todo-state: current_status {current_status} does not match "
                    f"{current_phase} status {phase_status}"
                )
            return

        raise TodoStateError("todo-state: current_status complete requires current_phase done")

    def require_file(self, phase: str, path: Path | None) -> None:
        if path is None or not path.is_file():
            message_path = str(path) if path is not None else "unknown path"
            raise TodoStateError(
                f"todo-state: required artifact missing for {phase}: {message_path}"
            )

    def require_file_contains(self, phase: str, path: Path | None, pattern: str) -> None:
        self.require_file(phase, path)
        assert path is not None
        if pattern not in path.read_text(encoding="utf-8"):
            raise TodoStateError(
                f"todo-state: required artifact content missing for {phase}: "
                f"{pattern} in {path}"
            )

    def require_file_not_contains(self, phase: str, path: Path | None, pattern: str) -> None:
        self.require_file(phase, path)
        assert path is not None
        if pattern in path.read_text(encoding="utf-8"):
            raise TodoStateError(
                f"todo-state: artifact still contains forbidden marker for {phase}: "
                f"{pattern} in {path}"
            )

    def reading_note_paths(self) -> tuple[Path | None, Path | None, Path | None, Path | None]:
        intermediate_dir = self.frontmatter_value("intermediate_dir").rstrip("/\\")
        output_path = self.frontmatter_value("output_path")
        return (
            self.workflow_path(f"{intermediate_dir}/formatted-article.md"),
            self.workflow_path(f"{intermediate_dir}/translation.md"),
            self.workflow_path(f"{intermediate_dir}/grammar-notes.md"),
            self.workflow_path(output_path),
        )

    def validate_reading_note_artifacts(self) -> None:
        formatted_article, translation, grammar_notes, final_note = self.reading_note_paths()

        if self.phase_status_for("P1") == "complete":
            self.require_file("P1", formatted_article)
        if self.phase_status_for("P2") == "complete":
            self.require_file("P2", translation)
        if self.phase_status_for("P3") == "complete":
            self.require_file("P3", grammar_notes)
        if self.phase_status_for("P5") == "complete":
            self.require_file_contains(
                "P5", formatted_article, "> [!abstract]- 长难句分析"
            )
        if self.phase_status_for("P6") == "complete":
            self.require_file_contains("P6", final_note, "<!-- VOCABULARY_SLOT -->")
        if self.phase_status_for("P7") == "complete":
            self.require_file_not_contains("P7", final_note, "<!-- VOCABULARY_SLOT -->")
            self.require_file_contains("P7", final_note, "## 生词表")
            self.require_file_contains("P7", final_note, "### 生词练习")
        if self.phase_status_for("P8") == "complete" or self.frontmatter_value(
            "current_phase"
        ) == "done":
            self.require_file("P8", formatted_article)
            self.require_file("P8", translation)
            self.require_file("P8", grammar_notes)
            self.require_file_not_contains("P8", final_note, "<!-- VOCABULARY_SLOT -->")
            self.require_file_contains("P8", final_note, "## 生词表")
            self.require_file_contains("P8", final_note, "### 生词练习")

    def validate_workflow_artifacts(self) -> None:
        if self.frontmatter_value("workflow_id") == "reading-note-generation":
            self.validate_reading_note_artifacts()

    def validate_phase_completion_requirements(self, phase: str) -> None:
        if self.frontmatter_value("workflow_id") != "reading-note-generation":
            return

        formatted_article, translation, grammar_notes, final_note = self.reading_note_paths()
        if phase == "P1":
            self.require_file("P1", formatted_article)
        elif phase == "P2":
            self.require_file("P2", translation)
        elif phase == "P3":
            self.require_file("P3", grammar_notes)
        elif phase == "P5":
            self.require_file_contains("P5", formatted_article, "> [!abstract]- 长难句分析")
        elif phase == "P6":
            self.require_file_contains("P6", final_note, "<!-- VOCABULARY_SLOT -->")
        elif phase == "P7":
            self.require_file_not_contains("P7", final_note, "<!-- VOCABULARY_SLOT -->")
            self.require_file_contains("P7", final_note, "## 生词表")
            self.require_file_contains("P7", final_note, "### 生词练习")
        elif phase == "P8":
            self.require_file("P8", formatted_article)
            self.require_file("P8", translation)
            self.require_file("P8", grammar_notes)
            self.require_file_not_contains("P8", final_note, "<!-- VOCABULARY_SLOT -->")
            self.require_file_contains("P8", final_note, "## 生词表")
            self.require_file_contains("P8", final_note, "### 生词练习")

    def validate_state(self) -> None:
        self.require_shape()
        self.validate_phase_order()
        self.validate_recovery_state()
        self.validate_workflow_artifacts()

    def start(self, phase: str) -> None:
        self.ensure_previous_phases_closed(phase)
        if self.phase_has_status(phase, "complete") or self.phase_has_status(
            phase, "skipped"
        ):
            raise TodoStateError(f"todo-state: cannot start completed or skipped phase: {phase}")
        self.replace_phase_status(phase, "🔲 进行中 {in_progress}")
        self.set_recovery_state(phase, "in_progress")
        self.set_visible_current_phase(phase)
        self.validate_state()

    def complete(self, phase: str) -> None:
        self.ensure_previous_phases_closed(phase)
        if self.phase_has_status(phase, "skipped"):
            raise TodoStateError(f"todo-state: cannot complete skipped phase: {phase}")
        if not self.phase_has_status(phase, "in_progress"):
            raise TodoStateError(
                f"todo-state: phase must be in progress before complete: {phase}"
            )

        self.validate_phase_completion_requirements(phase)
        self.replace_phase_status(phase, "✅ 已完成 {complete}")
        next_phase = self.next_pending_phase_after(phase)
        if next_phase:
            self.set_recovery_state(next_phase, "ready")
            self.set_visible_current_phase(next_phase)
        else:
            self.set_recovery_state("done", "complete")
            self.set_visible_current_phase("done")
        self.validate_state()

    def skip(self, phase: str, reason: str) -> None:
        self.ensure_previous_phases_closed(phase)
        self.ensure_exception_table()
        if self.phase_has_status(phase, "complete"):
            raise TodoStateError(f"todo-state: cannot skip completed phase: {phase}")

        self.replace_phase_status(phase, "⏭️ 跳过 {skipped}")
        self.append_exception_record(
            phase,
            f"跳过阶段：{reason or '未填写原因'}",
            "继续推进到下一未完成阶段",
        )
        next_phase = self.next_pending_phase_after(phase)
        if next_phase:
            self.set_recovery_state(next_phase, "ready")
            self.set_visible_current_phase(next_phase)
        else:
            self.set_recovery_state("done", "complete")
            self.set_visible_current_phase("done")
        self.validate_state()

    def block(self, phase: str, reason: str) -> None:
        self.ensure_previous_phases_closed(phase)
        self.ensure_exception_table()
        if self.phase_has_status(phase, "complete") or self.phase_has_status(
            phase, "skipped"
        ):
            raise TodoStateError(f"todo-state: cannot block completed or skipped phase: {phase}")

        self.replace_phase_status(phase, "🔲 进行中 {blocked}")
        self.set_recovery_state(phase, "blocked", reason)
        self.set_visible_current_phase(phase)
        self.append_exception_record(
            phase,
            f"阻塞：{reason or '未填写原因'}",
            "停在当前阶段，等待用户确认或补充资料",
        )
        self.validate_state()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="<agent-dir>/scripts/todo-state.py",
        description="Update workflow phase state files.",
        usage=argparse.SUPPRESS,
        add_help=True,
    )
    parser.add_argument("--root", help="Project root for resolving workflow artifacts.")
    parser.add_argument("todo_file", nargs="?")
    parser.add_argument("action", nargs="?")
    parser.add_argument("phase", nargs="?")
    parser.add_argument("reason", nargs="?")
    args = parser.parse_args(argv)

    if not args.todo_file or not args.action:
        raise TodoStateError(usage(), 2)
    if args.action not in VALID_ACTIONS:
        raise TodoStateError(f"todo-state: unknown action: {args.action}\n{usage()}", 2)
    if args.action != "validate":
        if not args.phase:
            raise TodoStateError(
                f"todo-state: missing phase for action: {args.action}\n{usage()}", 2
            )
        if not VALID_PHASE_RE.match(args.phase):
            raise TodoStateError("todo-state: phase must look like P0, P1, ...", 2)
    return args


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(list(sys.argv[1:] if argv is None else argv))
        state = WorkflowState(args.todo_file, args.root)

        if args.action != "validate":
            state.require_phase_line(args.phase)

        if args.action == "validate":
            state.validate_state()
        elif args.action == "start":
            state.start(args.phase)
        elif args.action == "complete":
            state.complete(args.phase)
        elif args.action == "skip":
            state.skip(args.phase, args.reason or "")
        elif args.action == "block":
            state.block(args.phase, args.reason or "")
        return 0
    except TodoStateError as error:
        print(str(error), file=sys.stderr)
        return error.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
