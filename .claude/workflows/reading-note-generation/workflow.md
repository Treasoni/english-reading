# Reading Note Generation Workflow

Use this workflow when a user wants a complete 考研英语阅读精读笔记 from an English reading passage. The workflow is required for full-note generation and is started through the `generate-reading-note` skill.

## Recovery Contract

- Before each phase, read the active state file under `workspace/workflow-runs/`.
- Create a state file from `state-template.md` if no matching run exists.
- Resume the first phase whose status is not complete or skipped.
- Change phase state only with `.claude/scripts/todo-state.sh`.
- Run `.claude/scripts/todo-state.sh <state-file> validate` before reporting workflow completion.
- Do not report the workflow complete until P9 has merged this passage into the root summary notes.
- Ask path and filename questions as plain text questions.
- Do not proceed from P4 to P5 until the user confirms the long-sentence list.

## Required Inputs

- English article text or source file path.
- Year, passage number, and topic slug.
- Intermediate directory, defaulting to `intermediate/<year>-passage<passage>-<topic>/`.
- Final output path, explicitly provided or confirmed by the user.
- Grammar notes input, or permission to extract grammar points from the article.

## Phase Summary

| Phase | Name | Main Output | Required Skill |
|------|------|-------------|----------------|
| P0 | 输入收集与状态初始化 | workflow run file | generate-reading-note |
| P1 | 文章排版 | formatted-article.md | format-article |
| P2 | 中英翻译 | translation.md | translate |
| P3 | 语法整理 | grammar-notes.md | organize-grammar |
| P4 | 长难句候选确认 | confirmed sentence list | generate-reading-note |
| P5 | 长难句分析与内联插入 | inline callouts | analyze-sentence |
| P6 | 综合笔记整合 | final study note | compile-note |
| P7 | 生词表与练习 | vocabulary section and exercises | extract-vocabulary |
| P8 | 最终验证与收尾 | verified study note | generate-reading-note |
| P9 | 全局汇总 | updated root summary notes | summarize-grammar |

## P0 输入收集与状态初始化

1. Confirm `.learnings/RULES.md`, `.learnings/LEARNINGS.md`, `.learnings/ERRORS.md`, and `.claude/rules/workflow-routing.md` are already in context from session start; re-read them only if absent.
2. Collect the article text or source file path.
3. Collect or infer year, passage number, and topic slug.
4. Confirm the intermediate directory.
5. Ask the user for the final output path if it has not been provided.
6. Create or resume `workspace/workflow-runs/reading-note-{year}-passage{passage}-{topic}.workflow.md`.
7. Start P0 with `.claude/scripts/todo-state.sh <state-file> start P0`.
8. Record the selected mode: `AI 候选 + 用户确认`.
9. Complete P0 only after all required inputs are known.

## P1 文章排版

1. Start P1 from the state file.
2. Use `format-article`.
3. Write or update `formatted-article.md` in the confirmed intermediate directory.
4. Verify that the English article content is preserved and Obsidian headings have a space after `#`.
5. Complete P1.

## P2 中英翻译

1. Start P2 from the state file.
2. Use `translate`.
3. Write or update `translation.md`.
4. Preserve paragraph boundaries and complete English source text.
5. Complete P2.

## P3 语法整理

1. Start P3 from the state file.
2. Use `organize-grammar`.
3. If the user provided grammar notes, use them as the source.
4. If the user did not provide grammar notes, extract exam-relevant grammar points from the article and state that this is inferred from the article.
5. Write or update `grammar-notes.md`.
6. Verify source coverage, including terms, etymology notes, tone differences, examples, and exam-use context when present.
7. Complete P3.

## P4 长难句候选确认

1. Start P4 from the state file.
2. Read `formatted-article.md`.
3. Propose 5-10 candidate long sentences.
4. For each candidate, state the reason: clause nesting, non-finite verb phrase, inserted modifier, inversion, emphasis, parallelism, or exam trap.
5. Ask the user to confirm, remove, or add sentences.
6. Block P4 if the user has not confirmed the sentence list.
7. Complete P4 only after confirmation.

## P5 长难句分析与内联插入

1. Start P5 from the state file.
2. Use `analyze-sentence` on the confirmed sentences.
3. Insert each analysis block into `formatted-article.md` immediately after the corresponding sentence in the article original section.
4. If one paragraph contains multiple analyzed sentences, use the alternating structure: original sentence, its callout, next original sentence, its callout.
5. Ensure every callout starts with `> **原句**：完整英文原句`.
6. Ensure every callout table has a blank line before the table.
7. Check that no following paragraph starts abnormally with punctuation, `and`, `or`, or `but`.
8. Complete P5.

## P6 综合笔记整合

1. Start P6 from the state file.
2. Use `compile-note`.
3. Use the final output path confirmed in P0.
4. Read `formatted-article.md`, `translation.md`, and `grammar-notes.md`.
5. Preserve inline long-sentence callouts in the article original section.
6. Include exactly one `<!-- VOCABULARY_SLOT -->` before the 心得 section.
7. Complete P6.

## P7 生词表与练习

1. Start P7 from the state file.
2. Use `extract-vocabulary` on the final study note.
3. Replace the vocabulary slot with `## 生词表` and `### 生词练习`.
4. Include standalone entries for important words inside extracted phrases.
5. Complete P7.

## P8 最终验证与收尾

1. Start P8 from the state file.
2. Verify that `formatted-article.md`, `translation.md`, `grammar-notes.md`, and the final study note exist.
3. Verify the final study note no longer contains `<!-- VOCABULARY_SLOT -->`.
4. Check Markdown heading spacing, simple YAML frontmatter, and blank lines before tables.
5. Complete P8.

## P9 全局汇总

1. Start P9 from the state file.
2. Use `summarize-grammar`.
3. Discover sources with both patterns, not just the first: `intermediate/**/grammar-notes.md` and `intermediate/**/固定搭配与词组笔记.md`.
4. Merge this passage's grammar points into the root `语法总结笔记.md` and its fixed collocations into the root `固定搭配与词组笔记.md`. Keep pure grammar out of the collocation file and collocations out of the grammar file; cross-link the two files with wikilinks.
5. Update both root files' frontmatter: `updated`, `total_sources`, `processed_sources`, and `categories`. Update each file's 快速索引 table so the index still matches the actual content.
6. Run the coverage diff. For `语法总结笔记.md` the diff between the discovered source list and `processed_sources` must be empty; a non-empty diff means P9 is not complete. For `固定搭配与词组笔记.md` a non-empty diff is allowed only for sources that carry no collocations, and each such source must be named and justified in the completion report.
7. Verify with `grep` that this passage's new headings exist in the target root file and that no table is missing the blank line before it.
8. Complete P9.
9. Run `.claude/scripts/todo-state.sh <state-file> validate`.
10. Report the intermediate directory, final output path, both updated root summary files, and any skipped or blocked phases.

## Blocking Rules

- Missing article text or source file path blocks P0.
- Missing final output path blocks P0 or P6.
- Missing intermediate files sends the workflow back to the producing phase.
- Unconfirmed long-sentence candidates block P4.
- A sentence that cannot be located in `formatted-article.md` blocks P5 until the user clarifies.
- Zero extracted vocabulary in P7 must be reported honestly; do not invent words.
- A non-empty coverage diff for `语法总结笔记.md` in P9 blocks P9 until the missing sources are merged.
- An unmerged root summary blocks workflow completion even when P0-P8 are all complete.
