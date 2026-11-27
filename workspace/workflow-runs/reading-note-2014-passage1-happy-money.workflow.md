---
workflow_id: reading-note-generation
workflow_name: Reading Note Generation
workflow_version: 1
state_file_type: workflow-run
run_id: "reading-note-2014-passage1-happy-money"
task: "2014 年 Passage 1 精读"
created_from: ".claude/workflows/reading-note-generation/state-template.md"
created_at: "2026-11-27"
last_updated: "2026-11-27"
current_phase: P8
current_status: in_progress
mode: guided
blocked_reason: ""
article_source: "/Users/zhqznc/Documents/英语阅读资料/2014阅读/passage_1.md"
year: "2014"
passage: "1"
topic: "happy-money"
intermediate_dir: "intermediate/2014-passage1-happy-money/"
output_path: "2014-passage1-happy-money-精读笔记.md"
long_sentence_mode: "AI 候选 + 用户确认"
---

# Reading Note Generation - Workflow Run

> 工作流：reading-note-generation
> 任务：2014 年 Passage 1 精读
> 运行标识：reading-note-2014-passage1-happy-money
> 创建时间：2026-11-27
> 当前阶段：阶段 8
> 状态图例：⬜ 未开始 | 🔲 进行中 | ✅ 已完成 | ⏭️ 跳过

---

## 阶段 0：输入收集与状态初始化

- [x] 已读取 `.learnings/` 经验库和 `.claude/rules/workflow-routing.md`
- [x] 已确认英文文章文本或源文件路径
- [x] 已确认 year、passage、topic
- [x] 已确认 intermediate 目录
- [x] 已确认最终输出路径
- [x] 已记录长难句模式：AI 候选 + 用户确认

- 已获批次确认：Vault 根目录按默认命名输出，从原文提取语法。

> [P0] ✅ 已完成 {complete}

---

## 阶段 1：文章排版

- [x] 已调用 `format-article`
- [x] 已生成或更新 `formatted-article.md`
- [x] 已确认原文内容未删改
- [x] 已确认标题格式适合 Obsidian

> [P1] ✅ 已完成 {complete}

---

## 阶段 2：中英翻译

- [x] 已调用 `translate`
- [x] 已生成或更新 `translation.md`
- [x] 已保持原文段落结构

> [P2] ✅ 已完成 {complete}

---

## 阶段 3：语法整理

- [x] 已调用 `organize-grammar`
- [x] 已生成或更新 `grammar-notes.md`
- [x] 已核验语法笔记信息密度未丢失
- [x] 已加入必要的跨节联动复习

> [P3] ✅ 已完成 {complete}

---

## 阶段 4：长难句候选确认

- [x] 已从 `formatted-article.md` 选出候选长难句
- [x] 已说明每个候选句的分析价值
- [x] 已获得用户确认、删改或补充
- 用户确认：全部分析。

### 候选句（待用户确认）

下列原句已全部确认。

- **A1**（第 1 段）This is now a question for Gloria MacKenzie, an 84-year-old widow who recently emerged from her small, tin-roofed house in Florida to collect the biggest undivided lottery jackpot in history.
  - 分析价值：同位语、定语从句与目的不定式。

- **A2**（第 1 段）If she hopes her new-found fortune will yield lasting feelings of fulfilment, she could do worse than read Happy Money by Elizabeth Dunn and Michael Norton.
  - 分析价值：条件从句内再套宾语从句，兼有委婉建议。

- **A3**（第 2 段）It is far better to spend money on experiences, say Ms. Dunn and Mr. Norton, like interesting trips, unique meals or even going to the cinema.
  - 分析价值：形式主语、报道语插入与举例归属。

- **A4**（第 3 段）It seems most people would be better off if they could shorten their commutes to work, spend more time with friends and family and less of it watching television (something the average American spends a whopping two months a year doing, and is hardly jollier for it).
  - 分析价值：条件、并列省略与括号里的评价。

- **A5**（第 3 段）This is apparently the reason McDonald’s restricts the availability of its popular McRib—a marketing trick that has turned the pork sandwich into an object of obsession.
  - 分析价值：零关系词、破折号同位说明与定语从句。

- **A6**（第 4 段）Not everyone will agree with the authors' policy ideas, which range from mandating more holiday time to reducing tax incentives for American homebuyers.
  - 分析价值：部分否定、非限制性定语从句与 from … to …。

> [P4] ✅ 已完成 {complete}

---

## 阶段 5：长难句分析与内联插入

- [ ] 已调用 `analyze-sentence`
- [ ] 已把分析块插入文章原文对应句子之后
- [ ] 已确认多句同段时采用逐句交替结构
- [ ] 已确认每个 callout 第一行包含完整原句
- [ ] 已确认 callout 内表格前有空行
- [ ] 已检查后续段落没有异常开头

> [P5] ✅ 已完成 {complete}

---

## 阶段 6：综合笔记整合

- [ ] 已调用 `compile-note`
- [ ] 已使用用户确认的最终输出路径
- [ ] 已保留文章原文中的内联长难句分析
- [ ] 已插入词汇占位符

> [P6] ✅ 已完成 {complete}

---

## 阶段 7：生词表与练习

- [ ] 已调用 `extract-vocabulary`
- [ ] 已生成或更新 `## 生词表`
- [ ] 已生成或更新 `### 生词练习`
- [ ] 已补充短语内重要独立词条

> [P7] ✅ 已完成 {complete}

---

## 阶段 8：最终验证与收尾

- [ ] 已确认所有中间文件存在
- [ ] 已确认最终精读笔记存在
- [ ] 已确认最终笔记不含词汇占位符
- [ ] 已检查 Markdown 标题、YAML 和表格格式
- [ ] 已向用户报告输出路径

> [P8] 🔲 进行中 {in_progress}

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
| 2026-11-27 20:21 | P4 | 阻塞：等待用户确认长难句候选（Passage 1：A1–A6；Passage 2：B1–B7） | 停在当前阶段，等待用户确认或补充资料 |
| | | | |

---

## 最终产出

- **中间目录**：`intermediate/2014-passage1-happy-money/`
- **最终笔记**：`2014-passage1-happy-money-精读笔记.md`
- **全局汇总**：`语法总结笔记.md`、`固定搭配与词组笔记.md`
- **完成状态**：
