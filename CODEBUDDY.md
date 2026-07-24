# CodeBuddy 使用范围

@AGENTS.md

CodeBuddy 仅维护精读流程直接需要的核心技能：文章排版、翻译、语法整理、长难句分析、综合笔记、词汇、Obsidian 与阅读心得。

技能同步、经验库维护、工作流状态、提示缓存和安全审计统一由 Codex 或 Claude Code 执行；不要假设 `.codebuddy/skills/` 与 `.agents/skills/` 完全对等。

<!-- env-template:codebuddy:begin -->
## Environment Variables

- Follow `.codebuddy/rules/common/env.md` whenever creating, updating, migrating, or auditing `.env`, `.env.example`, or environment-variable documentation.
- Keep committed env templates minimal, project-specific, and free of real secrets or machine-local absolute paths.
- After env template changes, run `.codebuddy/scripts/check-env-template.sh`. Use `--strict` when you want unused documented variables to fail the check.
<!-- env-template:codebuddy:end -->

<!-- prompt-cache-bootstrap:codebuddy:begin -->
## Prompt Cache

- Follow `.codebuddy/rules/common/prompt-cache.md` for high-frequency prompt design.
- Keep stable instructions and output formats before dynamic user input, file excerpts, dates, IDs, and runtime state.
- Reuse canonical templates and load long context only when needed.
<!-- prompt-cache-bootstrap:codebuddy:end -->

<!-- workflow-todo-state:start -->
## Workflow Todo State

Named workflow state files are the source of truth for every routed workflow.

- Workflow definitions live under `.codebuddy/workflows/{workflow-id}/`.
- Workflow state files live under `workspace/workflow-runs/` and should be named after the task, for example `payment-refactor.workflow.md`.
- Before any action that changes project files, runs project commands, or calls external services, read `.codebuddy/rules/workflow-routing.md` and match the user's original request against its triggers and exclusions.
- When a `Required: yes` workflow matches, read its `workflow.md`, create or resume its state file, and start the current phase before doing the work. Do not take the ordinary execution path instead.
- If the route is ambiguous, ask the user before acting.
- Read the active workflow state file before starting any phase; do not skip prerequisite phases.
- Change phase state only through `.codebuddy/scripts/todo-state.sh`.
- Use one unique phase status line per phase, for example `> [P0] ⬜ 未开始`.
- On resume after interruption, inspect the YAML frontmatter and current phase before acting.
- Each workflow directory must contain a `routing.yaml`. After creating, changing, renaming, or deleting a workflow, run `.codebuddy/scripts/sync-workflow-routing.sh`; the update is incomplete until `.codebuddy/scripts/sync-workflow-routing.sh --check` passes.
<!-- workflow-todo-state:end -->
