# 批量考研阅读笔记生成工作流设计

## 背景

单篇 `reading-note-generation` 工作流已经可以把一篇英文阅读文章处理成完整精读笔记。处理大量英语笔记时，瓶颈不在单篇步骤定义，而在批次调度、并发边界、人工确认关口和全局文件写入冲突。

本设计新增批量工作流 `reading-note-batch-generation`，并扩展 `generate-reading-note` 入口 skill。批量工作流不替代单篇流程，而是为每篇文章创建或恢复独立的单篇 workflow run，并用 fork subagent 处理互不依赖的分析任务。主 agent 保留确认、写入、整合和全局更新的控制权。

## 目标

- 支持用户一次提供多个英文阅读文件或一个待处理目录。
- 为每篇文章创建独立单篇 run，批量 run 只负责调度与收口。
- 明确 fork subagent 可用步骤和禁止并发写入步骤。
- 限制并发数量，默认每轮 3 篇，最高 5 篇。
- 长难句候选可以并行生成，但确认和插入必须串行。
- 全局笔记更新必须串行，避免 `语法总结笔记.md`、`固定搭配与词组笔记.md` 等共享文件冲突。
- Codex 与 Claude Code 两侧保持同等语义。

## 非目标

- 不实现无需用户确认的全自动长难句插入。
- 不让多个 subagent 同时编辑同一篇文章或同一个最终笔记。
- 不把单篇 workflow 的 P0-P8 逻辑复制成另一套独立流程。
- 不新增批量处理脚本；先用 workflow 和 skill 文档约束 agent 行为。

## 入口行为

`generate-reading-note` 根据用户请求选择模式：

- 单篇请求：使用 `reading-note-generation`。
- 批量请求：使用 `reading-note-batch-generation`。

批量触发词包括：

- 批量生成考研阅读笔记
- 处理大量英语笔记
- 处理一个目录里的阅读文章
- batch reading notes
- 多篇精读笔记

## 批量状态文件

批量状态文件：

```text
workspace/workflow-runs/reading-note-batch-{batch_id}.workflow.md
```

批量状态文件记录：

- 输入来源目录或文件清单
- 默认输出根目录
- 并发上限
- 每篇文章的 year、passage、topic、source、single-run state file
- 每篇文章的状态：queued、in_progress、needs_confirmation、blocked、complete
- fork subagent 的任务分配和报告路径

## 阶段设计

### P0 批量输入与状态初始化

- 读取经验库与 workflow routing。
- 收集目录或文件清单。
- 让用户确认并发上限，默认 3，最高 5。
- 创建或恢复批量状态文件。

### P1 清单盘点

- 可以使用 fork subagent 只读扫描不同文件组。
- 每个 subagent 输出标准清单：source、year、passage、topic、建议 intermediate 目录、建议输出路径。
- 主 agent 合并清单并消重。

### P2 单篇 run 初始化

- 主 agent 为每篇文章创建或恢复 `reading-note-generation` 单篇状态文件。
- 不使用 subagent 写状态文件，避免重复创建或命名漂移。

### P3 独立内容生成

适合 fork subagent 并行：

- P1 排版草稿生成或检查。
- P2 翻译。
- P3 语法点抽取和整理草稿。
- P4 长难句候选生成。

约束：

- 每个 subagent 只处理一个 topic 目录或一个只读文件组。
- 每个 subagent 必须写报告到对应 topic 目录或批量状态指定的报告路径。
- subagent 不更新共享汇总文件。

### P4 人工确认关口

- 主 agent 汇总每篇文章的长难句候选。
- 用户按篇确认、增删或暂跳过。
- 未确认的文章停在 needs_confirmation，不进入插入阶段。

### P5 串行写入与整合

必须由主 agent 串行执行：

- P5 长难句分析与插入。
- P6 综合笔记整合。
- P7 生词表与练习。

原因：

- 长难句插入需要遵守“原句 → 分析块”逐句分布铁律。
- 最终笔记同一文件不能多 agent 并发写。
- 生词表替换必须只改目标区域。

### P6 批量 QA

适合 fork reviewer 并行：

- 每篇最终笔记一个 reviewer。
- 检查 YAML、标题、表格空行、词汇占位符、长难句位置、练习题完整性。

主 agent 汇总 reviewer 报告并串行修复。

### P7 全局汇总更新

必须串行：

- `语法总结笔记.md`
- `固定搭配与词组笔记.md`
- `阅读心得.md`
- `单词辨析.md`

如果用户没有要求更新全局汇总，批量工作流只报告建议，不自动改全局文件。

### P8 收尾

- 检查每篇单篇 run 状态。
- 汇总完成、阻塞、跳过清单。
- 报告最终输出路径。

## subagent 分工规则

适合 fork subagent：

- 只读扫描和清单盘点。
- 单篇翻译、语法草稿、候选长难句。
- 单篇最终 QA。

不适合 fork subagent 直接写：

- 批量状态文件。
- 同一篇 `formatted-article.md` 的长难句插入。
- 同一篇最终精读笔记。
- 全局汇总笔记。

并发规则：

- 默认 3 个 fork subagent。
- 最高 5 个 fork subagent。
- 每个 subagent 必须有不重叠写入范围。
- 主 agent 必须审查 subagent 报告后再进入写入或合并。

## 验收标准

- 新增 Codex 和 Claude Code 两侧 `reading-note-batch-generation` workflow。
- `generate-reading-note` 能清楚区分单篇和批量模式。
- routing 表包含单篇与批量两个 workflow。
- 批量 workflow 明确 subagent 可用和禁用步骤。
- 状态模板可被 `todo-state.sh` 推进。
- skill 双平台同步检查通过。
- 表格前保留空行，标题格式合法。
