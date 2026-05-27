#!/bin/bash
# ThirdSpace Claude Code Stop Hook
# 存储位置（vault 内）：00-系统/运行时/hooks/claude-stop-hook.sh
# 安装位置（机器上）：~/.claude/hooks/session-stop.sh
#
# 功能：检测本次 session 有重大产出时，提示 Agent 写工作日志。
# 防死循环：写完日志 Agent 再次触发 Stop 时，检测锁文件直接放行。

set -euo pipefail

log() { echo "[stop-hook] $*" >&2; }

# ── 防死循环锁 ──────────────────────────────────────────────
STATE_DIR="$HOME/.claude/hook_state"
mkdir -p "$STATE_DIR"
LOCK_FILE="$STATE_DIR/stop_hook_active.flag"

if [ -f "$LOCK_FILE" ]; then
    rm -f "$LOCK_FILE"
    echo "{}"
    exit 0
fi

# ── 检测 vault（向上遍历查找 .thirdspace/workspace-index.yaml）──
find_vault() {
    local dir="${1:-$PWD}"
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

VAULT=$(find_vault "${PWD:-$HOME}") || { echo "{}"; exit 0; }

# ── 路径计算 ────────────────────────────────────────────────
DATE_STR=$(date "+%Y-%m-%d")
DATE_COMPACT=$(date "+%Y%m%d")
WEEKDAY_NUM=$(date "+%u")
case "$WEEKDAY_NUM" in
    1) WEEKDAY="周一" ;; 2) WEEKDAY="周二" ;; 3) WEEKDAY="周三" ;;
    4) WEEKDAY="周四" ;; 5) WEEKDAY="周五" ;; 6) WEEKDAY="周六" ;;
    *) WEEKDAY="周日" ;;
esac

WORKLOG_DIR="$VAULT/02-日记/工作日志"
FILEPATH="$WORKLOG_DIR/${DATE_COMPACT}_工作日志_${WEEKDAY}.md"

# ── 确保 worklog 文件存在 ───────────────────────────────────
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

## 重点记录

## 关键决策

## 问题与风险

## 明日计划
TMPL
fi

# ── 防重复触发 flag ─────────────────────────────────────────
FLAG_FILE="$STATE_DIR/worklog_saved_${DATE_STR}.flag"
MAJOR_FLAG="$STATE_DIR/major_work_${DATE_STR}.flag"

# ── 检测重大产出 ────────────────────────────────────────────
HAS_MAJOR=false
CWD="${PWD:-$HOME}"

# 今日有 git commit
if git -C "$CWD" log --oneline --since="midnight" 2>/dev/null | grep -q .; then
    HAS_MAJOR=true
fi

# stdin 包含完成关键词
STDIN_IN=$(cat 2>/dev/null || echo "")
if echo "$STDIN_IN" | grep -qiE '(completed|finished|commit|任务完成|全部通过|验收通过|merge|deploy)'; then
    HAS_MAJOR=true
fi

# ── 决策 ────────────────────────────────────────────────────
if [ "$HAS_MAJOR" = true ] && [ ! -f "$MAJOR_FLAG" ]; then
    touch "$LOCK_FILE"
    touch "$MAJOR_FLAG"
    date +%s > "$FLAG_FILE"
    cat << 'EOF'
{
  "decision": "block",
  "reason": "检测到本次 session 有重大产出。请将关键内容追加到今日工作日志（02-日记/工作日志/YYYYMMDD_工作日志_周X.md）的「重点记录」章节，格式：### HH:MM — 标题 / **为什么做** / **怎么做的** / **改了什么**。用 Edit 工具直接追加写入。写完后正常停止。"
}
EOF
    exit 0
fi

if [ ! -f "$FLAG_FILE" ]; then
    touch "$LOCK_FILE"
    date +%s > "$FLAG_FILE"
    cat << 'EOF'
{
  "decision": "block",
  "reason": "请在停止前将本次对话关键内容写入工作日志（02-日记/工作日志/YYYYMMDD_工作日志_周X.md），用 Edit 工具追加到「重点记录」章节。写完后正常停止。"
}
EOF
    exit 0
fi

echo "{}"
exit 0
