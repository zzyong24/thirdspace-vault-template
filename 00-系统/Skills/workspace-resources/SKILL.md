---
name: workspace-resources
description: Use when maintaining ThirdSpace `05-资源`, reusable materials, internal tool notes, workflows, templates, attachments, images, people profiles, or resource indexes.
triggers:
  - "资源"
  - "课程"
  - "书籍"
  - "附件"
---

# Workspace Resources Skill

## 工作区

`{VAULT}/05-资源`

## 规则来源

先读 `{VAULT}/05-资源/WORKSPACE.md`。

## 文件创建

- 工具资料写入 `CLI工具/YYYYMMDD_资源主题.md`；这里是历史工具资料和脚本说明，不是用户入口。
- 工作流说明写入 `工作流/YYYYMMDD_资源主题.md`。
- 模板说明写入 `模板/YYYYMMDD_资源主题.md`。
- 二进制文件放入 `附件/` 或 `图片/`，并用 Markdown 索引描述。

## 维护规则

- `05-资源` 保存可复用材料，不保存项目执行计划。
- 原始大文件允许在资源区保留，但必须有同名或同主题 Markdown 索引。
- 不创建多层资料库；需要细分时优先用 tags 和索引页。

## 自治维护回路

1. 判断资源类型：工具资料、工作流、模板、附件、图片或人物档案。
2. Markdown 资源补 `workspace=05-资源`、`type=resource|note`、`status=active`。
3. 二进制、图片和附件必须有同名或同主题 Markdown 索引。
4. 如果资源被项目使用，在项目内只放引用或索引，不复制出多个版本。
5. 可复用方法论可流转到 `03-知识`，发布材料可流转到 `06-输出`。

## 审计项

- 附件或图片是否缺索引。
- 是否混入项目执行计划。
- 是否出现多层资料库。
- Markdown 是否缺 Frontmatter。

## 修复策略

- 可自动修复：创建缺失目录、补资源 Frontmatter。
- 写队列：为附件或图片生成索引建议。
- 必须 trace：资源跨工作区迁移。
