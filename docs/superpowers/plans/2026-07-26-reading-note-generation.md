# Reading Note Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable workflow and entry skill that generate complete 考研英语阅读精读笔记 from one guided starting point.

**Architecture:** Add matching workflow definitions under `.codex/workflows/reading-note-generation/` and `.claude/workflows/reading-note-generation/`, then add matching `generate-reading-note` entry skills for `.agents` and `.claude`. The entry skill delegates each phase to the existing six reading skills and uses workflow state files for recovery.

**Tech Stack:** Markdown skill files, YAML routing metadata, existing `.codex/scripts/todo-state.sh`, existing `.codex/scripts/sync-workflow-routing.sh`, existing `.claude/scripts/todo-state.sh`, existing `.claude/scripts/sync-workflow-routing.sh`, existing platform skill sync script.

## Global Constraints

- Use `generate-reading-note` as the only new skill name.
- Use `reading-note-generation` as the workflow id.
- Use `workspace/workflow-runs/reading-note-{year}-passage{passage}-{topic}.workflow.md` as the state file pattern.
- Long-sentence analysis mode is “AI 候选 + 用户确认”.
- Do not bypass user confirmation before long-sentence insertion.
- Do not change the behavior or output contracts of existing core skills.
- Keep `.agents/skills/generate-reading-note/` and `.claude/skills/generate-reading-note/` functionally equivalent.
- Claude-only `manifest.yaml` stays only in `.claude/skills/generate-reading-note/`.
- Obsidian Markdown tables must have a blank line before the table.
- YAML frontmatter must use simple strings and lists, not nested object structures.
- Path and filename questions must be asked as plain text questions.

---

### Task 1: Add Workflow Definition

**Files:**
- Create: `.codex/workflows/reading-note-generation/workflow.md`
- Create: `.codex/workflows/reading-note-generation/state-template.md`
- Create: `.codex/workflows/reading-note-generation/routing.yaml`
- Create: `.claude/workflows/reading-note-generation/workflow.md`
- Create: `.claude/workflows/reading-note-generation/state-template.md`
- Create: `.claude/workflows/reading-note-generation/routing.yaml`
- Modify: `.codex/rules/workflow-routing.md`
- Modify: `.claude/rules/workflow-routing.md`

**Interfaces:**
- Consumes: existing `.codex/scripts/todo-state.sh`, `.claude/scripts/todo-state.sh`, and routing sync formats.
- Produces: registered `reading-note-generation` workflow with phases P0 through P8 for both Codex and Claude Code.

- [ ] **Step 1: Write workflow files**

Create the workflow directories with matching semantics:

```text
.codex/workflows/reading-note-generation/
  workflow.md
  state-template.md
  routing.yaml
.claude/workflows/reading-note-generation/
  workflow.md
  state-template.md
  routing.yaml
```

`routing.yaml` must contain one-line scalar values:

```yaml
workflow_id: reading-note-generation
required: true
when_to_use: "Generating complete 考研英语阅读精读笔记 from an English reading passage"
triggers: "生成考研阅读笔记; 启动精读工作流; 完整精读笔记; reading note generation; generate-reading-note; 排版 翻译 语法 长难句 整合 生词"
excludes: "single-step translation only; single sentence analysis only; vocabulary distinction only; add reading tip only; read-only inspection"
state_file_pattern: "workspace/workflow-runs/reading-note-{year}-passage{passage}-{topic}.workflow.md"
```

- [ ] **Step 2: Sync routing**

Run:

```bash
.codex/scripts/sync-workflow-routing.sh
.claude/scripts/sync-workflow-routing.sh
```

Expected: `.codex/rules/workflow-routing.md` and `.claude/rules/workflow-routing.md` generated tables include `reading-note-generation`.

- [ ] **Step 3: Verify routing is fresh**

Run:

```bash
.codex/scripts/sync-workflow-routing.sh --check
.claude/scripts/sync-workflow-routing.sh --check
```

Expected: both commands exit 0.

---

### Task 2: Add Entry Skill On Both Platforms

**Files:**
- Create: `.agents/skills/generate-reading-note/SKILL.md`
- Create: `.claude/skills/generate-reading-note/SKILL.md`
- Create: `.claude/skills/generate-reading-note/manifest.yaml`

**Interfaces:**
- Consumes: the workflow from Task 1 and existing reading skills `format-article`, `translate`, `organize-grammar`, `analyze-sentence`, `compile-note`, and `extract-vocabulary`.
- Produces: a discoverable `generate-reading-note` skill that starts or resumes the workflow.

- [ ] **Step 1: Add Codex-side skill**

Create `.agents/skills/generate-reading-note/SKILL.md` with frontmatter:

```yaml
---
name: generate-reading-note
description: Use when generating a complete 考研英语阅读精读笔记 from an English reading passage, especially when the user asks to 启动精读工作流, 生成考研阅读笔记, or 串联排版、翻译、语法、长难句、整合、生词提取。
---
```

The body must include:

- Required preflight reads: `.learnings/RULES.md`, `.learnings/LEARNINGS.md`, `.learnings/ERRORS.md`, `.codex/rules/workflow-routing.md`.
- Input collection checklist.
- State-file creation and resume rules.
- Phase handoff table for P0 through P8.
- Long-sentence confirmation gate.
- Recovery and blocking rules.
- Verification checklist.

- [ ] **Step 2: Add Claude-side skill and manifest**

Copy the same skill semantics to `.claude/skills/generate-reading-note/SKILL.md`, changing only platform-specific routing references from `.codex` to `.claude` where appropriate.

Create `.claude/skills/generate-reading-note/manifest.yaml` with:

```yaml
name: generate-reading-note
description: 启动考研英语阅读精读笔记生成工作流
version: 1.0.0
platforms:
  - claude-code
```

- [ ] **Step 3: Verify dual-platform sync**

Run:

```bash
python3 .agents/skills/maintain-learnings/scripts/sync_platform_skills.py --root . --skill generate-reading-note
```

Expected: command exits 0 and does not report missing `.agents` or `.claude` skill content.

---

### Task 3: Validate Workflow And Skill Quality

**Files:**
- Inspect: `.codex/workflows/reading-note-generation/workflow.md`
- Inspect: `.codex/workflows/reading-note-generation/state-template.md`
- Inspect: `.claude/workflows/reading-note-generation/workflow.md`
- Inspect: `.claude/workflows/reading-note-generation/state-template.md`
- Inspect: `.agents/skills/generate-reading-note/SKILL.md`
- Inspect: `.claude/skills/generate-reading-note/SKILL.md`
- Inspect: `.codex/rules/workflow-routing.md`
- Inspect: `.claude/rules/workflow-routing.md`

**Interfaces:**
- Consumes: files from Tasks 1 and 2.
- Produces: verified, committed implementation.

- [ ] **Step 1: Run shell syntax checks**

Run:

```bash
bash -n .codex/scripts/todo-state.sh
bash -n .codex/scripts/sync-workflow-routing.sh
bash -n .claude/scripts/todo-state.sh
bash -n .claude/scripts/sync-workflow-routing.sh
```

Expected: all commands exit 0.

- [ ] **Step 2: Smoke-test workflow state transitions**

Create a temporary copy of the state template under `/tmp/reading-note-generation.workflow.md`, replace template tokens with concrete values, then run:

```bash
.codex/scripts/todo-state.sh /tmp/reading-note-generation.workflow.md start P0
.codex/scripts/todo-state.sh /tmp/reading-note-generation.workflow.md complete P0
.codex/scripts/todo-state.sh /tmp/reading-note-generation.workflow.md start P1
```

Expected: commands exit 0 and the file advances to P1 in progress.

- [ ] **Step 3: Check Markdown and YAML contracts**

Run:

```bash
rg -n '^#[^ #]|^##[^ #]|^###[^ #]' .codex/workflows/reading-note-generation .agents/skills/generate-reading-note .claude/skills/generate-reading-note
rg -n '^#[^ #]|^##[^ #]|^###[^ #]' .claude/workflows/reading-note-generation
rg -n 'TBD|TODO|PLACEHOLDER|\\?\\?' .codex/workflows/reading-note-generation .claude/workflows/reading-note-generation .agents/skills/generate-reading-note .claude/skills/generate-reading-note
```

Expected: both searches return no matches.

- [ ] **Step 4: Commit implementation**

Run:

```bash
git status --short
git add docs/superpowers/plans/2026-07-26-reading-note-generation.md .codex/workflows/reading-note-generation .claude/workflows/reading-note-generation .codex/rules/workflow-routing.md .claude/rules/workflow-routing.md .agents/skills/generate-reading-note .claude/skills/generate-reading-note
git commit -m "feat: add reading note generation workflow"
```

Expected: commit succeeds on branch `codex/reading-note-generation-workflow`.
