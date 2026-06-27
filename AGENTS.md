# 考研英语阅读精读 Vault

考研英语阅读理解精读笔记库。使用 Claude Code（通过 Claudian 插件）进行翻译、语法分析、长难句拆解和综合笔记整理。

## 核心行为准则

1. **强制读取经验库**：在执行任何任务之前，你必须首先静默读取以下文件：
   - `.learnings/RULES.md`（如存在）— 提炼后的铁律
   - `.learnings/LEARNINGS.md`（如存在）— 学习心得与错误记录
   - `.learnings/ERRORS.md`（如存在）— 错误日志

2. **严格遵循经验**：这些文件记录了你在以往任务中犯过的错误和用户的纠正。将这些记录作为**最高优先级的规则**，绝对避免在本次任务中重蹈覆辙。

3. **经验记录风格**：提炼为简洁规则（如"用 X 而非 Y"），而非叙述故事。消耗最少 Token，获得最大效果。

## 学习工作流（六步精读流程）

按顺序执行，每步产出存入 `intermediate/<topic>/`：

| 步骤 | 技能 | 产出文件 | 说明 |
|------|------|----------|------|
| 1 | `format-article` | `formatted-article.md` | 格式化原始英文文章 |
| 2 | `translate` | `translation.md` | 中英对照段落翻译 |
| 3 | `organize-grammar` | `grammar-notes.md` | 按类别整理语法笔记 |
| 4 | `analyze-sentence` | （内联到原文） | 长难句结构分析，插入 `[!abstract]-` 可折叠 callout |
| 5 | `compile-note` | 根目录 `<topic>-精读笔记.md` | 整合为综合学习笔记 |
| 6 | `extract-vocabulary` | 替换 `<!-- VOCABULARY_SLOT -->` | 提取去重词汇表 |

附加：`digest` — 学习回顾，记录心得与错误到 `.learnings/`（用户明确要求时触发）

## 目录结构

```
├── <year>-<passage>-<topic>-精读笔记.md   # 最终综合笔记
├── intermediate/
│   └── <topic>/
│       ├── formatted-article.md           # 格式化原文
│       ├── translation.md                 # 中英对照翻译
│       └── grammar-notes.md               # 语法笔记
├── .learnings/
│   ├── LEARNINGS.md                       # 学习心得
│   ├── ERRORS.md                          # 错误日志
│   └── RULES.md                           # 提炼后的铁律（自动生成）
└── .claude/skills/                        # 技能定义
```

## 文件命名约定

- 最终笔记：`<year>-<passage>-<topic>-精读笔记.md`（如 `2000-passage1-america-精读笔记.md`）
- 中间文件目录：`intermediate/<year>-<passage>-<topic>/`
- 词汇占位符：笔记中的 `<!-- VOCABULARY_SLOT -->` 由 `extract-vocabulary` 替换

## Obsidian Markdown 规范

- 使用 YAML frontmatter（title, type, topic, tags, difficulty, created, updated, sources）
- 长难句分析使用 `> [!abstract]-` 可折叠 callout
- 语法要点使用 `> [!tip]`、`> [!warning]`、`> [!note]` callout
- 使用 `[[wikilink]]` 链接相关笔记
- 支持 LaTeX 数学公式和 Mermaid 图表
