# Agent Platform Registry

`manifest.yaml` is the contract for every Workflow, Skill, Subagent, and Hook. The registry discovers manifests from the four configured directories in `registry.yaml`, validates their version, dependencies, and requested permissions, and checks that each Hook is registered in the JSON file declared by `policy.hooksConfig`.

The registry is declarative: permissions are requests that a runtime policy must enforce; this validator does not grant tools or bypass host approvals.

## Commands

```bash
python3 <agent-dir>/platform/manifest-registry.py --root . validate
python3 <agent-dir>/platform/manifest-registry.py --root . list
python3 <agent-dir>/platform/manifest-registry.py --root . init \
  --kind Skill --name example --entrypoint SKILL.md \
  --description "Describe the new artifact"
```

The installer writes the registry into `<agent-dir>/platform` and generates discovery paths from its options. It infers `<agent-dir>` from the copied skill location when possible: the shared Codex skill directory maps to the Codex layout, `.claude/skills` maps to `.claude`, and `.agent/skills` maps to `.agent`. For a custom runtime directory, run the installer with `--agent-dir` and optional `--skills-dir`, `--workflows-dir`, `--subagents-dir`, `--hooks-dir`, and `--hooks-config`.

Keep each artifact’s `manifest.yaml` inside the directory configured for its kind. During migration, an agent or hook manifest may use a relative entrypoint such as `../outline-generator.md`; entrypoints may never leave the project root.

The validator fails if a conventional `SKILL.md`, `workflow.md`, flat agent `.md`, or flat hook `.sh` in a configured directory has no matching manifest. Bump `metadata.version` using SemVer: MAJOR for an incompatible contract, MINOR for compatible capabilities or dependencies, and PATCH for metadata-only corrections.

The supported YAML subset deliberately uses mappings, block lists, quoted strings, booleans, and empty `[]`/`{}` values. This keeps the validator dependency-free. Use the JSON Schema for editor completion or a fuller YAML toolchain.
