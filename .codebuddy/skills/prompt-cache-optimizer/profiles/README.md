# Agent Profiles

Profiles describe how reusable templates map into a target agent project.

| Profile | Skills | Rules | Hooks | Entry |
| --- | --- | --- | --- | --- |
| `codex` | `.agents/skills` | `.codex/rules` | `.codex/hooks` | `AGENTS.md` |
| `claude` | `.claude/skills` | `.claude/rules` | `.claude/hooks` | `CLAUDE.md` |
| `codebuddy` | `.codebuddy/skills` | `.codebuddy/rules` | `.codebuddy/hooks` | `CODEBUDDY.md` |
| `cursor` | `.cursor/skills` | `.cursor/rules` | — | `AGENTS.md` |
| `gemini` | `.gemini/skills` | `.gemini/rules` | — | `GEMINI.md` |
| `github-copilot` | `.github/skills` | `.github/instructions` | — | `.github/copilot-instructions.md` |
| `cline` | `.cline/skills` | `.clinerules` | — | `AGENTS.md` |
| `roo-code` | `.roo/skills` | `.roo/rules` | — | `AGENTS.md` |
| `windsurf` | `.windsurf/skills` | `.windsurf/rules` | — | `AGENTS.md` |
| `opencode` | `.opencode/skills` | `.opencode/rules` | — | `AGENTS.md` |
| `qwen-code` | `.qwen/skills` | `.qwen/rules` | — | `QWEN.md` |
| `generic` | `.agent/skills` | `.agent/rules` | `.agent/hooks` | `AGENTS.md` |

These files are runtime contracts. The Python template installers read them
directly, while shell tools use them when this repository is available and
retain their historical standalone defaults otherwise. `agent_dir` and
`scripts_dir` keep agent configuration and managed helper scripts separate
when an agent's native rules directory uses a different layout. Custom scalar
YAML profiles can be passed with `--profile-file`.

For the built-in profiles, `scripts/install.py --target <project> --detect`
reports matching layouts and `--profile <name>` keeps manual selection
available. The detector deliberately ignores an `AGENTS.md` file by itself,
because that shared filename is not enough evidence of a particular runtime.
