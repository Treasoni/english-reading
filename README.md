# 考研英语阅读精读项目

这是一个可以交给别人使用的考研英语阅读项目：既包含已经整理好的 Obsidian 精读笔记，也提供命令行工具，把电子版真题自动拆成阅读文章、题目、长难句分析任务和语法笔记草稿。

## 适合做什么

- 从 `.txt` / `.md` / `.docx` / `.pdf` 真题文件中提取 `Text 1`、`Text 2` 等阅读文章和选择题。
- 为每篇阅读生成 Obsidian 兼容的 `formatted-article.md`。
- 自动筛选长难句候选，生成可直接交给 `analyze-sentence` 技能处理的 `sentence-analysis-task.md`。
- 自动扫描从句、非谓语、被动语态、强调/形式主语、介词连接结构等语法现象，生成 `grammar-notes.md` 草稿。
- 继续沿用现有 Agent 技能完成翻译、长难句精修、综合笔记、生词表和跨篇语法总结。

> 扫描版 PDF 需要先 OCR 成可复制文本；本项目处理的是已经有文本层的电子版真题。

## 安装

```bash
python3 -m pip install -e .
```

如果要直接处理 PDF，安装任一 PDF 解析库即可：

```bash
python3 -m pip install pypdf
```

也可以使用 `pymupdf` 或 `pdfplumber`。

## 快速开始

用样例文本试跑：

```bash
kaoyan-reading init-workflow examples/sample-exam.txt --year 2000 --out intermediate
```

生成结果：

```text
intermediate/2000-text1/
├── reading.json                 # 结构化文章和题目
├── formatted-article.md          # Obsidian 原文 + 阅读题
├── sentence-analysis-task.md     # 长难句分析任务
└── grammar-notes.md              # 语法笔记草稿
```

处理自己的真题：

```bash
kaoyan-reading init-workflow path/to/2010真题.pdf --year 2010 --out intermediate
```

一次处理多篇阅读时，可以开启篇章级并行：

```bash
kaoyan-reading init-workflow path/to/2010真题.pdf --year 2010 --out intermediate --jobs 4
```

建议把 `--jobs` 设为 2-4。每篇文章会写入独立的 `intermediate/<year>-textN/` 目录；跨篇语法总结、生词总表等汇总步骤仍建议最后串行执行。

只提取文章和题目：

```bash
kaoyan-reading extract path/to/2010真题.docx --year 2010 --out extracted
```

只生成长难句候选：

```bash
kaoyan-reading sentences intermediate/2010-text1/formatted-article.md \
  --topic 2010-text1 \
  --out intermediate/2010-text1/sentence-analysis-task.md
```

只生成语法草稿：

```bash
kaoyan-reading grammar intermediate/2010-text1/formatted-article.md \
  --topic 2010-text1 \
  --out intermediate/2010-text1/grammar-notes.md
```

## 完整精读流程

| 步骤 | 命令/技能 | 产出 | 说明 |
|------|-----------|------|------|
| 1 | `kaoyan-reading init-workflow` | `reading.json` / `formatted-article.md` | 从电子版真题提取阅读文章和题目 |
| 2 | `translate` | `translation.md` | 中英对照翻译 |
| 3 | `kaoyan-reading grammar` + `organize-grammar` | `grammar-notes.md` | 先自动扫描，再由 Agent 精修语法笔记 |
| 4 | `kaoyan-reading sentences` + `analyze-sentence` | 内联到原文 | 先筛长难句，再插入可折叠 callout |
| 5 | `compile-note` | `<topic>-精读笔记.md` | 整合为综合学习笔记 |
| 6 | `extract-vocabulary` | 生词表 + 练习题 | 替换 `<!-- VOCABULARY_SLOT -->` |

附加技能：

- `summarize-grammar`：跨篇章语法总结，生成 `语法总结笔记.md` 和 `固定搭配与词组笔记.md`。
- `digest`：用户明确要求时，记录新的学习经验到 `.learnings/`。

## 项目结构

```text
├── src/kaoyan_reading/            # 可分发 Python 包
│   ├── cli.py                     # 命令行入口
│   ├── extract.py                 # 阅读文章和题目提取
│   ├── sentence_analysis.py       # 长难句候选筛选与任务生成
│   ├── grammar.py                 # 语法现象扫描与笔记草稿生成
│   └── workflow.py                # 一键初始化工作流
├── tests/                         # 本地测试
├── examples/                      # 可试跑样例
├── intermediate/                  # 工作流中间产物
├── 2000阅读/ ...                  # 已完成的精读笔记资产
├── .agents/skills/                # Codex 技能定义
└── .learnings/                    # 项目经验库
```

发布包只包含可复用的必要部分：`src/`、`tests/`、`examples/sample-exam.txt`、`.agents/skills/`、`README.md`、`AGENTS.md`、`CLAUDE.md` 和 `pyproject.toml`。

## 能力边界

本地 CLI 负责确定性处理：文件读取、阅读分段、题目结构化、长难句候选筛选、语法现象扫描。完整的长难句主干提取、修饰成分判断、译文和考点提示仍建议交给 `analyze-sentence` Agent 技能完成，因为这部分需要语言理解和教学判断。

## 发布与更新

更新项目后，先修改 `pyproject.toml` 里的版本号，再运行：

```bash
bash scripts/package-essential.sh
```

脚本会生成：

```text
dist/kaoyan-english-reading-essential-<version>.zip
```

这个压缩包只包含可复用的必要部分：CLI 源码、测试、样例、README、项目规则和 `.agents/skills/`。它会排除个人笔记、`intermediate/`、Obsidian 配置、Git 历史、本机 hook 和大体积真题素材。打包后脚本会自动解压验证，确认 CLI 能启动并能用样例生成工作流。
