---
name: translate
description: 将考研英语阅读文章翻译为中文，按段落生成中英对照格式，保存到 intermediate 目录。用户粘贴英文文本或提供文件路径，并指定主题名(topic)时触发。
---

# 翻译技能 (translate)

将英文阅读文章逐段翻译为中文，生成中英对照的 Obsidian 笔记，保存在 `intermediate/<topic>/translation.md`。

## 前置条件

本技能生成的笔记遵循 Obsidian Flavored Markdown 规范。输出格式参考：
- `obsidian-markdown` 技能 — 完整 Obsidian 语法（wikilinks、callouts、properties、embeds）
- `obsidian-markdown` 的 `references/PROPERTIES.md` — YAML frontmatter 属性类型
- `obsidian-markdown` 的 `references/CALLOUTS.md` — callout 类型

## 输入

用户提供两项：

1. **英文文章** — 两种方式任选其一：
   - 直接在消息中粘贴英文文本
   - 提供文件路径（如 `C:\Users\xxx\article.txt`），技能用 Read 工具读取
2. **主题名（topic）** — 用于生成输出路径，如 `2024-text1-ai`

## 工作流

### 步骤 1：读取输入

- 若用户粘贴文本，直接使用
- 若用户提供文件路径，用 Read 工具读取文件内容
- 识别文章的语言和大致长度

### 步骤 2：分析结构

识别原文的层次结构：
- 标题（`#`、`##` 层级）
- 段落边界（空行分隔）
- 列表、引用、代码块
- 保持原文的章节结构不变

### 步骤 3：逐段翻译

对每个段落/句子：
- 保留原文段落
- 在其下方添加中文翻译（用空行分隔）
- 标题保留原文，附加中文翻译，如：`## The Challenges of Standardized Testing 标准化考试的挑战`
- 对长难句，在翻译后可附加 `> [!note]` 简要解析翻译难点

### 步骤 4：构建 YAML frontmatter

```yaml
---
title: "[文章标题] 中英对照翻译"
type: translation
topic: "[用户提供的 topic]"
tags:
  - english-reading
  - translation
  - bilingual
difficulty: intermediate
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - "[文章来源，若能识别]"
---
```

### 步骤 5：写入输出文件

- 输出路径：`c:\code\english-reading\intermediate\<topic>\translation.md`
- 如果 `intermediate/<topic>/` 目录不存在，先创建（用 Bash `mkdir -p`）
- 写入双语笔记内容（frontmatter + 正文）
- 向用户报告输出路径和段落数

### 步骤 6：验证

- 确认文件已保存
- 显示段落计数和文件大小
- 提示用户检查翻译质量

### 步骤 7：自我学习（可选）

执行中若出现值得记录的问题（翻译选择、格式问题、输出改进点等），检查 `c:\code\english-reading\.learnings\` 是否存在。若存在且有意义，追加到 `LEARNINGS.md`：

```
## [LRN-YYYYMMDD-XXX] translate
**Priority**: low | medium | high
**Area**: translate

### Summary
单行简述

### Details
具体问题和建议
---
```

无有意义内容则跳过。

## 输出格式

文件结构参见 `references/TRANSLATION_TEMPLATE.md`。

核心格式约定：
- 每个原文段落后紧跟中文翻译
- 段落间用空行分隔
- 用 `> [!note]` 标注翻译说明（惯用语、文化背景等）
- 保留原文完整内容，不删减

## 约束

- 不得删除原文内容——必须保留完整原文供对照学习
- 不得合并段落——保持与原文相同的段落结构
- 不得添加原文中不存在的解释性内容（翻译说明除外，放在 `> [!note]` 中）

## 相关技能

此技能是考研英语阅读精讲工作流的第一步：
- `format-article` — 排版原始英文文章
- `organize-grammar` — 整理语法笔记
- `compile-note` — 将翻译、文章、语法整合为综合笔记
- `extract-vocabulary` — 从整合笔记中提取生词表
