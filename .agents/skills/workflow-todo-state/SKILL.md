---
name: workflow-todo-state
description: Create or retrofit reusable named workflow state machines for multi-step agent projects. Use when a project needs recoverable workflow state files, multiple workflow definitions, phase gates, restart-safe agent workflows, explicit skipped/blocked states, workflow routing rules, or reusable workflow templates across repositories.
---

# Workflow Todo State

Use this skill to make long-running agent workflows recoverable from named workflow state files. The pattern combines human-readable Markdown checklists with machine-readable YAML frontmatter and a deterministic state script.

## Quick Start

Install into another project:

```bash
skills/workflow-todo-state/scripts/install.sh /path/to/target-project --agent-dir .agent --with-skill --init-layout --update-agents
```

Use `--profile codex|claude|generic` for built-in layouts, or `--agent-dir`, `--skills-dir`, and `--entry-file` for a custom layout. The Codex profile correctly separates `.agents/skills` from `.codex`; omitting profile options keeps the historical `.claude` + `CLAUDE.md` default.

Then:

1. Create workflow definitions under `<agent-dir>/workflows/{workflow-id}/`.
2. Add `routing.yaml` to every workflow directory as the source of truth for its trigger conditions and state file pattern.
3. Generate the routing registry with `<agent-dir>/scripts/sync-workflow-routing.sh`.
4. Create run state files under `workspace/workflow-runs/{task-or-feature}.workflow.md`.
5. Create or update the state file from `references/basic-state-template.md`.
6. Ensure every phase has exactly one status line:
   ```markdown
   > [P0] ⬜ 未开始
   ```
7. Make every workflow skill or agent route the task, then read the relevant workflow state file before starting work.
8. Update state only through the script:
   ```bash
   <agent-dir>/scripts/todo-state.sh "${WORKFLOW_STATE_FILE}" start P1
   <agent-dir>/scripts/todo-state.sh "${WORKFLOW_STATE_FILE}" complete P1
   <agent-dir>/scripts/todo-state.sh "${WORKFLOW_STATE_FILE}" skip P2 "not needed"
   <agent-dir>/scripts/todo-state.sh "${WORKFLOW_STATE_FILE}" block P3 "waiting for user input"
   ```

## Recommended Layout

Use separate files for workflow definitions and workflow runs:

```text
.agent/
  workflows/
    feature-development/
      workflow.md
      state-template.md
      routing.yaml
    release-check/
      workflow.md
      state-template.md
      routing.yaml
  rules/
    workflow-routing.md
  scripts/
    sync-workflow-routing.sh
workspace/
  workflow-runs/
    payment-refactor.workflow.md
    release-v1-2.workflow.md
```

Do not name every run `todo.md` when a project can have multiple workflows. Prefer descriptive state files:

- `{feature-name}.workflow.md`
- `{task-name}.workflow.md`
- `{workflow-id}-{run-id}.workflow.md`

Use `todo.md` only for a single-purpose project where one workflow will ever exist.

## Required State File Shape

Each reusable workflow state file should contain:

- YAML frontmatter with `workflow_id`, `workflow_name`, `workflow_version`, `state_file_type`, `run_id`, `task`, `created_from`, `current_phase`, `current_status`, `mode`, and `blocked_reason`.
- A visible line beginning with `> 当前阶段：`.
- One unique phase status line per phase, using `> [PN] ...`.
- An `## 异常记录` table if `skip` or `block` should append history.

See `references/basic-state-template.md` for a minimal portable state template, `references/workflow-routing-template.md` for routing rules, and `references/integration.md` for retrofit instructions.

## Routing Metadata and Synchronization

Each workflow directory must contain a minimal scalar `routing.yaml`:

```yaml
workflow_id: feature-development
required: true
when_to_use: "Implementing or changing a product feature"
triggers: "new feature; bug fix; refactor"
excludes: "read-only question; inspect-only request"
state_file_pattern: "workspace/workflow-runs/feature-{task}.workflow.md"
```

`workflow_id` must match its directory name. Keep values on one line and do not use `|`, because they are rendered into a Markdown table.

After every workflow create, change, rename, or deletion, run:

```bash
<agent-dir>/scripts/sync-workflow-routing.sh
<agent-dir>/scripts/sync-workflow-routing.sh --check
```

The first command regenerates only the marked block in `<agent-dir>/rules/workflow-routing.md`; the second is suitable for pre-commit or CI and fails when the registry is stale.

## State Rules

- `start PN` requires all previous phases to be `✅ 已完成` or `⏭️ 跳过`.
- `complete PN` requires the phase to be `🔲 进行中`.
- `skip PN` refuses completed phases and records a reason.
- `block PN` marks an open phase in progress, writes `current_status: blocked`, and records a reason; completed and skipped phases are terminal.
- After `complete` or `skip`, the script advances `current_phase` to the next `⬜ 未开始` phase, or to `done` when no pending phase remains.

## When Retrofitting A Project

Keep the change small:

1. Add the script.
2. Add `<agent-dir>/workflows/`, `workspace/workflow-runs/`, and `<agent-dir>/rules/workflow-routing.md`.
3. Add `routing.yaml` to every existing workflow, then run `sync-workflow-routing.sh`.
4. Add frontmatter and unique phase lines to existing state files.
5. Replace ad hoc `sed` or manual status edits in skills/agents with `todo-state.sh`.
6. Add a project entry rule: before any mutating action, route the task; if a required workflow matches, create or resume its run and start the current phase.
7. Run `sync-workflow-routing.sh --check` in pre-commit or CI.
8. Test one happy path, one blocked/invalid transition, and one stale-routing failure.

Do not force a project to adopt this exact workflow structure. Preserve local phase names, output files, and user confirmation gates.
