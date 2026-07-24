## Mandatory Workflow Dispatch

以下规则适用于每一项用户任务，优先级高于普通执行流程。

在进行任何会修改项目文件、运行项目命令或调用外部服务的操作前，必须：

1. 读取当前 agent profile 的 `workflow-routing.md`，例如 `.agent/rules/workflow-routing.md` 或 `.codex/rules/workflow-routing.md`。
2. 用用户原始请求匹配其中的“正向触发条件”和“排除条件”。
3. 若命中 `Required: yes` 的工作流：
   - 读取 `<agent-dir>/workflows/{workflow-id}/workflow.md`；
   - 查找 `workspace/workflow-runs/` 中该任务的已有 run，存在则恢复；
   - 不存在则由 `state-template.md` 创建 run；
   - 读取 run 的 YAML frontmatter 与当前 phase；
   - 使用 `<agent-dir>/scripts/todo-state.sh` 将当前 phase 标记为 `start`；
   - 只执行该 phase 允许的操作。
4. 在当前 phase 完成、跳过或阻塞前，不得执行下一 phase。
5. 无法确定是否命中时，必须先询问用户；不得以“不确定”为由绕过工作流。
6. 每次进入工作流时，先向用户简短说明：`workflow_id`、状态文件和当前 phase。
