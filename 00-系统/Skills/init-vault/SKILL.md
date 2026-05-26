---
name: init-vault
description: >-
  ThirdSpace 知识库初始化子 Skill。
  仅在用户明确触发时加载（"初始化"、"setup"、"install"、"配置知识库"）。
  日常知识库操作不加载本 Skill，避免无谓 token 消耗。
triggers:
  - "初始化知识库"
  - "初始化"
  - "setup"
  - "install"
  - "配置知识库"
  - "帮我配置"
  - "第一次使用"
parent: thirdspace-vault
---

# ThirdSpace 知识库初始化

## Agent 合约

本 Skill 负责在**新机器**上完成知识库的自举配置。

**不决策用户环境**：Agent 自行感知运行环境（OS、Shell、可用工具链、当前使用的 Agent 平台），
选择合适的安装方式。本 Skill 只描述**需要做什么**和**脚本在哪里**，不写死命令。

---

## 需要完成的事项（What，不是 How）

### 1. 确认结构完整

vault 根必须存在以下文件，缺失则从 `.thirdspace/schema/` 下的模板补全：

```
.thirdspace/workspace-index.yaml     ← vault 根锚点
.thirdspace/schema/frontmatter.yaml
.thirdspace/schema/taxonomy.yaml
.thirdspace/schema/subsystems.yaml
.thirdspace/schema/event-capture.yaml
.thirdspace/schema/workspace-tools.yaml
```

### 2. Agent Stop Hook（可选，推荐）

**作用**：每次 Agent session 结束时，检测重大产出并提示记录工作日志。

**脚本位置**：`./00-系统/运行时/hooks/claude-stop-hook.sh`

**需要做的事**：将脚本注册为 Agent 平台的 session stop / post-conversation hook。
不同平台注册方式不同，由 Agent 根据当前平台自行判断：
- Claude Code：`~/.claude/hooks/session-stop.sh`
- 其他平台：参考各平台 hook 文档

**用户可以跳过此步**，不影响知识库核心功能。

### 3. Git Hook（可选，推荐）

**作用**：每次 git commit 后自动记录提交事实到工作日志。

**脚本位置**：`./00-系统/运行时/hooks/global-post-commit.sh`（全局）或 `repo-post-commit.sh`（单 repo）

**需要做的事**：注册为 git post-commit hook，方式因环境而异。

**用户可以跳过此步**。

### 4. 定时任务（可选）

**作用**：每日定时触发工作日志归档等任务。

**配置模板位置**：`./00-系统/运行时/crontab/`

**需要做的事**：按用户环境注册定时任务（crontab / systemd timer / Task Scheduler 等）。

**用户可以跳过此步**。

### 5. Skill 全局注册（按需）

**作用**：让 Agent 从 vault 目录**之外**也能加载 thirdspace-vault Skill。

**需要做的事**：将 `./00-系统/Skills/thirdspace-vault` 链接或复制到 Agent 平台的全局 skills 目录。

不同 Agent 平台位置不同，由 Agent 自行判断。

### 6. Obsidian 插件启用（需用户手动）

插件已随 vault 分发，位于：`.obsidian/plugins/thirdspace-dashboard/`

用户需要在 Obsidian 中手动启用（无法自动化）：
设置 → 第三方插件 → 允许社区插件 → 启用 ThirdSpace Dashboard

---

## 验收检查

完成初始化后，运行以下检查确认基础结构就绪：

```bash
# 1. 工作区结构
find . -maxdepth 2 -name WORKSPACE.md | sort

# 2. Schema 完整性
find .thirdspace/schema -type f | sort

# 3. 无硬编码绝对路径（期望：0）
grep -r "/Users/\|/home/\|C:\\\\" .thirdspace/ CLAUDE.md AGENTS.md 2>/dev/null | grep -v ".git" | wc -l
```

---

## 给用户的说明

初始化结束后，Agent 用自然语言告知用户：

1. 已完成的步骤（结构验证、已安装的 hooks）
2. 跳过的可选步骤及原因
3. 需要用户手动操作的步骤（Obsidian 插件启用）
4. 如何开始使用（在 vault 目录打开 Claude Code，直接说"帮我记一条笔记"）
