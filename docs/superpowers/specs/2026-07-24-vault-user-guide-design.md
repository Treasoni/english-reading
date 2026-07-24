---
title: 考研英语阅读精读 Vault 使用说明设计
type: design
topic: vault-user-guide
tags:
  - documentation
  - study-workflow
created: 2026-07-24
status: approved-for-drafting
---

# 考研英语阅读精读 Vault 使用说明设计

## 目标

为同时使用 Obsidian 与 AI 助手的学习者提供一份单一入口的中文使用说明，使其能从电子版 PDF 或扫描资料开始，完成一篇考研英语阅读的格式化、翻译、长难句分析、整合与词汇复习。

## 读者与范围

- 面向首次使用本 Vault 的学习者，以及需要向 Codex 或 Claude Code 下达任务的使用者。
- 文档覆盖核心流程、每步产物、可复制指令、完成检查和常见问题。
- 不把本 Vault 描述为独立命令行程序，也不包含安装、账户注册或具体模型配置的说明。

## 核心流程

1. 使用 [MinerU](https://mineru.net/) 将电子版 PDF 或扫描资料转换为 Markdown。
2. 使用 `format-article` 整理文章结构并生成规范模板。
3. 使用 `translate` 生成逐段中英对照翻译。
4. 在精读过程中随时使用 `analyze-sentence` 分析长难句，并将分析内联到原文对应句子之后。
5. 使用 `compile-note` 整合已完成的学习材料。
6. 使用 `extract-vocabulary` 生成词汇表与练习。

`organize-grammar` 作为可选扩展：学习者有零散语法笔记时，可在整合前使用它生成结构化语法笔记。

## 文档结构

1. Vault 是什么：说明用途和适用人群。
2. 开始前准备：在 Obsidian 中打开库，并将 PDF / 扫描资料先经 MinerU 转为 Markdown。
3. 一次完整精读：按核心流程逐步说明「用途、输入、产出、示例指令」。
4. 可选的语法整理与跨篇复习：介绍 `organize-grammar` 与 `summarize-grammar` 的使用场景。
5. 完成检查：核对中间文件、最终笔记、词汇练习及渲染效果。
6. 常见问题：处理转档效果、步骤顺序、长难句插入位置和输出路径。

## 内容约束

- 全文采用中文和 Obsidian Markdown；使用扁平 YAML frontmatter、标准标题和有效 wikilink。
- 以用户指定的六环主线为主，不强行把语法整理插入主线。
- 明确 `analyze-sentence` 是可随时穿插的学习步骤，而不是必须集中在翻译前后执行。
- 示例指令使用完整 topic slug，避免创建无法匹配中间目录和最终笔记的文件。

## 验收标准

- 读者可从 Markdown 原文开始，理解每一步该做什么、会得到什么文件、如何向 AI 助手提出请求。
- 文档清楚推荐 MinerU 作为 PDF / 扫描资料的 Markdown 化前置工具，并提供链接。
- 文档包含核心流程、可选语法路径、检查清单与常见问题。
- 在 Obsidian 阅读视图中，标题、列表、提示块和内部链接均正常渲染。
