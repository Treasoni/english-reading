# Integration Guide

## Install Into Another Project

Recommended one-command install from this source project:

```bash
skills/workflow-todo-state/scripts/install.sh /path/to/target-project --agent-dir .agent --with-skill --init-layout --update-agents
```

Omit `--agent-dir` to use the historical `.claude` default.

Script-only install:

```bash
skills/workflow-todo-state/scripts/install.sh /path/to/target-project --agent-dir .agent
```

Manual fallback:

```bash
mkdir -p /path/to/target-project/.agent/scripts
cp skills/workflow-todo-state/scripts/todo-state.sh /path/to/target-project/.agent/scripts/todo-state.sh
cp skills/workflow-todo-state/scripts/sync-workflow-routing.sh /path/to/target-project/.agent/scripts/sync-workflow-routing.sh
chmod +x /path/to/target-project/.agent/scripts/todo-state.sh /path/to/target-project/.agent/scripts/sync-workflow-routing.sh
```

## Recommended Layout

Use named workflow definitions and named run state files:

```text
.agent/workflows/
  feature-development/
    workflow.md
    state-template.md
    routing.yaml
.agent/rules/
  workflow-routing.md
.agent/scripts/
  sync-workflow-routing.sh
workspace/workflow-runs/
  payment-refactor.workflow.md
```

`todo-state.sh` accepts any Markdown state file path, so the run file does not need to be named `todo.md`.

## Register Workflows From Metadata

Do not hand-edit the generated workflow table. Add a one-line scalar `routing.yaml` to each workflow directory:

```yaml
workflow_id: feature-development
required: true
when_to_use: "Implementing product changes"
triggers: "new feature; bug fix; refactor"
excludes: "read-only question"
state_file_pattern: "workspace/workflow-runs/feature-{task}.workflow.md"
```

Then synchronize the routing registry:

```bash
.agent/scripts/sync-workflow-routing.sh
.agent/scripts/sync-workflow-routing.sh --check
```

The script owns only the section delimited by `workflow-routing:generated` markers. It leaves routing guidance and the active-run table intact.

## Add Project Rule

Add this to the project entry instructions:

```markdown
Before any action that changes project files, runs project commands, or calls external services, read `<agent-dir>/rules/workflow-routing.md` and match the user's request against its triggers and exclusions. When a required workflow matches, read its definition, create or resume its state file, and start the current phase before acting. Every workflow phase must read the active workflow state file before acting. Workflow state files live under `workspace/workflow-runs/` and should be named after the task, such as `payment-refactor.workflow.md`. Do not skip phases. Change phase state only through `<agent-dir>/scripts/todo-state.sh`. After every workflow change, run `<agent-dir>/scripts/sync-workflow-routing.sh` and require `<agent-dir>/scripts/sync-workflow-routing.sh --check` to pass.
```

## Retrofit Existing State Templates

1. Add YAML frontmatter:
   ```yaml
   ---
   workflow_id: your-flow
   workflow_name: Your Flow
   workflow_version: 1
   state_file_type: workflow-run
   run_id: "{run_id}"
   task: "{task}"
   created_from: "<agent-dir>/workflows/your-flow/state-template.md"
   created_at: "{date}"
   last_updated: "{date}"
   current_phase: P0
   current_status: not_started
   mode: standard
   blocked_reason: ""
   ---
   ```
2. Add a visible current phase line:
   ```markdown
   > 当前阶段：阶段 0
   ```
3. Ensure each phase has one unique status line:
   ```markdown
   > [P3] ⬜ 未开始
   ```
4. Replace manual edits:
   ```bash
   <agent-dir>/scripts/todo-state.sh "${WORKFLOW_STATE_FILE}" start P3
   <agent-dir>/scripts/todo-state.sh "${WORKFLOW_STATE_FILE}" complete P3
   <agent-dir>/scripts/todo-state.sh "${WORKFLOW_STATE_FILE}" skip P3 "optional phase not needed"
   <agent-dir>/scripts/todo-state.sh "${WORKFLOW_STATE_FILE}" block P3 "waiting for confirmation"
   ```

## Validation Checklist

- `bash -n <agent-dir>/scripts/todo-state.sh`
- Start and complete P0 on a copied workflow state file.
- Try starting P2 before P1 is complete; it should fail.
- Try skipping an optional phase; `current_phase` should advance to the next pending phase.
- Confirm `## 异常记录` receives skip/block rows when present.
- Change a `routing.yaml` value, confirm `sync-workflow-routing.sh --check` fails, then synchronize and confirm it passes.
