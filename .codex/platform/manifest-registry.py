#!/usr/bin/env python3
"""Discover and validate unified Agent Platform manifests without third-party packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

API_VERSION = "agent-platform/v1"
KINDS = ("Workflow", "Skill", "Subagent", "Hook")
PERMISSIONS = ("filesystem", "network", "subprocess", "git")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


class ManifestError(ValueError):
    pass


@dataclass(frozen=True)
class Artifact:
    path: Path
    data: dict[str, Any]

    @property
    def kind(self) -> str:
        return self.data["kind"]

    @property
    def name(self) -> str:
        return self.data["metadata"]["name"]

    @property
    def identifier(self) -> str:
        return f"{self.kind}/{self.name}"


def parse_scalar(value: str, path: Path, line_no: int) -> Any:
    value = value.strip()
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "~"}:
        return None
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ManifestError(f"{path}:{line_no}: invalid quoted string: {exc.msg}") from exc
        if not isinstance(parsed, str):
            raise ManifestError(f"{path}:{line_no}: scalar must be a string")
        return parsed
    if value.startswith("'"):
        if not value.endswith("'") or len(value) == 1:
            raise ManifestError(f"{path}:{line_no}: unterminated single-quoted string")
        return value[1:-1].replace("''", "'")
    if value.startswith(("[", "{")):
        raise ManifestError(f"{path}:{line_no}: use block lists and mappings (only [] and {{}} are supported inline)")
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    """Read the deliberately small YAML subset used by this manifest contract."""
    rows: list[tuple[int, int, str]] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if "\t" in raw:
            raise ManifestError(f"{path}:{line_no}: tabs are not supported for indentation")
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        rows.append((line_no, indent, raw[indent:]))
    if not rows:
        raise ManifestError(f"{path}: empty YAML file")

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(rows) or rows[index][1] != indent:
            raise ManifestError(f"{path}: expected an indented block")
        is_list = rows[index][2].startswith("- ") or rows[index][2] == "-"
        result: Any = [] if is_list else {}
        while index < len(rows):
            line_no, current_indent, content = rows[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise ManifestError(f"{path}:{line_no}: unexpected indentation")
            if is_list:
                if not (content.startswith("- ") or content == "-"):
                    raise ManifestError(f"{path}:{line_no}: cannot mix a list and a mapping")
                item = content[1:].strip()
                if not item:
                    if index + 1 >= len(rows) or rows[index + 1][1] <= indent:
                        raise ManifestError(f"{path}:{line_no}: list item requires a value")
                    child, index = parse_block(index + 1, rows[index + 1][1])
                    result.append(child)
                else:
                    result.append(parse_scalar(item, path, line_no))
                    index += 1
                continue
            match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):(.*)$", content)
            if not match:
                raise ManifestError(f"{path}:{line_no}: expected 'key: value'")
            key, raw_value = match.groups()
            if key in result:
                raise ManifestError(f"{path}:{line_no}: duplicate key '{key}'")
            value = raw_value.strip()
            if value:
                result[key] = parse_scalar(value, path, line_no)
                index += 1
            elif index + 1 < len(rows) and rows[index + 1][1] > indent:
                result[key], index = parse_block(index + 1, rows[index + 1][1])
            else:
                result[key] = None
                index += 1
        return result, index

    data, next_index = parse_block(0, rows[0][1])
    if next_index != len(rows) or not isinstance(data, dict):
        raise ManifestError(f"{path}: top-level value must be a mapping")
    return data


def project_root(raw_root: str) -> Path:
    root = Path(raw_root).resolve()
    if not root.is_dir():
        raise ManifestError(f"{root}: expected an existing project directory")
    return root


def relative_to(path: Path, base: Path) -> Path | None:
    try:
        return path.relative_to(base)
    except ValueError:
        return None


def project_relative_path(root: Path, raw_path: str, label: str) -> Path:
    path = (root / raw_path).resolve()
    if relative_to(path, root) is None:
        raise ManifestError(f"registry: {label} escapes the project: {raw_path}")
    return path


def registry_path(root: Path, raw_registry: str | None) -> Path:
    if raw_registry:
        raw_path = Path(raw_registry)
        return raw_path.resolve() if raw_path.is_absolute() else (root / raw_path).resolve()
    return Path(__file__).resolve().parent / "registry.yaml"


def load_registry(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ManifestError(f"{path}: registry configuration is missing; run the manifest-platform installer")
    data = load_yaml(path)
    if data.get("apiVersion") != API_VERSION:
        raise ManifestError(f"{path}: apiVersion must be {API_VERSION}")
    discovery = data.get("discovery")
    policy = data.get("policy")
    if not isinstance(discovery, dict) or not isinstance(discovery.get("kindDirectories"), dict):
        raise ManifestError(f"{path}: discovery.kindDirectories must be a mapping")
    if not isinstance(policy, dict) or not isinstance(policy.get("allowedPermissions"), dict):
        raise ManifestError(f"{path}: policy.allowedPermissions must be a mapping")
    return data


def manifest_paths(root: Path, registry: dict[str, Any]) -> list[tuple[str, Path]]:
    paths: list[tuple[str, Path]] = []
    for kind in KINDS:
        raw_dir = registry["discovery"]["kindDirectories"].get(kind)
        if not isinstance(raw_dir, str):
            raise ManifestError(f"registry: discovery.kindDirectories.{kind} must be a string")
        base = project_relative_path(root, raw_dir, f"discovery.kindDirectories.{kind}")
        if base.exists():
            paths.extend((kind, path) for path in sorted(base.glob("*/manifest.yaml")))
    return paths


def missing_manifest_errors(root: Path, registry: dict[str, Any], discovered: list[tuple[str, Path]]) -> list[str]:
    """Require manifests for the repository's established artifact conventions."""
    known = {path.resolve() for _, path in discovered}
    directories = registry["discovery"]["kindDirectories"]
    errors: list[str] = []
    for kind, entrypoint in (("Skill", "SKILL.md"), ("Workflow", "workflow.md")):
        base = root / directories[kind]
        if not base.is_dir():
            continue
        for child in base.iterdir():
            expected = child / "manifest.yaml"
            if child.is_dir() and (child / entrypoint).is_file() and expected.resolve() not in known:
                errors.append(f"{child.relative_to(root)}: {kind} entrypoint exists but manifest.yaml is missing")
    agent_base = root / directories["Subagent"]
    if agent_base.is_dir():
        for entrypoint in agent_base.glob("*.md"):
            expected = agent_base / entrypoint.stem / "manifest.yaml"
            if expected.resolve() not in known:
                errors.append(f"{entrypoint.relative_to(root)}: Subagent entrypoint exists but {expected.relative_to(root)} is missing")
    hook_base = root / directories["Hook"]
    if hook_base.is_dir():
        for entrypoint in hook_base.glob("*.sh"):
            expected = hook_base / entrypoint.stem / "manifest.yaml"
            if expected.resolve() not in known:
                errors.append(f"{entrypoint.relative_to(root)}: Hook entrypoint exists but {expected.relative_to(root)} is missing")
    return errors


def require_mapping(value: Any, label: str, path: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManifestError(f"{path}: {label} must be a mapping")
    return value


def require_allowed_keys(value: dict[str, Any], label: str, allowed: set[str], path: Path) -> None:
    unexpected = sorted(set(value) - allowed)
    if unexpected:
        raise ManifestError(f"{path}: {label} has unsupported field(s): {', '.join(unexpected)}")


def require_string(value: Any, label: str, path: Path) -> str:
    if not isinstance(value, str) or not value:
        raise ManifestError(f"{path}: {label} must be a non-empty string")
    return value


def validate_manifest(root: Path, registry: dict[str, Any], expected_kind: str, path: Path) -> Artifact:
    data = load_yaml(path)
    require_allowed_keys(data, "manifest", {"apiVersion", "kind", "metadata", "spec"}, path)
    if data.get("apiVersion") != API_VERSION:
        raise ManifestError(f"{path}: apiVersion must be {API_VERSION}")
    kind = data.get("kind")
    if kind not in KINDS:
        raise ManifestError(f"{path}: kind must be one of {', '.join(KINDS)}")
    if kind != expected_kind:
        raise ManifestError(f"{path}: discovered below {expected_kind} but declares {kind}")
    metadata = require_mapping(data.get("metadata"), "metadata", path)
    require_allowed_keys(metadata, "metadata", {"name", "version", "description"}, path)
    name = require_string(metadata.get("name"), "metadata.name", path)
    if not NAME_RE.fullmatch(name):
        raise ManifestError(f"{path}: metadata.name must be lowercase kebab-case")
    if path.parent.name != name:
        raise ManifestError(f"{path}: metadata.name must match its directory name ({path.parent.name})")
    version = require_string(metadata.get("version"), "metadata.version", path)
    if not SEMVER_RE.fullmatch(version):
        raise ManifestError(f"{path}: metadata.version must be SemVer (for example 1.2.0)")
    require_string(metadata.get("description"), "metadata.description", path)
    spec = require_mapping(data.get("spec"), "spec", path)
    require_allowed_keys(spec, "spec", {"entrypoint", "capabilities", "permissions", "dependsOn", "lifecycle", "event"}, path)
    entrypoint = require_string(spec.get("entrypoint"), "spec.entrypoint", path)
    entrypoint_path = (path.parent / entrypoint).resolve()
    if relative_to(entrypoint_path, root) is None:
        raise ManifestError(f"{path}: spec.entrypoint must remain inside the project root")
    if not entrypoint_path.is_file():
        raise ManifestError(f"{path}: spec.entrypoint does not exist: {entrypoint}")
    capabilities = spec.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities or not all(isinstance(item, str) and item for item in capabilities):
        raise ManifestError(f"{path}: spec.capabilities must be a non-empty list of strings")
    if len(capabilities) != len(set(capabilities)):
        raise ManifestError(f"{path}: spec.capabilities must not contain duplicates")
    permissions = require_mapping(spec.get("permissions"), "spec.permissions", path)
    require_allowed_keys(permissions, "spec.permissions", set(PERMISSIONS), path)
    if set(permissions) != set(PERMISSIONS):
        raise ManifestError(f"{path}: spec.permissions must declare exactly: {', '.join(PERMISSIONS)}")
    allowed = registry["policy"]["allowedPermissions"]
    for permission in PERMISSIONS:
        allowed_values = allowed.get(permission)
        if not isinstance(allowed_values, list) or permissions[permission] not in allowed_values:
            raise ManifestError(f"{path}: unsupported {permission} permission '{permissions[permission]}'")
    dependencies = spec.get("dependsOn")
    if not isinstance(dependencies, list) or not all(isinstance(item, str) for item in dependencies):
        raise ManifestError(f"{path}: spec.dependsOn must be a list of Artifact IDs")
    if len(dependencies) != len(set(dependencies)):
        raise ManifestError(f"{path}: spec.dependsOn must not contain duplicates")
    lifecycle = require_mapping(spec.get("lifecycle"), "spec.lifecycle", path)
    require_allowed_keys(lifecycle, "spec.lifecycle", {"discoverable", "deprecated"}, path)
    if not isinstance(lifecycle.get("discoverable"), bool) or not isinstance(lifecycle.get("deprecated"), bool):
        raise ManifestError(f"{path}: spec.lifecycle.discoverable and deprecated must be booleans")
    event = spec.get("event")
    if kind == "Hook":
        events = registry["policy"].get("hookEvents")
        if not isinstance(events, list) or event not in events:
            raise ManifestError(f"{path}: Hook spec.event must be an allowed event")
    elif event is not None:
        raise ManifestError(f"{path}: spec.event is only valid for Hook manifests")
    return Artifact(path=path, data=data)


def hook_config_path(root: Path, registry: dict[str, Any]) -> Path:
    policy = registry.get("policy")
    if not isinstance(policy, dict):
        raise ManifestError("registry: policy must be a mapping")
    configured = policy.get("hooksConfig")
    if configured is not None:
        if not isinstance(configured, str) or not configured:
            raise ManifestError("registry: policy.hooksConfig must be a non-empty string")
        return project_relative_path(root, configured, "policy.hooksConfig")

    raw_hook_dir = registry["discovery"]["kindDirectories"].get("Hook")
    if not isinstance(raw_hook_dir, str):
        raise ManifestError("registry: discovery.kindDirectories.Hook must be a string")
    hook_dir = project_relative_path(root, raw_hook_dir, "discovery.kindDirectories.Hook")
    return hook_dir.parent / "hooks.json"


def validate_hooks(root: Path, registry: dict[str, Any], artifacts: list[Artifact]) -> list[str]:
    hook_artifacts = [artifact for artifact in artifacts if artifact.kind == "Hook"]
    if not hook_artifacts:
        return []
    config_path = hook_config_path(root, registry)
    if not config_path.is_file():
        return [f"{config_path}: Hook manifests exist but the hook registration JSON is missing"]
    try:
        hooks = json.loads(config_path.read_text(encoding="utf-8")).get("hooks", {})
    except json.JSONDecodeError as exc:
        return [f"{config_path}: invalid JSON: {exc.msg}"]
    errors: list[str] = []
    for artifact in hook_artifacts:
        event = artifact.data["spec"]["event"]
        if not isinstance(hooks.get(event), list):
            errors.append(f"{artifact.path}: event {event} is not registered in {config_path.relative_to(root)}")
            continue
        entrypoint = (artifact.path.parent / artifact.data["spec"]["entrypoint"]).resolve()
        entry_rel = entrypoint.relative_to(root).as_posix()
        if entry_rel not in json.dumps(hooks[event], ensure_ascii=False):
            errors.append(f"{artifact.path}: {config_path.relative_to(root)} {event} registration does not reference {entry_rel}")
    return errors


def discover_and_validate(root: Path, registry: dict[str, Any]) -> tuple[list[Artifact], list[str]]:
    artifacts: list[Artifact] = []
    errors: list[str] = []
    discovered = manifest_paths(root, registry)
    errors.extend(missing_manifest_errors(root, registry, discovered))
    for expected_kind, path in discovered:
        try:
            artifacts.append(validate_manifest(root, registry, expected_kind, path))
        except ManifestError as exc:
            errors.append(str(exc))
    identifiers: dict[str, Artifact] = {}
    for artifact in artifacts:
        if artifact.identifier in identifiers:
            errors.append(f"{artifact.path}: duplicate artifact ID {artifact.identifier}")
        identifiers[artifact.identifier] = artifact
    for artifact in artifacts:
        for dependency in artifact.data["spec"]["dependsOn"]:
            if dependency not in identifiers:
                errors.append(f"{artifact.path}: unknown dependency {dependency}")
    errors.extend(validate_hooks(root, registry, artifacts))
    return artifacts, errors


def print_table(artifacts: list[Artifact]) -> None:
    print("| ID | Version | Entrypoint | Permissions |")
    print("| --- | --- | --- | --- |")
    for artifact in sorted(artifacts, key=lambda item: (item.kind, item.name)):
        spec = artifact.data["spec"]
        permissions = ", ".join(f"{key}={spec['permissions'][key]}" for key in PERMISSIONS)
        print(f"| {artifact.identifier} | {artifact.data['metadata']['version']} | {spec['entrypoint']} | {permissions} |")


def scaffold_manifest(kind: str, name: str, entrypoint: str, description: str) -> str:
    event = "  event: Stop\n" if kind == "Hook" else ""
    return (
        f"apiVersion: {API_VERSION}\nkind: {kind}\nmetadata:\n"
        f"  name: {name}\n  version: 0.1.0\n  description: {json.dumps(description, ensure_ascii=False)}\n"
        f"spec:\n  entrypoint: {entrypoint}\n  capabilities:\n    - {kind.lower()}.execute\n"
        "  permissions:\n    filesystem: read\n    network: none\n    subprocess: none\n    git: none\n"
        "  dependsOn: []\n  lifecycle:\n    discoverable: true\n    deprecated: false\n"
        f"{event}"
    )


def command_init(root: Path, registry: dict[str, Any], args: argparse.Namespace) -> int:
    if not NAME_RE.fullmatch(args.name):
        raise ManifestError("--name must be lowercase kebab-case")
    directory = registry["discovery"]["kindDirectories"][args.kind]
    target = root / directory / args.name / "manifest.yaml"
    if target.exists():
        raise ManifestError(f"{target}: already exists")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(scaffold_manifest(args.kind, args.name, args.entrypoint, args.description), encoding="utf-8")
    print(f"Created {target.relative_to(root)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover and validate unified Agent Platform manifests.")
    parser.add_argument("--root", default=".", help="Project root (default: current directory)")
    parser.add_argument(
        "--registry",
        default=None,
        help="Registry YAML path. Defaults to registry.yaml beside this script.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="Validate all discovered manifests and hook registrations")
    list_parser = subparsers.add_parser("list", help="List discovered artifacts")
    list_parser.add_argument("--json", action="store_true", help="Emit JSON instead of a Markdown table")
    init_parser = subparsers.add_parser("init", help="Create a minimal manifest for one artifact")
    init_parser.add_argument("--kind", required=True, choices=KINDS)
    init_parser.add_argument("--name", required=True)
    init_parser.add_argument("--entrypoint", required=True, help="Path relative to the manifest directory")
    init_parser.add_argument("--description", required=True)
    args = parser.parse_args()
    try:
        root = project_root(args.root)
        registry = load_registry(registry_path(root, args.registry))
        if args.command == "init":
            return command_init(root, registry, args)
        artifacts, errors = discover_and_validate(root, registry)
        if args.command == "list":
            if args.json:
                payload = [artifact.data | {"path": artifact.path.relative_to(root).as_posix(), "id": artifact.identifier} for artifact in artifacts]
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                print_table(artifacts)
        if errors:
            for error in errors:
                print(f"FAIL: {error}", file=sys.stderr)
            return 1
        if args.command == "validate":
            print(f"Manifest registry validation passed ({len(artifacts)} artifacts).")
        return 0
    except ManifestError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
