---
name: generate-cloze-note
description: Use when generating a complete 考研英语完形填空精读笔记 from one cloze passage, especially when the user asks to 做完形精读, 生成完形笔记, 逐空分析, 统计完形错因, or 串联原文、翻译、语法、搭配、逐空分析、错因清单。
---

# Generate Cloze Note

Start or resume the recoverable workflow that turns one 完形填空 passage into a complete 考研英语完形填空精读笔记 plus a cross-article 错因清单 entry.

## When to Use

Use this skill when the user asks for:

- 完形填空精读
- 做完形精读 / 启动完形工作流
- 生成完形笔记 / 完形填空精读笔记
- 逐空分析 / 20 空分析
- 完形错因 / 错因统计
- 串联原文、翻译、语法、搭配、逐空分析、错因清单

Do not use this skill for:

- 阅读 Passage 精读笔记 → use `generate-reading-note` / `reading-note-generation`.
- A single isolated step: only translation, only one sentence analysis, only vocabulary distinction, only adding a reading tip.
- Multiple cloze passages or a directory of passages → route to a batch workflow instead.

## Platform Paths

Choose paths by the active runtime:

| Runtime | Routing File | Workflow | State Template | State Script |
|---------|--------------|----------|----------------|--------------|
| Codex | `.codex/rules/workflow-routing.md` | `.codex/workflows/cloze-note-generation/workflow.md` | `.codex/workflows/cloze-note-generation/state-template.md` | `.codex/scripts/todo-state.sh` |
| Claude Code | `.claude/rules/workflow-routing.md` | `.claude/workflows/cloze-note-generation/workflow.md` | `.claude/workflows/cloze-note-generation/state-template.md` | `.claude/scripts/todo-state.sh` |

Workflow id: `cloze-note-generation`

## Preflight

Before changing files, running project commands, or calling external services:

1. Confirm `.learnings/RULES.md`, `.learnings/LEARNINGS.md`, and `.learnings/ERRORS.md` are already in context from session start; re-read them only if absent.
2. Read the active runtime's routing file from the Platform Paths table.
3. Read the `cloze-note-generation` workflow file.
4. Create or resume the state file under `workspace/workflow-runs/`.
5. Read the active state file before starting each phase.

Change phase state only with the active runtime's state script:

```bash
<state-script> <state-file> start P0
<state-script> <state-file> complete P0
<state-script> <state-file> validate
```

## State File Pattern

```text
workspace/workflow-runs/cloze-note-{year}-{cloze_slug}.workflow.md
```

## Input Collection

Collect these once at the workflow entrance. Ask path and filename questions as plain text questions.

| Field | Requirement |
|-------|-------------|
| 原文 | Passage text or source file path, blanks marked `【n】` |
| 选项 | 20 option groups (A-D). Photos are acceptable via native multimodal; never an OCR MCP |
| 答案 | Official answer key, with provenance confirmed. Never claim official without confirmation |
| 我的作答 | User's own answers per blank, explicitly including which blanks were left empty |
| year / slug | Default slug `<year>-cloze-<topic>` |
| intermediate | Default `intermediate/<year>-cloze-<topic>/` |
| 输出路径 | Explicit. Default proposal: `完形填空/<year>-cloze-<topic>-精读笔记.md`, confirmed by the user |
| 错因清单 | Default `完形错因清单.md` at vault root |

漏答 is never the same as 错. Ask directly: "哪几个空你是空着的？"

## Output Template

The final note has exactly ten sections, in this order. Do not add, remove, or reorder.

| # | 章节 | 内容要点 |
|---|------|---------|
| 一 | 作答记录 | 20 行表（你的答案 / 正确答案 / 判定 / 订正）+ 统计 |
| 二 | 全文主旨与段落功能 | 三句话主旨 + 段落功能表 + 可折叠文章原文 |
| 三 | 逐空分析 | 20 行六列表（判断依据 / 干扰项为何错 / 错因标签）+ 重点错题深挖 |
| 四 | 逻辑关系地图 | 信号词表 + 全篇逻辑链 + `> [!tip] 完形读法` |
| 五 | 选项词汇辨析 | 20 行选项辨析表 |
| 六 | 固定搭配与介词 | 搭配表，📌 标注本篇考点 |
| 七 | 语法与长难句 | 只保留与空格或陷阱相关的结构 |
| 八 | 生词表 | 主题词 / 动词 / 名词形容词 / 短语 + `### 生词练习` |
| 九 | 错因复盘 | 错因统计 + 可迁移规则 + 最该回炉的空 |
| 十 | 二刷自测 | 20 空答题卡 + 线索词填空 + 逻辑关系判断 + 参考答案 |

## 五类错因标签

Every lost blank gets exactly one tag:

| 标签 | 判定标准 |
|------|---------|
| 词义辨析 | 选项都认识，但选的词在本句语义/语域不成立 |
| 逻辑关系 | 转折、因果、时间、并列、条件线索没抓住，取义方向反了 |
| 固定搭配 | 空处属于固定短语或固定介词框架，未识别 |
| 语法 | 结构判断错误（从句、非谓语、语态、主谓一致） |
| 粗心超纲 | 漏答、涂错、看错题号，或纯生词导致无法判断 |

Tag counts must sum to the number of lost blanks.

## Phase Handoff

| Phase | Name | Coordinator | Reused Skills |
|-------|------|-------------|---------------|
| P0 | 输入收集与状态初始化 | main agent | generate-cloze-note |
| P1 | 原文与选项固化 | main agent | format-article |
| P2 | 逐段中英翻译 | main agent | translate |
| P3 | 语法整理 | main agent | organize-grammar |
| P4 | 固定搭配整理 | main agent | organize-grammar |
| P5 | 逐空分析与错因归类 | main agent | analyze-sentence |
| P6 | 综合笔记整合 | main agent | compile-note |
| P7 | 生词表与练习 | main agent | extract-vocabulary |
| P8 | 错因清单更新 | main agent | generate-cloze-note |
| P9 | 全局汇总 | main agent | summarize-grammar |

P8 and P9 are both mandatory closing phases. The workflow is not complete when only the note exists.

## Recovery Rules

- Missing passage, options, answer key, or user answers blocks P0.
- A blank count other than the expected 20 must be reported before P1; do not proceed silently.
- Missing intermediate files returns to the phase that should produce them.
- A tag count that does not sum to the lost-blank count blocks P5.
- Dropped English text detected by the visible-text diff blocks P6.
- Zero extracted vocabulary must be reported honestly.
- An unupdated `完形错因清单.md` blocks completion.
- A non-empty coverage diff for `语法总结笔记.md` blocks P9.

## Markdown Rules

- Blank line before every table.
- Blank line before every `---`, or the preceding line becomes a setext H2.
- Space after every `#`.
- No nested `[!tip]` inside `[!abstract]-`; use a flat callout.
- Simple YAML only: strings and flat lists, no nested objects.

## Final Verification

Before reporting completion:

- Confirm the material note, all five intermediate files, the final note, and the updated `完形错因清单.md` exist.
- Confirm the final note no longer contains `<!-- VOCABULARY_SLOT -->`.
- Confirm all ten sections exist in order.
- Confirm the note's English text matches the source material (visible-text diff).
- Run `<state-script> <state-file> validate` and require it to pass.
