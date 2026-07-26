# Reading Note Batch Generation Workflow

Use this workflow when a user wants complete 考研英语阅读精读笔记 for multiple English reading passages, a directory of source files, or a large note backlog. This workflow coordinates many single-article `reading-note-generation` runs.

## Recovery Contract

- Before each phase, read the active batch state file under `workspace/workflow-runs/`.
- Create a state file from `state-template.md` if no matching batch run exists.
- Change batch phase state only with `.codex/scripts/todo-state.sh`.
- Create and update per-article single-run state files from `reading-note-generation`.
- Ask path, file list, output-root, and concurrency questions as plain text questions.
- Do not dispatch more than 5 fork subagents at once.
- Do not let fork subagents write the same topic directory, final note, batch state file, or global summary file concurrently.

## Required Inputs

- Source directory or explicit file list.
- Batch id, or permission to derive one from the date and source name.
- Default output root for final notes.
- Default topic naming rule.
- Fork subagent concurrency, default 3 and maximum 5.
- Whether global summary notes should be updated after per-note completion.

## Phase Summary

| Phase | Name | Main Output | Parallelism |
|------|------|-------------|-------------|
| P0 | 批量输入与状态初始化 | batch workflow run | main only |
| P1 | 清单盘点 | article inventory | fork read-only |
| P2 | 单篇 run 初始化 | per-article state files | main only |
| P3 | 独立内容生成 | per-topic drafts | fork isolated writes |
| P4 | 人工确认关口 | confirmed sentence lists | main only |
| P5 | 串行写入与整合 | final notes | main only |
| P6 | 批量 QA | reviewer reports | fork read-only |
| P7 | 全局汇总更新 | shared summary notes | main only |
| P8 | 最终收尾 | batch report | main only |

## P0 批量输入与状态初始化

1. Read `.learnings/RULES.md`, `.learnings/LEARNINGS.md`, `.learnings/ERRORS.md`, and `.codex/rules/workflow-routing.md`.
2. Collect source directory or file list.
3. Confirm batch id, output root, topic naming rule, and concurrency.
4. Clamp concurrency to 1-5. Use 3 if the user does not specify.
5. Create or resume `workspace/workflow-runs/reading-note-batch-{batch_id}.workflow.md`.
6. Start P0 with `.codex/scripts/todo-state.sh <state-file> start P0`.
7. Complete P0 only after the source set and concurrency are known.

## P1 清单盘点

1. Start P1 from the batch state file.
2. If there are many source files, dispatch fork subagents in non-overlapping read-only groups.
3. Each fork subagent returns a report with source path, year, passage, topic, suggested intermediate directory, suggested final output path, and missing metadata.
4. The main agent merges reports, removes duplicates, and marks missing metadata as blocked or needs_confirmation.
5. Complete P1 after the inventory is stable.

## P2 单篇 run 初始化

1. Start P2 from the batch state file.
2. For each inventory item, create or resume one `reading-note-generation` state file.
3. The main agent owns all state-file writes.
4. Record every per-article state path in the batch state file.
5. Complete P2 after all queued articles have a state file.

## P3 独立内容生成

1. Start P3 from the batch state file.
2. Dispatch fork subagents only when their write scopes do not overlap.
3. Safe fork subagent tasks:
   - P1 formatted article draft or check for one topic directory.
   - P2 translation for one topic directory.
   - P3 grammar extraction or grammar-notes draft for one topic directory.
   - P4 candidate long sentences for one source article.
4. Each fork subagent must write or return a report path before the main agent proceeds.
5. The main agent reviews reports and updates per-article state files.
6. Complete P3 after independent drafts and candidate lists are ready or explicitly skipped.

## P4 人工确认关口

1. Start P4 from the batch state file.
2. Present long-sentence candidates grouped by article.
3. Ask the user to confirm, remove, add, or defer candidates.
4. Mark unconfirmed articles as `needs_confirmation`.
5. Do not enter P5 for an article until its candidates are confirmed.
6. Complete P4 when all ready articles have a confirmed sentence list or are intentionally deferred.

## P5 串行写入与整合

1. Start P5 from the batch state file.
2. Process one article at a time.
3. Run P5 long-sentence analysis and insertion only after user confirmation.
4. Insert callouts with the alternating structure: original sentence, callout, next original sentence, callout.
5. Run P6 compile-note for that article.
6. Run P7 extract-vocabulary for that article.
7. Complete P5 after every ready article is complete, blocked, or deferred.

## P6 批量 QA

1. Start P6 from the batch state file.
2. Dispatch fork reviewer subagents for independent final notes.
3. Reviewers are read-only unless the main agent assigns one isolated file.
4. QA must check YAML simplicity, heading spacing, table blank lines, removed vocabulary slot, vocabulary exercises, and long-sentence callout placement.
5. The main agent serially applies any fixes.
6. Complete P6 after reviewer reports are resolved or recorded.

## P7 全局汇总更新

1. Start P7 from the batch state file.
2. Update global notes only if the user requested it.
3. Global notes are main-agent-only writes:
   - `语法总结笔记.md`
   - `固定搭配与词组笔记.md`
   - `阅读心得.md`
   - `单词辨析.md`
4. If global updates are not requested, skip P7 with a reason.
5. Complete P7 or skip it.

## P8 最终收尾

1. Start P8 from the batch state file.
2. Summarize completed, blocked, deferred, and skipped articles.
3. Report final note paths and per-article state paths.
4. Verify the batch state file is updated.
5. Complete P8.

## Fork Subagent Rules

- Use fork-mode subagents for independent, bounded work.
- Default concurrency is 3. The maximum is 5.
- Give each subagent one article or one read-only file group.
- Tell each subagent its exact write scope.
- Require each subagent to report changed files, skipped files, and blockers.
- Main agent reviews every report before merging, inserting, or updating state.

## Main-Agent-Only Rules

- Batch state files.
- Per-article workflow state files.
- User confirmation prompts.
- Long-sentence insertion into `formatted-article.md`.
- Final note compilation when a final path could collide.
- Vocabulary slot replacement.
- Global summary notes.
