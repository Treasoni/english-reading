---
workflow_id: reading-note-batch-generation
workflow_name: Reading Note Batch Generation
workflow_version: 1
state_file_type: workflow-run
run_id: "{run_id}"
task: "{task}"
created_from: ".claude/workflows/reading-note-batch-generation/state-template.md"
created_at: "{date}"
last_updated: "{date}"
current_phase: P0
current_status: not_started
mode: batch
blocked_reason: ""
batch_id: "{batch_id}"
source_set: "{source_set}"
output_root: "{output_root}"
topic_rule: "{topic_rule}"
concurrency: 3
subagent_mode: "fork"
single_workflow_id: reading-note-generation
global_updates: "{global_updates}"
---

# Reading Note Batch Generation - Workflow Run

> 工作流：reading-note-batch-generation
> 任务：{task}
> 批次：{batch_id}
> 创建时间：{date}
> 当前阶段：阶段 0
> 状态图例：⬜ 未开始 | 🔲 进行中 | ✅ 已完成 | ⏭️ 跳过

---

## 阶段 0：批量输入与状态初始化

- [ ] 已读取 `.learnings/` 经验库和 `.claude/rules/workflow-routing.md`
- [ ] 已确认 source directory 或 file list
- [ ] 已确认 batch id、output root、topic rule
- [ ] 已确认 fork subagent 并发上限，默认 3，最高 5
- [ ] 已确认是否更新全局汇总笔记

> [P0] ⬜ 未开始 {not_started}

---

## 阶段 1：清单盘点

- [ ] 已扫描输入文件
- [ ] 已生成文章清单
- [ ] 已标记缺失元数据
- [ ] 已合并 fork subagent 只读盘点报告

> [P1] ⬜ 未开始 {not_started}

---

## 阶段 2：单篇 run 初始化

- [ ] 已为每篇文章创建或恢复 `reading-note-generation` 状态文件
- [ ] 已记录每篇文章的 single-run state path
- [ ] 已避免重复创建状态文件

> [P2] ⬜ 未开始 {not_started}

---

## 阶段 3：独立内容生成

- [ ] 已按不重叠写入范围派发 fork subagent
- [ ] 已完成每篇文章的排版、翻译、语法草稿或候选长难句任务
- [ ] 已收集 subagent 报告
- [ ] 已由主 agent 审查报告并更新单篇状态

> [P3] ⬜ 未开始 {not_started}

---

## 阶段 4：人工确认关口

- [ ] 已按篇汇总长难句候选
- [ ] 已获得用户确认、删改、补充或暂跳过决定
- [ ] 未确认文章已标记为 needs_confirmation

> [P4] ⬜ 未开始 {not_started}

---

## 阶段 5：串行写入与整合

- [ ] 已逐篇执行长难句分析与插入
- [ ] 已逐篇整合最终精读笔记
- [ ] 已逐篇生成生词表与练习
- [ ] 已确保同一最终文件没有并发写入

> [P5] ⬜ 未开始 {not_started}

---

## 阶段 6：批量 QA

- [ ] 已派发或执行每篇最终笔记 QA
- [ ] 已检查 YAML、标题、表格空行、词汇占位符、长难句位置
- [ ] 已串行修复 QA 发现的问题

> [P6] ⬜ 未开始 {not_started}

---

## 阶段 7：全局汇总更新

- [ ] 已根据用户要求更新或跳过全局汇总笔记
- [ ] 已串行处理共享文件
- [ ] 已记录未更新原因

> [P7] ⬜ 未开始 {not_started}

---

## 阶段 8：最终收尾

- [ ] 已汇总完成、阻塞、暂缓和跳过文章
- [ ] 已列出最终输出路径
- [ ] 已确认批量状态文件更新

> [P8] ⬜ 未开始 {not_started}

---

## 文章清单

| 状态 | Source | Year | Passage | Topic | Single Run | Final Note | Notes |
|------|--------|------|---------|-------|------------|------------|-------|
| queued | | | | | | | |

---

## subagent 分配

| 时间 | Agent | 范围 | 写入权限 | 报告路径 | 状态 |
|------|-------|------|----------|----------|------|
| | | | | | |

---

## 异常记录

| 时间 | 阶段 | 问题描述 | 处理方式 |
|------|------|---------|---------|
| | | | |

---

## 最终产出

- **批次**：`{batch_id}`
- **输出根目录**：`{output_root}`
- **完成文章数**：
- **阻塞文章数**：
- **暂缓文章数**：
