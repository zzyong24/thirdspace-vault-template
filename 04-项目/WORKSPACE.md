---
type: "note"

title: 04-项目工作区
description: 管理正在推进的创作、产品、运营和工程项目
created: 2026-05-24
project: workspace
tags: [规范, 工作区]---

# 04-项目 工作区规范

## 用途

管理正在推进的创作、产品、运营和工程项目。

## 允许

- 项目计划
- 项目素材索引
- 需求文档
- 脚本草稿
- 局部 AGENTS.md 或 CLAUDE.md
- 项目内 `.codex/skills/`，用于维护该项目独有流程

## 禁止

- 全局知识库规范
- 无项目归属的长期知识笔记

## 命名

一级分类按项目意图划分：

- `内容创作/`
- `产品系统/`
- `运营增长/`
- `商业合作/`
- `研究验证/`
- `实验原型/`

项目目录使用 `YYYYMMDDHHMM_项目名/`。历史项目目录若只有日期没有时分，可以先保留，后续重命名必须通过分类审计和迁移 trace。项目内文档可使用 `brief.md`、`plan.md`、`assets.md`、`review.md`。

复杂项目允许保留 `_assets/`、`_template/`、`research/`、`renders/` 等内部结构；这些目录属于项目运行上下文，不按全库一层目录规则强制打散。旧 prompt 入口不得留在项目资产中，必须迁入 Skill references 或归档。

## Frontmatter

项目内核心 Markdown 必须包含 `project` 字段，并尽量包含：

- `project_type`
- `project_category`
- `stage`

分类规则以 `00-系统/规范/06_项目工作区分类治理规则.md` 和 `.thirdspace/schema/project-taxonomy.yaml` 为准。

## 子 Skill

使用 `workspace-projects`。