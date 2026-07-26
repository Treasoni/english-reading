# Workflow Routing

Use this rule file to decide which named workflow to use and where to find active run state.

## Workflow Directory Layout

```text
.codex/workflows/{workflow-id}/workflow.md        # workflow definition
.codex/workflows/{workflow-id}/state-template.md # state file template
workspace/workflow-runs/*.workflow.md                   # active or historical run state
```

## Available Workflows

<!-- workflow-routing:generated:start -->
| Workflow ID | Required | When To Use | Positive Triggers | Excludes | Definition | State File Pattern |
| --- | --- | --- | --- | --- | --- | --- |
| `reading-note-batch-generation` | yes | Generating complete 考研英语阅读精读笔记 for multiple English reading passages or a source directory | 批量生成考研阅读笔记; 处理大量英语笔记; 多篇精读笔记; batch reading notes; directory reading note generation; fork subagent | single passage only; one sentence analysis only; read-only inspection; vocabulary distinction only | `.codex/workflows/reading-note-batch-generation/workflow.md` | `workspace/workflow-runs/reading-note-batch-{batch_id}.workflow.md` |
| `reading-note-generation` | yes | Generating complete 考研英语阅读精读笔记 from an English reading passage | 生成考研阅读笔记; 启动精读工作流; 完整精读笔记; reading note generation; generate-reading-note; 排版 翻译 语法 长难句 整合 生词 | single-step translation only; single sentence analysis only; vocabulary distinction only; add reading tip only; read-only inspection | `.codex/workflows/reading-note-generation/workflow.md` | `workspace/workflow-runs/reading-note-{year}-passage{passage}-{topic}.workflow.md` |
<!-- workflow-routing:generated:end -->

## Routing Rules

- Before any action that changes project files, runs project commands, or calls external services, choose the matching `workflow_id` from the table.
- Match the user's original request against positive triggers and exclusions. A matching `Required: yes` workflow cannot use the ordinary execution path.
- If multiple workflows match, choose the more specific workflow; if the route remains ambiguous, ask the user before acting.
- If a matching run already exists under `workspace/workflow-runs/`, resume it instead of creating a duplicate.
- If no run exists, create a named state file from the workflow's `state-template.md`.
- Name state files after the task or feature, not `todo.md`, unless the project has exactly one workflow.
- Every phase must read the active state file before acting.
- Phase state must be changed only through `.codex/scripts/todo-state.sh`.
- On Windows, use `.codex/scripts/todo-state.cmd` or `python .codex/scripts/todo-state.py` with the same arguments.
- Before reporting completion for a routed workflow, run `.codex/scripts/todo-state.sh <state-file> validate`; failed validation blocks completion.
- Each workflow directory must have a `routing.yaml`; it is the source of truth for the generated table above.
- After creating, changing, renaming, or deleting a workflow, run `.codex/scripts/sync-workflow-routing.sh`. Use `.codex/scripts/sync-workflow-routing.sh --check` in pre-commit or CI.

## Active Runs

| State File | Workflow ID | Task | Current Phase | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| | | | | | |
