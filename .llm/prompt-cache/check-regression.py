#!/usr/bin/env python3
"""Check local regression inputs and render the fork template without a model call."""

import json
import re
import sys
from pathlib import Path
from string import Formatter

SUITE_DIR = Path(__file__).resolve().parent
ROOT = SUITE_DIR.parents[1]
BOUNDARY = "\nParameters:\n"
PLACEHOLDER = re.compile(r"\{[a-z_][a-z_0-9]*\}")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_fixture(relative_path):
    path = (SUITE_DIR / relative_path).resolve()
    require(path.is_relative_to(SUITE_DIR / "fixtures"), f"Not a fixture path: {relative_path}")
    text = path.read_text(encoding="utf-8")
    require(text.strip(), f"Empty fixture: {relative_path}")
    return text


def check_fork_prefix(template, dispatches):
    require(template.count(BOUNDARY) == 1, "Expected one Parameters boundary")
    fixed, _ = template.split(BOUNDARY)
    require(not PLACEHOLDER.search(fixed), "Substitution field in the fixed prefix")
    fields = {name for _, name, _, _ in Formatter().parse(template) if name is not None}
    require(fields and len(dispatches) >= 2, "Need parameters and at least two dispatches")
    prefixes, suffixes = set(), set()
    for index, dispatch in enumerate(dispatches, start=1):
        require(fields == dispatch.keys(), f"Dispatch {index} does not match template fields")
        rendered = template.format_map(dispatch)
        require(not PLACEHOLDER.search(rendered), f"Unexpanded field in dispatch {index}")
        require(rendered.count(BOUNDARY) == 1, f"Boundary changed in dispatch {index}")
        prefix, suffix = rendered.split(BOUNDARY)
        prefixes.add((prefix + BOUNDARY).encode("utf-8"))
        suffixes.add(suffix)
    require(prefixes == {(fixed + BOUNDARY).encode("utf-8")}, "Rendered prefixes differ")
    require(len(suffixes) == len(dispatches), "Dispatch suffixes must differ")


def check_translation_seed(source, seed):
    source_heading, *paragraphs = source.strip().split("\n\n")
    _, _, bilingual = seed.split("---\n", 2)
    heading, *pairs = bilingual.strip().split("\n\n")
    require(heading.startswith(source_heading) and len(pairs) == 4 and len(paragraphs) == 3,
            "Incremental fixture must have two seed pairs and three current paragraphs")
    old_first, _, old_second, _ = pairs
    require(old_first == paragraphs[0], "Incremental fixture lost its unchanged paragraph")
    require("one in four" in old_second and "one in five" in paragraphs[1]
            and old_second.replace("one in four", "one in five", 1) == paragraphs[1],
            "Incremental fixture lost the intended change in paragraph two")
    require(paragraphs[2] not in pairs, "Incremental fixture lost its new paragraph")


def main():
    manifest = json.loads((SUITE_DIR / "regression-cases.json").read_text(encoding="utf-8"))
    offline_count = replay_count = 0
    checked_replays = set()
    seen = set()
    for case in manifest["cases"]:
        case_id = case["id"]
        require(case_id not in seen, f"Duplicate case ID: {case_id}")
        seen.add(case_id)
        if not case["enabled"]:
            continue
        require(case["quality_checks"], f"No quality checks: {case_id}")
        source = read_fixture(case["input_fixture"])
        params = case["parameters"]
        if case.get("mode") == "offline":
            require(case["template_id"] == "prompt:fork-subagent", f"Unknown offline case: {case_id}")
            template = (ROOT / params["template_path"]).read_bytes().decode("utf-8")
            check_fork_prefix(template, json.loads(source))
            offline_count += 1
            print(f"[OK] {case_id}: byte-identical rendered prefixes")
            continue
        setup = case.get("setup", {})
        copies = {dest: read_fixture(path) for dest, path in setup.get("copy_fixtures", {}).items()}
        dependencies = setup.get("prerequisite_cases", {}).values()
        require(set(dependencies) <= checked_replays, f"Unknown or out-of-order prerequisite: {case_id}")
        if params.get("source_already_loaded"):
            check_translation_seed(source, copies[f'{params["output_dir"]}/translation.md'])
        if case["request_type"] == "analyze_sentence":
            require(all(sentence in copies[params["source_path"]] for sentence in params["sentences"]),
                    f"Selected sentence not in the target fixture: {case_id}")
        if case["request_type"] == "extract_vocabulary":
            note = copies[params["note_path"]]
            require(note.count("<!-- VOCABULARY_SLOT -->") == 1 and re.search(r"\*\*[A-Za-z]", note),
                    f"Missing vocabulary marks or a unique slot: {case_id}")
        checked_replays.add(case_id)
        replay_count += 1
    print(f"[OK] {offline_count} offline test(s); {replay_count} model replay inputs checked, not executed")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as exc:
        sys.exit(f"[FAIL] {exc}")
