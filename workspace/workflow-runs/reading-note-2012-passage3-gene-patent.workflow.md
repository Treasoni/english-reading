---
workflow_id: reading-note-generation
workflow_name: Reading Note Generation
workflow_version: 1
state_file_type: workflow-run
run_id: "reading-note-2012-passage3-gene-patent"
task: "2012 Passage 3 基因专利之争 精读笔记"
created_from: ".claude/workflows/reading-note-generation/state-template.md"
created_at: "2026-09-11"
last_updated: "2026-09-11"
current_phase: done
current_status: complete
mode: guided
blocked_reason: ""
article_source: "/Users/zhqznc/Documents/英语阅读资料/2012阅读/passage_3.md"
year: "2012"
passage: "3"
topic: "gene-patent"
intermediate_dir: "intermediate/2012-passage3-gene-patent/"
output_path: "2012阅读/2012-passage3-gene-patent-精读笔记.md"
long_sentence_mode: "AI 候选 + 用户确认"
---

# Reading Note Generation - Workflow Run

> 工作流：reading-note-generation
> 任务：2012 Passage 3 基因专利之争 精读笔记
> 运行标识：reading-note-2012-passage3-gene-patent
> 创建时间：2026-09-11
> 当前阶段：完成
> 状态图例：⬜ 未开始 | 🔲 进行中 | ✅ 已完成 | ⏭️ 跳过

---

## 阶段 0：输入收集与状态初始化

- [x] 已读取 `.learnings/` 经验库和 `.claude/rules/workflow-routing.md`
- [x] 已确认英文文章文本或源文件路径
- [x] 已确认 year、passage、topic
- [x] 已确认 intermediate 目录
- [x] 已确认最终输出路径
- [x] 已记录长难句模式：AI 候选 + 用户确认

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

> [P4] ✅ 已完成 {complete}

---

## 阶段 5：长难句分析与内联插入

- [x] 已调用 `analyze-sentence`
- [x] 已把分析块插入文章原文对应句子之后
- [x] 已确认多句同段时采用逐句交替结构
- [x] 已确认每个 callout 第一行包含完整原句
- [x] 已确认 callout 内表格前有空行
- [x] 已检查后续段落没有异常开头

> [P5] ✅ 已完成 {complete}

---

## 阶段 6：综合笔记整合

- [x] 已调用 `compile-note`
- [x] 已使用用户确认的最终输出路径
- [x] 已保留文章原文中的内联长难句分析
- [x] 已插入词汇占位符

> [P6] ✅ 已完成 {complete}

---

## 阶段 7：生词表与练习

- [x] 已调用 `extract-vocabulary`
- [x] 已生成或更新 `## 生词表`
- [x] 已生成或更新 `### 生词练习`
- [x] 已补充短语内重要独立词条

> [P7] ✅ 已完成 {complete}

---

## 阶段 8：最终验证与收尾

- [x] 已确认所有中间文件存在
- [x] 已确认最终精读笔记存在
- [x] 已确认最终笔记不含词汇占位符
- [x] 已检查 Markdown 标题、YAML 和表格格式
- [x] 已向用户报告输出路径

> [P8] ✅ 已完成 {complete}

---

## 阶段 9：全局汇总

- [x] 已调用 `summarize-grammar`
- [x] 源发现已同时覆盖 `intermediate/**/grammar-notes.md` 与 `intermediate/**/固定搭配与词组笔记.md`
- [x] 已合并进根目录 `语法总结笔记.md`
- [x] 已合并进根目录 `固定搭配与词组笔记.md`
- [x] 已更新两个根文件的 frontmatter（updated / total_sources / processed_sources / categories）
- [x] 已更新两个根文件的快速索引表
- [x] 已通过差集核验（`语法总结笔记.md` 差集必须为空）
- [x] 已向用户报告两个根文件的更新内容

> [P9] ✅ 已完成 {complete}

---

## 异常记录

| 时间 | 阶段 | 问题描述 | 处理方式 |
|------|------|---------|---------|
| 2026-09-11 | P4/P5 | P5 长难句分析与内联插入先于 P4 候选确认执行（用户连写 `/translate /analyze-sentence` 直接触发） | 由用户事后确认 5 句候选清单，确认后 P4 补记通过 |
| 2026-09-11 | P0-P5 | P0-P2、P5 在状态文件创建之前已由用户逐个技能调用完成 | 建文件时回填为已完成，用 todo-state.sh 逐阶段补记 |
| 2026-09-11 | P6/P7 | `todo-state.sh complete P7` 触发 P6 期校验失败：P6 要求笔记含 `<!-- VOCABULARY_SLOT -->`，而 P7 正是要删除它，两个断言互斥，导致 P7 无法完成 | 移植 Codex 侧已有修复到 Claude 侧三份 `todo-state.py`：P7 一旦开始（非 not_started）不再复检 P6 占位符；修复后 P7/P8/P9 依次通过 |

---

## 最终产出

- **中间目录**：`intermediate/2012-passage3-gene-patent/`
- **最终笔记**：`2012阅读/2012-passage3-gene-patent-精读笔记.md`
- **全局汇总**：`语法总结笔记.md`、`固定搭配与词组笔记.md`
- **完成状态**：P0-P9 全部完成（✅），`validate` 通过
