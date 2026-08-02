---
name: summarize-grammar
description: 读取 intermediate 下所有 grammar-notes.md，按语法类别（从句、非谓语动词等）去重合并，生成跨篇章的综合语法总结笔记。支持增量更新——新增篇章语法笔记后重新运行自动合并，不重复已有内容。用户提到"语法总结"、"汇总语法"、"语法笔记汇总"时触发。
---

# 语法总结技能 (summarize-grammar)

将 intermediate 下所有单篇语法笔记（grammar-notes.md）按语法类别合并去重，生成一份跨篇章、可增量更新的综合语法总结笔记，方便考研备考系统复习。

## 前置条件

- `intermediate/` 目录下至少有一个 `<topic>/grammar-notes.md` 文件（由 `organize-grammar` 技能产出）
- 输出格式遵循 Obsidian Flavored Markdown 规范。参考：
  - `obsidian-markdown` 技能 — 完整语法
  - `obsidian-markdown/references/CALLOUTS.md` — callout 类型（折叠式 callout 用于渐进展示）
  - `obsidian-markdown/references/PROPERTIES.md` — frontmatter 属性
  - `organize-grammar` 技能 — 单篇语法笔记的格式和分类标准

## 输入

此技能**无需用户手动提供输入**。技能自动扫描 `intermediate/` 目录。

## 工作流

### 步骤 1：发现所有源文件

用 Bash 执行：

```bash
find intermediate -name "grammar-notes.md" -type f | sort
```

对每个文件用以下命令获取最后修改日期（macOS）：

```bash
stat -f "%Sm" -t "%Y-%m-%d" "<file>"
```

记录每个文件的**相对路径**和**最后修改日期**。

若扫描结果为 0 个文件，报告："未找到任何 grammar-notes.md 文件。请先通过 organize-grammar 整理至少一篇语法笔记。"流程结束。

向用户报告找到的源文件清单（文件名 + 修改日期），请求确认继续。

### 步骤 1b：检测已有总结并确定模式

检查项目根目录下 `语法总结笔记.md` 是否存在：

**若不存在 → 全量新建模式**：继续执行步骤 2-8。

**若存在 → 增量更新模式**：

1. 读取 `语法总结笔记.md` 的 YAML frontmatter，提取 `processed_sources` 列表
2. 将步骤 1 的源文件清单与 `processed_sources` 比对，将文件分为四类：
   - **unchanged**：路径相同且 `last_modified` 日期匹配 → 跳过
   - **new**：路径不在 `processed_sources` 中 → 需解析
   - **modified**：路径相同但 `last_modified` 日期不同 → 需重新解析
   - **removed**：在 `processed_sources` 中但不在当前扫描结果中 → 标记 `status: removed`，内容保留
3. 若 new + modified 数量为 0，报告："所有源文件均未变动，总结已是最新。"流程结束。
4. 若有变化：向用户报告 X 个未变、Y 个新增、Z 个修改、W 个移除。请求确认后 → **跳转到步骤 9（增量合并）**

### 步骤 2：读取并解析每个语法笔记

对每个需处理的 grammar-notes.md：

- 用 Read 读取完整内容
- 解析 YAML frontmatter，提取 `topic` 和 `concepts`
- 去除 frontmatter，保留正文
- 按 `###` 或 `##` 标题切分为独立语法区块，记录每个区块的：
  - 标题文本
  - 完整内容（callout、表格、段落、例句）

### 步骤 3：建立标准类别映射

将各文件的语法区块标题映射到标准类别。匹配规则（按优先级从上到下）：

| 标准类别 (##) | 子主题 (###) | 标题匹配关键词 |
|------|------|---------|
| **从句 (Clauses)** | 定语从句 | 定语从句、Attributive |
| | 状语从句 | 状语从句、Adverbial |
| | 宾语从句 | 宾语从句、Object Clause |
| | 主语从句 | 主语从句、Subject Clause |
| | 名词性从句对比 | 名词性从句、Noun Clause |
| **非谓语动词 (Non-finite Verbs)** | 动名词作主语 | 动名词、V-ing 作主语、Gerund |
| | 分词（现在/过去） | 分词、Participle |
| | 非谓语动词综合 | 非谓语动词（非以上子类） |
| **介词与连词 (Prepositions & Conjunctions)** | As 的用法 | As、Multi-functional |
| | Since | Since |
| | As Well As | As Well As |
| | However | However |
| | Between...And | Between |
| | 介词短语 | 介词短语、介词与 |
| **固定搭配 (Fixed Collocations)** | Make/Find + A + B | Make、Find、Complex Object |
| | Used To 家族 | Used To |
| | There Be 句型 | There Be |
| | take for granted | take、granted |
| | attribute to | attribute |
| | yield to | yield |
| | 其他固定搭配 | 固定搭配（非以上子类） |
| **倒装与强调 (Inversion & Emphasis)** | 原级比较 (as...as) | as...as、原级比较 |
| | 倒装结构 | 倒装 |
| **补充要点 (Additional Notes)** | A of B 核心词判定 | A of B、核心词判定 |
| | 形式主语 It | 形式主语、Formal Subject |
| | 插入语 | 插入语、Parenthesis |
| | What vs That 引导词 | What、That、引导词 |
| | 主语从句谓语单数原则 | 谓语单数、主谓一致 |

**映射补充规则**：
- 完全不匹配任何关键词的区块 → 归入 `补充要点 > 其他补充`
- 同一区块匹配多个子主题时，取第一个匹配项
- 跨类别内容放在主要内容所属类别，在 `补充要点` 中建立交叉引用

### 步骤 4：按类别合并内容

对每个标准类别的每个子主题：

**4a. 收集**：汇集所有映射到该子主题的语法区块，标注来源 topic。

**4b. 表格合并**：
- 以"结构"列为 key 去重
- 相同结构不同例句的，追加例句并用 `；` 分隔，标注各自来源
- 相同结构不同解释的，保留最详细的版本

**4c. Callout 合并**：
- 相同标题的 callout 合并为一个（保留措辞最清晰的版本）
- 不同标题的 callout 按重要性排列：`[!warning]` > `[!tip]` > `[!note]` > `[!example]`

**4d. 段落合并**：
- 相同内容的段落只保留一份
- 不同角度/补充的段落合并排列

**4e. 逻辑排序**：按 基础概念 → 规则表格 → 注意事项(callout) → 进阶用法 → 考研提示 排列。

### 步骤 5：构建学习型布局

**5a. 快速索引区**：在 `## 快速索引` 下用表格列出：

```markdown
| 类别 | 子主题 | 涉及篇章 | 考查频率 |
|------|--------|---------|---------|
| 从句 | 定语从句、状语从句、宾语从句... | 3 | ★★★★★ |
```

考查频率根据考研英语命题规律推断（从句和非谓语动词最高频）。

**5b. 渐进式展示**：
- 核心规则和表格**直接可见**
- 多篇章补充例句使用折叠 callout：`> [!example]- 更多篇章例句`
- 详细解释使用折叠：`> [!note]- 详细说明`

**5c. 来源标注**：
- 每条例句末尾标 `（来源：<topic>）`
- Callout 若来自特定篇章，在标题中标注：`> [!warning] 常见错误（来源：2000-passage1-america）`

**5d. 考点高亮**：
- 考研高频考点在 callout 标题前加 📌：`> [!tip] 📌 考研核心考点`
- 考查频率用 ★ 评级（★★★★★ 最高）

**5e. 交叉引用**：
- 关联子主题末尾添加 `> [!quote]- 相关内容` 折叠块，列出交叉引用

### 步骤 6：构建 YAML frontmatter

```yaml
---
title: "考研英语语法总结笔记"
type: grammar-summary
tags:
  - english-reading
  - grammar
  - summary
  - reference
created: YYYY-MM-DD
updated: YYYY-MM-DD
total_sources: N
processed_sources:
  - path: "intermediate/<topic>/grammar-notes.md"
    last_modified: "YYYY-MM-DD"
    status: processed
categories:
  - 从句
  - 非谓语动词
  - 介词与连词
  - 固定搭配
  - 倒装与强调
  - 补充要点
---
```

- `total_sources`：已处理的源文件数（不含 status: removed 的）
- `processed_sources`：追踪数组，记录每个文件路径、最后修改日期和处理状态
- `status` 可选值：`processed`、`removed`
- `categories`：本次涵盖的标准类别

### 步骤 7：组装完整文档

文档结构（从上到下）：

1. YAML frontmatter
2. `# 考研英语语法总结笔记`
3. `> [!abstract] 使用说明` callout
4. `## 快速索引` — 索引表格
5. 各 `##` 类别章节（按：从句 → 非谓语动词 → 介词与连词 → 固定搭配 → 倒装与强调 → 补充要点）
6. 每个类别内包含对应的 `###` 子主题
7. 类别之间用 `---` 分隔

### 步骤 8：保存并报告（全量新建模式）

- 输出路径：项目根目录 `语法总结笔记.md`
- 用 Write 写入
- 向用户报告：处理文件数、涵盖类别数/子主题数、总例句数

### 步骤 9：增量合并（增量更新模式专用）

9a. 对标记为 new 和 modified 的源文件，执行步骤 2 的解析逻辑。

9b. 读取已有 `语法总结笔记.md` 完整内容，解析其结构：
- 读取 frontmatter（保留 `created`）
- 识别各 `##` 类别和 `###` 子主题
- 识别每个子主题下的已有表格行（按"结构"列）、callout 块、段落

9c. 对新解析的语法区块执行合并：

- **子主题已存在**：对比已有表格行，新结构追加、已存在结构检查例句是否新增；新 callout 追加、已有 callout 保留；新段落追加、重复跳过
- **子主题不存在**：创建新的 `###` 子主题，写入完整内容

9d. 更新索引表格（重新统计篇章数和考查频率）。

9e. 更新 YAML frontmatter：
- 保留 `created`，更新 `updated`
- 更新 `processed_sources` 中对应条目的 `last_modified` 和 `status`
- 标记 removed 文件为 `status: removed`
- 更新 `total_sources` 和 `categories`

9f. 用 Write 覆盖写入 `语法总结笔记.md`。

9g. 报告变更摘要：新增/修改/移除的文件数，新增/更新的语法条目数。

### 步骤 10：记录候选学习条目（不落盘）

若执行中出现值得记录的合并问题或格式改进，仅在会话内记下候选条目，**不要中途写入 `.learnings/`**。学习心得统一由 `digest` 技能在用户明确要求时整理落盘，避免中途修改每次会话强制加载的经验库文件而破坏提示缓存前缀。无有意义内容则跳过。

## 输出格式

示例参见 `references/GRAMMAR_SUMMARY_TEMPLATE.md`。

核心约定：
- `#` 用于文档标题，`##` 用于标准类别，`###` 用于子主题
- 规则用 callout 突出（`[!tip]`、`[!warning]`、`[!note]`）
- 多篇章例句用 `[!example]-` 折叠（`-` 表示默认折叠）
- 结构模式用表格（结构 | 用法 | 例句）
- 交叉引用用 `[!quote]-` 折叠
- 例句末标注 `（来源：<topic>）`
- 关键术语用 `**粗体**`，重点用 `==高亮==`
- 考查频率用 ★ 评级

## 约束

- **不得编造内容**：所有语法规则和例句必须来源于 grammar-notes.md，不得自行添加
- **不得丢失来源**：每条例句必须标注来源篇章
- **增量不删除**：更新时只追加/修改，不删除已有内容。removed 源文件只标记、不删内容
- **去重要保守**：只对"结构+例句"完全一致的条目去重；稍有不同即保留，宁多勿漏
- **格式前后一致**：同类别的表格列数、callout 风格、标注格式保持一致
- **索引表实时反映内容**：索引中的子主题和篇章数必须与实际内容对应
- **日期格式统一**：使用 `YYYY-MM-DD`

## 相关技能

- `organize-grammar` — **上游**：产出每篇的 grammar-notes.md 作为本技能的输入
- `obsidian-markdown` — **格式参考**：提供 callout、frontmatter、wikilink 语法
- `compile-note` — **下游**：语法总结笔记可作为精读笔记中语法要点的引用来源
- `extract-vocabulary` — **并列**：不同维度的学习参考
