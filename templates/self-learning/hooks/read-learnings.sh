#!/bin/bash
# Hook: read .learnings into the agent context at session start.

set -u

LEARNINGS_DIR=".learnings"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "<system-reminder>"
echo "# Learnings Reminder"
echo ""

if [ -f "$PROJECT_ROOT/$LEARNINGS_DIR/RULES.md" ]; then
    echo "## Rules (highest priority)"
    echo ""
    cat "$PROJECT_ROOT/$LEARNINGS_DIR/RULES.md"
    echo ""
    echo "---"
    echo ""
fi

if [ -f "$PROJECT_ROOT/$LEARNINGS_DIR/ERRORS.md" ]; then
    echo "## Error Log (avoid repeating)"
    echo ""
    cat "$PROJECT_ROOT/$LEARNINGS_DIR/ERRORS.md"
    echo ""
    echo "---"
    echo ""
fi

if [ -f "$PROJECT_ROOT/$LEARNINGS_DIR/LEARNINGS.md" ]; then
    echo "## Recent Learnings"
    echo ""
    tail -50 "$PROJECT_ROOT/$LEARNINGS_DIR/LEARNINGS.md"
    echo ""
fi

echo ""
echo "Before doing task work, apply the rules and avoid repeating recorded errors."
echo "</system-reminder>"
