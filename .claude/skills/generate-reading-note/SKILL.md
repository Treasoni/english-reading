---
name: generate-reading-note
description: Use when generating complete 考研英语阅读精读笔记 from one or many English reading passages, especially when the user asks to 启动精读工作流, 批量生成考研阅读笔记, 处理大量英语笔记, or 串联排版、翻译、语法、长难句、整合、生词提取。
---

# Generate Reading Note

Start or resume the recoverable workflow that turns English reading passages into complete 考研英语阅读精读笔记. Route single-passage requests to the single workflow and multi-passage requests to the batch workflow.

## When to Use

Use this skill when the user asks for:

- 生成考研阅读笔记
- 启动精读工作流
- 完整精读笔记
- 批量生成考研阅读笔记
- 处理大量英语笔记
- 多篇精读笔记
- 从英文阅读文章生成学习笔记
- 串联排版、翻译、语法、长难句、整合、生词提取

Do not use this skill for a single isolated step such as only translation, only one long-sentence analysis, only vocabulary distinction, or only adding a reading tip.

## Platform Paths

Choose paths by the active runtime:

| Runtime | Routing File | Single Workflow | Batch Workflow | State Script |
|---------|--------------|-----------------|----------------|--------------|
| Codex | `.codex/rules/workflow-routing.md` | `.codex/workflows/reading-note-generation/workflow.md` | `.codex/workflows/reading-note-batch-generation/workflow.md` | `.codex/scripts/todo-state.sh` |
| Claude Code | `.claude/rules/workflow-routing.md` | `.claude/workflows/reading-note-generation/workflow.md` | `.claude/workflows/reading-note-batch-generation/workflow.md` | `.claude/scripts/todo-state.sh` |

Workflow ids:

- Single passage: `reading-note-generation`
- Multiple passages or source directory: `reading-note-batch-generation`

## Workflow Selection

Use `reading-note-generation` when the user provides or refers to one passage.

Use `reading-note-batch-generation` when the request mentions any batch signal:

- multiple passages, many notes, 大量英语笔记, 批量, 多篇
- a source directory of English reading files
- a backlog of note generation tasks
- fork subagent planning for reading notes

If the request could be either single or batch, ask one plain text question: "这是处理一篇文章，还是处理多个文件/一个目录？"

## Preflight

Before changing files, running project commands, or calling external services:

1. Confirm `.learnings/RULES.md`, `.learnings/LEARNINGS.md`, and `.learnings/ERRORS.md` are already in context from session start; re-read them only if absent.
2. Read the active runtime's routing file from the Platform Paths table.
3. Select the matching workflow id.
4. Read the selected workflow file from the Platform Paths table.
5. Create or resume the matching state file under `workspace/workflow-runs/`.
6. Read the active state file before starting each phase.

Change phase state only with the active runtime's state script:

```bash
<state-script> <state-file> start P0
<state-script> <state-file> complete P0
<state-script> <state-file> block P4 "waiting for confirmed long sentences"
```

## Single-Passage Mode

Use the state pattern:

```text
workspace/workflow-runs/reading-note-{year}-passage{passage}-{topic}.workflow.md
```

Collect these fields once at the workflow entrance:

- English article text or source file path.
- Year, passage number, and topic slug.
- Intermediate directory, defaulting to `intermediate/<year>-passage<passage>-<topic>/`.
- Final output path. This must be explicitly provided or confirmed by the user.
- Grammar notes input. If absent, ask whether to infer exam-relevant grammar points from the article.

Then follow `reading-note-generation`.

## Batch Mode

Use the state pattern:

```text
workspace/workflow-runs/reading-note-batch-{batch_id}.workflow.md
```

Collect these fields once at the workflow entrance:

- Source directory or explicit file list.
- Batch id, or permission to derive one from date and source name.
- Default output root for final notes.
- Default topic naming rule.
- Fork subagent concurrency. Default to 3 and never exceed 5.
- Whether global summary notes should be updated after per-note completion.

Then follow `reading-note-batch-generation`.

## Phase Handoff

| Mode | Phase Range | Coordinator | Reused Skills |
|------|-------------|-------------|---------------|
| Single | P0-P8 | main agent | format-article, translate, organize-grammar, analyze-sentence, compile-note, extract-vocabulary |
| Batch | P0-P8 | main agent with fork subagents | reading-note-generation per article plus the same core skills |

## Fork Subagent Rules For Batch Mode

Use fork-mode subagents only for independent, bounded work. In Codex, use forked context when dispatching a subagent. In Claude Code, use fork subagent mode when available.

Good fork subagent tasks:

- Read-only inventory for a subset of files.
- P1 formatted-article draft or check for one topic directory.
- P2 translation for one topic directory.
- P3 grammar extraction or grammar-notes draft for one topic directory.
- P4 candidate long sentences for one source article.
- Read-only QA for one final note.

Main-agent-only tasks:

- Batch state files and per-article state files.
- User confirmation prompts.
- Long-sentence insertion into `formatted-article.md`.
- Final compile when a final note path could collide.
- Vocabulary slot replacement.
- Global summary notes such as `语法总结笔记.md`, `固定搭配与词组笔记.md`, `阅读心得.md`, and `单词辨析.md`.

Dispatch constraints:

- Compose each fork prompt from the stable template in `prompts/fork-subagent.md`; keep the fixed prefix byte-stable and fill only the final `Parameters` block per subagent.
- Default concurrency is 3. Maximum concurrency is 5.
- Give each subagent one article or one read-only file group.
- Tell each subagent its exact write scope.
- Do not let two subagents write the same topic directory, final note, or shared summary file.
- Require each subagent to report changed files, skipped files, blockers, and recommended next phase.
- Main agent reviews every report before writing state, inserting callouts, compiling notes, or updating global files.

## Long-Sentence Gate

The long-sentence mode is always `AI 候选 + 用户确认`.

In candidate phases:

1. Read `formatted-article.md` or the source article.
2. Propose 5-10 candidate long sentences per article.
3. Give a short reason for each candidate.
4. Ask the user to confirm, remove, add, defer, or skip sentences.
5. Block or mark `needs_confirmation` if the user has not confirmed.

In insertion phases:

- Use `analyze-sentence` only on confirmed sentences.
- Insert each analysis block after its corresponding sentence in the article original section.
- If one paragraph has multiple analyzed sentences, use the alternating structure: original sentence, callout, next original sentence, callout.
- Every callout must begin with `> **原句**：完整英文原句`.
- Every callout table must have a blank line before the table.
- After insertion, check that later paragraphs were not truncated.

## Recovery Rules

- Missing article text, source directory, or file list blocks P0.
- Missing final output path blocks single mode P0 or P6.
- Missing batch output root blocks batch mode P0.
- Missing intermediate output returns to the phase that should produce it.
- Unconfirmed long-sentence candidates block single mode P4 or mark a batch article as `needs_confirmation`.
- A sentence that cannot be located in `formatted-article.md` blocks insertion until the user clarifies.
- Vocabulary count of 0 must be reported honestly.

## Final Verification

Before reporting completion:

- Confirm expected intermediate and final files exist.
- Confirm final notes no longer contain `<!-- VOCABULARY_SLOT -->`.
- Confirm Markdown headings have a space after `#`.
- Confirm YAML frontmatter uses simple strings and lists.
- Confirm every Markdown table has a blank line before it.
- Complete the final phase with the active runtime's state script.
