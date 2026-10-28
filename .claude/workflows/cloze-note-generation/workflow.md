# Cloze Note Generation Workflow

Use this workflow when a user wants a complete 考研英语完形填空精读笔记 from one cloze passage. The workflow is required for full cloze-note generation. Its pilot output is `完形填空/2010-cloze-swine-flu-精读笔记.md`.

The output template is **ten sections, fixed order**: 一、作答记录 二、全文主旨与段落功能 三、逐空分析 四、逻辑关系地图 五、选项词汇辨析 六、固定搭配与介词 七、语法与长难句 八、生词表 九、错因复盘 十、二刷自测. Do not add, remove, or reorder sections.

## Recovery Contract

- Before each phase, read the active state file under `workspace/workflow-runs/`.
- Create a state file from `state-template.md` if no matching run exists.
- Resume the first phase whose status is not complete or skipped.
- Change phase state only with `.claude/scripts/todo-state.sh`.
- Run `.claude/scripts/todo-state.sh <state-file> validate` before reporting workflow completion.
- Do not report the workflow complete until P8 has updated the root `完形错因清单.md` and P9 has merged this passage into the root summary notes.
- Ask path and filename questions as plain text questions.
- Never invent the user's answers. If a blank's user answer is unknown, record 漏答 and say so in the report.
- Do not proceed from P0 to P1 until the answer key is confirmed.

## Core Principle

完形填空的失分主区不是"看不懂句子"，而是**线索没抓住**和**选项差异没辨清**。Every phase serves that:

- 逐空分析以「判断依据 / 线索词」为第一列结论，不写语法书式长文。
- 逻辑关系与固定搭配是主线，长难句只按需分析，不做全文句法拆解。
- 每篇必须产出可迁移的防错规则，并把失分点按五类标签归档到根目录清单。

## Required Inputs

- Cloze passage text or source file path, with all blanks marked.
- The 20 options (A-D per blank), as text or image.
- The official answer key, or explicit user confirmation of the correct answers.
- The user's own answers, blank by blank, including which blanks were left empty.
- Year and a slug, defaulting to `<year>-cloze-<topic>`.
- Intermediate directory, defaulting to `intermediate/<year>-cloze-<topic>/`.
- Final output path, explicit. Default when the user has no preference: `完形填空/<year>-cloze-<topic>-精读笔记.md`. Confirm it in P0.

## Phase Summary

| Phase | Name | Main Output | Required Skill |
|------|------|-------------|----------------|
| P0 | 输入收集与状态初始化 | workflow run file | generate-cloze-note |
| P1 | 原文与选项固化 | `formatted-article.md` + 素材原文 | format-article |
| P2 | 逐段中英翻译 | `translation.md` | translate |
| P3 | 语法整理 | `grammar-notes.md` | organize-grammar |
| P4 | 固定搭配整理 | `固定搭配与词组笔记.md` | organize-grammar |
| P5 | 逐空分析与错因归类 | `逐空分析.md` | analyze-sentence |
| P6 | 综合笔记整合 | 完形精读笔记 | compile-note |
| P7 | 生词表与练习 | vocabulary + 生词练习 | extract-vocabulary |
| P8 | 错因清单更新 | updated `完形错因清单.md` | generate-cloze-note |
| P9 | 全局汇总 | updated root summary notes | summarize-grammar |

## P0 输入收集与状态初始化

1. Confirm `.learnings/RULES.md`, `.learnings/LEARNINGS.md`, `.learnings/ERRORS.md`, and `.claude/rules/workflow-routing.md` are already in context from session start; re-read them only if absent.
2. Collect the passage text or source file path; verify the passage has exactly the expected number of blanks (20 for standard 考研完形).
3. Collect the 20 option groups. Reading photos via native multimodal is acceptable; do not use an OCR MCP.
4. Collect the official answer key and confirm its provenance (official vs. user-verified). Record it as `answer_key: official` only when it is the official key.
5. Collect the user's own answers per blank. Explicitly ask which blanks were left empty; empty blanks are recorded as 漏答, never as 错.
6. Confirm year, slug, intermediate directory, and final output path.
7. Create or resume `workspace/workflow-runs/cloze-note-{year}-{cloze_slug}.workflow.md`.
8. Start P0 with `.claude/scripts/todo-state.sh <state-file> start P0`.
9. Complete P0 only after the passage, options, answer key, and user answers are all known.

## P1 原文与选项固化

1. Start P1 from the state file.
2. Use `format-article` to normalize the passage: one `## 第 N 段` heading per paragraph, blanks marked as `【n】`, no reformatting of the English.
3. Write `formatted-article.md` in the intermediate directory, containing: the passage, a 20-row options table, the answer key line, and the 结构速览 table.
4. Also write or update the raw material note `完形填空/素材/<year>-cloze-<topic>-原文.md` with `type: cloze-source` and the user's first-attempt table. This file is the stable source of record; the note links to it.
5. Verify: blank count matches, option count is 4 per blank, no English text was altered or dropped.
6. Complete P1.

## P2 逐段中英翻译

1. Start P2 from the state file.
2. Use `translate`.
3. Write `translation.md`: per paragraph, the **English first with the correct answer bolded inside `【n xxx】`**, then **中文**.
4. End the file with `## 全篇译文要点` covering the timeline, the logical turns, and terminology.
5. Verify paragraph boundaries match `formatted-article.md` one-to-one.
6. Complete P2.

## P3 语法整理

1. Start P3 from the state file.
2. Use `organize-grammar`.
3. Extract only exam-relevant structures that actually carry a blank or a trap. Do not do a full syntactic annotation of the passage.
4. Use flat `###` headings, one per structure, each naming the blank it serves.
5. Write `grammar-notes.md`.
6. Complete P3.

## P4 固定搭配整理

1. Start P4 from the state file.
2. Use `organize-grammar`.
3. Write `固定搭配与词组笔记.md` with four blocks: 主题词、高频固定搭配（mark 本篇考点 with 📌）、动词搭配与干扰项辨析、速记卡片（one row per paragraph mapping signal words to answers）.
4. Keep pure grammar out of this file. Where a collocation rests on a grammar point, cross-link `[[语法总结笔记]]` instead of restating it.
5. Every blank whose answer is a fixed collocation must appear here with its 干扰项 explained.
6. Complete P4.

## P5 逐空分析与错因归类

1. Start P5 from the state file.
2. For each of the 20 blanks build a row: `| 空 | 你的答案 | 正确 | 判断依据 / 线索词 | 干扰项为何错 | 错因标签 |`.
3. Assign exactly one 错因标签 per lost blank from the five fixed tags: 词义辨析 / 逻辑关系 / 固定搭配 / 语法 / 粗心超纲. Choose the single dominant cause; do not multi-tag.
4. For the highest-value wrong blanks (at least the 5-8 with the most reusable lessons), write a 重点错题深挖 block: what the passage gives you, why the chosen option fails, why the correct one wins, and the transferable rule.
5. Use `analyze-sentence` only for blanks whose failure is genuinely structural; record those analyses for P6 section 七.
6. Write `intermediate/<year>-cloze-<topic>/逐空分析.md`.
7. Verify: 20 rows, tag counts sum to the number of lost blanks, and 漏答 blanks are tagged 粗心超纲 and never credited as correct.
8. Complete P5.

## P6 综合笔记整合

1. Start P6 from the state file.
2. Use `compile-note`.
3. Use the final output path confirmed in P0.
4. Assemble the ten sections in fixed order, drawing from `formatted-article.md`, `translation.md`, `grammar-notes.md`, `固定搭配与词组笔记.md`, and `逐空分析.md`.
5. Section 一 作答记录 must be a complete 20-row table with 你的答案 / 正确答案 / 判定 / 订正 plus a statistics block. Section 二 must carry a collapsed `> [!quote]- 文章原文（点击展开，空格标为【n】）`.
6. Section 三 carries the 20-row six-column table plus `### 重点错题深挖`. Section 四 carries the signal-word table, the 全篇逻辑链, and a `> [!tip] 完形读法`. Section 七 keeps only the structures selected in P5.
7. Include exactly one `<!-- VOCABULARY_SLOT -->` where section 八 belongs.
8. Obsidian rules that are mandatory here: blank line before every table, blank line before every `---`, space after `#`, no nested `[!tip]` inside `[!abstract]-`.
9. After assembly, run a visible-text diff between the source material note and the final note — the English word sequence, excluding `>` lines and frontmatter, must match. Whole-sentence or whole-paragraph loss is a defect; fix before completing.
10. Complete P6.

## P7 生词表与练习

1. Start P7 from the state file.
2. Use `extract-vocabulary` on the final note.
3. Replace the vocabulary slot with section 八: 主题词 / 动词 / 名词形容词 / 短语 four tables, then `### 生词练习` with 选词填空, 短语翻译, 语境理解, closed by `> [!success]- 参考答案`.
4. Include standalone entries for important words inside extracted phrases.
5. Verify the slot marker is gone and both `## 生词表` and `### 生词练习` exist.
6. Complete P7.

## P8 错因清单更新

1. Start P8 from the state file.
2. Open the root `完形错因清单.md`. If absent, create it from the five-tag structure.
3. Append a `### <year> 完形（<topic>）` block containing: 精读笔记 wikilink, 成绩 line, 失分点明细 table (one row per lost blank), 本篇统计 table (five tags + 空号), 本篇结论 (2-3 points), and 沉淀的防错规则 table mapping each rule to the blanks it covers.
4. Update the frontmatter: `updated`, `total_sources`, and `processed` (append `"<year> 完形（<topic>） | <对>/20 | <date>"`).
5. Update the 按标签汇总 table so each tag's 累计次数 and 涉及篇章 reflect the new piece, and refresh the `> [!warning] 当前优先级` note if the ranking changed.
6. Do not paste per-blank detail here that already lives in the note; this file is a loss-point register, not a duplicate note.
7. Complete P8.

## P9 全局汇总

1. Start P9 from the state file.
2. Use `summarize-grammar`.
3. Discover sources with both patterns, not just the first: `intermediate/**/grammar-notes.md` and `intermediate/**/固定搭配与词组笔记.md`.
4. Merge this passage's grammar points into the root `语法总结笔记.md` and its fixed collocations into the root `固定搭配与词组笔记.md`. Keep pure grammar out of the collocation file and collocations out of the grammar file; cross-link the two files with wikilinks.
5. Merge by deduplication, not by dumping. Before adding a point, `grep` the root file for the same structure; if it is already covered, extend the existing section or skip it and say so. Only genuinely new points get a new `##` section, appended at end of file after a `---` separator. Never insert a new section into the middle of an existing section.
6. Update both root files' frontmatter: `updated`, `total_sources`, `processed_sources`, and `categories`. Update each file's 快速索引 table so the index still matches the actual content.
7. Run the coverage diff. For `语法总结笔记.md` the diff between the discovered source list and `processed_sources` must be empty; a non-empty diff means P9 is not complete. For `固定搭配与词组笔记.md` a non-empty diff is allowed only for sources that carry no collocations, and each such source must be named and justified in the completion report.
8. Verify with `grep` that this passage's new headings exist in the target root file and that no table is missing the blank line before it.
9. Complete P9.
10. Run `.claude/scripts/todo-state.sh <state-file> validate`.
11. Report the intermediate directory, final note path, raw material note, the updated `完形错因清单.md`, both updated root summary files, and any skipped or blocked phases.

## Blocking Rules

- Missing passage text, options, answer key, or user answers blocks P0.
- A blank count other than the expected 20 must be reported explicitly before P1; do not silently proceed.
- An unconfirmed answer key blocks P1. Never treat a guessed key as `answer_key: official`.
- Missing intermediate files sends the workflow back to the producing phase.
- A tag count that does not sum to the lost-blank count blocks P5.
- A visible-text diff showing dropped English in P6 blocks P6 until repaired.
- Zero extracted vocabulary in P7 must be reported honestly; do not invent words.
- A non-empty coverage diff for `语法总结笔记.md` in P9 blocks P9 until the missing sources are merged.
- An unupdated `完形错因清单.md` blocks workflow completion even when P0-P7 are all complete.
- An unmerged root summary blocks workflow completion even when P0-P8 are all complete.
