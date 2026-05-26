#!/bin/bash
# ============================================================
# ThirdSpace Vault — 沙箱初始化测试脚本
#
# 用法：
#   Docker:  docker compose run sandbox        （自动传入 /vault-template）
#   本机:    TEMPLATE=/path/to/template bash test-init.sh
# ============================================================
set -euo pipefail

TEMPLATE="${TEMPLATE:-/vault-template}"
VAULT="/tmp/ts-sandbox-$$"
TEST_REPO="/tmp/ts-testrepo-$$"
PASS=0; FAIL=0

green() { echo -e "\033[32m✓ $*\033[0m"; }
red()   { echo -e "\033[31m✗ $*\033[0m"; }
cyan()  { echo -e "\033[36m▶ $*\033[0m"; }

check() {
  local desc="$1"; shift
  if "$@" > /dev/null 2>&1; then
    green "$desc"; PASS=$((PASS + 1))
  else
    red  "$desc"; FAIL=$((FAIL + 1))
  fi
}

cleanup() { rm -rf "$VAULT" "$TEST_REPO" 2>/dev/null || true; }
trap cleanup EXIT

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   ThirdSpace Vault — Sandbox Init Test       ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── STEP 1: 模板结构验证 ─────────────────────────────────────
cyan "STEP 1: 复制模板 → 测试 vault"
rm -rf "$VAULT"
cp -r "$TEMPLATE" "$VAULT"

check "workspace-index.yaml 存在"         test -f "$VAULT/.thirdspace/workspace-index.yaml"
check "schema/ 包含 5 个文件"             bash -c "[ $(ls $VAULT/.thirdspace/schema/*.yaml 2>/dev/null | wc -l) -eq 5 ]"
check "Skills/thirdspace-vault 存在"      test -d "$VAULT/00-系统/Skills/thirdspace-vault"
check "Skills/init-vault 存在"            test -d "$VAULT/00-系统/Skills/init-vault"
check "运行时/hooks 存在"                 test -d "$VAULT/00-系统/运行时/hooks"
check "CLAUDE.md 存在"                    test -f "$VAULT/CLAUDE.md"
check "AGENTS.md 存在"                    test -f "$VAULT/AGENTS.md"
check "8 个工作区目录"                    bash -c "[ $(ls -d $VAULT/0[0-9]-* $VAULT/99-* 2>/dev/null | wc -l) -ge 8 ]"

echo ""

# ── STEP 2: 路径无关性检查 ───────────────────────────────────
cyan "STEP 2: 路径无关性验证（期望 0 个硬编码绝对路径）"

check "schema/ 无硬编码路径" \
  bash -c "! grep -r '/Users/\|/home/' $VAULT/.thirdspace/ 2>/dev/null | grep -qv '#'"
check "运行时/ 无硬编码路径（test-init.sh 除外）" \
  bash -c "! grep -r '/Users/' $VAULT/00-系统/运行时/ --include='*.sh' --include='*.yaml' \
    --exclude='test-init.sh' 2>/dev/null | grep -q ."
check "thirdspace-vault.mjs 无硬编码路径" \
  bash -c "! grep -q '/Users/' $VAULT/00-系统/Skills/thirdspace-vault/scripts/thirdspace-vault.mjs"

echo ""

# ── STEP 3: Node.js 脚本 ─────────────────────────────────────
cyan "STEP 3: Node.js 脚本测试"
SCRIPT="$VAULT/00-系统/Skills/thirdspace-vault/scripts/thirdspace-vault.mjs"

check "node 可用"                test -n "$(node --version 2>/dev/null)"
check "resolve-vault（从 vault 目录）" \
  bash -c "cd $VAULT && node $SCRIPT resolve-vault --cwd . 2>&1 | grep -q vaultRoot"
check "resolve-vault（无 vault 时报错，不 fallback）" \
  bash -c "cd /tmp && THIRDSPACE_VAULT= node $SCRIPT resolve-vault --cwd . 2>&1 | grep -qiE 'error|Cannot resolve'"

echo ""

# ── STEP 4: git hook 全流程 ──────────────────────────────────
cyan "STEP 4: git hook → worklog 写入测试"

# 安装模板自己的 hook（测试应自给自足，不依赖系统已安装版本）
mkdir -p ~/.config/git/hooks
cp "$VAULT/00-系统/运行时/hooks/global-post-commit.sh" ~/.config/git/hooks/post-commit
chmod +x ~/.config/git/hooks/post-commit
git config --global core.hooksPath ~/.config/git/hooks

# 清空旧工作日志（模板 cp 可能带入遗留文件）
rm -f "$VAULT/02-日记/工作日志/"*.md 2>/dev/null || true

mkdir -p "$TEST_REPO" && cd "$TEST_REPO"
git init -b main -q
git config user.email "sandbox@test.local"
git config user.name  "Sandbox"
echo "# test" > file.md && git add file.md

THIRDSPACE_VAULT="$VAULT" git commit -m "test: verify hook creates worklog" -q

LOGFILE=$(ls "$VAULT/02-日记/工作日志/"*.md 2>/dev/null | head -1 || echo "")

check "worklog 文件已创建"                test -n "$LOGFILE"
check "worklog 含 Frontmatter"            bash -c "grep -q '^type:' '$LOGFILE' 2>/dev/null"
check "worklog 含 ## Git 提交 section"    bash -c "grep -q '## Git 提交' '$LOGFILE' 2>/dev/null"
check "worklog 含 commit 记录"            bash -c "grep -q 'ts-testrepo' '$LOGFILE' 2>/dev/null"
check "worklog 含 ## 今日Todo"            bash -c "grep -q '## 今日Todo' '$LOGFILE' 2>/dev/null"
check "worklog 含 ## 重点记录"            bash -c "grep -q '## 重点记录' '$LOGFILE' 2>/dev/null"

cd ~

echo ""

# ── STEP 5: stop hook 语法检查 ───────────────────────────────
cyan "STEP 5: Stop hook 语法检查"
check "claude-stop-hook.sh 语法正确" \
  bash -n "$VAULT/00-系统/运行时/hooks/claude-stop-hook.sh"
check "global-post-commit.sh 语法正确" \
  bash -n "$VAULT/00-系统/运行时/hooks/global-post-commit.sh"
check "repo-post-commit.sh 语法正确" \
  bash -n "$VAULT/00-系统/运行时/hooks/repo-post-commit.sh"

echo ""

# ── 结果 ─────────────────────────────────────────────────────
echo "╔══════════════════════════════════════════════╗"
printf  "║  结果: ✓ %d PASS   ✗ %d FAIL%*s║\n" $PASS $FAIL $((26 - ${#PASS} - ${#FAIL})) ""
echo "╚══════════════════════════════════════════════╝"

if [ -n "${LOGFILE:-}" ]; then
  echo ""
  echo "生成的 worklog 内容预览："
  echo "──────────────────────────"
  head -25 "$LOGFILE"
fi

[ "$FAIL" -eq 0 ] && exit 0 || exit 1
