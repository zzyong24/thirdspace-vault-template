---
name: thirdspace-vault
description: >-
  激活词：知识库。任何时候用户说"知识库"、"存进知识库"、"记到知识库"、"查知识库"、"整理知识库"，
  或涉及 ThirdSpace vault 的操作（创建笔记、归类文件、工作区路由、Frontmatter 规范、审计结构），
  立即加载本 Skill。从任意目录工作，无需用户手动指定路径。
  Activation: any mention of "知识库", "ThirdSpace", "vault", or knowledge-base operations.
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
---

# ThirdSpace Vault Root Skill

## Agent-native Contract

用户不需要手动执行命令。Agent 触发本 Skill 后，应该直接调用 `scripts/thirdspace-vault.mjs` 完成检测、初始化、创建文件、更新 Frontmatter 和审计。

## 渐进式加载

1. 用 `resolve-vault --cwd "$PWD"` 定位 vault。
2. 读取 `{VAULT}/.thirdspace/workspace-index.yaml`。
3. 读取 `{VAULT}/.thirdspace/schema/taxonomy.yaml`。
4. 读取 `{VAULT}/.thirdspace/schema/subsystems.yaml`。
5. 读取 `{VAULT}/.thirdspace/schema/event-capture.yaml`。
6. 读取 `{VAULT}/.thirdspace/schema/workspace-tools.yaml`。
7. 先根据用户意图匹配工作区、允许的一层目录、自治子系统契约、事件采集策略和工具 Skill；如果当前 `pwd` 在 vault 内，再用 `pwd` 校准。
8. 读取 `<workspace>/WORKSPACE.md`。
9. 加载 workspace 对应子 Skill。
10. 只有意图命中时加载领域 Skill，例如 `lifeos`、`worklog`、`article`。
11. 执行文件创建、更新、标签、Frontmatter、流转、审计、修复和高价值事件记录。

## Script Interface

```bash
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs resolve-vault --cwd "$PWD"
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs detect --vault {VAULT} --cwd "$PWD"
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs init --vault /path/to/new-vault
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs init --vault /path/to/new-vault --install-runtime
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs route-create --cwd "$PWD" --intent "写一篇开发文档" --title "项目部署流程"
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs migrate-flux-intake --vault {VAULT} --dry-run
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs create --vault {VAULT} --workspace 03-知识 --subdir AI工程 --title "Agent工作流" --topic ai --type note
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs ensure-worklog
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs record-agent-event --cwd "$PWD" --summary "完成重要产出" --decision "采用当前方案" --reason "更符合知识库自治目标"
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs register-hooks --repo "$PWD"
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs ensure-runtime-assets --vault {VAULT}
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs install-runtime --vault {VAULT} --all
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs update-frontmatter --file /path/to/file.md --topic ai --type note
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs audit-system --vault {VAULT}
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs audit-projects --vault {VAULT} --write-report
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs audit-workspaces --vault {VAULT} --write-report
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs audit-subsystems --vault {VAULT} --write-report
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs audit-skill-locations --vault {VAULT} --write-report
```

## Create File Policy

- Agent 必须优先用 `create` 创建新 Markdown。
- 当前工作区可由 `detect` 推断；不确定时写入 `01-收件箱/待整理`。
- `create` 会自动生成 `YYYYMMDD_主题.md` 和标准 Frontmatter。
- 更新旧文件 Frontmatter 时用 `update-frontmatter`，保留正文。

## 默认行为

- 不确定放哪里时，先放入 `01-收件箱/待整理/`。
- 不直接删除历史文件。
- 不直接批量迁移；先生成 queue 或 manifest。
- Prompt 能力统一转成 Skill，不写入全局 prompts 目录。
- 结构异常、缺失目录和深层嵌套用 `audit-workspaces` 检查。
- 子系统契约漂移、Skill 缺失、Frontmatter 缺失用 `audit-subsystems` 检查，并写入 `subsystem-maintenance.yaml`。
- 任意目录写入知识库时先 `resolve-vault`，再 `route-create`。
- Git Hook 只记录 commit 级事实；Agent Hook 只记录重大产出、关键决策和理由。
- CLI 不是用户入口；旧 CLI 能力必须被包装成 Skill。
- 所有 Skill scripts 的 canonical 根目录是 `00-系统/Skills`；不得再把可维护脚本散落到 Workbase、`.codex/skills` 或项目子目录的 Skill 中。
- Hook、crontab 和 Agent 自动化规格必须在 `00-系统/运行时` 留存；跨电脑迁移时由 Agent 调用 `install-runtime --all` 自动注册。
- `flux/`、`space/crafted/lifeos` 只能作为 legacy source，不作为新内容入口。
- 旧 `flux/intake` 已迁入 `01-收件箱/网页剪藏` 和 `05-资源/图片/flux-intake-assets`，需要追溯时读取 migration manifest。

## Project Classification Policy

- `04-项目` 的分类以项目意图为准，不以历史来源为准。
- 发现项目分类不准时，先运行 `audit-projects`，输出建议路径、置信度和理由。
- `audit-projects` 不移动文件；跨分类移动必须由后续明确任务执行，并写 trace。
- 低置信度项目必须人工确认。

## 工作区映射

| 路径 | Skill |
|---|---|
| `00-系统` | `workspace-system` |
| `01-收件箱` | `workspace-inbox` |
| `02-日记` | `workspace-journal` |
| `03-知识` | `workspace-knowledge` |
| `04-项目` | `workspace-projects` |
| `05-资源` | `workspace-resources` |
| `06-输出` | `workspace-outputs` |
| `99-归档` | `workspace-archive` |

## 初始化

用户触发"初始化"/"setup"/"install"时，加载子 Skill：
`00-系统/Skills/init-vault/SKILL.md`

## Frontmatter 规范（必填 9 字段）

```yaml
---
title: "标题"
type: note              # 见 .thirdspace/schema/taxonomy.yaml
topic: work             # ai|dev|reading|work|project|tools|writing|life|system
workspace: "01-收件箱"  # 当前工作区目录名
created: "2026-05-26 10:00:00"
modified: "2026-05-26 10:00:00"
tags: ["note", "draft"]
source: manual          # mcp|manual|obsidian-clipper|web|import
status: draft           # draft|active|processed|archived
---
```
