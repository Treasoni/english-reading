---
name: manifest-platform
description: Install, configure, migrate, and validate a portable manifest registry for agent workflows, skills, subagents, and hooks. Use when a project needs manifest.yaml-based discovery, artifact versioning, dependency checks, capability declarations, permission-policy review, or reusable agent-platform setup.
---

# Manifest Platform

Install the bundled registry before creating or migrating manifests. In this repository, `skills/manifest-platform` is the canonical distributable package; runtime mirrors under `.agents/skills` or other profiles are generated from it.

```bash
bash skills/manifest-platform/scripts/install.sh --target .
```

For another project, copy this entire `skills/manifest-platform/` folder into that project's skill source or profile `skills_dir`, then run the installer from the copied location. The installer infers a default runtime directory from where the skill lives: the shared Codex skill directory installs a Codex-style registry, while `.claude/skills` and `.agent/skills` install under their matching runtime directories. Use `--agent-dir` and related directory options when the target project needs a layout different from the inferred default:

```bash
bash <skills-dir>/manifest-platform/scripts/install.sh --target /path/to/project --agent-dir .claude
bash <skills-dir>/manifest-platform/scripts/install.sh --target /path/to/project --agent-dir .agent --skills-dir .agent/skills
```

Read [the manifest contract](references/manifest-contract.md) before defining a manifest, and read `assets/platform/README.md` before changing the registry layout or its commands.

## Workflow

1. Inspect the project layout and preserve unrelated changes.
2. Install the registry. Review a differing existing registry before using `--force`; never overwrite it by default.
3. Review `<agent-dir>/platform/registry.yaml`. Its defaults are generated from the installer options; change only the discovery paths or hook registration file that do not match the target project.
4. Add `manifest.yaml` for every artifact in a configured discovery directory. Keep `metadata.name` equal to its containing directory.
5. Declare the narrowest truthful permissions. A manifest requests permissions; enforce them separately through the host runtime’s approval and tool policy.
6. Add dependency IDs only after their target manifests exist. For a Hook, retain the actual registration in the JSON file declared by `policy.hooksConfig`.
7. Run `python3 <agent-dir>/platform/manifest-registry.py --root . validate` and resolve every failure before handoff.

## Reuse

Copy or sync this entire skill folder into another project's skill directory, then run its installer against that project. The installer supplies a dependency-free validator, JSON Schema, registry policy, and reference documentation, and it can generate registry paths for `.codex`, `.claude`, `.agent`, or a custom agent directory. Use `manifest-registry.py init` to create an initial manifest before refining its capabilities and permissions.

Do not treat the manifest as a sandbox. It is an auditable declaration, not a permission grant or a bypass of host policy.
