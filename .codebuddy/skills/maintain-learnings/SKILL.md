---
name: maintain-learnings
description: 维护 .learnings/ 经验库，把过多或反复出现的学习记录、错误日志、规则失效问题聚类诊断，追溯并修改对应 skill、模板、hook、校验脚本或项目规则；修复并验证后再归档或移除已解决记录。用户提到 learnings 太多、错误反复犯、清理经验库、维护自我学习、压缩错误日志或从错误中修技能时触发。
---

# maintain-learnings（经验库维护）

让 `.learnings/` 保持小而有用：它是发现流程缺陷的雷达，不是永久堆放错误的仓库。重复错误必须优先修源头，验证有效后再清理活跃记录。

## Step 1: 审计经验库

先读取：

- `.learnings/RULES.md`
- `.learnings/LEARNINGS.md`
- `.learnings/ERRORS.md`

然后运行审计脚本。通用示例：

```bash
python3 <skills-dir>/maintain-learnings/scripts/audit_learnings.py --root . --skills-dir <skills-dir> --rules-file <entry-file> --hooks-path <hooks-dir>
```

Codex 内置 profile 示例：

```bash
python3 .agents/skills/maintain-learnings/scripts/audit_learnings.py --root . --skills-dir .agents/skills --rules-file AGENTS.md --hooks-path .codex/hooks
```

Claude Code 内置 profile 示例：

```bash
python3 .claude/skills/maintain-learnings/scripts/audit_learnings.py --root . --skills-dir .claude/skills --rules-file CLAUDE.md --hooks-path .claude/hooks
```

## Step 2: 选择修复目标

优先处理：

1. 活跃记录中同一 skill 出现 2 次及以上。
2. 历史归档和活跃记录合计出现 3 次及以上。
3. 已写入 `RULES.md` 但仍在 `ERRORS.md` / `LEARNINGS.md` 中复发。
4. 活跃文件超过 100 行且包含明显重复主题。

## Step 3: 追溯源头

根据审计报告读取对应源文件：

- skill 问题：`<skills-dir>/<skill>/SKILL.md`
- skill 模板问题：`<skills-dir>/<skill>/references/`
- 项目规则问题：`AGENTS.md` / `CLAUDE.md` / `INSTRUCTIONS.md` / 项目自定义规则文件
- hook 问题：`.codex/hooks/` / `.claude/hooks/` / 项目自定义 hook
- 工具脚本问题：对应 `scripts/`

## Step 4: 修改机制

修复必须落到可执行机制之一：

- 在对应 `SKILL.md` 中加入明确步骤、硬性约束或验证 checklist。
- 修改 reference 模板，使正确格式自然生成。
- 添加或修改校验脚本，让错误能被自动发现。
- 更新项目规则，但只提升跨 skill 的铁律。

不要只把“下次注意”追加到 `.learnings/`。如果没有源头修改，不能清理对应错误记录。

## Step 5: 验证修复

至少验证两件事：

1. skill 元数据存在：

```bash
python3 -c 'from pathlib import Path; p=Path("<skills-dir>/<skill>/SKILL.md"); t=p.read_text(encoding="utf-8"); assert t.startswith("---\n") and "\n---" in t[4:]; assert "name:" in t and "description:" in t; print("skill metadata ok")'
```

2. 每条待归档记录都能对应到新的步骤、模板或校验逻辑。

## Step 6: 清理活跃 learnings

只处理已经验证修复的记录：

1. 在 `.learnings/archive/YYYY-MM-DD-maintenance.md` 追加归档块，包含原记录摘要、修复路径、验证方式、处理结果。
2. 从 `.learnings/LEARNINGS.md` 或 `.learnings/ERRORS.md` 移除对应详细记录。
3. 保留或更新 `.learnings/RULES.md` 中的简短铁律。
4. 未修复、未验证或仍需观察的记录继续留在活跃文件中。

## 禁止行为

- 不要为了“变短”直接清空 `.learnings/`。
- 不要归档未修复的问题。
- 不要把多个不同根因的错误合并成一条模糊规则。
- 不要把只适用于某个 skill 的细节提升到项目总规则。
- 不要同步其他 Agent 的配置；跨 profile 的 skills、rules、hooks、scripts、workflows 和 MCP 配置由 `multi-agent-sync` 负责。
