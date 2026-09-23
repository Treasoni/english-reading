---
workflow_id: reading-note-generation
workflow_name: Reading Note Generation
workflow_version: 1
state_file_type: workflow-run
run_id: "reading-note-2015-passage4-voluntary-part-time"
task: "生成 2015-passage4-voluntary-part-time 综合精读笔记并放入 2015阅读"
created_from: ".claude/workflows/reading-note-generation/state-template.md"
created_at: "2026-09-23"
last_updated: "2026-09-23"
current_phase: P6
current_status: in_progress
mode: guided
blocked_reason: ""
article_source: "/Users/zhqznc/Documents/英语阅读资料/2015阅读/passage_4.md"
year: "2015"
passage: "4"
topic: "voluntary-part-time"
intermediate_dir: "intermediate/2015-passage4-voluntary-part-time/"
output_path: "2015阅读/2015-passage4-voluntary-part-time-精读笔记.md"
long_sentence_mode: "AI 候选 + 用户确认"
---

# Reading Note Generation - Workflow Run

> 工作流：reading-note-generation
> 任务：生成 2015-passage4-voluntary-part-time 综合精读笔记并放入 2015阅读
> 运行标识：reading-note-2015-passage4-voluntary-part-time
> 创建时间：2026-09-23
> 当前阶段：阶段 6
> 状态图例：⬜ 未开始 | 🔲 进行中 | ✅ 已完成 | ⏭️ 跳过

---

## 阶段 0：输入收集与状态初始化

- [x] 已读取 `.learnings/` 经验库和 `.claude/rules/workflow-routing.md`
- [x] 已确认英文文章文本或源文件路径
- [x] 已确认 year、passage、topic
- [x] 已确认 intermediate 目录（`intermediate/2015-passage4-voluntary-part-time/`）
- [x] 已确认最终输出路径（用户确认 `2015阅读/2015-passage4-voluntary-part-time-精读笔记.md`）
- [x] 已记录长难句模式：AI 候选 + 用户确认
- [x] 已确认语法笔记来源：无现成语法笔记（`passage_1_语法.md` 为 0 字节空文件），采用**推断模式**（从文章推断考研相关语法点）

> [P0] ✅ 已完成 {complete}

---

## 阶段 1：文章排版

- [ ] 已调用 `format-article`
- [ ] 已生成或更新 `formatted-article.md`
- [ ] 已确认原文内容未删改
- [ ] 已确认标题格式适合 Obsidian

> [P1] ✅ 已完成 {complete}

---

## 阶段 2：中英翻译

- [ ] 已调用 `translate`
- [ ] 已生成或更新 `translation.md`
- [ ] 已保持原文段落结构

> [P2] ✅ 已完成 {complete}

---

## 阶段 3：语法整理

- [x] 已调用 `organize-grammar`
- [x] 已生成或更新 `grammar-notes.md`（`intermediate/2015-passage4-voluntary-part-time/grammar-notes.md`，565 行，23 个 `###` 扁平小节 + `### 跨节联动复习`）
- [x] 已生成 `固定搭配与词组笔记.md`（`intermediate/2015-passage4-voluntary-part-time/固定搭配与词组笔记.md`，400 行，`## 一`–`## 七` 七节，`## 六、易混辨析` 下 `### 1.`–`### 8.` 编号子项，符合"固定搭配与词组独立成笔记"铁律）
- [x] 已核验语法笔记信息密度未丢失（逐段核对源文章，含词源拆解、术语、熟词生义、命题定位等教学细节）
- [x] 已加入必要的跨节联动复习（`### 跨节联动复习` 19 行对照表 + 与 2015 Passage 1/2/3 的横向对照 callout；两文件以 `[[语法总结笔记]]` / `[[固定搭配与词组笔记]]` 双向引用）
- [x] 已通过结构校验：标题缺空格 0 / 表格前缺空行 0 / callout 嵌套 0 / callout 未闭合 0（两文件均通过）

> [P3] ✅ 已完成 {complete}

---

## 阶段 4：长难句候选确认

- [x] 已从 `formatted-article.md` 选出候选长难句（10 句正选 + 1 句备选，覆盖第 1–6 段；候选清单与推荐理由已输出给用户）
- [x] 已说明每个候选句的分析价值（逐句给出结构难点 + 命题关联）
- [x] 已获得用户确认、删改或补充（用户回复「全部」→ 10 正选 + 1 备选全部保留；另将第 7 段结论句一并纳入，共 12 句进入 P5）

> [P4] ✅ 已完成 {complete}

---

## 阶段 5：长难句分析与内联插入

- [x] 已调用 `analyze-sentence`
- [x] 已把分析块插入文章原文对应句子之后（`formatted-article.md` 共插入 12 个 `> [!abstract]- 长难句分析` 块，覆盖 7 个段落）
- [x] 已确认多句同段时采用逐句交替结构（12/12 校验：每个分析块的 `原句` 均为其前置原文行的**末句**，逐句交替成立）
- [x] 已确认每个 callout 第一行包含完整原句（12/12 含 `> **原句**：`，且与前置原句逐字一致）
- [x] 已确认 callout 内表格前有空行（表格首行前缺空行 0）
- [x] 已检查后续段落没有异常开头（正文 13 行段落均完整；`formatted-article.md` 与原文的可见英文内容归一化比对**完全一致**，3204 == 3204 字符，无截断）
- [x] 结构校验：标题缺空格 0 / 嵌套 callout 0 / 未闭合 callout 0 / 代码围栏 24（12 对）且每块均含 主干提取·修饰成分·结构图解·参考译文·考点提示

> [P5] ✅ 已完成 {complete}

---

## 阶段 6：综合笔记整合

- [ ] 已调用 `compile-note`
- [ ] 已使用用户确认的最终输出路径
- [ ] 已保留文章原文中的内联长难句分析
- [ ] 已插入词汇占位符

> [P6] 🔲 进行中 {in_progress}

---

## 阶段 7：生词表与练习

- [ ] 已调用 `extract-vocabulary`
- [ ] 已生成或更新 `## 生词表`
- [ ] 已生成或更新 `### 生词练习`
- [ ] 已补充短语内重要独立词条

> [P7] ⬜ 未开始 {not_started}

---

## 阶段 8：最终验证与收尾

- [ ] 已确认所有中间文件存在
- [ ] 已确认最终精读笔记存在
- [ ] 已确认最终笔记不含词汇占位符
- [ ] 已检查 Markdown 标题、YAML 和表格格式
- [ ] 已向用户报告输出路径

> [P8] ⬜ 未开始 {not_started}

---

## 阶段 9：全局汇总

- [ ] 已调用 `summarize-grammar`
- [ ] 源发现已同时覆盖 `intermediate/**/grammar-notes.md` 与 `intermediate/**/固定搭配与词组笔记.md`
- [ ] 已合并进根目录 `语法总结笔记.md`
- [ ] 已合并进根目录 `固定搭配与词组笔记.md`
- [ ] 已更新两个根文件的 frontmatter（updated / total_sources / processed_sources / categories）
- [ ] 已更新两个根文件的快速索引表
- [ ] 已通过差集核验（`语法总结笔记.md` 差集必须为空）
- [ ] 已向用户报告两个根文件的更新内容

> [P9] ⬜ 未开始 {not_started}

---

## 异常记录

| 时间 | 阶段 | 问题描述 | 处理方式 |
|------|------|---------|---------|
| 2026-09-23 12:26 | P4 | 阻塞：等待用户确认长难句候选清单（10 正选 + 1 备选） | 停在当前阶段，等待用户确认或补充资料 |
| | | | |

---

## 最终产出

- **中间目录**：`intermediate/2015-passage4-voluntary-part-time/`
- **最终笔记**：`2015阅读/2015-passage4-voluntary-part-time-精读笔记.md`
- **全局汇总**：`语法总结笔记.md`、`固定搭配与词组笔记.md`
- **完成状态**：
