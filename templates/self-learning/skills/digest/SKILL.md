---
name: digest
description: 自我学习阶段。回顾本次会话，记录真实发生的学习点和错误到 .learnings/；当经验库过长时压缩去重并更新 RULES.md；如果发现重复错误或规则失效，转交 maintain-learnings 先修源头。用户明确要求记录学习、复盘、写入 learnings、digest 时触发。
---

# digest（自我学习）

记录真实发生的学习和错误。不要为了“显得有产出”编造条目；质量比数量重要。

## Step 1: 检查压缩阈值

```bash
wc -l .learnings/LEARNINGS.md .learnings/ERRORS.md 2>/dev/null || true
```

如果任一文件超过 100 行，先判断：

- 只是旧记录堆积：压缩、去重、归档。
- 同类错误复发或 `RULES.md` 已有规则仍失效：停止单纯压缩，改用 `maintain-learnings` 修 skill / 模板 / hook / 项目规则，验证后再归档。

## Step 2: 确保目录存在

```bash
mkdir -p .learnings .learnings/archive
```

若文件不存在，创建最小头部：

- `.learnings/LEARNINGS.md`
- `.learnings/ERRORS.md`
- `.learnings/RULES.md`

## Step 3: 回顾本次任务

只记录本次任务中实际发生的内容：

- 用户纠正了什么？
- 哪个判断、操作或输出有问题？
- 根因是什么？
- 下次应该用什么可执行规则避免？
- 是否需要修改 skill、模板、hook、脚本或项目规则？

## Step 4: 写入条目

学习条目追加到 `.learnings/LEARNINGS.md`：

```markdown
## YYYY-MM-DD

### <简短主题>

**类别**：correction | knowledge_gap | best_practice | workflow
**优先级**：low | medium | high
**状态**：pending
**范围**：<skill / module / workflow / docs>

**摘要**：一句话说明学到了什么。

**详情**：
- 事实：
- 根因：
- 下次做法：

---
```

错误条目追加到 `.learnings/ERRORS.md`：

```markdown
## YYYY-MM-DD

### <skill 或阶段>：<错误标题>

**错误**：实际发生了什么。

**触发场景**：什么时候发生。

**根因**：为什么发生。

**修复**：
- 已采取的修复动作。

**预防措施**：
- 下次必须执行的检查或规则。

---
```

## Step 5: 更新 RULES.md

只把高价值、可复用、可执行的规则提炼到 `.learnings/RULES.md`。格式保持短：

```markdown
## <area>

- **规则名**：用 X，而不是 Y。
```

## Step 6: 无意义则不记录

如果本次任务没有错误、没有纠正、没有可迁移经验，不写空条目。

## 禁止行为

- 不要编造学习点。
- 不要把长故事塞进 `RULES.md`。
- 不要把“下次注意”当成源头修复。
- 不要在未修复、未验证前归档复发错误。
