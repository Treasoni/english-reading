---
name: compile-note
description: 将翻译、排版文章、语法笔记和长难句分析整合为一份全面的综合学习笔记，遵循AI实战参考模板格式，包含背景、原文、翻译、长难句分析、语法、心得、延伸、思考题等完整章节。用户指定输出路径。
---

# 笔记整合技能 (compile-note)

接收技能 1-3、6 的四个中间文件，整合为一份自包含的综合考研英语学习笔记。输出遵循 `C:\办公\Study-Notes\AI实战` 的笔记模板标准。

## 前置条件

- 用户需准备好 `intermediate/` 下的一个文件夹路径，内含已完成的前置技能产出文件
- 用户需已决定最终笔记的存放位置
- 输出格式参考 `obsidian-markdown` 技能及其 reference 文件

## 输入

用户提供两项：

1. **资料文件夹路径** — `intermediate/` 下的文件夹路径（如 `intermediate/2000-passage1-america/`），技能自动从该文件夹读取以下文件：
   - `formatted-article.md`
   - `translation.md`
   - `grammar-notes.md`
   - `sentence-analysis.md`
2. **输出路径** — 完整文件路径，如 `C:\办公\Study-Notes\英语阅读\2024-text1-精读笔记.md`

## 工作流

### 步骤 1：收集源文件

- 向用户询问："请提供 intermediate 下的资料文件夹路径（如 `intermediate/2000-passage1-america/`）："
- 用户提供路径后，用 Bash `ls` 列出该文件夹内容
- 用 Read 工具依次读取四个文件：
  - `intermediate/<folder>/formatted-article.md`
  - `intermediate/<folder>/translation.md`
  - `intermediate/<folder>/grammar-notes.md`
  - `intermediate/<folder>/sentence-analysis.md`
- 若 formatted-article、translation、grammar-notes 任一缺失，报告并提示先执行对应技能
- 若 sentence-analysis.md 缺失，在笔记中保留占位提示，不阻断整合
- 向用户确认已读取的文件列表

### 步骤 2：提取并合并元数据

从四个源文件中读取 YAML frontmatter，提取：
- 标题、主题、标签、来源
- 统一构建合并后的 frontmatter

### 步骤 3：构建 YAML frontmatter

```yaml
---
title: "[主题] 英语精读笔记"
type: study-note
topic: "[从源文件提取]"
tags:
  - english-reading
  - intensive-reading
  - study-note
  - exam-prep
difficulty: intermediate
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - "[从源文件合并]"
---
```

### 步骤 4：构建笔记主体

按以下章节组织（参考 AI实战 模板风格）：

1. **`# [文章标题] 精读笔记`** — 主标题

2. **`## 背景`** — 文章简介：
   - 主题背景和上下文
   - 为什么选择这篇文章
   - 文章来源和难度说明

3. **`## 文章原文`** — 格式化后的英文原文（来自 format-article）：
   - 从 formatted-article.md 中读取正文内容，**直接插入到当前笔记中**
   - 去除源文件的 YAML frontmatter（第一个 `---` 到第二个 `---` 之间），只保留正文
   - 保留原文的所有格式（标题、粗体、高亮、引用等）
   - **长难句分析 callout 保留在原位**：若 formatted-article.md 中包含 `> [!abstract]- 长难句分析` callout（由 analyze-sentence 插入），保持其在对应段落之后的位置，**不要**将其移出或汇总到其他章节

4. **`## 翻译对照`** — 中英对照翻译（来自 translate）：
   - 从 translation.md 中读取内容，去 frontmatter 后直接插入
   - 保留中英对照格式和 `> [!note]` 翻译说明
   - 若文件中包含行内 `> [!abstract]- 长难句分析` callout（由 analyze-sentence 技能插入），保留在原位

5. **`## 长难句分析`** — 句子结构分析（仅 sentence-analysis.md 独立内容）：
   - **不在此章节汇总 callout**：formatted-article.md 或 translation.md 中的内联 callout 已保留在各自章节中，不在本处重复
   - 若 sentence-analysis.md 存在且包含 formatted-article.md 中未涉及的补充分析内容：读取后插入本章节
   - 若 sentence-analysis.md 存在但其内容已全部内联在 formatted-article.md 中：跳过本条目，不在笔记中创建此章节
   - 若 sentence-analysis.md 不存在且原文/翻译中无 callout：输出占位提示 `> [!note] 提示：使用 /analyze-sentence 添加长难句分析内容`

6. **`## 语法要点`** — 结构化语法笔记（来自 organize-grammar）：
   - 从 grammar-notes.md 中读取内容，去 frontmatter 后直接插入
   - 保留所有 callout、表格和分类结构

7. **`<!-- VOCABULARY_SLOT -->`** — 生词表占位符：
   - 必须是 HTML 注释格式，供 Skill 5 定位和替换
   - 不要在这行前后添加任何其他内容

8. **`## 心得`** — 学习心得：
   - AI 根据文章内容和考研命题特点生成初步心得
   - 可用 `> [!tip]` 标记解题技巧
   - 可用 `> [!warning]` 标记易错点
   - 可用 `> [!question]` 提出反思问题

9. **`## 延伸`** — 拓展内容：
   - 相关主题推荐
   - 后续文章建议
   - 补充学习资源
   - 用 `[[wikilinks]]` 链接到其他笔记

10. **`## 思考题`** — 考研风格练习题：
    - 3-5 道基于文章的理解/分析题
    - 模拟考研命题风格（主旨题、细节题、推断题、词义题）

11. **`## 相关笔记`** — 笔记库内的关联链接：
    - 用 `[[wikilinks]]` 指向相关笔记

### 步骤 5：应用格式美化

- 关键术语用 `**粗体**`
- 重点内容用 `==高亮==`
- 技巧/注意用 `> [!tip]` / `> [!warning]` / `> [!note]` / `> [!abstract]`
- 对比分析用表格
- 关系展示用 Mermaid 图（如文章论证结构）
- 跨笔记引用用 `[[wikilinks]]`
- 章节间用 `---` 分隔（参考 AI实战 风格）

### 步骤 6：保存并验证

- 写入用户指定的输出路径
- 自动创建父目录（如不存在）
- 验证：总字数、章节数
- 向用户报告完整路径

### 步骤 7：记录候选学习条目（不落盘）

若出现值得记录的整合问题或改进，仅在会话内记下候选条目，**不要中途写入 `.learnings/`**。学习心得统一由 `digest` 技能在用户明确要求时整理落盘，避免中途修改每次会话强制加载的经验库文件而破坏提示缓存前缀。

## 关键设计决策

- **直接包含源内容**：所有源文件内容直接嵌入到最终笔记中，不使用 `![[wikilink]]`。笔记完全自包含，不依赖外部文件的 Obsidian 链接解析。读取源文件后去除 YAML frontmatter，仅保留正文。
- **`<!-- VOCABULARY_SLOT -->`**：HTML 注释不会被 Obsidian 显示，但 Skill 5 可以准确定位插入位置。
- **长难句分析保持内联**：formatted-article.md 或 translation.md 中的 `> [!abstract]-` callout 保留在原位（文章原文 / 翻译对照章节），不单独汇总到长难句分析章节。
- **遵循格式参考**：章节命名和结构对标 `C:\办公\Study-Notes\AI实战` 下的笔记标准（背景、心得、延伸、思考题）。

## 输出格式

完整示例参见 `references/STUDY_NOTE_TEMPLATE.md`。

## 约束

- 不得删除或修改源文件——它们作为独立参考保留
- 笔记中的源内容直接包含，不依赖 Obsidian wikilink 嵌入机制
- 读取源文件时去除 YAML frontmatter，只取正文内容
- `<!-- VOCABULARY_SLOT -->` 占位符必须精确放置，供 Skill 5 替换
- 若 `sentence-analysis.md` 不存在，不阻断整合，但在 `## 长难句分析` 章节给出占位提示

## 相关技能

此技能是考研英语阅读精讲工作流的第四步：
- `translate` — 产出翻译文件（前置）
- `format-article` — 产出排版文件（前置）
- `organize-grammar` — 产出语法文件（前置）
- `analyze-sentence` — 产出长难句分析文件（前置）
- `extract-vocabulary` — 从本笔记提取生词（后续）

## 输出格式参考

生成的笔记遵循 Obsidian Flavored Markdown，参考：
- `obsidian-markdown` — 完整语法
- `obsidian-markdown/references/PROPERTIES.md` — 属性类型
- `obsidian-markdown/references/CALLOUTS.md` — callout 类型
- `C:\办公\Study-Notes\AI实战` — 笔记模板参考标准
