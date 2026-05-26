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
    ↓  symlink
~/.skills-manager/skills/thirdspace-vault/   ← 中央库（skills-manager 管理）
    ↓  symlink                ↓  symlink
~/.claude/skills/             ~/.codebuddy/skills/
thirdspace-vault              thirdspace-vault
（Claude Code）               （CodeBuddy）
```

**链路规则：**
- vault 是唯一维护点：SKILL.md 和 scripts/ 只在 vault 里改
- 中央库是 skills-manager 的注册中心：通过软链接指向 vault，更新自动同步
- Agent 目录都指向中央库，保持与其他 skills 一致的管理方式

---

## 二、skills-manager 机制说明

`~/.skills-manager/` 是本机 Skills Manager 桌面应用的数据目录：

| 路径 | 说明 |
|------|------|
| `~/.skills-manager/skills/` | 中央库，存放所有已注册 skill（实际文件或软链接） |
| `~/.skills-manager/skills-manager.db` | SQLite 元数据库，记录安装状态和 skill 信息 |
| `~/.claude/skills/<name>` | Claude Code 全局 skill 目录，软链接到中央库 |
| `~/.codebuddy/skills/<name>` | CodeBuddy 全局 skill 目录，软链接到中央库 |

**分发路径**：vault 源 → 中央库（软链接）→ 各 Agent 目录（软链接）→ Agent 加载

---

## 三、当前安装状态

| 位置 | 路径 | 状态 |
|------|------|------|
| canonical 源 | `vault/00-系统/Skills/thirdspace-vault/` | ✅ 维护中 |
| skills-manager 中央库 | `~/.skills-manager/skills/thirdspace-vault` | ✅ 软链接到 vault |
| Claude Code | `~/.claude/skills/thirdspace-vault` | ✅ 软链接到中央库 |
| CodeBuddy | `~/.codebuddy/skills/thirdspace-vault` | ✅ 软链接到中央库 |

---

## 四、换电脑初始化步骤

在新机器上，clone vault 后执行：

```bash
VAULT="/path/to/vault"          # vault 实际路径
SKILL="$VAULT/00-系统/Skills/thirdspace-vault"

# 1. 注册到 skills-manager 中央库
mkdir -p ~/.skills-manager/skills
ln -sf "$SKILL" ~/.skills-manager/skills/thirdspace-vault

# 2. Claude Code 全局安装
mkdir -p ~/.claude/skills
ln -sf ~/.skills-manager/skills/thirdspace-vault ~/.claude/skills/thirdspace-vault

# 3. CodeBuddy 全局安装（如果使用 CodeBuddy）
mkdir -p ~/.codebuddy/skills
ln -sf ~/.skills-manager/skills/thirdspace-vault ~/.codebuddy/skills/thirdspace-vault

# 4. 可选：设置机器级配置（vault 目录外触发时使用）
mkdir -p ~/.thirdspace
cat > ~/.thirdspace/config.yaml << EOF
vault: $VAULT
EOF
```

---

## 五、触发词配置

`thirdspace-vault/SKILL.md` 的触发词（当前）：

```yaml
triggers:
  - "知识库"
  - "存进知识库"
  - "记到知识库"
  - "查知识库"
  - "整理知识库"
  - "知识库里"
  - "维护知识库"
  - "初始化知识库"
  - "当前工作区"
  - "ThirdSpace"
  - "vault"
```

任意 Agent 平台，说出这些词即自动激活。

---

## 六、路径约定（SKILL.md 编写规范）

所有 skill 内的路径引用必须使用占位符，禁止硬编码：

| 占位符 | 含义 | 解析方式 |
|--------|------|---------|
| `{VAULT}` | vault 根目录 | 向上遍历找 `.thirdspace/workspace-index.yaml`，或读 `~/.thirdspace/config.yaml` |
| `{SKILLS}` | skills 根目录（`vault/00-系统/Skills`） | `{VAULT}/00-系统/Skills` |
| `{REMOTION_WORKSPACE}` | Remotion 工作目录 | 机器级配置，可加入 `~/.thirdspace/config.yaml` 的 `remotion_workspace` 字段 |

违例格式（已修复）：
- ~~`{VAULT_PATH}/...`~~ → `{VAULT}/...`
- ~~`{USER_HOME}/remotions`~~ → `{REMOTION_WORKSPACE}`

---

## 七、维护说明

- **更新 SKILL.md**：只改 `vault/00-系统/Skills/thirdspace-vault/SKILL.md`，软链接自动生效
- **新增 Agent 平台支持**：`ln -sf ~/.skills-manager/skills/thirdspace-vault ~/.new-agent/skills/thirdspace-vault`
- **清理注册**：删除中央库软链接 + 各 Agent 目录软链接即可
- **Scripts 更新**：直接改 `vault/00-系统/Skills/thirdspace-vault/scripts/thirdspace-vault.mjs`，全平台即时生效

---

*记录于 2026-05-26，工作电脑*
