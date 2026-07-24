# Prompt Cache Measurement

`.llm/prompt-cache/` 是可选的字段合同，不是采集器。只有 agent 已找到项目的 LLM API 调用边界，并能从 provider response 或已有结构化日志自动获得 usage 时，才用 `--with-observability` 安装它。agent 随后在调用处接入自动事件记录，推荐写入项目已有的结构化日志系统；没有日志系统时，可以写入已被 `.gitignore` 排除的本地 JSONL 文件。

直接使用 Codex 而没有项目 API 调用边界时，不能可靠取得平台内部 usage；不要创建 `/.llm`，也不要让用户手动填写 token、缓存读取量、延迟或费用。

## Required Fields

由 agent 从实际调用结果自动记录每条调用的：

- `request_type`：业务调用类型，例如 `answer_question`、`summarize_document`。
- `template_id` 与 `template_version`：稳定模板的身份与版本。
- `model`：实际模型标识。
- `input_tokens`、`output_tokens`、`latency_ms`。
- `cache_read_tokens`、`cache_write_tokens`：提供方返回时记录；不支持时可省略，不能编造为零。
- `cost_usd`：提供方返回或由 agent 按项目统一费率自动估算时记录，并注明估算方式。

不要记录原始用户输入、完整提示词、模型输出、密钥或个人数据。使用安全的文件路径、fixture ID 或内容哈希填入 `input_reference`。

## Cache Rate

当提供方返回 `cache_read_tokens` 时，可按同一 `request_type + template_id + template_version + model` 分组计算：

```text
cache_read_rate = sum(cache_read_tokens) / sum(input_tokens)
```

这不是所有平台的官方“缓存命中率”定义，但适合作为同项目内的趋势指标。模型、工具定义或模板版本发生变化时，应分组比较，不能混在同一基线中。

## Regression Cases

只有 agent 能自动重放请求并采集指标时，才复制 `prompt-cache-regression-cases.json` 到 `.llm/prompt-cache/regression-cases.json`，并将示例替换为 3-10 个稳定、脱敏、具有代表性的高频请求。

每个样本应包含：

- 固定 `template_id` 和安全的 `input_fixture`。
- 稳定的参数字段和顺序。
- 可人工或自动检查的输出质量条件。
- agent 自动采集的 token、延迟、费用和质量基线。

每次修改模板、模型、工具定义或上下文加载策略后，使用同一批样本重新运行。只有质量检查通过时，才将缓存读取 token、总输入 token、延迟和费用的变化视为有效优化。

## Minimal Review Table

| 请求类型 | 模板版本 | 样本数 | 输入 token | 缓存读取 token | 输出 token | 延迟 | 费用 | 质量 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `replace-me` | `v1` | 0 | 0 | N/A | 0 | 0 ms | N/A | 未评估 |
 
