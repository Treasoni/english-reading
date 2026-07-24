---
workflow_id: example-flow
workflow_name: Example Flow
workflow_version: 1
state_file_type: workflow-run
run_id: "{run_id}"
task: "{task}"
created_from: "<agent-dir>/workflows/example-flow/state-template.md"
created_at: "{date}"
last_updated: "{date}"
current_phase: P0
current_status: not_started
mode: standard
blocked_reason: ""
---

# Example Flow - Workflow Run

> 工作流：example-flow
> 任务：{task}
> 运行标识：{run_id}
> 创建时间：{date}
> 当前阶段：阶段 0
> 状态图例：⬜ 未开始 | 🔲 进行中 | ✅ 已完成 | ⏭️ 跳过

---

## 阶段 0：Plan
- [ ] Goal is clear
- [ ] Inputs are available
- [ ] Output location is confirmed

> [P0] ⬜ 未开始 {not_started}

---

## 阶段 1：Collect
- [ ] Required sources are collected
- [ ] Source quality is checked
- [ ] Collection notes are saved

> [P1] ⬜ 未开始 {not_started}

---

## 阶段 2：Build
- [ ] Main artifact is created
- [ ] Local validation is complete
- [ ] User confirmation gate is satisfied

> [P2] ⬜ 未开始 {not_started}

---

## 异常记录

| 时间 | 阶段 | 问题描述 | 处理方式 |
|------|------|---------|---------|
| | | | |

---

## 最终产出

- **输出文件**：
- **完成状态**：
