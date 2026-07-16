---
name: prompt-cache-optimizer
description: 审计并优化 LLM 提示缓存命中率、输入 token、延迟与调用成本。用于用户要求“优化缓存命中”“降低 token 成本”“审计 LLM 调用”“提示词缓存优化”“优化 AI 调用费用”，或需要为任意 agent profile 与应用代码建立可观测性和固定回归样本时。
---

# Prompt Cache Optimizer

以项目真实的提示构造、调用日志和回归样本为依据优化缓存；不要把缩短提示词或删除必要上下文误当成优化。

## Resources

- 运行 `scripts/prompt-cache-bootstrap.sh` 安装或检查规则、调用事件 schema 与回归样本模板。
- 需要接入指标或解释比较方式时，读取 `references/measurement.md`。
- 使用 `assets/llm-usage-event.schema.json` 作为调用日志字段合同。
- 使用 `assets/prompt-cache-regression-cases.json` 创建脱敏、稳定的回归样本。

## Workflow

### 1. Establish Scope

1. Read the target project's entry instructions and check `git status --short` before editing.
2. Identify the LLM provider, request entry points, model settings, prompt templates, tool definitions, subagent prompts, and available usage logs.
3. Treat absent cache metrics as a data gap. Do not estimate a cache hit rate from prompt text alone.
4. Preserve user changes, secrets, output quality, and safety constraints. Do not commit or push unless explicitly requested.

### 2. Install and Inspect Foundation

1. Run a read-only check first:

```bash
bash scripts/prompt-cache-bootstrap.sh --check --platform both --target <target-project>
```

2. When the target lacks the foundation and the user authorizes changes, install it:

```bash
bash scripts/prompt-cache-bootstrap.sh --apply --platform both --target <target-project>
```

3. For a single built-in profile, replace `both` with `codex` or `claude`.
4. For a custom agent profile, use `--platform none --agent name,agent_dir,entry_file`.
5. Keep platform-specific rule entry files in their own profile directories; do not manually mirror generated files between profiles.

### 3. Audit High-Value Requests

1. Group requests by `request_type`, `template_id`, `template_version`, and model.
2. Prioritize groups with high call volume, long input, low cache-read token share, or high cost.
3. Check that stable role, output format, tool constraints, and safety rules appear first and remain byte-stable across the group.
4. Check that user input, file excerpts, timestamps, IDs, git status, task state, and runtime values appear only in the final parameter block.
5. Find unnecessary full-file loads, repeated history, mirrored directories, webpage bodies, and subagents returning raw source text.
6. Prefer paths, anchors, summaries, references, and structured intermediate artifacts over repeated long content.

### 4. Measure and Build Regression Coverage

1. Read `references/measurement.md` before adding telemetry or interpreting cache metrics.
2. Record template version, model, input/output token counts, cache read/write token counts when supplied, latency, and cost without logging raw prompts or sensitive data.
3. Replace the disabled regression example with 3-10 representative, stable, and sanitized high-frequency requests.
4. Define output quality checks before accepting a token or cache improvement.

### 5. Report, Change, and Validate

1. Report findings in descending expected impact with file evidence, risk, proposed change, and validation method.
2. When the user has not authorized edits, stop after the audit and plan.
3. When edits are authorized, make small isolated changes, preserve the stable prefix, and avoid unrelated refactors.
4. Run project checks and the same regression cases after each meaningful change.
5. Compare quality, input token, cache-read token, latency, and cost using the same request grouping. Clearly separate measured outcomes from expected outcomes.

## Completion Criteria

- The target has a stable prompt-cache rule and entry-point reference for the selected platform.
- Usage events use the schema or an explicitly documented compatible equivalent.
- Regression cases cover representative high-frequency requests and include quality expectations.
- Findings and changes are traceable to files and measured metrics.
- No claim of savings is made without comparable before-and-after data.
