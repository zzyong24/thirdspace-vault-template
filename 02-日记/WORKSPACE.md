# 02-日记 工作区规范

## 用途

记录每日状态、工作日志、反思、周期复盘和 LifeOS 人际事件。

## 允许

- 每日记录
- 工作日志
- 反思
- 周报和月报
- 工作日志索引 `工作日志/INDEX.md`
- 人际事件
- 关系复盘与事件原始记录

## 禁止

- 外部网页原文
- 长期课程资源
- 项目资产文件

## 命名

每日记录使用 `YYYYMMDD_每日.md`。工作日志使用 `YYYYMMDD_工作日志_主题.md`，常规每日工作日志可使用 `YYYYMMDD_工作日志_周X.md`。反思使用 `YYYYMMDD_反思主题.md`。人际事件使用 `YYYYMMDD_事件主题.md`，旧 LifeOS 文件可保留 `event_YYYYMMDD_主题.md` 作为迁移 trace。

`02-日记` 只保留一层主题目录：`每日/`、`工作日志/`、`反思/`、`复盘/`、`人际事件/`。不得再创建 `worklog/YYYY/MM` 这类年月嵌套；需要按时间检索时更新 `工作日志/INDEX.md` 或交给 Agent 生成索引。`人际事件/` 允许内部保留 `事件/` 与 `原始记录/` 两类目录，作为 LifeOS 子系统边界。

## Frontmatter

`workspace` 必须为 `02-日记`，`type` 使用 `worklog`、`reflection`、`review`、`event` 或 `event-raw`。

## 子 Skill

使用 `workspace-journal`。

## 领域 Skill

- `worklog`：工作日志、Git 提交、Agent 产出。
- `reflect`：反思。
- `review`：周/月复盘。
- `lifeos`：人际事件、人物画像、关系复盘和事件决策。

## LifeOS 规则

- 人际事件放在 `人际事件/事件/`。
- 原始事件记录放在 `人际事件/原始记录/`。
- 人物档案不放在日记区，放在 `05-资源/人物档案/people.json`。
- 不再向 `space/crafted/lifeos` 写入新内容。
