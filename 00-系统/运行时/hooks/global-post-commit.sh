#!/bin/bash
# =============================================================================
# ThirdSpace Global Git post-commit hook
# Source of truth: vault/00-系统/运行时/hooks/global-post-commit.sh
# Install to: ~/.config/git/hooks/post-commit
#
# 设计：
#   - 全局生效（git config --global core.hooksPath ~/.config/git/hooks）
#   - 直接写文件，不依赖 MCP 或外部进程
#   - 向上遍历目录查找 vault 根（.thirdspace/workspace-index.yaml）
#   - 写入 02-日记/工作日志/YYYYMMDD_工作日志_周X.md
# =============================================================================

# ── 动态发现 vault 根（向上遍历） ──────────────────────────────
find_vault() {
    local dir="$1"
    while [ "$dir" != "/" ]; do
        if [ -f "$dir/.thirdspace/workspace-index.yaml" ]; then
            echo "$dir"
            return 0
        fi
        dir=$(dirname "$dir")
    done
    # 兜底：$THIRDSPACE_VAULT 环境变量
    if [ -n "${THIRDSPACE_VAULT:-}" ] && [ -f "$THIRDSPACE_VAULT/.thirdspace/workspace-index.yaml" ]; then
        echo "$THIRDSPACE_VAULT"
        return 0
    fi
    # 兜底：~/.thirdspace/config.yaml
    local configured=""
    configured=$(awk -F: '/^(default_vault|vault_root|vault):/{gsub(/^[ \t"]+|[ \t"]+$/, "", $2); print $2; exit}' "$HOME/.thirdspace/config.yaml" 2>/dev/null || true)
    if [ -n "$configured" ] && [ -f "$configured/.thirdspace/workspace-index.yaml" ]; then
        echo "$configured"
        return 0
    fi
    return 1
}

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
VAULT=$(find_vault "$REPO_ROOT") || exit 0

# ── 路径计算 ────────────────────────────────────────────────────
DATE_COMPACT=$(date "+%Y%m%d")
DATE_STR=$(date "+%Y-%m-%d")
TIME_STR=$(date "+%H:%M")
WEEKDAY_NUM=$(date "+%u")
case "$WEEKDAY_NUM" in
    1) WEEKDAY="周一" ;; 2) WEEKDAY="周二" ;; 3) WEEKDAY="周三" ;;
    4) WEEKDAY="周四" ;; 5) WEEKDAY="周五" ;; 6) WEEKDAY="周六" ;;
    *) WEEKDAY="周日" ;;
esac

WORKLOG_DIR="$VAULT/02-日记/工作日志"
FILEPATH="$WORKLOG_DIR/${DATE_COMPACT}_工作日志_${WEEKDAY}.md"

# ── 确保 worklog 文件存在 ────────────────────────────────────────
mkdir -p "$WORKLOG_DIR"
if [ ! -f "$FILEPATH" ]; then
    cat > "$FILEPATH" << TMPL
---
title: "${DATE_STR} ${WEEKDAY} 工作日志"
type: "worklog"
topic: "work"
workspace: "02-日记"
created: "$(date '+%Y-%m-%d %H:%M:%S')"
modified: "$(date '+%Y-%m-%d %H:%M:%S')"
tags: ["worklog", "work"]
source: "agent"
status: "active"
---
# ${DATE_STR} ${WEEKDAY} 工作日志

## 今日重点

## 今日Todo

## Git 提交

## 重点记录

## 关键决策

## 问题与风险

## 明日计划
TMPL
fi

# ── 获取 commit 信息 ────────────────────────────────────────────
COMMIT_HASH=$(git rev-parse --short HEAD 2>/dev/null)
COMMIT_MSG=$(git log -1 --pretty=format:"%s" 2>/dev/null)
REPO_NAME=$(basename "$REPO_ROOT")
BRANCH=$(git branch --show-current 2>/dev/null)
FILE_COUNT=$(git diff-tree --no-commit-id -r --name-only HEAD 2>/dev/null | wc -l | tr -d ' ')
FILES_CHANGED=$(git diff-tree --no-commit-id -r --name-only HEAD 2>/dev/null | head -5 | tr '\n' ' ' | sed 's/ $//')

ENTRY="- **[$TIME_STR]** \`$REPO_NAME/$BRANCH\` \`$COMMIT_HASH\`: $COMMIT_MSG (${FILE_COUNT}文件: $FILES_CHANGED)"

# ── 插入到「## Git 提交」章节下 ─────────────────────────────────
TMPFILE=$(mktemp)
INSERTED=false

while IFS= read -r line; do
    echo "$line" >> "$TMPFILE"
    if [ "$INSERTED" = false ] && echo "$line" | grep -q "^## Git 提交"; then
        echo "" >> "$TMPFILE"
        echo "$ENTRY" >> "$TMPFILE"
        INSERTED=true
    fi
done < "$FILEPATH"

if [ "$INSERTED" = false ]; then
    echo "" >> "$TMPFILE"
    echo "$ENTRY" >> "$TMPFILE"
fi

mv "$TMPFILE" "$FILEPATH"
exit 0
