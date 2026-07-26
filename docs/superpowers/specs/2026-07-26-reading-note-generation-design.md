# 考研阅读笔记生成工作流设计

## 背景

当前考研英语阅读精读流程依赖多个独立 skill：排版、翻译、语法整理、长难句分析、综合笔记整合、生词提取。用户需要手动决定下一步、重复提供路径，并在长难句分析阶段人工协调插入位置。

本设计新增一个可恢复的命名工作流和一个入口 skill，把这些步骤串成稳定流程。入口 skill 负责启动、收集必要输入、创建或恢复状态文件，并按阶段调用现有 skill。工作流保留关键人工判断：长难句由 AI 给出候选，用户确认后再分析并插入。

## 目标

- 用户用一个入口 skill 启动整篇考研阅读精读笔记生成。
- 工作流能中断后恢复，状态记录在 `workspace/workflow-runs/`。
- 复用现有 skill，不重写已有排版、翻译、语法、长难句、整合、生词提取逻辑。
- 减少重复询问路径：入口统一收集中间目录与最终输出路径。
- 长难句分析采用“AI 候选 + 用户确认”模式。
- 保持 Obsidian Markdown 规范和项目经验库铁律。
- 同步 Codex 与 Claude Code 两侧共享 skill 语义。

## 非目标

- 不开发批量处理多年真题的自动流水线。
- 不把长难句选择改成完全自动无确认。
- 不新增独立翻译或语法分析脚本。
- 不改变现有六个核心 skill 的输出格式。

## 用户入口

新增入口 skill：`generate-reading-note`。

触发方式包括：

- “生成考研阅读笔记”
- “启动精读工作流”
- “用 generate-reading-note 处理这篇文章”
- 用户粘贴英文文章并要求生成完整精读笔记

入口 skill 首次启动时收集：

- 英文文章文本或源文件路径
- 年份、passage 编号、topic slug
- 中间目录，默认 `intermediate/<year>-passage<n>-<topic>/`
- 最终笔记输出路径，必须由用户明确提供或确认
- 语法笔记输入；如果用户没有单独提供，则从文章中提炼语法整理输入

路径、文件名等自定义输入使用普通文本提问，不使用预设选项。

## 工作流结构

新增工作流目录：

```text
.codex/workflows/reading-note-generation/
  workflow.md
  state-template.md
  routing.yaml
```

状态文件保存到：

```text
workspace/workflow-runs/reading-note-{year}-passage{n}-{topic}.workflow.md
```

每个状态文件包含 YAML frontmatter、当前阶段行、每阶段唯一状态行，以及异常记录表。阶段状态只能通过 `.codex/scripts/todo-state.sh` 更新。

## 阶段设计

### P0 输入收集与状态初始化

- 读取 `.learnings/` 规则。
- 读取 `.codex/rules/workflow-routing.md`。
- 收集或确认文章、年份、passage、topic、中间目录、最终输出路径。
- 创建或恢复对应 workflow run。
- 记录用户选择：长难句模式为“AI 候选 + 用户确认”。

### P1 文章排版

- 调用 `format-article`。
- 生成或更新 `formatted-article.md`。
- 验证文章内容未被删改，标题、段落和 frontmatter 符合 Obsidian 规范。

### P2 中英翻译

- 调用 `translate`。
- 生成或更新 `translation.md`。
- 保持原文段落结构，不合并、不删减。

### P3 语法整理

- 调用 `organize-grammar`。
- 如果用户提供了语法笔记，则以该内容为输入。
- 如果没有提供，则从文章中提炼考研相关语法点作为输入。
- 生成或更新 `grammar-notes.md`。
- 执行逐段完整性核验，保留词源、术语、感情色彩、实战场景等教学细节。

### P4 长难句候选确认

- 从 `formatted-article.md` 中选出 5-10 个候选长难句。
- 按优先级说明候选原因：句法层级、从句嵌套、非谓语结构、插入成分、考研易错点。
- 询问用户确认要分析的句子，可接受用户增删。
- 用户确认前不进入插入分析。

### P5 长难句分析与内联插入

- 调用 `analyze-sentence` 分析用户确认的句子。
- 分析块插入到“文章原文”中对应句子后面。
- 同一段多个句子必须按“原句 → 对应分析块 → 下一句”交替分布。
- 每个分析块第一行必须包含 `> **原句**：完整英文原句`。
- callout 内表格前必须留空行。
- 插入后检查后续段落是否被截断或异常开头。

### P6 综合笔记整合

- 调用 `compile-note`。
- 使用用户确认的最终输出路径。
- 从 `formatted-article.md`、`translation.md`、`grammar-notes.md` 读取内容。
- 保留内联长难句分析在“文章原文”对应段落之后。
- 插入 `<!-- VOCABULARY_SLOT -->`，供下一阶段替换。

### P7 生词表与练习

- 调用 `extract-vocabulary`。
- 扫描综合笔记中的加粗词汇。
- 生成或更新 `## 生词表` 与 `### 生词练习`。
- 同时列出短语中的重要独立单词。

### P8 最终验证与收尾

- 检查关键产物是否存在：
  - `formatted-article.md`
  - `translation.md`
  - `grammar-notes.md`
  - 最终精读笔记
- 检查最终笔记不再包含 `<!-- VOCABULARY_SLOT -->`。
- 检查 Markdown 标题格式、YAML 简单结构、表格前空行。
- 将 workflow run 状态推进到完成。
- 向用户报告输出路径和完成情况。

## 路由规则

工作流 `reading-note-generation` 为 required workflow。

匹配场景：

- 用户要求生成考研阅读笔记。
- 用户要求启动精读流程。
- 用户要求从英文阅读文章产出完整学习笔记。
- 用户提到需要串联排版、翻译、语法、长难句、整合、生词提取。

排除场景：

- 用户只要求单步翻译。
- 用户只要求单句长难句分析。
- 用户只要求添加阅读技巧或维护单词辨析。
- 用户只询问已有文件内容，不要求修改或生成笔记。

## 文件与同步

新增 Codex 文件：

- `.codex/workflows/reading-note-generation/workflow.md`
- `.codex/workflows/reading-note-generation/state-template.md`
- `.codex/workflows/reading-note-generation/routing.yaml`
- `.agents/skills/generate-reading-note/SKILL.md`

新增 Claude Code 对应文件：

- `.claude/skills/generate-reading-note/SKILL.md`
- `.claude/skills/generate-reading-note/manifest.yaml`

更新路由：

- `.codex/rules/workflow-routing.md`
- `.claude/rules/workflow-routing.md`，如同步脚本或现有规则需要保持一致

新增或更新共享 skill 后，运行：

```bash
python3 .agents/skills/maintain-learnings/scripts/sync_platform_skills.py --root . --skill generate-reading-note
.codex/scripts/sync-workflow-routing.sh
.codex/scripts/sync-workflow-routing.sh --check
```

如同步检查发现 Claude 侧缺失功能，先补齐再结束。

## 错误处理

- 文章输入为空：阻塞 P0，要求用户补充文章或文件路径。
- 目标输出路径缺失：阻塞 P0 或 P6，必须用文本问题向用户确认。
- 中间文件缺失：返回对应阶段补做，不跳过。
- 用户未确认长难句：阻塞 P4，不自动进入 P5。
- 句子无法在原文中定位：报告具体句子前缀，等待用户指定处理方式。
- 词汇提取为 0：如实报告，提示检查加粗标记，不编造词汇。

## 验收标准

- 入口 skill 能清楚说明启动条件、输入收集、状态文件、阶段推进和恢复规则。
- Codex workflow 定义包含 P0-P8，并明确每阶段产出。
- `routing.yaml` 能被同步脚本写入 `.codex/rules/workflow-routing.md`。
- 新增共享 skill 在 `.agents` 与 `.claude` 两侧功能一致。
- 所有新增 Markdown 文件标题格式合法。
- 表格前有空行。
- 工作流不绕过用户确认长难句的关口。
