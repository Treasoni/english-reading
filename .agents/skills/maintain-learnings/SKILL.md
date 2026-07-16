---
name: maintain-learnings
description: 维护 .learnings/ 经验库，把过多或反复出现的学习记录、错误日志、铁律失效问题聚类诊断，追溯并修改对应 skill、模板、校验脚本或项目规则；修复并验证后再归档或移除已解决记录；同时检查 .agents/skills 与 .claude/skills 的共享功能同步，防止更新 Codex 后 Claude Code 丢失对应能力。用户提到 learnings 太多、错误反复犯、清理经验库、维护自我学习、压缩错误日志、从错误中修技能、同步 Codex 和 Claude Code 技能时触发。
---

# maintain-learnings（经验库维护）

让 `.learnings/` 保持小而有用：它不是长期堆放错误的仓库，而是发现流程缺陷的雷达。重复错误必须优先修源头，验证有效后再清理活跃记录。

## 使用场景

- `.learnings/LEARNINGS.md` 或 `.learnings/ERRORS.md` 过长，已经影响上下文质量。
- 同一 skill 或同类格式错误反复出现。
- 某条规则已经写入 `.learnings/RULES.md`，但后续仍然犯同样的错。
- 用户要求“清理 learnings”“维护自我学习”“把反复错误修掉”。

## 工作流

### Step 1: 审计经验库

先按项目规则静默读取：

- `.learnings/RULES.md`
- `.learnings/LEARNINGS.md`
- `.learnings/ERRORS.md`

然后运行审计脚本：

```bash
python3 .agents/skills/maintain-learnings/scripts/audit_learnings.py --root .
```

脚本会输出：

- 活跃文件行数和是否超过阈值
- 按 skill / 主题聚类的热点错误
- 建议检查的源文件
- 可归档候选记录

### Step 2: 选择修复目标

优先处理以下目标：

1. 活跃记录中同一 skill 出现 2 次及以上。
2. 历史归档和活跃记录合计出现 3 次及以上。
3. 已写入 `RULES.md` 但仍在 `ERRORS.md` / `LEARNINGS.md` 中复发。
4. 活跃文件超过 100 行且包含明显重复主题。

如果多个目标都符合，先修影响当前学习流程最多的 skill。只有用户明确要求全面维护时，才一次处理多个 cluster。

### Step 3: 追溯源头

根据审计报告读取对应源文件：

- skill 问题：`.agents/skills/<skill>/SKILL.md`
- skill 模板问题：`.agents/skills/<skill>/references/`
- 项目级规则问题：`AGENTS.md`
- Codex hook 问题：`.codex/hooks/`
- Obsidian 格式问题：优先检查 `.agents/skills/obsidian-markdown/`，再检查具体业务 skill

如果准备同步 Claude Code 语义，必须先 `diff` 比对 `.agents/skills/<skill>/` 与 `.claude/skills/<skill>/`，保留 Claude 专属说明；不要用 Codex 版本覆盖 `.claude/`。

### Step 4: 修改机制，而不是只写提醒

修复必须落到可执行机制之一：

- 在对应 `SKILL.md` 中加入明确步骤、硬性约束或验证 checklist。
- 修改 reference 模板，使正确格式自然生成。
- 添加或修改校验脚本，让错误能被自动发现。
- 更新 `AGENTS.md` 中的通用规则，但只用于跨 skill 的铁律。

不要只把“下次注意”追加到 `.learnings/`。如果没有源头修改，不能清理对应错误记录。

### Step 5: 验证修复

完成源头修改后，至少做两类验证：

1. 运行 skill 结构校验：

```bash
python3 -c 'from pathlib import Path; p=Path(".agents/skills/<skill>/SKILL.md"); t=p.read_text(encoding="utf-8"); assert t.startswith("---\n") and "\n---" in t[4:]; assert "name:" in t and "description:" in t; print("skill metadata ok")'
```

2. 用历史错误反查修复点：
   - 每条待移除记录都能对应到新的步骤、模板或校验逻辑。
   - 若是 Markdown / Obsidian 格式问题，用 `rg` 或脚本抽查新模板中是否包含必要格式。
   - 若无法验证，保留该记录，不归档。

### Step 6: 双平台同步守护

如果本次修改了任何共享 skill，必须检查 Codex 与 Claude Code 两边是否都保留同等功能：

```bash
python3 .agents/skills/maintain-learnings/scripts/sync_platform_skills.py --root . --skill <skill>
```

若报告另一侧缺失，可先 dry-run：

```bash
python3 .agents/skills/maintain-learnings/scripts/sync_platform_skills.py --root . --from-platform agents --to-platform claude --skill <skill>
```

确认无误后再应用：

```bash
python3 .agents/skills/maintain-learnings/scripts/sync_platform_skills.py --root . --from-platform agents --to-platform claude --skill <skill> --apply
```

同步后必须重新读取目标侧文件，保留平台专属内容：

- Codex 的 `agents/openai.yaml` 只留在 `.agents/`。
- Claude Code 的 `.claude/hooks/`、`.claude/settings*.json` 只按 Claude 规则处理。
- 不用 Codex 版本覆盖 Claude Code 专属命令、Hook、工具说明和平台限制。

### Step 7: 清理活跃 learnings

只处理已经验证修复的记录：

1. 在 `.learnings/archive/YYYY-MM-DD-maintenance.md` 追加归档块，包含：
   - 原记录摘要
   - 修复的源文件路径
   - 验证方式
   - 处理结果：`resolved`
2. 从 `.learnings/LEARNINGS.md` 或 `.learnings/ERRORS.md` 移除对应详细记录。
3. 保留或更新 `.learnings/RULES.md` 中的简短铁律。
4. 未修复、未验证或仍需观察的记录继续留在活跃文件中。

## 禁止行为

- 不要为了“变短”直接清空 `.learnings/`。
- 不要归档未修复的问题。
- 不要把多个不同根因的错误合并成一条模糊规则。
- 不要把只适用于某个 skill 的细节提升到 `AGENTS.md`。
- 不要在未比对差异的情况下修改 `.claude/`。

## 完成汇报

向用户报告：

- 发现了哪些热点问题。
- 修改了哪些 skill / 模板 / 规则。
- 哪些记录已归档，哪些仍保留观察。
- 执行了哪些验证。
