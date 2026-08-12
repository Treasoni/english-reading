#!/usr/bin/env python3
"""Render host-local agent hook settings from portable templates."""

from __future__ import annotations

import argparse
import copy
import json
import platform
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


SCRIPT_PATH = re.compile(r"""(?:"([^"]+\.py)"|'([^']+\.py)'|(\S+\.py))(?:\s|$)""")


def render_hook_template(
    template: dict[str, Any],
    *,
    python_executable: str,
    hook_script: str,
) -> dict[str, Any]:
    """Replace the two supported placeholders throughout a hook template."""

    def render(value: Any) -> Any:
        if isinstance(value, str):
            return value.replace("{{PYTHON_EXECUTABLE}}", python_executable).replace(
                "{{HOOK_SCRIPT}}", hook_script
            )
        if isinstance(value, list):
            return [render(item) for item in value]
        if isinstance(value, dict):
            return {key: render(item) for key, item in value.items()}
        return value

    return render(template)


def _hook_script_paths(entry: Any) -> set[str]:
    paths: set[str] = set()
    if isinstance(entry, dict):
        command = entry.get("command")
        if isinstance(command, str):
            for match in SCRIPT_PATH.finditer(command):
                paths.add(next(group for group in match.groups() if group is not None))
        for value in entry.values():
            paths.update(_hook_script_paths(value))
    elif isinstance(entry, list):
        for value in entry:
            paths.update(_hook_script_paths(value))
    return paths


def _managed_hook_nodes(entry: Any) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    if isinstance(entry, dict):
        command = entry.get("command")
        if isinstance(command, str) and _hook_script_paths({"command": command}):
            nodes.append(entry)
        else:
            for value in entry.values():
                nodes.extend(_managed_hook_nodes(value))
    elif isinstance(entry, list):
        for value in entry:
            nodes.extend(_managed_hook_nodes(value))
    return nodes


def _replace_matching_hook(
    entry: Any,
    paths: set[str],
    replacement: dict[str, Any],
) -> tuple[Any, bool]:
    if isinstance(entry, dict):
        command = entry.get("command")
        if isinstance(command, str) and any(path in command for path in paths):
            merged = copy.deepcopy(entry)
            merged.update(copy.deepcopy(replacement))
            return merged, True
        for key, value in entry.items():
            rendered, replaced = _replace_matching_hook(value, paths, replacement)
            if replaced:
                entry[key] = rendered
                return entry, True
    elif isinstance(entry, list):
        for index, value in enumerate(entry):
            rendered, replaced = _replace_matching_hook(value, paths, replacement)
            if replaced:
                entry[index] = rendered
                return entry, True
    return entry, False


def merge_managed_hooks(
    current: dict[str, Any],
    desired: dict[str, Any],
) -> dict[str, Any]:
    """Replace matching managed hook entries while preserving unrelated settings."""

    merged = copy.deepcopy(current)
    current_hooks = merged.setdefault("hooks", {})
    desired_hooks = desired.get("hooks", {})
    if not isinstance(current_hooks, dict) or not isinstance(desired_hooks, dict):
        raise ValueError("hook settings must contain a hooks object")

    for event, desired_entries in desired_hooks.items():
        if not isinstance(desired_entries, list):
            raise ValueError(f"hooks.{event} must be a list")
        current_entries = current_hooks.setdefault(event, [])
        if not isinstance(current_entries, list):
            raise ValueError(f"hooks.{event} must be a list")
        for desired_entry in desired_entries:
            managed_nodes = _managed_hook_nodes(desired_entry)
            if len(managed_nodes) != 1:
                raise ValueError(
                    f"hooks.{event} entry must contain exactly one Python hook command"
                )
            replacement = managed_nodes[0]
            script_paths = _hook_script_paths(replacement)
            replaced = False
            for index, current_entry in enumerate(current_entries):
                rendered, replaced = _replace_matching_hook(
                    current_entry,
                    script_paths,
                    replacement,
                )
                if replaced:
                    current_entries[index] = rendered
                    break
            if not replaced:
                current_entries.append(copy.deepcopy(desired_entry))
    return merged


def write_json_atomically(path: Path, data: dict[str, Any]) -> None:
    """Write formatted JSON through a sibling temporary file."""

    temp = path.with_name(path.name + ".tmp")
    temp.parent.mkdir(parents=True, exist_ok=True)
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    temp.replace(path)


def _load_profiles(root: Path) -> list[dict[str, Any]]:
    script_dir = Path(__file__).resolve().parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    from sync_agents import load_profiles

    return load_profiles(root)


def _load_json_object(path: Path, *, missing_ok: bool = False) -> dict[str, Any]:
    if missing_ok and not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _json_matches(path: Path, expected: dict[str, Any]) -> bool:
    if not path.exists():
        return False
    return _load_json_object(path) == expected


def desired_outputs(
    root: Path,
    profiles: list[dict[str, Any]],
) -> list[tuple[Path, dict[str, Any]]]:
    """Build every host-local JSON output before writing any of them."""

    runtime = root / ".agent-sync"
    outputs: list[tuple[Path, dict[str, Any]]] = []
    host = {
        "platform": platform.system(),
        "python_executable": sys.executable,
    }
    outputs.append((runtime / "local/host.json", host))
    for profile in profiles:
        template_path = runtime / "hook-templates" / f"{profile['id']}.json"
        template = _load_json_object(template_path)
        hook_script = str(
            PurePosixPath(profile["paths"]["hooks"]) / "read_learnings.py"
        )
        desired = render_hook_template(
            template,
            python_executable=sys.executable,
            hook_script=hook_script,
        )
        for rendered_script in sorted(_hook_script_paths(desired)):
            script_path = PurePosixPath(rendered_script)
            if script_path.is_absolute() or ".." in script_path.parts:
                raise ValueError(
                    f"{profile['id']}: rendered hook script must be project-relative: "
                    f"{rendered_script}"
                )
            if not (root / script_path).is_file():
                raise ValueError(
                    f"{profile['id']}: rendered hook script does not exist: "
                    f"{rendered_script}"
                )
        config_path = root / profile["paths"]["hook_config"]
        current = _load_json_object(config_path, missing_ok=True)
        outputs.append((config_path, merge_managed_hooks(current, desired)))
    return outputs


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--apply", action="store_true", help="write host-local settings")
    parser.add_argument("--check", action="store_true", help="explicit check-only mode")
    parser.add_argument(
        "--agent",
        action="append",
        help="limit rendering to one or more agent profile ids",
    )
    args = parser.parse_args(argv)
    if args.apply and args.check:
        parser.error("--apply and --check cannot be used together")

    root = Path(args.root).resolve()
    try:
        profiles = _load_profiles(root)
        if args.agent:
            requested = set(args.agent)
            known = {profile["id"] for profile in profiles}
            if unknown := sorted(requested - known):
                raise ValueError(f"unknown --agent profile: {', '.join(unknown)}")
            profiles = [profile for profile in profiles if profile["id"] in requested]
        outputs = desired_outputs(root, profiles)
        drift = [
            (path, "updated" if path.exists() else "created")
            for path, expected in outputs
            if not _json_matches(path, expected)
        ]
        if args.apply:
            for path, expected in outputs:
                if not _json_matches(path, expected):
                    write_json_atomically(path, expected)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 2

    if not drift:
        print("[OK] host-local hook settings are current")
        return 0
    for path, action in drift:
        print(f"[DRIFT] {action}: {path.relative_to(root)}")
    if args.apply:
        print("[OK] host-local hook settings applied")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
