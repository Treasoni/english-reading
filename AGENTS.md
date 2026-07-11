# 考研英语阅读精读 Vault

考研英语阅读理解精读笔记库。支持 Claude Code（通过 Claudian 插件）和 Codex 并行使用，进行翻译、语法分析、长难句拆解和综合笔记整理。

## 多 Agent 兼容说明

- **共享规则入口**：`AGENTS.md` 是 Codex 的项目规则入口；`CLAUDE.md` 通过 `@AGENTS.md` 引用同一套规则，避免两份规则漂移。
- **Claude Code 配置保持原样**：`.claude/` 目录保留给 Claude Code 使用，不为 Codex 修改其中配置。
- **平台目录隔离**：Codex 架构、Hook、技能适配只修改 `.agents/` 与 `.codex/`；不得用 Codex 版本覆盖 `.claude/`，避免 Claude Code 专属功能丢失。
- **技能语义同步**：`.agents/skills/` 与 `.claude/skills/` 尽量保持同名技能和学习流程一致，但实现细节允许平台差异。
- **Codex 经验库 Hook**：Codex 专用配置放在 `.codex/`，通过 `.codex/hooks.json` 调用 `.codex/hooks/read-learnings.sh`，读取 `.learnings/` 中的经验库。
- **同步原则**：新增或更新通用学习规则时，可分别更新两套技能的对应语义；更新 Codex 架构或 Codex 专用能力时，只改 `.agents/` / `.codex/`。同步前必须先比对两边差异，保留 Claude Code 专属命令、Hook、工具说明和平台限制。

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
├── .claude/skills/                        # Claude Code 技能定义
├── .agents/skills/                        # Codex 技能定义
└── .codex/                                # Codex 专用 hook / 配置说明
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
