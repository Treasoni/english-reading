---
name: organize-grammar
category: 学习工作流
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

用户提供：

1. **语法笔记** — 两种方式：
   - 直接在消息中粘贴语法内容
   - 提供文件路径

用户提供语法笔记后，技能询问目标文件夹路径。

## 工作流

### 步骤 1：读取输入

从粘贴文本或文件读取语法笔记。

### 步骤 1b：询问目标文件夹并检测合并模式

- 向用户询问："请提供 intermediate 下的目标文件夹路径（如 `intermediate/2000-passage1-america/`）："
- 从文件夹路径解析出 topic（取路径最后一段目录名）
- 用 Read 工具检查 `intermediate/<folder>/grammar-notes.md` 是否存在

**若文件已存在（合并模式）**：
- 读取已有 grammar-notes.md，解析结构：
  - 按 `###` 标题识别已有类别
  - 提取每个类别下的表格条目（结构 | 用法 | 例句 各列内容）
  - 提取已有 callout 规则说明
- 建立已有语法目录索引

**若文件不存在（新建模式）**：
- 继续执行以下步骤，创建目录和新文件

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

### 步骤 2b：合并新旧语法点（仅合并模式）

在合并模式下，对每个新输入的语法点：

- 检查该语法点所属类别是否在已有笔记中存在
  - **若类别已存在**：对比该类别下已有表格条目
    - 表格中已有相同结构+用法 → 跳过，不重复添加
    - 表格中无此条目 → 追加到该类别表格末尾
  - **若类别不存在**：创建新的 `###` 类别章节，按标准格式添加
- 已有条目的 Callout 规则说明保留不变；若有新的规则补充，追加新的 callout
- 保持已有条目的顺序不变，新增条目追加到末尾
- 判断重复的标准：核心语法结构模式和例句高度一致时视为重复

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

- 新建模式：
  - 输出路径：`intermediate/<folder>/grammar-notes.md`
  - 自动创建目录（用 Bash `mkdir -p`）
  - 写入完整文件
- 合并模式：
  - 将已有内容与新条目合并为完整文档
  - 保留原 YAML frontmatter 的 `created` 字段，更新 `updated` 字段
  - 合并 `concepts` 列表（去重）
  - 用 Write 工具写入原文件
- 验证：显示语法类别数和总条目数
- 向用户报告输出路径

### 步骤 5b：完整性核验（必须执行）

结构化完成或合并后，产出文件写入前，执行完整性核验：

1. **逐段比对源文件**：逐段读取源语法笔记的每个 `##` / 编号标题，检查其下的所有内容是否都体现在产出文件中：
   - 词源拆解（如 never the less → nevertheless）
   - 术语定义（如"暗含否定"、"部分否定"）
   - 逐词拆解（如 in one's own right）
   - 标点细节（如 whereas 前的逗号）
   - 感情色彩差异（如 nevertheless vs. nonetheless）
   - 实战场景与例句
2. **交叉引用检查**：检查相关语法点之间是否已建立联动复习引用（如 Nevertheless ↔ Whereas、暗含否定 ↔ Neither...nor...）
3. **漏缺处理**：若发现遗漏，在对应类别下补充完整，不丢失任何信息密度
4. **确认通过**：确认所有源内容已体现后，继续下一步

### 步骤 6：自我学习（可选）

检查 `.learnings/`，若存在且有值得记录的分类或格式问题，追加到 `LEARNINGS.md`。

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
- 合并模式下不得删除或修改已有语法点
- 新增语法点与已有条目重复时跳过不添加

## 相关技能

此技能是考研英语阅读精讲工作流的第三步：
- `translate` — 翻译文章
- `format-article` — 排版文章
- `compile-note` — 整合为综合笔记
- `extract-vocabulary` — 提取生词表
