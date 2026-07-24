# Vault 使用说明文档 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 Vault 根目录新增一份面向学习者和 AI 助手使用者的中文使用说明，覆盖 MinerU 前置转档和完整精读主线。

**Architecture:** 使用一个独立的 Obsidian Markdown 文档承载说明，避免把现有 README 的项目维护信息与学习操作混在一起。文档按“准备 → 核心流程 → 可选扩展 → 检查与排错”组织；每个核心步骤固定说明用途、输入、产出和可复制指令。

**Tech Stack:** Obsidian Flavored Markdown、仓库已有 AI 技能说明、Markdown 链接。

## Global Constraints

- 创建文件必须使用扁平 YAML frontmatter；YAML 列表项用 2 空格缩进。
- Markdown 标题的 `#` 后必须保留空格；任何表格前保留一个空行。
- 核心顺序固定为：MinerU 转 Markdown → `format-article` → `translate` →（随时）`analyze-sentence` → `compile-note` → `extract-vocabulary`。
- `organize-grammar` 仅作为按需扩展，不插入核心主线。
- 说明不得把本 Vault 描述为独立命令行程序，也不得臆造账户配置或工具安装步骤。

---

### Task 1: 核对技能输入、产物与示例指令

**Files:**
- Read: `README.md`
- Read: `.agents/skills/format-article/SKILL.md`
- Read: `.agents/skills/translate/SKILL.md`
- Read: `.agents/skills/analyze-sentence/SKILL.md`
- Read: `.agents/skills/compile-note/SKILL.md`
- Read: `.agents/skills/extract-vocabulary/SKILL.md`
- Read: `.agents/skills/organize-grammar/SKILL.md`

**Interfaces:**
- Consumes: 已确认的文档设计 `docs/superpowers/specs/2026-07-24-vault-user-guide-design.md`。
- Produces: 每个章节中可验证的输入、输出和自然语言示例指令。

- [x] **Step 1: 提取核心流程的真实约定**

阅读上述技能文件，记录每项技能的触发条件、所需输入、输出文件和已知限制；以仓库实际技能为准，不根据名称推测行为。

- [x] **Step 2: 核对命名与目录约定**

从 `README.md` 和 `AGENTS.md` 确认完整 topic slug、`intermediate/<topic>/`、最终笔记以及输出路径的约定。

- [x] **Step 3: 形成示例场景**

采用统一示例 topic `2005-passage2-global-warming`；每条示例指令均说明输入材料与期望产物，且不要求用户使用命令行。

### Task 2: 撰写可操作的使用说明

**Files:**
- Create: `使用说明.md`
- Reference: `docs/superpowers/specs/2026-07-24-vault-user-guide-design.md`

**Interfaces:**
- Consumes: Task 1 已核对的技能行为与 topic 命名约定。
- Produces: 可在 Obsidian 阅读视图正常使用的单一入口说明文档。

- [x] **Step 1: 添加 Obsidian 属性与文档导航**

建立 `使用说明.md`，包含标题、类型、标签、创建日期和适用范围；开头用简短说明介绍 Vault 的用途，并给出主流程目录链接。

- [x] **Step 2: 撰写“开始前”章节**

说明在 Obsidian 中打开库；推荐使用 [MinerU](https://mineru.net/) 将电子版 PDF 或扫描资料先转换为 Markdown，并提醒用户转档后快速检查标题、段落和乱码。

- [x] **Step 3: 撰写核心六环流程**

以有序编号逐项写明：

1. `format-article` 对 MinerU 产出的 Markdown 进行清理和模板化；
2. `translate` 生成中英对照；
3. `analyze-sentence` 在学习过程中按需插入，分析块紧跟对应原句；
4. `compile-note` 整合前先提示用户指定最终笔记的输出路径；
5. `extract-vocabulary` 补齐生词表与练习。

每项包含“什么时候用、需要什么、会得到什么、示例指令”四个小节。流程图中单独强调 `analyze-sentence` 是穿插步骤，不等待某一固定阶段。

- [x] **Step 4: 增加按需扩展、检查清单和常见问题**

说明何时用 `organize-grammar` 和 `summarize-grammar`；提供完成检查（中间文件、最终笔记、词汇练习、Obsidian 渲染）以及常见问题（转档质量、步骤顺序、长难句位置、输出路径）。

- [ ] **Step 5: 提交文档**

```bash
git add 使用说明.md
git commit -m "docs: add vault usage guide"
```

### Task 3: 文档验证

**Files:**
- Verify: `使用说明.md`

**Interfaces:**
- Consumes: Task 2 的 Markdown 文档。
- Produces: 已验证的用户可用说明。

- [ ] **Step 1: 运行结构检查**

Run: `git diff --check HEAD~1..HEAD`

Expected: 无输出，表明没有尾随空格或 Markdown 表格的格式问题。

- [ ] **Step 2: 核对内容覆盖**

逐项对照设计说明的“核心流程”“文档结构”“验收标准”：确认 MinerU 链接、六环主线、可选语法扩展、检查清单和常见问题均存在。

- [ ] **Step 3: 核对示例的可执行性**

确认示例使用完整 topic slug，未把 `analyze-sentence` 描述成独立汇总步骤，且 `compile-note` 的示例要求用户明确输出路径。
