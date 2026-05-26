---
name: workspace-journal
description: Use when maintaining ThirdSpace `02-日记`, daily notes, worklogs, reflections, reviews, interpersonal events, LifeOS records, timeline cleanup, or extracting reusable knowledge from personal records.
triggers:
  - "写日记"
  - "工作日志"
  - "反思"
  - "复盘"
---

# Workspace Journal Skill

## 工作区

`{VAULT}/02-日记`

## 规则来源

先读 `{VAULT}/02-日记/WORKSPACE.md`。

## 文件创建

- 每日记录写入 `每日/YYYYMMDD_每日.md`。
- 工作日志写入 `工作日志/YYYYMMDD_工作日志_主题.md`；常规每日记录使用 `工作日志/YYYYMMDD_工作日志_周X.md`。
- 反思写入 `反思/YYYYMMDD_反思主题.md`。
- 复盘写入 `复盘/YYYYMMDD_复盘主题.md`。
- 人际事件写入 `人际事件/事件/YYYYMMDD_主题.md`。
- 人际原始记录写入 `人际事件/原始记录/YYYYMMDD_主题.md`。

## 维护规则

- 不创建 `worklog/YYYY/MM`、`daily/YYYY/MM` 等年月嵌套目录。
- 不向旧路径 `space/crafted/lifeos` 写入新内容。
- 人际事件、人物关系、事件复盘任务需要渐进加载 `lifeos` Skill。
- 需要时间索引时更新 `工作日志/INDEX.md`，索引是生成物，不替代文件命名规范。
- 长期可复用技术指南、部署手册、工具方法论应迁入 `03-知识` 或 `05-资源`，不要留在日记工作流里。

## 自治维护回路

1. 判断内容是每日记录、工作日志、反思还是复盘。
2. 写入一层主题目录，并补 `workspace=02-日记`、`type=worklog|reflection|review|event|event-raw`。
3. 更新 `工作日志/INDEX.md` 或生成索引维护项。
4. 识别可复用知识、技术指南、项目行动，将其建议流转到 `03-知识` 或 `04-项目`。
5. 对迁出日记区的内容写入报告或 trace。

## 审计项

- 是否出现 `worklog/YYYY/MM` 深层嵌套。
- 工作日志是否缺索引。
- 是否混入长期技术知识或项目执行文件。
- 是否还有 LifeOS 内容滞留在 `space/crafted/lifeos`。
- Markdown 是否缺 Frontmatter。

## 修复策略

- 可自动修复：创建标准目录、更新索引、补基础 Frontmatter。
- 写队列：建议把长期知识迁入 `03-知识`。
- 必须 trace：将文件迁出日记区。
