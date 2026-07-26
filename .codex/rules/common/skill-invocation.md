# Skill Invocation

## 技能列表
<!-- skill-registry:managed ["add-reading-tip","analyze-sentence","compile-note","defuddle","digest","extract-vocabulary","format-article","generate-reading-note","json-canvas","maintain-learnings","manifest-platform","obsidian-bases","obsidian-cli","obsidian-markdown","organize-grammar","prompt-cache-optimizer","security-secret-audit","summarize-grammar","sync-skill-registry","translate","vocab-diff","workflow-todo-state"] -->

#### 未分类

| 技能 | 触发场景 | 关键触发词 |
|------|----------|-----------|
| `add-reading-tip` | 向阅读心得.md添加新的阅读技巧。当用户提到"添加阅读技巧"、"新增心得"、"记录技巧"、"阅读技巧"时触发。 | 添加阅读技巧、新增心得、记录技巧、阅读技巧 |
| `analyze-sentence` | 对考研英语文章中的长难句进行结构分析，提取主干、标记修饰成分、绘制结构图解、给出参考译文和考点提示。 | 对考研英语文章中的长难句进行结构分析，提取主干、标记修饰成分、绘制结构图解、给出… |
| `compile-note` | 将翻译、排版文章、语法笔记和长难句分析整合为一份全面的综合学习笔记，遵循AI实战参考模板格式 | 将翻译、排版文章、语法笔记和长难句分析整合为一份全面的综合学习笔记，遵循AI实战… |
| `defuddle` | Extract clean markdown content from web pages using Defuddle CLI | Extract clean markdown content from web … |
| `digest` | 自我学习阶段。回顾本次学习会话，记录学习心得和错误到 .learnings/，当文件超阈值时自动压缩去重，更新 RULES.md | 自我学习阶段 |
| `extract-vocabulary` | 扫描整合笔记中加粗的生词，提取去重后生成词汇表，替换笔记中的<!-- VOCABULARY_SLOT -->占位符。原地修改笔记文件，不改变其他内容。 | 扫描整合笔记中加粗的生词，提取去重后生成词汇表，替换笔记中的<!-- VOCAB… |
| `format-article` | 对英文文章进行美化排版，清理原始格式，添加正确的标题层级、段落分隔和列表结构，输出为规范的Obsidian Markdown格式 | 对英文文章进行美化排版，清理原始格式，添加正确的标题层级、段落分隔和列表结构，输… |
| `generate-reading-note` | Use when generating complete 考研英语阅读精读笔记 from one or many English reading pass… | Use when generating complete 考研英语阅读精读笔记 … |
| `json-canvas` | Create and edit JSON Canvas files (.canvas) with nodes, edges, groups | Create and edit JSON Canvas files (.canv… |
| `maintain-learnings` | 维护 .learnings/ 经验库，把过多或反复出现的学习记录、错误日志、铁律失效问题聚类诊断，追溯并修改对应 skill、模板、校验脚本或项目规则； | 维护 .learnings/ 经验库，把过多或反复出现的学习记录、错误日志、铁律… |
| `manifest-platform` | Install, configure, migrate, and validate a portable manifest registry for ag… | Install, configure, migrate, and validat… |
| `obsidian-bases` | Create and edit Obsidian Bases (.base files) with views, filters, formulas | Create and edit Obsidian Bases (.base fi… |
| `obsidian-cli` | Interact with Obsidian vaults using the Obsidian CLI to read, create, search | Interact with Obsidian vaults using the … |
| `obsidian-markdown` | Create and edit Obsidian Flavored Markdown with wikilinks, embeds, callouts | Create and edit Obsidian Flavored Markdo… |
| `organize-grammar` | 整理零散的英语语法笔记，按类别（时态、语态、从句等）组织为结构化参考。 | 整理零散的英语语法笔记，按类别（时态、语态、从句等）组织为结构化参考 |
| `prompt-cache-optimizer` | 审计并优化 LLM 提示缓存命中率、输入 token、延迟与调用成本。 | 优化缓存命中、降低 token 成本、审计 LLM 调用、提示词缓存优化、优化 AI 调用费用 |
| `security-secret-audit` | Audit a Git repository for exposed API keys, tokens, passwords, private keys | Audit a Git repository for exposed API k… |
| `summarize-grammar` | 读取 intermediate 下所有 grammar-notes.md，按语法类别（从句、非谓语动词等）去重合并，生成跨篇章的综合语法总结笔记。 | 语法总结、汇总语法、语法笔记汇总 |
| `translate` | 将考研英语阅读文章翻译为中文，按段落生成中英对照格式，保存到 intermediate 目录。用户粘贴英文文本或提供文件路径，并指定主题名(topic)时触发。 | 将考研英语阅读文章翻译为中文，按段落生成中英对照格式，保存到 intermedi… |
| `vocab-diff` | 管理考研英语易混淆单词辨析笔记。当用户提到"记混了"、"易混淆词"、"单词辨析"、"添加单词"、"这几个词分不清"、"statue还是statute"、"… | 记混了、易混淆词、单词辨析、添加单词、这几个词分不清、statue还是statute、affect还是effect |
| `workflow-todo-state` | Create or retrofit reusable named workflow state machines for multi-step agen… | Create or retrofit reusable named workfl… |

#### 工具发现

| 技能 | 触发场景 | 关键触发词 |
|------|----------|-----------|
| `sync-skill-registry` | 技能注册表同步工具。扫描任意 agent skill 目录中的 */SKILL.md 并自动更新对应 skill-invocation.md 中的技能列表… | 同步注册表、更新技能列表、sync skill registry、update skill registration、刷新技能列表、同步技能表格 |

### 1. 分析意图

根据用户请求选择最合适的可复用 skill 或模板。
