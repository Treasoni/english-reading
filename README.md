# 考研英语阅读精读 Vault

这是一个 Obsidian 学习库：沉淀考研英语**阅读 Passage、完形填空、英语二作文**的原文、翻译、语法、长难句、生词与跨篇总结。它通过 Codex 与 Claude Code 的同名技能辅助学习，不提供或承诺独立的 Python CLI。

详细操作步骤与可复制指令请看：[使用说明](使用说明.md)

## 三条学习路线

| 路线 | 入口技能 | 工作流 | 最终产物 |
| --- | --- | --- | --- |
| 阅读 Passage（单篇） | `generate-reading-note` | `reading-note-generation`（P0–P9） | `<年份>阅读/<year>-passage<n>-<topic>-精读笔记.md` |
| 阅读 Passage（批量） | `generate-reading-note` | `reading-note-batch-generation`（P0–P8） | 多篇精读笔记 + 批量报告 |
| 完形填空 | `generate-cloze-note` | `cloze-note-generation`（P0–P9） | `完形填空/<year>-cloze-<topic>-精读笔记.md` + `完形错因清单.md` |
| 英语二作文批改 | `grade-essay` | 无状态文件 | `作文/<YYYY-MM-DD>-<类型>-<话题>-批改.md` + 作文台账 |

三条路线互不混用：阅读笔记不会顺手做完形，作文批改也不处理阅读或完形。

## 阅读 Passage 精读

单篇流程由 `generate-reading-note` 启动，分阶段执行，每阶段读取 `workspace/workflow-runs/` 下的状态文件：

| 阶段 | 技能 | 产出 |
| --- | --- | --- |
| P1 文章排版 | `format-article` | `intermediate/<topic>/formatted-article.md` |
| P2 中英翻译 | `translate` | `intermediate/<topic>/translation.md` |
| P3 语法整理 | `organize-grammar` | `intermediate/<topic>/grammar-notes.md` |
| P4 长难句候选确认 | `generate-reading-note` | 待分析句清单（需你确认） |
| P5 长难句分析 | `analyze-sentence` | 内联到原文对应句后的 `> [!abstract]-` callout |
| P6 综合笔记 | `compile-note` | 最终精读笔记 |
| P7 生词与练习 | `extract-vocabulary` | 生词表 + 生词练习 |
| P8 最终验证 | `generate-reading-note` | 校验通过的笔记 |
| P9 全局汇总 | `summarize-grammar` | 更新根目录 `语法总结笔记.md`、`固定搭配与词组笔记.md` |

多篇或整目录走 `reading-note-batch-generation`，并发上限 5，单篇写入串行，最后由 P7 统一做全局汇总。

## 完形填空精读

`generate-cloze-note` 是独立工作流，不与阅读 Passage 混用。输入必须齐全：原文、20 组选项、官方答案、你逐空作答（含漏答）。漏答不等于错，工作流会单独确认。

笔记固定十章：作答记录、全文主旨与段落功能、逐空分析、逻辑关系地图、选项词汇辨析、固定搭配与介词、语法与长难句、生词表、错因复盘、二刷自测。每空失分只归一类，五类标签固定为 **词义辨析 / 逻辑关系 / 固定搭配 / 语法 / 粗心超纲**，并汇总进根目录 `完形错因清单.md`。

## 英语二作文批改

`grade-essay` 只覆盖英语二：小作文 10 分（书信、通知，约 100 词）、大作文 15 分（图表作文，约 150 词）。

流程为转写确认 → 任务点核对 → 结构分析 → 错误归类 → 定档评分 → 双版本改稿 → 提分路径 → 落盘。其中 **P1 转写是硬门禁**：转写稿必须经你确认后才能评分，未确认的存疑处不得用于扣分。

评分只引用 `references/english2-scoring-criteria.md` 的官方标准，先定档再给分，不做维度分值加权。六类错因标签固定为 **内容要点缺失 / 语言准确性 / 词汇与搭配 / 句式与衔接 / 篇章结构 / 字数与格式**。

## 跨篇汇总与台账

| 文件 | 作用 | 更新时机 |
| --- | --- | --- |
| `语法总结笔记.md` | 跨篇语法去重汇总 | 每篇精读的全局汇总阶段 |
| `固定搭配与词组笔记.md` | 跨篇固定搭配与词组 | 每篇精读的全局汇总阶段 |
| `完形错因清单.md` | 完形五类错因跨篇登记 | 每篇完形 P8 |
| `作文/作文错因清单.md` | 作文六类错因跨篇登记 | 每次批改 P8 |
| `作文/高分表达库.md` | 从本人作文升级而来的可迁移表达 | 每次批改 P8 |
| `作文/作文索引.md` | 分数、档位与稿次索引 | 每次批改 P8 |
| `单词辨析.md` | 易混淆词辨析 | 使用 `vocab-diff` 时 |
| `阅读心得.md` | 阅读技巧沉淀 | 使用 `add-reading-tip` 时 |

## 目录约定

```text
├── 20xx阅读/<year>-passage<n>-<topic>-精读笔记.md   # 阅读最终笔记
├── 完形填空/
│   ├── <year>-cloze-<topic>-精读笔记.md             # 完形最终笔记
│   └── 素材/<year>-cloze-<topic>-原文.md            # 完形原始素材
├── 作文/
│   ├── <YYYY-MM-DD>-<类型>-<话题>-批改.md           # 作文批改笔记
│   ├── 素材/                                        # 手写原文图片
│   ├── 作文错因清单.md / 高分表达库.md / 作文索引.md
├── intermediate/<topic>/                            # 单篇阶段性产物
├── workspace/workflow-runs/*.workflow.md            # 工作流运行状态
├── .agents/skills/                                  # Codex 技能定义
├── .claude/skills/                                  # Claude Code 技能定义
├── .codebuddy/skills/                               # CodeBuddy 核心技能
├── .claude/workflows/ · .codex/workflows/           # 工作流定义与状态模板
├── .learnings/                                      # 经验库（本地状态，不纳入版本控制）
├── docs/                                            # 设计与实施计划存档
└── scripts/                                         # Vault 一致性校验
```

`<topic>` 必须使用完整 slug，例如 `2024-passage2-uk-timber` 或 `2010-cloze-swine-flu`；中间目录名、最终笔记的 YAML `topic` 与文件名应保持一致。阅读笔记必须存放在对应年份的 `20xx阅读/` 目录下。

## 工作流状态

三个工作流（`reading-note-generation`、`reading-note-batch-generation`、`cloze-note-generation`）都以 `workspace/workflow-runs/` 下的状态文件为准：

- 启动前先读 `.claude/rules/workflow-routing.md`（Codex 为 `.codex/rules/workflow-routing.md`），匹配触发词；
- 已有同名运行则续跑，不重复创建；
- 阶段状态只能用 `.claude/scripts/todo-state.sh`（Codex 为 `.codex/scripts/todo-state.sh`）修改；
- 报告完成前必须运行 `todo-state.sh <state-file> validate`，校验失败不得收尾。

作文批改不建状态文件；若批量批改成为常态，再升级为工作流。

## 校验

每次修改共享技能、规则或笔记目录后运行：

```bash
bash scripts/verify-vault.sh
```

它会依次检查：

- 阅读中间产物、最终笔记、所在年份目录和 YAML `topic` 是否一致；
- Codex 与 Claude Code 的共享技能语义是否一致（平台专属 frontmatter 除外）；
- 两套工作流路由与环境变量模板规则是否有效。

发布级完整性检查使用 `bash scripts/verify-vault.sh --strict`。学习中或暂不完整的篇章可在 `intermediate/<topic>/STATUS.md` 声明 `status: in_progress`：普通校验只提示，严格校验仍视为未完成。

> [!note] 当前校验范围
> `scripts/verify-vault.py` 目前只校验 `20xx阅读/` 下的阅读笔记；`完形填空/` 与 `作文/` 的产物尚未纳入结构校验。

## 多 Agent 支持范围

项目共享技能共 24 项，`.claude/skills/` 与 `.agents/skills/` 同名部分通过 `sync_platform_skills.py` 守护语义一致（`.claude/skills/` 另含本机专属技能）。CodeBuddy 提供其中 21 项核心学习技能，不含 `generate-reading-note`、`generate-cloze-note`、`grade-essay`。系统维护、工作流与安全审计能力以 Codex / Claude Code 为准。详见 [AGENTS.md](AGENTS.md)、[CLAUDE.md](CLAUDE.md) 与 [CODEBUDDY.md](CODEBUDDY.md)。

## 相关文档

- [使用说明](使用说明.md)：分步骤操作与可直接复制的指令。
- [AGENTS.md](AGENTS.md)：完整项目规则、技能协作与同步约定。
- [docs/superpowers/specs/](docs/superpowers/specs/)：阅读笔记工作流的设计文档。
