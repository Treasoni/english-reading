# 考研英语阅读精读 Vault

这是一个 Obsidian 学习库：沉淀考研英语阅读真题的原文、翻译、语法、长难句、生词与跨篇总结。它通过 Codex 和 Claude Code 的同名技能辅助精读，不提供或承诺独立的 Python CLI。

## 使用方式

在 Obsidian 中打开此目录。处理一篇新阅读时，按项目规则使用以下六步流程：

| 步骤 | 技能 | 产出 |
| --- | --- | --- |
| 1 | `format-article` | `intermediate/<topic>/formatted-article.md` |
| 2 | `translate` | `intermediate/<topic>/translation.md` |
| 3 | `organize-grammar` | `intermediate/<topic>/grammar-notes.md` |
| 4 | `analyze-sentence` | 分析块内联至 `formatted-article.md` |
| 5 | `compile-note` | `<year>阅读/<topic>-精读笔记.md` |
| 6 | `extract-vocabulary` | 最终笔记中的词汇表与练习 |

跨篇整理使用 `summarize-grammar`；只有用户明确提出时才运行 `digest` 维护经验库。

## 目录约定

```text
├── 2000阅读/ ...                  # 已完成的最终精读笔记
├── intermediate/<topic>/          # 每篇文章的阶段性产物
├── .agents/skills/                # Codex 技能定义
├── .claude/skills/                # Claude Code 同步技能定义
├── .codebuddy/skills/             # CodeBuddy 的核心学习技能
├── .learnings/                    # 经验库（本地状态，不纳入版本控制）
└── scripts/                       # Vault 一致性校验
```

`<topic>` 必须使用完整 slug，例如 `2005-passage2-global-warming`；中间目录、最终文件名与 YAML frontmatter 的 `topic` 应完全一致。

## 校验

每次修改共享技能、规则或笔记目录后运行：

```bash
bash scripts/verify-vault.sh
```

该命令会检查：

- Codex 与 Claude Code 的共享技能语义是否一致（平台专属 frontmatter 字段除外）；
- 两套工作流路由与环境模板规则是否有效；
- 中间产物、最终笔记、所在年份目录和 YAML `topic` 是否一致。

进行发布级完整性检查时使用：

```bash
bash scripts/verify-vault.sh --strict
```

处于学习中的篇章可在对应 `intermediate/<topic>/STATUS.md` 中声明 `status: in_progress`；普通校验会提示它，严格校验仍会阻止将其视为完成。

## 多 Agent 支持范围

Codex 与 Claude Code 共享完整的 20 项技能并通过同步脚本守护。CodeBuddy 仅提供精读流程直接需要的核心技能；系统维护、工作流和安全审计能力以 Codex / Claude Code 为准。详见 [AGENTS.md](AGENTS.md) 与 [CODEBUDDY.md](CODEBUDDY.md)。
