# Self-Learning Skills Template

这是一个可移植的自学习模板包，用于把 `digest` 和 `maintain-learnings` 带到其他项目。

它提供三件事：

- `digest`：记录本次任务中真实发生的学习点和错误。
- `maintain-learnings`：当 `.learnings/` 变长或错误反复出现时，先修 skill / 模板 / hook / 项目规则，再归档已解决记录。
- hooks：在会话开始时自动读取 `.learnings/RULES.md`、`.learnings/ERRORS.md` 和最近的 `.learnings/LEARNINGS.md`。
- 双平台同步守护：检查 Codex `.agents/skills` 与 Claude Code `.claude/skills` 是否保留同等功能。

## Install

把 `templates/self-learning/` 复制到目标项目后，在目标项目根目录执行：

```bash
python3 templates/self-learning/install.py --target .
```

如果只安装 Codex 侧：

```bash
python3 templates/self-learning/install.py --target . --no-claude
```

如果只安装 Claude Code 侧：

```bash
python3 templates/self-learning/install.py --target . --no-codex
```

如果不想安装 hooks：

```bash
python3 templates/self-learning/install.py --target . --no-hooks
```

手动安装也可以：

```bash
mkdir -p .agents/skills .claude/skills .learnings
cp -R templates/self-learning/skills/digest .agents/skills/
cp -R templates/self-learning/skills/maintain-learnings .agents/skills/
cp -R templates/self-learning/skills/digest .claude/skills/
cp -R templates/self-learning/skills/maintain-learnings .claude/skills/
rm -rf .claude/skills/maintain-learnings/agents
mkdir -p .codex/hooks .claude/hooks
cp templates/self-learning/hooks/read-learnings.sh .codex/hooks/
cp templates/self-learning/hooks/read-learnings.sh .claude/hooks/
cp templates/self-learning/learnings/LEARNINGS.md .learnings/LEARNINGS.md
cp templates/self-learning/learnings/ERRORS.md .learnings/ERRORS.md
cp templates/self-learning/learnings/RULES.md .learnings/RULES.md
```

然后把 `hooks/codex-hooks.json.template` 合并进 `.codex/hooks.json`，把 `hooks/claude-settings.json.template` 合并进 `.claude/settings.json`。

## Project Rules Snippet

把 `AGENTS.snippet.md` 中的内容合并进目标项目的 `AGENTS.md`。如果目标项目也用 Claude Code，并且 `CLAUDE.md` 通过 `@AGENTS.md` 引用项目规则，不需要再复制一份规则。

## Commands

审计经验库：

```bash
python3 .agents/skills/maintain-learnings/scripts/audit_learnings.py --root . --skills-dir .agents/skills --rules-file AGENTS.md --hooks-path .codex/hooks
```

Claude Code 侧审计：

```bash
python3 .claude/skills/maintain-learnings/scripts/audit_learnings.py --root . --skills-dir .claude/skills --rules-file CLAUDE.md --hooks-path .claude/hooks
```

检查 Codex / Claude Code skill 是否都有对应功能：

```bash
python3 .agents/skills/maintain-learnings/scripts/sync_platform_skills.py --root . --skill maintain-learnings
```

从 Codex dry-run 同步到 Claude Code：

```bash
python3 .agents/skills/maintain-learnings/scripts/sync_platform_skills.py --root . --from-platform agents --to-platform claude --skill maintain-learnings
```

确认后应用：

```bash
python3 .agents/skills/maintain-learnings/scripts/sync_platform_skills.py --root . --from-platform agents --to-platform claude --skill maintain-learnings --apply
```

## Customize

- 把 `AGENTS.snippet.md` 中的 `<PROJECT_NAME>`、`<PRIMARY_OUTPUT>`、`<WORKFLOW>` 替换成目标项目自己的名称。
- 如果项目不用 Claude Code，可以只安装 `.agents/skills`，但保留同步脚本也无妨。
- 如果项目不用 Codex UI，可以删除 `.agents/skills/maintain-learnings/agents/openai.yaml`。
- 如果目标项目已有 hook 配置，不要直接覆盖；合并 `SessionStart` 中的 read-learnings command 即可。
