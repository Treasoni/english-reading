---
name: compile-note
description: 将翻译、排版文章和语法笔记整合为一份全面的综合学习笔记，遵循AI实战参考模板格式，包含背景、原文、翻译、语法、心得、延伸、思考题等完整章节。用户指定输出路径。
---

# 笔记整合技能 (compile-note)

接收技能 1-3 的三个中间文件，整合为一份自包含的综合考研英语学习笔记。输出遵循 `C:\办公\Study-Notes\AI实战` 的笔记模板标准。

## 前置条件

- 技能 1-3 必须已执行完毕，三个中间文件已存在于 `intermediate/<topic>/` 下
- 用户需已决定最终笔记的存放位置
- 输出格式参考 `obsidian-markdown` 技能及其 reference 文件

## 输入

用户提供两项：

1. **主题名（topic）** — 与技能 1-3 使用的 topic 一致
2. **输出路径** — 完整文件路径，如 `C:\办公\Study-Notes\英语阅读\2024-text1-精读笔记.md`

技能自动从 `c:\code\english-reading\intermediate\<topic>\` 读取：
- `translation.md`
- `formatted-article.md`
- `grammar-notes.md`

## 工作流

### 步骤 1：验证输入

检查三个中间文件是否存在：
```
c:\code\english-reading\intermediate\<topic>\translation.md
c:\code\english-reading\intermediate\<topic>\formatted-article.md
c:\code\english-reading\intermediate\<topic>\grammar-notes.md
```
若任一文件缺失，向用户报告并提示先执行对应的技能。

### 步骤 2：提取并合并元数据

从三个源文件中读取 YAML frontmatter，提取：
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
related:
  - "[[translation]]"
  - "[[formatted-article]]"
  - "[[grammar-notes]]"
---
```

### 步骤 4：构建笔记主体

按以下章节组织（参考 AI实战 模板风格）：

1. **`# [文章标题] 精读笔记`** — 主标题

2. **`## 背景`** — 文章简介：
   - 主题背景和上下文
   - 为什么选择这篇文章
   - 文章来源和难度说明

3. **`## 文章原文`** — 格式化后的英文原文（来自 Skill 2）：
   - 用 `![[wikilink]]` 嵌入（如 `![[formatted-article]]`）
   - 或直接包含内容（若用户偏好自包含笔记）
   - 默认使用嵌入方式保持 Obsidian 链接实时性

4. **`## 翻译对照`** — 中英对照翻译（来自 Skill 1）：
   - 同样用 `![[translation]]` 嵌入或直接包含

5. **`## 语法要点`** — 结构化语法笔记（来自 Skill 3）：
   - 用 `![[grammar-notes]]` 嵌入或直接包含

6. **`<!-- VOCABULARY_SLOT -->`** — 生词表占位符：
   - 必须是 HTML 注释格式，供 Skill 5 定位和替换
   - 不要在这行前后添加任何其他内容

7. **`## 心得`** — 学习心得：
   - AI 根据文章内容和考研命题特点生成初步心得
   - 可用 `> [!tip]` 标记解题技巧
   - 可用 `> [!warning]` 标记易错点
   - 可用 `> [!question]` 提出反思问题

8. **`## 延伸`** — 拓展内容：
   - 相关主题推荐
   - 后续文章建议
   - 补充学习资源
   - 用 `[[wikilinks]]` 链接到其他笔记

9. **`## 思考题`** — 考研风格练习题：
   - 3-5 道基于文章的理解/分析题
   - 模拟考研命题风格（主旨题、细节题、推断题、词义题）

10. **`## 相关笔记`** — 笔记库内的关联链接：
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
- 验证：总字数、章节数、嵌入数
- 向用户报告完整路径

### 步骤 7：自我学习（可选）

检查 `c:\code\english-reading\.learnings\` 目录。若存在且有值得记录的整合问题或改进，追加到 `LEARNINGS.md`。

## 关键设计决策

- **嵌入 vs 包含**：默认使用 `![[wikilink]]` 嵌入源文件。若用户希望笔记自包含（不依赖外部文件），改为直接包含内容。
- **`<!-- VOCABULARY_SLOT -->`**：HTML 注释不会被 Obsidian 显示，但 Skill 5 可以准确定位插入位置。
- **遵循格式参考**：章节命名和结构对标 `C:\办公\Study-Notes\AI实战` 下的笔记标准（背景、心得、延伸、思考题）。

## 输出格式

完整示例参见 `references/STUDY_NOTE_TEMPLATE.md`。

## 约束

- 不得删除或修改三个中间文件——它们作为独立参考保留
- 笔记中的源内容通过 `![[wikilink]]` 引用或直接包含，二选一；默认选嵌入
- `<!-- VOCABULARY_SLOT -->` 占位符必须精确放置，供 Skill 5 替换

## 相关技能

此技能是考研英语阅读精讲工作流的第四步：
- `translate` — 产出翻译文件（前置）
- `format-article` — 产出排版文件（前置）
- `organize-grammar` — 产出语法文件（前置）
- `extract-vocabulary` — 从本笔记提取生词（后续）

## 输出格式参考

生成的笔记遵循 Obsidian Flavored Markdown，参考：
- `obsidian-markdown` — 完整语法
- `obsidian-markdown/references/PROPERTIES.md` — 属性类型
- `obsidian-markdown/references/CALLOUTS.md` — callout 类型
- `C:\办公\Study-Notes\AI实战` — 笔记模板参考标准
