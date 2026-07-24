---
name: sync-skill-registry
description: 技能注册表同步工具。扫描任意 agent skill 目录中的 */SKILL.md 并自动更新对应 skill-invocation.md 中的技能列表表格。用于新增、修改或删除本地技能后同步注册表。触发词：同步注册表、更新技能列表、sync skill registry、update skill registration、刷新技能列表、同步技能表格。
category: 工具发现
---

# sync-skill-registry（技能注册表同步）

读取任意 agent skill 目录中的 `*/SKILL.md` frontmatter 元数据，自动更新 `skill-invocation.md` 中的技能表格，确保注册表与本地技能文件保持一致。

## 工作流程

```bash
# 1️⃣ 预览变更（推荐先 dry-run）
python3 .claude/skills/sync-skill-registry/scripts/sync_skill_registry.py --dry-run

# 2️⃣ 确认无误后应用
python3 .claude/skills/sync-skill-registry/scripts/sync_skill_registry.py

# Generic profile 示例
python3 skills/sync-skill-registry/scripts/sync_skill_registry.py --profile generic --root /path/to/project --create --dry-run

# 完全自定义路径
python3 skills/sync-skill-registry/scripts/sync_skill_registry.py --root /path/to/project --skills-dir .my-agent/skills --registry-file .my-agent/rules/common/skill-invocation.md --dry-run
```

## 何时使用

| 场景 | 说明 |
|------|------|
| 新增本地技能 | 创建了新的 `<skills-dir>/<name>/SKILL.md` 后运行 |
| 修改现有技能 | 更新了 SKILL.md 的 name、description 或 category 后运行 |
| 删除本地技能 | 移除了某个 SKILL.md 后运行（自动移除表格条目） |
| 定期同步 | 不确定当前注册表是否最新时运行 `--dry-run` 检查 |
| 批量清理 | 多个技能变更后一次同步 |

## 工作原理

1. **扫描**：遍历 `<skills-dir>/*/SKILL.md`，解析 YAML frontmatter（name, description, category）
2. **解析**：读取当前 `skill-invocation.md`，提取现有表格条目
3. **比较**：
   - 新增：SKILL.md 存在但表格中缺失 → 生成新行加入对应分类
   - 更新：SKILL.md 和表格中都存在 → 用 frontmatter 覆盖表格行
   - 删除：上次同步标记为受管、但 SKILL.md 已不存在 → 移除行
   - 保留：无 SKILL.md 的条目（如 excalidraw-diagram、dataviz）→ 保持不变
4. **生成**：按分类重新生成 Markdown 表格
5. **写入**：替换 `## 技能列表` 至 `### 1. 分析意图` 之间的内容

## 分类确定优先级

```
1. SKILL.md frontmatter 中的 category 字段（首选）
2. FALLBACK_CATEGORIES 映射（symlink 技能如 skill-creator）
3. 当前表格中的位置推断
4. 默认值"未分类"
```

## 注意事项

- 只管理 `## 技能列表` ~ `### 1. 分析意图` 之间的表格内容
- 生成区会写入 `skill-registry:managed` 所有权标记；首次升级保留无法判定来源的旧条目，后续同步可准确删除已移除的本地 skill
- 不修改手动维护部分（核心原则、Obsidian 说明、分析意图、匹配技能、错误处理）
- 不创建或删除任何 SKILL.md 文件
- 支持 `--profile codex|claude|generic`，也支持 `--skills-dir` 与 `--registry-file` 完全自定义路径
- 同步 `--dry-run` 预览变更，确认后再应用
