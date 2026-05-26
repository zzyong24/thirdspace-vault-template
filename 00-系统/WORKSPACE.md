# 00-系统 工作区规范

## 用途

管理知识库规范、Schema、Agent 协议、Skills、运行时资产、审计报告和迁移记录。

## 允许

- 规范文档
- Skill 索引
- Agent 入口文档
- Schema
- 可迁移运行时资产：hook、crontab、Agent 自动化任务规格
- 审计报告
- 迁移 manifest

## 禁止

- 普通知识卡片
- 日记和反思
- 项目执行素材
- 成品文章和发布稿

## 命名

规范文档使用 `NN_中文标题.md`。审计报告使用 `YYYYMMDD_审计主题.md`。

## Frontmatter

`workspace` 必须为 `00-系统`，`type` 使用 `spec`、`skill` 或 `review`。

## 子 Skill

使用 `workspace-system`。

## Prompt 与 CLI 迁移规则

- Prompt 不再作为全局目录维护。
- 可复用提示词必须沉淀到具体 Skill 的 `prompts/`、`templates/` 或 `references/`。
- CLI 不作为普通用户入口；对外入口是 Skills。
- Python 脚本可以保留为 Skill 内部实现。
- 所有 Skill scripts 的 canonical 根目录是 `00-系统/Skills`。
- Hook、crontab、Agent 自动化任务规格必须在 `00-系统/运行时` 留存。

## 自治子系统规则

- `00-系统/规范/07_自治子系统设计规范.md` 是所有工作区的上位协议。
- `00-系统/规范/08_全局路由与Hook事件采集规范.md` 是任意目录路由、Git Hook、Agent Hook 和工作日志的上位协议。
- `.thirdspace/schema/subsystems.yaml` 是机器可读契约。
- `.thirdspace/schema/event-capture.yaml` 是事件采集、意图路由和工作日志结构的机器可读契约。
- `00-系统/运行时` 是跨电脑迁移时恢复本机 hook、crontab、自动化任务的源规格目录。
- 修改任何工作区边界、流转规则、状态机、审计策略或事件采集策略时，必须同步更新规范、Schema、对应 workspace Skill 和 README。
- 完成修改后运行 `audit-subsystems --write-report`。
