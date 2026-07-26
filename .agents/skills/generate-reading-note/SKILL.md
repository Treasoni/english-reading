---
name: generate-reading-note
description: Use when generating a complete 考研英语阅读精读笔记 from an English reading passage, especially when the user asks to 启动精读工作流, 生成考研阅读笔记, or 串联排版、翻译、语法、长难句、整合、生词提取。
---

# Generate Reading Note

Start or resume the recoverable workflow that turns one English reading passage into a complete 考研英语阅读精读笔记.

## When to Use

Use this skill when the user asks for any full-note workflow:

- 生成考研阅读笔记
- 启动精读工作流
- 完整精读笔记
- 从英文阅读文章生成学习笔记
- 串联排版、翻译、语法、长难句、整合、生词提取

Do not use this skill for a single isolated step such as only translation, only one long-sentence analysis, only vocabulary distinction, or only adding a reading tip.

## Platform Paths

Choose paths by the active runtime:

| Runtime | Routing File | Workflow File | State Script |
|---------|--------------|---------------|--------------|
| Codex | `.codex/rules/workflow-routing.md` | `.codex/workflows/reading-note-generation/workflow.md` | `.codex/scripts/todo-state.sh` |
| Claude Code | `.claude/rules/workflow-routing.md` | `.claude/workflows/reading-note-generation/workflow.md` | `.claude/scripts/todo-state.sh` |

Use the same workflow id on both platforms: `reading-note-generation`.

## Preflight

Before changing files, running project commands, or calling external services:

1. Read `.learnings/RULES.md`, `.learnings/LEARNINGS.md`, and `.learnings/ERRORS.md`.
2. Read the active runtime's routing file from the Platform Paths table.
3. Match the user request against `reading-note-generation`.
4. Read the active runtime's workflow file from the Platform Paths table.
5. Create or resume the state file under `workspace/workflow-runs/`.
6. Read the active state file before starting each phase.

Change phase state only with the active runtime's state script:

```bash
<state-script> <state-file> start P0
<state-script> <state-file> complete P0
<state-script> <state-file> block P4 "waiting for confirmed long sentences"
```

## Input Collection

Collect these fields once at the workflow entrance instead of asking each downstream skill again:

- English article text or source file path.
- Year, passage number, and topic slug.
- Intermediate directory, defaulting to `intermediate/<year>-passage<passage>-<topic>/`.
- Final output path. This must be explicitly provided or confirmed by the user.
- Grammar notes input. If absent, ask whether to infer exam-relevant grammar points from the article.

Ask custom paths and filenames with plain text questions. Do not use preset-choice UI for custom paths.

## State File

Use the pattern:

```text
workspace/workflow-runs/reading-note-{year}-passage{passage}-{topic}.workflow.md
```

If the file exists, resume it. If it does not exist, create it from the active runtime's `state-template.md` and replace the template tokens with the collected values.

## Phase Handoff

| Phase | Action | Skill | Output |
|------|--------|-------|--------|
| P0 | Collect inputs and initialize state | generate-reading-note | workflow run file |
| P1 | Format article | format-article | formatted-article.md |
| P2 | Translate article | translate | translation.md |
| P3 | Organize grammar notes | organize-grammar | grammar-notes.md |
| P4 | Propose candidate long sentences | generate-reading-note | confirmed sentence list |
| P5 | Analyze confirmed sentences inline | analyze-sentence | callouts in formatted-article.md |
| P6 | Compile final note | compile-note | final study note |
| P7 | Extract vocabulary and exercises | extract-vocabulary | 生词表 and 生词练习 |
| P8 | Verify and close | generate-reading-note | completed state |

## Long-Sentence Gate

The long-sentence mode is always `AI 候选 + 用户确认`.

In P4:

1. Read `formatted-article.md`.
2. Propose 5-10 candidate long sentences.
3. Give a short reason for each candidate.
4. Ask the user to confirm, remove, or add sentences.
5. Block P4 if the user has not confirmed.

In P5:

- Use `analyze-sentence` only on confirmed sentences.
- Insert each analysis block after its corresponding sentence in the article original section.
- If one paragraph has multiple analyzed sentences, use the alternating structure: original sentence, callout, next original sentence, callout.
- Every callout must begin with `> **原句**：完整英文原句`.
- Every callout table must have a blank line before the table.
- After insertion, check that later paragraphs were not truncated.

## Recovery Rules

- Missing article text or source file path blocks P0.
- Missing final output path blocks P0 or P6.
- Missing intermediate output returns to the phase that should produce it.
- Unconfirmed long-sentence candidates block P4.
- A sentence that cannot be located in `formatted-article.md` blocks P5 until the user clarifies.
- Vocabulary count of 0 in P7 must be reported honestly.

## Final Verification

Before reporting completion:

- Confirm `formatted-article.md`, `translation.md`, `grammar-notes.md`, and the final study note exist.
- Confirm the final study note no longer contains `<!-- VOCABULARY_SLOT -->`.
- Confirm Markdown headings have a space after `#`.
- Confirm YAML frontmatter uses simple strings and lists.
- Confirm every Markdown table has a blank line before it.
- Complete P8 with the active runtime's state script.
