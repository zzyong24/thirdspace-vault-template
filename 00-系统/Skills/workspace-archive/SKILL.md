---
name: workspace-archive
description: Use when maintaining ThirdSpace `99-归档`, migration records, deprecated systems, deprecated tools, completed projects, archived files, or historical trace.
triggers:
  - "归档"
  - "迁移记录"
  - "废弃系统"
  - "废弃工具"
  - "完结项目"
---

# Workspace Archive Skill

## 工作区

`{VAULT}/99-归档`

## 规则来源

先读 `{VAULT}/99-归档/WORKSPACE.md`。

## 文件创建

- 归档目录使用 `YYYYMMDD_归档主题/`。
- 单文件使用 `YYYYMMDD_归档说明.md`。
- `status` 必须为 `archived`。

## 自治维护回路

1. 判断归档来源：迁移记录、废弃系统、废弃工具、完结项目或迁移前备份。
2. 保留必要上下文和原始相对结构，不参与活跃工作区审计。
3. 归档说明补 `workspace=99-归档`、`status=archived`。
4. 从活跃区迁入归档时记录原路径、目标路径、理由和时间。
5. 迁移记录可反向链接到 `00-系统/审计` 或 `.thirdspace/reports/`。

## 审计项

- 是否有活跃工作入口指向归档目录。
- 归档说明是否缺 `status=archived`。
- 完结项目是否缺迁移 trace。

## 修复策略

- 可自动修复：补 `archived` 状态、创建归档目录。
- 写队列：建议补归档索引。
- 必须 trace：从活跃区迁入归档。
