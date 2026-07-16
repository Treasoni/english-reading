# Prompt Cache Rules

## Prompt Order

For every high-frequency request, keep this order:

1. Stable role, task boundaries, and safety rules.
2. Stable tool constraints, output format, and quality requirements.
3. Stable examples, only when they materially improve the result.
4. Dynamic parameters: user request, file excerpts, dates, runtime state, and IDs.

Keep stable content at the beginning and dynamic content at the end. Reuse the same stable prefix for the same task type.

## Stability

- Do not put timestamps, random IDs, UUIDs, git status, live TODOs, or user input in the stable prefix.
- Do not casually reorder or reword stable prompt sections, punctuation, or whitespace.
- Keep one authoritative template for each high-frequency task.
- Keep model settings and tool definitions stable when cache reuse matters.
- Keep dynamic parameter names and order stable; use `none` for missing values.

## Context Loading

- Prefer paths, headings, anchors, and summaries before loading full content.
- Load only the file sections needed for the current task.
- Do not preload build output, dependencies, logs, mirrored configuration, or unrelated examples.
- Save reusable long results as structured files and reference them instead of pasting them again.

## Subagents

- Put fixed responsibilities, output format, and prohibitions before the parameter block.
- Put all task-specific values in a final `Parameters` block.
- Return structured summaries, links, citations, and conclusions instead of full source text.

## Standard Template

```text
You are {stable_role}.

Task boundaries:
{stable_boundaries}

Output format:
{stable_output_format}

Quality requirements:
{stable_quality_requirements}

Prohibitions:
{stable_prohibitions}

Parameters:
- Task: {dynamic_task}
- User request: {dynamic_request}
- Input reference: {dynamic_input_reference}
- Current state: {dynamic_state}
- Extra constraints: {dynamic_constraints}
```
