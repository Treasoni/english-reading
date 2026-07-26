# Batch Reading Note Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a recoverable batch workflow for many English reading notes and teach `generate-reading-note` how to route single-note vs batch-note requests.

**Architecture:** Keep `reading-note-generation` as the single-article workflow. Add `reading-note-batch-generation` as a coordinator workflow under both `.codex/workflows/` and `.claude/workflows/`, and update the existing entry skill to select the right workflow and describe safe fork subagent boundaries.

**Tech Stack:** Markdown workflow files, YAML routing metadata, existing `todo-state.sh`, existing `sync-workflow-routing.sh`, existing skill sync and registry scripts.

## Global Constraints

- Use `reading-note-batch-generation` as the batch workflow id.
- Use `workspace/workflow-runs/reading-note-batch-{batch_id}.workflow.md` as the batch state pattern.
- Keep `generate-reading-note` as the only entry skill.
- Do not create a separate batch entry skill.
- Default fork subagent concurrency is 3 and maximum is 5.
- Main agent owns state files, user confirmation, final insertion, final compile, vocabulary replacement, and global summary updates.
- Fork subagents may handle only independent scanning, per-article drafts, long-sentence candidates, and per-note QA.
- Do not let multiple subagents write the same topic directory, final note, or global summary file concurrently.
- Keep `.agents` and `.claude` skill semantics equivalent.

---

### Task 1: Add Batch Workflow Definitions

**Files:**
- Create: `.codex/workflows/reading-note-batch-generation/routing.yaml`
- Create: `.codex/workflows/reading-note-batch-generation/workflow.md`
- Create: `.codex/workflows/reading-note-batch-generation/state-template.md`
- Create: `.claude/workflows/reading-note-batch-generation/routing.yaml`
- Create: `.claude/workflows/reading-note-batch-generation/workflow.md`
- Create: `.claude/workflows/reading-note-batch-generation/state-template.md`

**Interfaces:**
- Consumes: existing single-article workflow `reading-note-generation`.
- Produces: batch workflow phases P0 through P8 and a batch state template.

- [ ] **Step 1: Write routing metadata**

Use one-line scalar YAML values:

```yaml
workflow_id: reading-note-batch-generation
required: true
when_to_use: "Generating complete 考研英语阅读精读笔记 for multiple English reading passages or a source directory"
triggers: "批量生成考研阅读笔记; 处理大量英语笔记; 多篇精读笔记; batch reading notes; directory reading note generation; fork subagent"
excludes: "single passage only; one sentence analysis only; read-only inspection; vocabulary distinction only"
state_file_pattern: "workspace/workflow-runs/reading-note-batch-{batch_id}.workflow.md"
```

- [ ] **Step 2: Write workflow and state templates**

Define P0 through P8 exactly as in the design: input, inventory, single-run initialization, independent generation, confirmation gate, serial write/compile, QA, global updates, closeout.

- [ ] **Step 3: Sync workflow routing**

Run:

```bash
.codex/scripts/sync-workflow-routing.sh
.claude/scripts/sync-workflow-routing.sh
```

Expected: both routing tables include `reading-note-batch-generation`.

---

### Task 2: Update Entry Skill

**Files:**
- Modify: `.agents/skills/generate-reading-note/SKILL.md`
- Modify: `.claude/skills/generate-reading-note/SKILL.md`

**Interfaces:**
- Consumes: `reading-note-generation` and `reading-note-batch-generation`.
- Produces: one entry skill that routes single and batch requests.

- [ ] **Step 1: Update description and routing table**

Keep the name `generate-reading-note`. Add batch triggers to the description and add a Workflow Selection section.

- [ ] **Step 2: Add batch subagent rules**

Document safe fork subagent steps and forbidden concurrent writes. Include default concurrency 3 and maximum 5.

- [ ] **Step 3: Keep both platform skill files equivalent**

Use a Platform Paths table so the same file content works for Codex and Claude Code.

---

### Task 3: Verify And Commit

**Files:**
- Inspect: `.codex/workflows/reading-note-batch-generation/`
- Inspect: `.claude/workflows/reading-note-batch-generation/`
- Inspect: `.agents/skills/generate-reading-note/SKILL.md`
- Inspect: `.claude/skills/generate-reading-note/SKILL.md`
- Inspect: `.codex/rules/workflow-routing.md`
- Inspect: `.claude/rules/workflow-routing.md`

**Interfaces:**
- Consumes: Tasks 1 and 2.
- Produces: committed batch workflow implementation.

- [ ] **Step 1: Run sync checks**

```bash
.codex/scripts/sync-workflow-routing.sh --check
.claude/scripts/sync-workflow-routing.sh --check
python3 .agents/skills/maintain-learnings/scripts/sync_platform_skills.py --root . --skill generate-reading-note --strict
```

- [ ] **Step 2: Run state smoke tests**

Copy the Codex and Claude batch state templates to `/tmp`, replace tokens, and advance P0 to P1 with each platform's `todo-state.sh`.

- [ ] **Step 3: Run Markdown checks**

Check heading spacing, table blank lines, placeholder words, shell syntax, and `git diff --check`.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-07-26-batch-reading-note-generation-design.md docs/superpowers/plans/2026-07-26-batch-reading-note-generation.md .codex/workflows/reading-note-batch-generation .claude/workflows/reading-note-batch-generation .agents/skills/generate-reading-note .claude/skills/generate-reading-note .codex/rules/workflow-routing.md .claude/rules/workflow-routing.md .codex/rules/common/skill-invocation.md .claude/rules/common/skill-invocation.md
git commit -m "feat: add batch reading note workflow"
```
