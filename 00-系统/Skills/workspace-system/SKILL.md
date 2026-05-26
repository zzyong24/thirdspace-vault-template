---
name: workspace-system
description: Use when maintaining ThirdSpace `00-系统`, changing workspace rules, schemas, Agent entrypoints, Skills, runtime assets, audits, migration traces, or subsystem contracts.
triggers:
  - "系统规范"
  - "更新工作区规则"
  - "迁移记录"
---

# Workspace System Skill

## 工作区

`{VAULT}/00-系统`

## 规则来源

先读 `{VAULT}/00-系统/WORKSPACE.md`。

## 维护动作

- 创建或更新规范文件。
- 更新 `.thirdspace/schema/`。
- 维护 Skills 索引。
- 维护 `00-系统/运行时` 中的 hook、crontab 和自动化任务规格。
- 记录审计和迁移 manifest。

## 自治维护回路

1. 读取 `00-系统/WORKSPACE.md`、`.thirdspace/schema/subsystems.yaml` 和相关规范。
2. 判断变更属于规范、Schema、Skill、审计还是迁移 trace。
3. 更新对应控制面文件，避免把普通内容写入系统区。
4. 运行或建议运行 `audit-workspaces` 与 `audit-subsystems`。
5. 将结构漂移、旧 context、旧 prompt、缺失 Schema 写入审计报告或维护队列。

## 审计项

- `00-系统/规范` 是否包含最新规则。
- `.thirdspace/schema` 是否覆盖工作区、项目分类和子系统契约。
- `00-系统/Agent` 是否只保留当前 Agent 入口与 profile。
- `00-系统/Skills` 是否保存所有 canonical Skills 和内部 scripts。
- `00-系统/运行时` 是否保存可迁移 hook、crontab、自动化任务规格。

## 修复策略

- 可自动修复：创建缺失目录、补索引链接、更新审计报告。
- 写队列：发现旧 context、旧 prompt、路径失效但不确定可删。
- 必须 trace：移动或删除历史系统文件。

## 禁止

- 不在本区写入普通笔记、日记、项目素材和发布成品。
