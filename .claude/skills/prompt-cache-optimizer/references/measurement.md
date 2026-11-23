# Prompt Cache Measurement

使用技能的 `assets/llm-usage-event.schema.json` 作为 `.llm/prompt-cache/` 的事件合同，优先复用项目已有的结构化日志；否则写入被 `.gitignore` 排除的本地 JSONL。

## Usage Events

- 记录调用时间、真实的 `request_type`、`template_id`、`template_version`、实际模型、输入/输出 token 和每次请求的实测延迟。只有转写时间戳时，不能用距最近用户消息的时间冒充请求延迟；关键词推断出的标签也不是模板基线。
- 缓存字段仅在提供方返回时记录；缺字段不是零。费用只用提供方返回值或有文档依据的统一费率估算。
- 不记录原始用户输入、完整提示词、模型输出、密钥或个人数据。`input_reference` 只使用脱敏路径、fixture ID 或内容哈希。

## Cache Read Share

先按实际提供方或网关的文档确认字段语义，再对每条记录换算总输入：

| `input_tokens` 口径 | 单次总输入 |
| --- | --- |
| 未缓存余量，不含读取和写入（Anthropic 原生；两种缓存字段互斥于余量） | `input_tokens + cache_read_tokens + cache_write_tokens` |
| 未命中读取的总数，已含写入（由提供方确认） | `input_tokens + cache_read_tokens` |
| 完整输入，已含缓存读取与写入（由提供方确认） | `input_tokens` |

例如 Anthropic 原生的余量 200、读取 700、写入 100，对应总输入 1,000，缓存读取占比 70%。不要因为 `cache_read_tokens > input_tokens` 就反推网关口径；它只说明该记录不能按完整输入口径解释。

按同一提供方/网关、字段口径、`request_type`、`template_id`、`template_version` 和模型分组，计算 `sum(cache_read_tokens) / sum(总输入 token)`。这是 token 加权读取占比，不是有缓存命中的请求占比。缺少换算所需字段、口径未确认、总输入为零或结果超出 `[0, 1]` 的记录不纳入占比，并报告覆盖率。不要用只有关键词标签的历史日志做模板级前后对照。

## Regression Cases

复制 `prompt-cache-regression-cases.json` 到 `.llm/prompt-cache/regression-cases.json`，并将示例替换为 3-10 个稳定、脱敏、具有代表性的高频请求。

每个样本应包含：

- 固定 `template_id` 和安全的 `input_fixture`。
- 稳定的参数字段和顺序。
- 可人工或自动检查的输出质量条件。
- 首次采集的 token、延迟、费用和质量基线。

每次修改模板、模型、工具定义或上下文加载策略后，使用同一批样本重新运行。只有质量检查通过时，才将缓存读取 token、总输入 token、延迟和费用的变化视为有效优化。

## Minimal Review Table

| 请求类型 | 模板版本 | 样本数 | 输入 token | 缓存读取 token | 输出 token | 延迟 | 费用 | 质量 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `replace-me` | `v1` | 0 | 0 | N/A | 0 | 0 ms | N/A | 未评估 |
 
