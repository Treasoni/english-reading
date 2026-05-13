---
name: organize-grammar
description: 整理零散的英语语法笔记，按类别（时态、语态、从句等）组织为结构化参考。使用Obsidian callouts突出关键点，使用表格展示语法模式，保存到 intermediate 目录。用户提供语法笔记和主题名时触发。
---

# 语法整理技能 (organize-grammar)

将零散、杂乱的语法笔记转化为结构化的语法参考，按标准语法类别组织，方便考研备考复习。

## 前置条件

输出遵循 Obsidian Flavored Markdown 规范。参考：
- `obsidian-markdown` 技能 — 完整语法
- `obsidian-markdown/references/CALLOUTS.md` — callout 类型（用于突出关键规则）
- `obsidian-markdown/references/PROPERTIES.md` — frontmatter 属性

## 输入

用户提供两项：

1. **语法笔记** — 两种方式：
   - 直接在消息中粘贴语法内容
   - 提供文件路径
2. **主题名（topic）** — 如 `2024-text1-ai`

## 工作流

### 步骤 1：读取输入

从粘贴文本或文件读取语法笔记。

### 步骤 2：分类语法点

分析输入，将语法点归入以下标准类别：

| 类别 | 包含内容 |
|------|---------|
| **时态 (Tenses)** | 一般现在/过去/将来、现在/过去/将来完成、进行时等 |
| **语态 (Voice)** | 主动/被动语态，特殊被动结构 |
| **非谓语动词 (Non-finite Verbs)** | 不定式、动名词、分词（现在分词/过去分词） |
| **从句 (Clauses)** | 定语从句、状语从句、名词性从句 |
| **虚拟语气 (Subjunctive Mood)** | 条件句、wish/if only、should 省略等 |
| **倒装与强调 (Inversion & Emphasis)** | 部分倒装、完全倒装、强调句 |
| **介词与连词 (Prepositions & Conjunctions)** | 常见搭配、长难句中的连词 |
| **固定搭配 (Fixed Collocations)** | 动词短语、习惯表达 |

若输入中的点不属于以上类别，创建「补充要点」章节收纳。

### 步骤 3：结构化每个语法类别

对每个类别：

1. **添加 `###` 标题**（类别的中英文名称）
2. **概述**：1-2 句简要说明该语法点
3. **使用 callout 突出关键规则**：
   - `> [!tip]` — 解题技巧、记忆方法
   - `> [!warning]` — 常见错误、易混淆点
   - `> [!note]` — 补充说明
4. **使用表格展示模式**：
   ```markdown
   | 结构 | 用法 | 例句 |
   |------|------|------|
   | [语法结构] | [何时使用] | [英文例句] |
   ```
5. 类别之间用 `---` 分隔

### 步骤 4：构建 YAML frontmatter

```yaml
---
title: "[主题] 语法整理"
type: grammar-reference
topic: "[用户提供的 topic]"
tags:
  - english-reading
  - grammar
  - reference
difficulty: intermediate
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - "[用户原始来源]"
concepts:
  - "[语法概念1]"
  - "[语法概念2]"
---
```

### 步骤 5：保存并验证

- 输出路径：`c:\code\english-reading\intermediate\<topic>\grammar-notes.md`
- 自动创建目录
- 验证：显示语法类别数和总条目数
- 向用户报告输出路径

### 步骤 6：自我学习（可选）

检查 `c:\code\english-reading\.learnings\`，若存在且有值得记录的分类或格式问题，追加到 `LEARNINGS.md`。

## 输出格式

示例参见 `references/GRAMMAR_TEMPLATE.md`。

核心约定：
- 每个语法类别使用 `###` 标题
- 规则用 callout 突出
- 模式用表格展示（结构 | 用法 | 例句）
- 类别间用 `---` 分隔
- 关键术语用 `**粗体**` 和 `==高亮==`

## 约束

- 不得引入原始笔记中不存在的语法规则
- 不得修改用户提供的例句——只重新组织排列
- 若语法点可用表格表达，优先使用表格而非长段落

## 相关技能

此技能是考研英语阅读精讲工作流的第三步：
- `translate` — 翻译文章
- `format-article` — 排版文章
- `compile-note` — 整合为综合笔记
- `extract-vocabulary` — 提取生词表
