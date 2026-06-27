#!/bin/bash
# Hook: 在每个 agent 启动前读取错误文件和经验库
# 输出会被注入到 agent 的上下文中作为系统提醒

LEARNINGS_DIR=".learnings"
VAULT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

# 输出分隔符，让 agent 知道这是来自 hook 的内容
echo "<system-reminder>"
echo "# 经验库提醒"
echo ""

# 读取 RULES.md
if [ -f "$VAULT_ROOT/$LEARNINGS_DIR/RULES.md" ]; then
    echo "## 铁律（最高优先级）"
    echo ""
    cat "$VAULT_ROOT/$LEARNINGS_DIR/RULES.md"
    echo ""
    echo "---"
    echo ""
fi

# 读取 ERRORS.md
if [ -f "$VAULT_ROOT/$LEARNINGS_DIR/ERRORS.md" ]; then
    echo "## 错误日志（必须避免）"
    echo ""
    cat "$VAULT_ROOT/$LEARNINGS_DIR/ERRORS.md"
    echo ""
    echo "---"
    echo ""
fi

# 读取 LEARNINGS.md（只读最近的条目，避免过长）
if [ -f "$VAULT_ROOT/$LEARNINGS_DIR/LEARNINGS.md" ]; then
    echo "## 最近学习心得"
    echo ""
    # 只读取文件的最后 50 行（最新的条目）
    tail -50 "$VAULT_ROOT/$LEARNINGS_DIR/LEARNINGS.md"
    echo ""
fi

echo ""
echo "**提醒：执行任何任务前，必须先检查以上铁律和错误记录，避免重蹈覆辙。**"
echo "</system-reminder>"
