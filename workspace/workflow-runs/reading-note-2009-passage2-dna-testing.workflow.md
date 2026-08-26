---
workflow_id: reading-note-generation
workflow_name: Reading Note Generation
workflow_version: 1
state_file_type: workflow-run
run_id: "2009-passage2-dna-testing"
task: "整合 2009 Passage 2 DNA testing 精读笔记"
created_from: ".codex/workflows/reading-note-generation/state-template.md"
created_at: "2026-08-26"
last_updated: "2026-08-26"
current_phase: P6
current_status: in_progress
mode: guided
blocked_reason: ""
article_source: "intermediate/2009-passage2-dna-testing/formatted-article.md"
year: "2009"
passage: "2"
topic: "dna-testing"
intermediate_dir: "intermediate/2009-passage2-dna-testing/"
output_path: "/Users/zhqznc/Documents/英语阅读资料/2009阅读/2009-passage2-dna-testing-精读笔记.md"
long_sentence_mode: "AI 候选 + 用户确认"
---

# Reading Note Generation - Workflow Run

> 工作流：reading-note-generation
> 任务：整合 2009 Passage 2 DNA testing 精读笔记
> 运行标识：2009-passage2-dna-testing
> 创建时间：2026-08-26
> 当前阶段：阶段 6
> 状态图例：⬜ 未开始 | 🔲 进行中 | ✅ 已完成 | ⏭️ 跳过

---

## 阶段 0：输入收集与状态初始化

- [ ] 已读取 `.learnings/` 经验库和 `.codex/rules/workflow-routing.md`
- [ ] 已确认英文文章文本或源文件路径
- [ ] 已确认 year、passage、topic
- [ ] 已确认 intermediate 目录
- [ ] 已确认最终输出路径
- [ ] 已记录长难句模式：AI 候选 + 用户确认

> [P0] ✅ 已完成 {complete}

---

## 阶段 1：文章排版

- [ ] 已调用 `format-article`
- [ ] 已生成或更新 `formatted-article.md`
- [ ] 已确认原文内容未删改
- [ ] 已确认标题格式适合 Obsidian

> [P1] ⏭️ 跳过 {skipped}

---

## 阶段 2：中英翻译

- [ ] 已调用 `translate`
- [ ] 已生成或更新 `translation.md`
- [ ] 已保持原文段落结构

> [P2] ⏭️ 跳过 {skipped}

---

## 阶段 3：语法整理

- [ ] 已调用 `organize-grammar`
- [ ] 已生成或更新 `grammar-notes.md`
- [ ] 已核验语法笔记信息密度未丢失
- [ ] 已加入必要的跨节联动复习

> [P3] ⏭️ 跳过 {skipped}

---

## 阶段 4：长难句候选确认

- [ ] 已从 `formatted-article.md` 选出候选长难句
- [ ] 已说明每个候选句的分析价值
- [ ] 已获得用户确认、删改或补充

> [P4] ⏭️ 跳过 {skipped}

---

## 阶段 5：长难句分析与内联插入

- [ ] 已调用 `analyze-sentence`
- [ ] 已把分析块插入文章原文对应句子之后
- [ ] 已确认多句同段时采用逐句交替结构
- [ ] 已确认每个 callout 第一行包含完整原句
- [ ] 已确认 callout 内表格前有空行
- [ ] 已检查后续段落没有异常开头

> [P5] ⏭️ 跳过 {skipped}

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

## 异常记录

| 时间 | 阶段 | 问题描述 | 处理方式 |
|------|------|---------|---------|
| 2026-08-26 17:36 | P5 | 跳过阶段：长难句分析已提前内联完成 | 继续推进到下一未完成阶段 |
| 2026-08-26 17:36 | P4 | 跳过阶段：长难句候选已由用户确认并完成分析 | 继续推进到下一未完成阶段 |
| 2026-08-26 17:36 | P3 | 跳过阶段：语法整理文件已提前完成 | 继续推进到下一未完成阶段 |
| 2026-08-26 17:36 | P2 | 跳过阶段：翻译文件已提前完成 | 继续推进到下一未完成阶段 |
| 2026-08-26 17:36 | P1 | 跳过阶段：排版文件已提前完成 | 继续推进到下一未完成阶段 |
| | | | |

---

## 最终产出

- **中间目录**：`intermediate/2009-passage2-dna-testing/`
- **最终笔记**：`/Users/zhqznc/Documents/英语阅读资料/2009阅读/2009-passage2-dna-testing-精读笔记.md`
- **完成状态**：
