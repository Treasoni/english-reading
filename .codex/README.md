# Codex 配置说明

本目录只放 Codex 专用配置，避免影响已有 Claude Code 配置。

## 对应关系

- 规则入口：Codex 读取仓库根目录的 `AGENTS.md`。
- 技能目录：Codex 使用 `.agents/skills/`。
- 经验库：每次任务前读取 `.learnings/RULES.md`、`.learnings/LEARNINGS.md`、`.learnings/ERRORS.md`。
- Hook：`.codex/hooks.json` 调用 `.codex/hooks/read-learnings.sh` 注入经验库提醒。

## 与 Claude Code 的隔离

- 不修改 `.claude/settings.json`、`.claude/settings.local.json` 或 `.claude/hooks/`。
- `.claude/skills/` 仍归 Claude Code 使用。
- `.agents/skills/` 是 Codex 侧技能副本；除平台适配外，应与 `.claude/skills/` 保持同步。

## 当前平台差异

- `.agents/skills/digest/SKILL.md` 中的核心规则提升目标是 `AGENTS.md`。
- `.claude/skills/digest/SKILL.md` 中的核心规则提升目标仍是 `CLAUDE.md`。
