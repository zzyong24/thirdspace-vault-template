---
title: "ThirdSpace Vault Skill 全局分发方案"
type: "spec"
topic: "system"
workspace: "00-系统"
created: "2026-05-26 00:00:00"
modified: "2026-05-26 00:00:00"
tags: ["system", "spec", "active"]
source: "manual"
status: "active"
---

# ThirdSpace Vault Skill 全局分发方案

> 目标：在任何目录、任何 Agent 平台说"知识库"，都能激活 `thirdspace-vault` skill。

---

## 一、整体架构

```
vault/00-系统/Skills/thirdspace-vault/   ← canonical 源（唯一维护点）
         ↓  symlink                ↓  symlink          ↓  symlink
~/.claude/skills/          ~/.cursor/rules/      ~/.opencode/skills/
thirdspace-vault           thirdspace-vault      thirdspace-vault
（Claude Code）             （Cursor）             （OpenCode）
         ↓  …更多 Agent 按需添加
```

**设计原则：**
- vault 是唯一维护点：`SKILL.md` 和 `scripts/` 只在 vault 里改
- 各 Agent 目录直接软链到 vault 源，**无任何中间层**
- 更新时只改 vault，所有 Agent 立即生效

---

## 二、初始化方式

### 自动初始化（推荐）

在 vault 目录打开 Agent，执行初始化指令，Agent 根据当前机器上已安装的 Agent 平台自动完成软链：

```
帮我初始化这个知识库
```

Agent 读取 `init-vault` Skill → 感知当前 Agent 平台和 OS → 创建对应软链。

### 手动初始化

```bash
VAULT="/path/to/vault"
SKILL="$VAULT/00-系统/Skills/thirdspace-vault"

# 按需选择对应 Agent 平台
mkdir -p ~/.claude/skills
ln -sf "$SKILL" ~/.claude/skills/thirdspace-vault        # Claude Code

mkdir -p ~/.cursor/rules
ln -sf "$SKILL" ~/.cursor/rules/thirdspace-vault         # Cursor

mkdir -p ~/.opencode/skills
ln -sf "$SKILL" ~/.opencode/skills/thirdspace-vault      # OpenCode

# … 其他 Agent 参考 MANUAL.md 中的路径表
```

---

## 三、各 Agent Skill 路径

| Agent | 全局 Skill 路径 |
|-------|----------------|
| Claude Code | `~/.claude/skills/` |
| Cursor | `.cursor/rules/`（项目级）|
| Windsurf | `.windsurf/rules/`（项目级）|
| OpenCode | `~/.opencode/skills/` |
| Codex | `~/.codex/skills/` |
| Amp | `~/.amp/skills/` |
| Goose | `~/.goose/skills/` |
| Gemini CLI | `~/.gemini/skills/` |

> 项目级规则（Cursor / Windsurf）：在 vault 目录打开时自动生效；全局安装需软链到各 Agent 的用户目录。

---

## 四、路径占位符规范

SKILL.md 内的所有路径必须使用占位符，禁止硬编码绝对路径：

| 占位符 | 含义 | 解析方式 |
|--------|------|---------|
| `{VAULT}` | vault 根目录 | 向上遍历找 `.thirdspace/workspace-index.yaml` |
| `{SKILLS}` | skills 根目录 | `{VAULT}/00-系统/Skills` |

---

## 五、维护说明

- **更新 Skill**：只改 `vault/00-系统/Skills/thirdspace-vault/`，软链自动生效
- **新增 Agent 支持**：`ln -sf "$SKILL" ~/.<agent>/skills/thirdspace-vault`
- **触发词调整**：修改 `thirdspace-vault/SKILL.md` 的 `triggers:` 字段
- **Scripts 更新**：直接改 `scripts/thirdspace-vault.mjs`，全平台即时生效
