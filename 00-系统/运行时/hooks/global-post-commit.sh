#!/bin/sh
# ThirdSpace portable global post-commit hook.
# Source of truth: 00-系统/运行时/hooks/global-post-commit.sh
VAULT="${VAULT_PATH}"
SCRIPT="${VAULT_PATH}/00-系统/Skills/thirdspace-vault/scripts/thirdspace-vault.mjs"
NODE_BIN="$(command -v node 2>/dev/null)"
[ -n "$NODE_BIN" ] || exit 0
[ -f "$SCRIPT" ] || exit 0
[ -d "$VAULT" ] || exit 0
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
"$NODE_BIN" "$SCRIPT" capture-git-commit --vault "$VAULT" --repo "$REPO_ROOT" >/dev/null 2>&1 || true
exit 0
