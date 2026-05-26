# Skills 索引

本文记录 ThirdSpace 当前 Skill 的真实位置、分层职责和加载规则。后续 Agent 不应再寻找旧 `prompts/`、`ai-context/` 或人类手动 CLI 入口。

## Skill 位置

| 层级 | 路径 | 用途 |
|---|---|---|
| 全局入口 | `{AGENTS_SKILLS}/thirdspace-vault/SKILL.md` | 任意目录触发知识库操作时首先加载的入口 Skill。 |
| 全局领域入口 | `{AGENTS_SKILLS}/lifeos/SKILL.md` | LifeOS 的全局轻量入口，指向 canonical Skill。 |
| Canonical ThirdSpace Skills | `{VAULT}/00-系统/Skills/` | 工作区 Skill、领域 Skill、局部创作 Skill 和内部脚本的唯一主维护位置。 |
| 运行时资产 | `{VAULT}/00-系统/运行时/` | hook、crontab、Agent 自动化规格的可迁移源。 |

## 对外入口

对外只暴露一个根 Skill：

```text
thirdspace-vault
```

根 Skill 负责：

- 从任意目录解析 vault。
- 读取工作区索引和 schema。
- 根据用户意图路由目标工作区，`pwd` 只作为辅助信号。
- 渐进加载工作区 Skill 和领域 Skill。
- 调用内部脚本完成创建、Frontmatter 更新、审计、日志和 Hook 注册。
- 从 `00-系统/运行时` 安装本机 hook、crontab 和自动化任务。

## 工作区 Skills

| 工作区 | Skill | 主要职责 |
|---|---|---|
| `00-系统` | `workspace-system` | 规范、Schema、Agent 入口、Skill 索引、审计。 |
| `01-收件箱` | `workspace-inbox` | 网页剪藏、临时想法、素材暂存、待整理队列。 |
| `02-日记` | `workspace-journal` | 每日、工作日志、反思、复盘、人际事件。 |
| `03-知识` | `workspace-knowledge` | 知识卡片、主题笔记、长期知识沉淀。 |
| `04-项目` | `workspace-projects` | 活跃项目分类、项目文档、项目内局部上下文。 |
| `05-资源` | `workspace-resources` | 模板、附件、图片、人物档案、可复用工具资料。 |
| `06-输出` | `workspace-outputs` | 文章、口播稿、视频脚本、PPT、发布稿。 |
| `99-归档` | `workspace-archive` | 迁移记录、废弃系统、废弃工具、完结项目。 |

## 领域 Skills

领域 Skill 只在意图命中时加载：

| 场景 | Skill |
|---|---|
| 人际事件、人物档案、关系复盘 | `lifeos` |
| 工作日志、Git Hook、Agent 产出记录 | `worklog` |
| 文章、教程、发布稿 | `article` |
| 项目文档、MVP、实践迭代 | `mvp-project`、`ship-learn-next` |
| 视频收集、视频分析 | `video-collector`、`video-analyzer` |
| Canvas 可视化 | `obsidian-canvas` |
| 知识卡片、学习文档 | `knowledge` |
| 创作数据、内容健康度 | `creation-tracking` |
| Markdown 转图片 | `mkd2pic` |
| 飞书导入、提醒、任务协同 | `feishu` |

## Prompt 与旧 CLI 规则

- Prompt 不再作为全局目录维护。
- 可复用提示词必须归入具体 Skill 的 `prompts/`、`templates/` 或 `references/`。
- CLI 不是用户入口；脚本只能作为 Skill 内部实现。
- 旧 `ai-context/`、`flux/`、`space/`、`space/crafted/lifeos` 只能作为迁移追溯来源，不能作为当前写入目标。

## 当前内部脚本入口

```text
{VAULT}/00-系统/Skills/thirdspace-vault/scripts/thirdspace-vault.mjs
```

常用能力：

- `resolve-vault`
- `detect`
- `init`
- `create`
- `route-create`
- `ensure-worklog`
- `record-agent-event`
- `capture-git-commit`
- `register-hooks`
- `ensure-runtime-assets`
- `install-runtime`
- `update-frontmatter`
- `audit-system`
- `audit-projects`
- `audit-workspaces`
- `audit-subsystems`
- `audit-skill-locations`

## 渐进式加载协议

1. 全局入口加载 `thirdspace-vault`。
2. 根 Skill 读取 `AGENTS.md`、`.thirdspace/workspace-index.yaml` 和 `.thirdspace/schema/*.yaml`。
3. 先根据意图选择工作区；如果当前目录在 vault 内，再用 `pwd` 校准。
4. 读取目标工作区 `WORKSPACE.md`。
5. 加载对应 `workspace-*` Skill。
6. 只有在场景命中时加载领域 Skill。
7. 所有写入必须使用当前工作区规则完成命名、Frontmatter、标签、状态和流转。
