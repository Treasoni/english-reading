# 学习心得

## 2026-05-17

### 会话概要

本次完成了 2000-passage2 的完整工作流：
- `compile-note` → 整合综合学习笔记
- `organize-grammar` → 合并模式更新语法笔记
- `analyze-sentence` → 长难句分析并插入笔记
- `extract-vocabulary` → 提取生词生成词汇表

### 改进记录

#### 1. 生词提取：短语中的单独词汇也应提取

**问题**：用户指出 `grand mediocrity` 作为短语被提取，但 `mediocrity` 作为单独单词的含义也需要列出。

**改进**：在提取短语时，如果短语中包含用户可能不认识的单词，应该同时：
- 保留短语词条（如 `grand mediocrity`）
- 单独列出该单词的词条（如 `mediocrity`）

#### 2. 语法笔记合并模式

**观察**：当目标文件已存在且内容完整时，合并模式只需更新 `updated` 时间戳，无需重复添加已有的语法条目。

**原则**：判断重复的标准是核心语法结构模式和例句高度一致时视为重复。

### 技能执行顺序建议

对于首次处理一篇文章，推荐顺序：
1. `format-article` — 排版原始文章
2. `translate` — 翻译文章
3. `organize-grammar` — 整理语法笔记
4. `analyze-sentence` — 分析长难句
5. `compile-note` — 整合为综合笔记
6. `extract-vocabulary` — 提取生词
