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
- `.agents/skills/` 是 Codex 侧技能副本；不得用 `.agents/skills/` 反向覆盖 `.claude/skills/`。
- Codex 架构、Hook、工具调用方式或技能加载方式的更新，只修改 `.agents/` 与 `.codex/`。
- 只有通用学习流程、输出格式、错误经验等平台无关内容，才需要在比对差异后同步到 `.claude/skills/`；同步时必须保留 Claude Code 专属能力。

## 当前平台差异

- `.agents/skills/digest/SKILL.md` 中的核心规则提升目标是 `AGENTS.md`。
- `.claude/skills/digest/SKILL.md` 中的核心规则提升目标仍是 `CLAUDE.md`。
