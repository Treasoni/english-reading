# 考研英语阅读精读 Vault

考研英语阅读理解精读笔记库。使用 Claude Code + Obsidian 进行翻译、语法分析、长难句拆解和综合笔记整理。

## 功能

六步精读流程，每步产出存入 `intermediate/<topic>/`：

| 步骤 | 技能 | 产出 | 说明 |
|------|------|------|------|
| 1 | `format-article` | `formatted-article.md` | 英文文章美化排版 |
| 2 | `translate` | `translation.md` | 逐段中英对照翻译 |
| 3 | `organize-grammar` | `grammar-notes.md` | 按语法类别整理笔记 |
| 4 | `analyze-sentence` | 内联到原文 | 长难句结构分析，插入可折叠 callout |
| 5 | `compile-note` | `<topic>-精读笔记.md` | 整合为综合学习笔记 |
| 6 | `extract-vocabulary` | 替换占位符 | 提取去重生词表 + 练习题 |

附加技能：
- `summarize-grammar` — 跨篇章语法总结，生成 `语法总结笔记.md`
- `digest` — 学习回顾，记录心得与错误到 `.learnings/`

## 目录结构

```
├── 2000阅读/                              # 2000 年真题精读笔记
│   ├── 2000-passage1-america-精读笔记.md
│   ├── 2000-passage2-精读笔记.md
│   ├── 2000-passage3-futurist-精读笔记.md
│   ├── 2000-passage4-japan-精读笔记.md
│   └── 2000-passage5-ambition-精读笔记.md
├── 2001阅读/                              # 2001 年真题精读笔记
│   ├── 2001-passage1-specialization-精读笔记.md
│   ├── 2001-passage2-digital-divide-精读笔记.md
│   ├── 2001-passage3-newspaper-credibility-精读笔记.md
│   └── 2001-passage4-merger-精读笔记.md
├── intermediate/                          # 中间产物
│   └── <year>-<passage>-<topic>/
│       ├── formatted-article.md
│       ├── translation.md
│       └── grammar-notes.md
├── 语法总结笔记.md                         # 跨篇章语法汇总
├── .learnings/                            # 学习经验库
│   ├── RULES.md                           # 铁律（最高优先级规则）
│   ├── LEARNINGS.md                       # 学习心得
│   └── ERRORS.md                          # 错误日志
└── .claude/skills/                        # 技能定义
```
