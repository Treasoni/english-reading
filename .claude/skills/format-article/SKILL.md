---
name: format-article
description: 对英文文章进行美化排版，清理原始格式，添加正确的标题层级、段落分隔和列表结构，输出为规范的Obsidian Markdown格式，保存到 intermediate 目录。用户提供原始英文文章和主题名时触发。
---

# 文章排版技能 (format-article)

将原始/未格式化的英文文章转换为干净、结构化的 Obsidian Markdown，保留原文内容不变，仅改善排版和可读性。

## 前置条件

输出遵循 Obsidian Flavored Markdown 规范。参考：
- `obsidian-markdown` 技能 — 完整语法参考
- `obsidian-markdown/references/PROPERTIES.md` — frontmatter 属性类型

## 输入

用户提供两项：

1. **原始英文文章** — 两种方式：
   - 直接在消息中粘贴文本
   - 提供文件路径，技能用 Read 工具读取
2. **主题名（topic）** — 如 `2024-text1-ai`

## 工作流

### 步骤 1：读取输入

- 从粘贴文本或文件路径读取原文
- 确认文本不为空

### 步骤 2：清理和标准化

- 合并连续空行（3+ 个空行 → 1 个空行）
- 标准化换行为 Unix 风格 `\n`
- 去除行首/行尾空格
- 将 Tab 缩进转换为空格
- 修复断行（散文中不自然的换行）

### 步骤 3：检测结构

识别以下元素，推测原作者意图：
- **标题**：没有 `#` 标记但有标题特征的文字（全大写行、短行后跟空行、编号如 "I."、"Part 1" 等）
- **段落**：由空行分隔的文本块
- **列表**：以 `-`、`*`、`1.`、`a)` 等开头的行
- **引用**：缩进段落或以引号包裹的段落
- **强调词**：原文中用引号、斜体、大写等标记的重点词汇

### 步骤 4：应用 Obsidian Markdown 格式

- 为章节标题添加 `#`、`##`、`###` 前缀
- 确保段落间有且仅有一个空行
- 正确格式化嵌套列表（子项缩进 4 空格或 1 Tab）
- 将引用包裹在 `>` 语法中
- 用 `**粗体**` 标记关键术语（考研重点词汇）
- 用 `==高亮==` 标记文章中值得注意的表达

### 步骤 5：构建 YAML frontmatter

```yaml
---
title: "[文章标题]"
type: article
topic: "[用户提供的 topic]"
tags:
  - english-reading
  - formatted-article
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - "[来源名称，若能识别]"
---
```

### 步骤 6：保存并验证

- 输出路径：`c:\code\english-reading\intermediate\<topic>\formatted-article.md`
- 自动创建目录（如不存在）
- 写入文件后验证：
  - 总字数
  - 段落数
  - 标题数
- 向用户报告输出路径

### 步骤 7：自我学习（可选）

若执行中出现值得记录的模式（排版识别问题、结构检测改进等），检查 `c:\code\english-reading\.learnings\` 是否存在。若存在且有内容，追加到 `LEARNINGS.md`，格式同 translate 技能。

## 输出格式

示例参见 `references/ARTICLE_TEMPLATE.md`。

核心约定：
- 每段后一个空行
- 标题层级清晰（`#` → `##` → `###`）
- 列表缩进一致
- 关键术语用 `**粗体**` 标记

## 约束

- 不得改动文章内容或词汇——只改善排版
- 不得添加原文中不存在的章节、评论或分析
- 不得删除原文的任何部分

## 相关技能

此技能是考研英语阅读精讲工作流的第二步：
- `translate` — 翻译排版后的文章
- `organize-grammar` — 整理语法笔记
- `compile-note` — 整合为综合笔记
- `extract-vocabulary` — 提取生词表
