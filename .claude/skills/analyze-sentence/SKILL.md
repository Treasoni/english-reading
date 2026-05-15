---
name: analyze-sentence
description: 对考研英语文章中的长难句进行结构分析，提取主干、标记修饰成分、绘制结构图解、给出参考译文和考点提示。用户粘贴英文句子并指定主题名时触发。
---

# 长难句分析技能 (analyze-sentence)

对考研英语阅读中的长难句进行深度结构分析，拆解每个句子的语法层次，输出到 `intermediate/<topic>/sentence-analysis.md`，供 compile-note 技能整合。

## 前置条件

输出遵循 Obsidian Flavored Markdown 规范。参考：
- `obsidian-markdown` 技能 — 完整语法
- `obsidian-markdown/references/CALLOUTS.md` — callout 类型（用于考点提示）

## 输入

用户提供两项：

1. **英文句子** — 从文章中选取的 1-5 个长难句：
   - 直接在消息中粘贴句子（每句一行或空行分隔）
   - 或提供文件路径
2. **主题名（topic）** — 与技能 1-3 使用的 topic 一致

## 工作流

### 步骤 1：读取输入

- 从粘贴文本或文件读取句子
- 按空行或编号识别每个独立句子
- 确认句子数量和内容

### 步骤 2：逐句分析

对每个句子执行以下分析：

#### 2a. 句子原文
展示完整英文句子，用 `>` 引用块包裹。

#### 2b. 主干提取
找出主句的核心结构（SVOCA）：
- **S (Subject)**：主语
- **V (Verb/Predicate)**：谓语动词
- **O (Object)**：宾语
- **C (Complement)**：补语
- **A (Adverbial)**：状语（仅主句级别）

去除所有修饰成分后，展示主句的简化版本。

#### 2c. 修饰成分分析
逐一标记所有修饰成分：

| 修饰类型 | 示例引导词 | 缩写标记 |
|---------|-----------|---------|
| 定语从句 | that, which, who, whom, whose, when, where, why | 定从 |
| 状语从句 | although, because, if, when, while, unless, so that | 状从 |
| 名词性从句 | that, what, whether, whoever | 名从 |
| 非谓语短语 | V-ing, V-ed, to V | 非谓语 |
| 介词短语 | in, of, with, by, for, from, to | 介短 |
| 同位语 | that, 破折号, 逗号 | 同位 |

#### 2d. 结构图解
用树形缩进展示句子层次关系：

```
主句: [主语 + 谓语 + 宾语]
  ├── 定从: (that ...) → 修饰 [先行词]
  │     └── 介短: (in ...) → 修饰定从中的[名词]
  ├── 状从: (Although ...) → 让步状语
  │     └── 非谓语: (V-ing ...) → 伴随
  └── 非谓语: (to V ...) → 目的状语
```

#### 2e. 参考译文
给出符合考研翻译"信达雅"标准的中文译文。

#### 2f. 考点提示
用 `> [!tip]` callout 标注考研真题中常考的语法点：
- 定语从句的省略与分隔
- 虚拟语气的倒装
- 强调句型
- 名词性从句的识别
- 非谓语动词的逻辑主语判断
- 省略与替代

### 步骤 3：构建 YAML frontmatter

```yaml
---
title: "[主题] 长难句分析"
type: sentence-analysis
topic: "[用户提供的 topic]"
tags:
  - english-reading
  - sentence-analysis
  - complex-sentences
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - "[文章来源]"
concepts:
  - "[涉及的语法概念]"
---
```

### 步骤 4：保存并验证

- 输出路径：`c:\code\english-reading\intermediate\<topic>\sentence-analysis.md`
- 自动创建目录
- 验证：句子数量、分析完整度
- 向用户报告输出路径

### 步骤 5：自我学习（可选）

若执行中出现值得记录的分析难点或格式改进，检查 `c:\code\english-reading\.learnings\` 目录。若存在，追加到 `LEARNINGS.md`。

## 输出格式

完整示例参见 `references/SENTENCE_ANALYSIS_TEMPLATE.md`。

核心约定：
- 每个句子用 `### 句子 N` 标题
- 原文用 `>` 引用块
- 主干提取分项列出（主句 + 从句）
- 结构图解用 ASCII 树形缩进（`├──` `└──` `│`）
- 参考译文单独一段
- 考点提示用 `> [!tip]` 或 `> [!warning]`

## 约束

- 只分析用户提供的句子，不自行从文章中选取
- 结构图解必须清晰展示层次关系，不可省略修饰成分
- 考点提示需对应考研真题的实际考点类型，不可泛泛而谈
- 每个句子的分析需完整（六要素缺一不可：原文、主干、修饰、图解、译文、考点）

## 相关技能

此技能是考研英语阅读精讲工作流的第六步（中间产出）：
- `translate` — 翻译文章
- `format-article` — 排版文章
- `organize-grammar` — 整理语法笔记
- `compile-note` — 整合笔记（使用本技能产出）
- `extract-vocabulary` — 提取生词表
