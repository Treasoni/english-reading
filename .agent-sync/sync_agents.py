#!/usr/bin/env python3
"""Synchronize shared agent files from a canonical profile to configured targets."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


TEXT_SUFFIXES = {".md", ".py", ".sh", ".json", ".yaml", ".yml", ".txt"}
PRIVATE_SKILL_PARTS = {"agents"}
MCP_BEGIN = "# BEGIN agent-sync:mcp"
MCP_END = "# END agent-sync:mcp"
PATH_KEYS = {"skills", "rules", "hooks", "hook_config", "scripts", "workflows", "instructions", "mcp"}
SCOPES = ("skills", "rules", "hooks", "scripts", "workflows", "mcp")


@dataclass(frozen=True)
class Finding:
    level: str
    message: str


def yaml_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def load_profile(path: Path) -> dict[str, Any]:
    """Read the plain mapping subset used by project agent-profile YAML files."""
    profile: dict[str, Any] = {}
    section: dict[str, Any] | None = None
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if ":" not in raw:
            raise ValueError(f"{path}:{number}: expected key: value")
        key, value = raw.strip().split(":", 1)
        if indent == 0:
            if value.strip():
                profile[key] = yaml_scalar(value)
                section = None
            else:
                section = {}
                profile[key] = section
        elif indent == 2 and section is not None and value.strip():
            section[key] = yaml_scalar(value)
        else:
            raise ValueError(f"{path}:{number}: only top-level keys and one mapping level are supported")

    paths = profile.get("paths")
    missing = [key for key in ("id", "name", "canonical", "mcp_format") if key not in profile]
    if not isinstance(paths, dict):
        missing.append("paths")
    elif missing_paths := sorted(PATH_KEYS - set(paths)):
        missing.append("paths." + ", paths.".join(missing_paths))
    if missing:
        raise ValueError(f"{path}: missing " + ", ".join(missing))
    if not isinstance(profile["id"], str) or not profile["id"]:
        raise ValueError(f"{path}: id must be a non-empty string")
    return profile


def load_profiles(root: Path) -> list[dict[str, Any]]:
    profile_dir = root / ".agent-sync/agents"
    files = sorted(profile_dir.glob("*.yaml")) + sorted(profile_dir.glob("*.yml"))
    if not files:
        raise ValueError(f"no agent profile YAML files found in {profile_dir}")
    profiles = [load_profile(path) for path in files]
    ids = [profile["id"] for profile in profiles]
    if len(ids) != len(set(ids)):
        raise ValueError("agent profile ids must be unique")
    canonicals = [profile for profile in profiles if profile["canonical"] is True]
    if len(canonicals) != 1:
        raise ValueError("exactly one agent profile must set canonical: true")
    return profiles


def transform(text: str, source: dict[str, Any], target: dict[str, Any]) -> str:
    output = text
    keys = sorted(PATH_KEYS - {"mcp"}, key=lambda key: len(source["paths"][key]), reverse=True)
    for key in keys:
        source_path = source["paths"][key]
        target_path = target["paths"][key]
        if source_path != target_path:
            output = output.replace(source_path, target_path)
    output = output.replace(f":{source['id']}:", f":{target['id']}:")
    output = output.replace(f"{source['name']} hook", f"{target['name']} hook")
    output = output.replace(f"{source['id']}-hook", f"{target['id']}-hook")
    return output


def normalized(text: str, profiles: list[dict[str, Any]]) -> str:
    output = text.replace("\r\n", "\n")
    replacements = [
        (profile["paths"][key], "{" + key.upper() + "}")
        for profile in profiles
        for key in PATH_KEYS - {"mcp"}
    ]
    for path, placeholder in sorted(replacements, key=lambda item: len(item[0]), reverse=True):
        output = output.replace(path, placeholder)
    for profile in profiles:
        output = output.replace(f":{profile['id']}:", ":{AGENT}:")
        output = output.replace(f"{profile['name']} hook", "{HOOK}")
        output = output.replace(f"{profile['id']}-hook", "{HOOK}")
    return output.strip()


def source_files(base: Path, *, skill_mode: bool = False) -> dict[Path, Path]:
    if not base.exists():
        return {}
    files: dict[Path, Path] = {}
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(base)
        if skill_mode and PRIVATE_SKILL_PARTS.intersection(rel.parts):
            continue
        files[rel] = path
    return files


def rendered_bytes(source_path: Path, source: dict[str, Any], target: dict[str, Any]) -> bytes:
    if source_path.suffix.lower() not in TEXT_SUFFIXES:
        return source_path.read_bytes()
    return transform(source_path.read_text(encoding="utf-8"), source, target).encode("utf-8")


def sync_tree(root: Path, source_root: Path, target_root: Path, source: dict[str, Any], target: dict[str, Any], profiles: list[dict[str, Any]], apply: bool, *, skill_mode: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    for rel, source_path in sorted(source_files(source_root, skill_mode=skill_mode).items()):
        target_path = target_root / rel
        expected = rendered_bytes(source_path, source, target)
        actual = target_path.read_bytes() if target_path.exists() else None
        if actual == expected:
            continue
        if actual is not None and source_path.suffix.lower() in TEXT_SUFFIXES and target_path.suffix.lower() in TEXT_SUFFIXES:
            if normalized(source_path.read_text(encoding="utf-8"), profiles) == normalized(target_path.read_text(encoding="utf-8"), profiles):
                continue
        action = "updated" if actual is not None else "created"
        findings.append(Finding("DRIFT", f"{action}: {target_path.relative_to(root)}"))
        if apply:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(expected)
    return findings


def sync_instructions(root: Path, source: dict[str, Any], target: dict[str, Any], apply: bool) -> list[Finding]:
    source_path = root / source["paths"]["instructions"]
    target_path = root / target["paths"]["instructions"]
    expected = rendered_bytes(source_path, source, target)
    actual = target_path.read_bytes() if target_path.exists() else None
    if actual == expected:
        return []
    if apply:
        target_path.write_bytes(expected)
    return [Finding("DRIFT", f"{'updated' if actual is not None else 'created'}: {target_path.relative_to(root)}")]


def sync_hook_config(root: Path, source: dict[str, Any], target: dict[str, Any], apply: bool) -> list[Finding]:
    source_path = root / source["paths"]["hook_config"]
    target_path = root / target["paths"]["hook_config"]
    source_data = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(source_data, dict) or "hooks" not in source_data:
        raise ValueError(f"{source_path} must be a JSON object with a hooks key")
    transformed_hooks = json.loads(transform(json.dumps(source_data["hooks"], ensure_ascii=False), source, target))
    target_data: dict[str, Any] = {}
    if target_path.exists():
        current = json.loads(target_path.read_text(encoding="utf-8"))
        if not isinstance(current, dict):
            raise ValueError(f"{target_path} must be a JSON object")
        target_data = current
    target_data["hooks"] = transformed_hooks
    expected = json.dumps(target_data, ensure_ascii=False, indent=2) + "\n"
    actual = target_path.read_text(encoding="utf-8") if target_path.exists() else None
    if actual == expected:
        return []
    if apply:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(expected, encoding="utf-8")
    return [Finding("DRIFT", f"{'updated' if actual is not None else 'created'}: {target_path.relative_to(root)}")]


def quote_toml(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def toml_mcp_block(servers: dict[str, Any]) -> str:
    lines = [MCP_BEGIN, "# Generated from .agent-sync/mcp-servers.json. Do not edit this block."]
    for name, raw in sorted(servers.items()):
        if not isinstance(raw, dict):
            raise ValueError(f"MCP server {name!r} must be an object")
        transport = raw.get("type", "stdio")
        table = f'[mcp_servers.{quote_toml(name)}]'
        if transport in ("stdio", None):
            command = raw.get("command")
            args = raw.get("args", [])
            env = raw.get("env", {})
            if not isinstance(command, str) or not command or not isinstance(args, list) or not all(isinstance(item, str) for item in args) or not isinstance(env, dict) or not all(isinstance(key, str) and isinstance(value, str) for key, value in env.items()):
                raise ValueError(f"stdio MCP server {name!r} needs command, string args, and string env values")
            lines.extend(["", table, f"command = {quote_toml(command)}", "args = [" + ", ".join(quote_toml(item) for item in args) + "]"])
            if env:
                lines.append(f'[mcp_servers.{quote_toml(name)}.env]')
                lines.extend(f"{quote_toml(key)} = {quote_toml(value)}" for key, value in sorted(env.items()))
        elif transport in ("http", "streamable-http"):
            url = raw.get("url")
            headers = raw.get("headers", {})
            if not isinstance(url, str) or not url or not isinstance(headers, dict) or not all(isinstance(key, str) and isinstance(value, str) for key, value in headers.items()):
                raise ValueError(f"HTTP MCP server {name!r} needs url and string headers")
            lines.extend(["", table, f"url = {quote_toml(url)}"])
            if headers:
                lines.append(f'[mcp_servers.{quote_toml(name)}.http_headers]')
                lines.extend(f"{quote_toml(key)} = {quote_toml(value)}" for key, value in sorted(headers.items()))
        else:
            raise ValueError(f"MCP server {name!r} has unsupported transport {transport!r}")
    lines.append(MCP_END)
    return "\n".join(lines) + "\n"


def replace_mcp_block(existing: str, block: str) -> str:
    start, end = existing.find(MCP_BEGIN), existing.find(MCP_END)
    if start == -1 and end == -1:
        return (existing.rstrip() + "\n\n" if existing.strip() else "") + block
    if start == -1 or end == -1 or end < start:
        raise ValueError("Codex MCP configuration has an incomplete agent-sync block")
    return existing[:start] + block.rstrip("\n") + existing[end + len(MCP_END):]


def sync_mcp(root: Path, profiles: list[dict[str, Any]], apply: bool) -> list[Finding]:
    manifest = root / ".agent-sync/mcp-servers.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if set(data) != {"mcpServers"} or not isinstance(data["mcpServers"], dict):
        raise ValueError("mcp-servers.json must contain exactly one object: mcpServers")
    json_output = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    toml_output = toml_mcp_block(data["mcpServers"])
    outputs: dict[Path, str] = {}
    for profile in profiles:
        path = root / profile["paths"]["mcp"]
        if profile["mcp_format"] == "project-json":
            outputs[path] = json_output
        elif profile["mcp_format"] == "codex-toml":
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            outputs[path] = replace_mcp_block(current, toml_output)
        else:
            raise ValueError(f"{profile['id']}: unsupported mcp_format {profile['mcp_format']!r}")
    findings: list[Finding] = []
    for path, expected in outputs.items():
        actual = path.read_text(encoding="utf-8") if path.exists() else None
        if actual == expected:
            continue
        findings.append(Finding("DRIFT", f"{'updated' if actual is not None else 'created'}: {path.relative_to(root)}"))
        if apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
    return findings


def synchronize(root: Path, scopes: list[str], apply: bool, source_id: str | None = None) -> list[Finding]:
    profiles = load_profiles(root)
    source = next(profile for profile in profiles if profile["canonical"] is True)
    if source_id is not None:
        source = next((profile for profile in profiles if profile["id"] == source_id), None)
        if source is None:
            known = ", ".join(profile["id"] for profile in profiles)
            raise ValueError(f"unknown --from profile {source_id!r}; configured profiles: {known}")
    targets = [profile for profile in profiles if profile is not source]
    findings: list[Finding] = []
    for scope in scopes:
        if scope == "mcp":
            findings.extend(sync_mcp(root, profiles, apply))
            continue
        for target in targets:
            if scope == "rules":
                findings.extend(sync_tree(root, root / source["paths"]["rules"], root / target["paths"]["rules"], source, target, profiles, apply))
                findings.extend(sync_instructions(root, source, target, apply))
            elif scope == "skills":
                findings.extend(sync_tree(root, root / source["paths"]["skills"], root / target["paths"]["skills"], source, target, profiles, apply, skill_mode=True))
            elif scope == "hooks":
                findings.extend(sync_tree(root, root / source["paths"]["hooks"], root / target["paths"]["hooks"], source, target, profiles, apply))
                findings.extend(sync_hook_config(root, source, target, apply))
            else:
                findings.extend(sync_tree(root, root / source["paths"][scope], root / target["paths"][scope], source, target, profiles, apply))
    return findings


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--apply", action="store_true", help="write generated outputs; default is check only")
    parser.add_argument("--check", action="store_true", help="explicit check-only mode")
    parser.add_argument("--scope", choices=SCOPES, action="append", help="limit to one or more shared areas")
    parser.add_argument("--from", dest="source_id", help="use this profile as the source for this run instead of canonical")
    args = parser.parse_args(argv)
    if args.apply and args.check:
        parser.error("--apply and --check cannot be used together")
    try:
        findings = synchronize(Path(args.root).resolve(), args.scope or list(SCOPES), args.apply, args.source_id)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 2
    if not findings:
        print("[OK] shared agent configuration is synchronized")
        return 0
    for finding in findings:
        print(f"[{finding.level}] {finding.message}")
    if args.apply:
        print("[OK] synchronization applied")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
