---
workflow_id: reading-note-generation
workflow_name: Reading Note Generation
workflow_version: 1
state_file_type: workflow-run
run_id: "reading-note-2009-passage3-education-20260829"
task: "2009 Passage 3 考研英语阅读精读笔记生成"
created_from: ".codex/workflows/reading-note-generation/state-template.md"
created_at: "2026-08-29"
last_updated: "2026-08-29"
current_phase: done
current_status: complete
mode: guided
blocked_reason: ""
article_source: "/Users/zhqznc/Documents/英语阅读资料/2009阅读/passgae_3.md"
year: "2009"
passage: "3"
topic: "education"
intermediate_dir: "intermediate/2009-passage3/"
output_path: "2009阅读/2009-passage3-精读笔记.md"
long_sentence_mode: "AI 候选 + 用户确认"
---

# Reading Note Generation - Workflow Run

> 工作流：reading-note-generation
> 任务：2009 Passage 3 考研英语阅读精读笔记生成
> 运行标识：reading-note-2009-passage3-education-20260829
> 创建时间：2026-08-29
> 当前阶段：完成
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

> [P1] ✅ 已完成 {complete}

---

## 阶段 2：中英翻译

- [ ] 已调用 `translate`
- [ ] 已生成或更新 `translation.md`
- [ ] 已保持原文段落结构

> [P2] ✅ 已完成 {complete}

---

## 阶段 3：语法整理

- [ ] 已调用 `organize-grammar`
- [ ] 已生成或更新 `grammar-notes.md`
- [ ] 已核验语法笔记信息密度未丢失
- [ ] 已加入必要的跨节联动复习

> [P3] ✅ 已完成 {complete}

---

## 阶段 4：长难句候选确认

- [ ] 已从 `formatted-article.md` 选出候选长难句
- [ ] 已说明每个候选句的分析价值
- [ ] 已获得用户确认、删改或补充

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

> [P8] ✅ 已完成 {complete}

---

## 异常记录

| 时间 | 阶段 | 问题描述 | 处理方式 |
|------|------|---------|---------|
| | | | |

---

## 最终产出

- **中间目录**：`intermediate/2009-passage3-education/`
- **最终笔记**：`2009阅读/2009-passage3-精读笔记.md`
- **完成状态**：
