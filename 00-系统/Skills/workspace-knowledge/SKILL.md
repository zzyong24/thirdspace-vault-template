---
name: workspace-knowledge
description: Use when maintaining ThirdSpace `03-知识`, knowledge cards, topic notes, concept pages, study notes, processed clippings, or long-term knowledge memory.
triggers:
  - "知识卡片"
  - "主题笔记"
  - "知识沉淀"
---

# Workspace Knowledge Skill

## 工作区

`{VAULT}/03-知识`

## 规则来源

先读 `{VAULT}/03-知识/WORKSPACE.md`。

## 文件创建

- 根据主题写入现有一级目录，例如 `AI工程/YYYYMMDD_标题.md`、`开发/YYYYMMDD_标题.md`、`书籍笔记/YYYYMMDD_标题.md`。
- 主题子目录只保留一层。
- `type` 使用 `note` 或 `card`。

## 禁止

- 不保存原始网页全文。
- 不写项目执行文件。
- 不创建临时 `主题/`、`杂项/`、`未分类/` 目录；不确定时放回 `01-收件箱/待整理`。

## 自治维护回路

1. 判断内容是否已经被处理，原始网页全文不直接进入知识区。
2. 选择现有一级主题目录，不创建临时未分类目录。
3. 补齐 `workspace=03-知识`、`type=note|card`、`topic`、`status=active`。
4. 识别可产出内容，建议流转到 `06-输出`。
5. 识别项目执行内容，建议回流到 `04-项目`。

## 审计项

- 是否出现原始剪藏全文。
- 是否混入项目计划、任务清单、发布稿。
- 是否存在临时目录或多层目录。
- 是否缺 `topic`、`type` 或 Frontmatter。

## 修复策略

- 可自动修复：补基础 Frontmatter、创建缺失主题目录。
- 写队列：建议原始材料回 `01-收件箱` 或 `05-资源`。
- 必须 trace：跨工作区移动知识文件。
