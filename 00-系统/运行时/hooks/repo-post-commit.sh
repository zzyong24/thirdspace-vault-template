#!/bin/sh
# ThirdSpace repo-level post-commit hook（可选，放在单个 repo 的 .git/hooks/post-commit）
# Source of truth: vault/00-系统/运行时/hooks/repo-post-commit.sh
#
# vault 通过向上遍历 .thirdspace/workspace-index.yaml 自动定位，不硬编码路径。

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# 向上遍历找 vault 根
find_vault() {
    local dir="$1"
    while [ "$dir" != "/" ]; do
        if [ -f "$dir/.thirdspace/workspace-index.yaml" ]; then
            echo "$dir"; return 0
        fi
        dir=$(dirname "$dir")
    done
    [ -n "${THIRDSPACE_VAULT:-}" ] && echo "$THIRDSPACE_VAULT" && return 0
    return 1
}

VAULT=$(find_vault "$REPO_ROOT") || exit 0
SCRIPT="$VAULT/00-系统/Skills/thirdspace-vault/scripts/thirdspace-vault.mjs"
NODE_BIN="$(command -v node 2>/dev/null)"

[ -n "$NODE_BIN" ] || exit 0
[ -f "$SCRIPT" ]   || exit 0

"$NODE_BIN" "$SCRIPT" capture-git-commit --vault "$VAULT" --repo "$REPO_ROOT" >/dev/null 2>&1 || true
exit 0
