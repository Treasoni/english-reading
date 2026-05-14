---
name: digest
description: 自我学习阶段。回顾本次学习会话，记录学习心得和错误到 .learnings/，当文件超阈值时自动压缩去重，更新 RULES.md，促进系统持续改进。触发时机：用户审核通过 evaluate 产出并明确要求记录学习后，Phase 6。
---

# Skill: digest（自我学习）

## 触发时机
用户审核通过 evaluate 产出后，且用户明确要求记录会话学习时。

## 输入
- `SYSTEM_ROOT`: StudySystem 根路径，如 `{VAULT_PATH}/StudySystem`
- `topic`: 主题名称

## 执行步骤

### Step 1: 检查压缩阈值

在记录新条目之前，检查是否需要先做压缩：

```bash
wc -l .learnings/LEARNINGS.md .learnings/ERRORS.md 2>/dev/null || echo "0 .learnings/LEARNINGS.md\n0 .learnings/ERRORS.md"
```

如果任一文件超过 100 行，先执行压缩流程：

1. 读取 `.learnings/LEARNINGS.md` 和 `.learnings/ERRORS.md` 中的所有条目
2. 按主题/模式分组，去重
3. 写入/更新 `.learnings/RULES.md`：
   - `## Do` — 值得坚持的做法
   - `## Don't` — 需要避免的错误
   - `## Watch For` — 需要特别注意的情况
   - 每行一条规则，合并重复出现：`(3x) 用 X 而非 Y`
   - 丢弃只出现一次的孤立噪声
4. 如果某规则对核心 Study System 流程至关重要，提升到 CLAUDE.md
5. 归档旧条目到 `.learnings/archive/YYYY-MM-DD.md`
6. 截断 `.learnings/LEARNINGS.md` 和 `.learnings/ERRORS.md` 只保留头部

### Step 2: 确保 .learnings/ 目录存在

```bash
mkdir -p .learnings
```

如果 `.learnings/LEARNINGS.md` 或 `.learnings/ERRORS.md` 不存在，创建最小头部。

### Step 3: 回顾本次会话

扫描评估发现和会话过程中遇到的任何问题：
- 是否有论断被判定为不准确？ → 记录到 `.learnings/LEARNINGS.md`，类别 `correction`
- 整理资料是否有缺口？ → 记录到 `.learnings/LEARNINGS.md`，类别 `knowledge_gap`
- collect/curate/write/beautify 阶段是否有报错？ → 记录到 `.learnings/ERRORS.md`
- 是否有值得未来 Study System 运行时参考的模式？ → 记录到 `.learnings/LEARNINGS.md`，类别 `best_practice`

### Step 4: 记录条目

使用自改进格式记录：

**学习条目**（追加到 `.learnings/LEARNINGS.md`）：
```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high
**Status**: pending
**Area**: docs

### Summary
One-line description

### Details
What happened, what was learned

### Suggested Action
What to do differently next time

---
```

**错误条目**（追加到 `.learnings/ERRORS.md`）：
```markdown
## [ERR-YYYYMMDD-XXX] phase_name

**Logged**: ISO-8601 timestamp
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
Brief description of what failed

### Error
```
Actual error message
```

### Context
What was being attempted

---
```

### Step 5: 无意义则不记录

如果本次会话没有错误且没有值得记录的学习点，跳过记录 —— 不创建空条目。质量比数量重要。

## 产出
- `.learnings/LEARNINGS.md`：追加新学习条目（如有）
- `.learnings/ERRORS.md`：追加新错误条目（如有）
- `.learnings/RULES.md`：去重压缩后的规则（如触发压缩）
- `.learnings/archive/YYYY-MM-DD.md`：归档文件（如触发压缩）

## 禁止行为
- 不要修改笔记本身
- 不要编造学习条目
- 不要跳过压缩阈值检查
- 不要归档未压缩的条目
- 不要在无意义时强行记录

## 硬停止 (Hard Stop)

本阶段任务完成。向用户展示捕获的学习摘要和压缩结果（如有）。

**严禁调用其他阶段技能。**
询问用户："学习记录完成。可以结束了吗？"
