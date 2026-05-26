---
name: workspace-inbox
description: Use when handling ThirdSpace `01-收件箱`, web clippings, old flux intake, temporary ideas, unclassified materials, intake routing, frontmatter normalization, or content flow queues.
triggers:
  - "整理收件箱"
  - "网页剪藏"
  - "待整理"
---

# Workspace Inbox Skill

## 工作区

`{VAULT}/01-收件箱`

## 规则来源

先读 `{VAULT}/01-收件箱/WORKSPACE.md`。

## 文件创建

- 网页剪藏写入 `网页剪藏/YYYYMMDD_主题.md`。
- 临时想法写入 `临时想法/YYYYMMDD_主题.md`。
- 不确定内容写入 `待整理/YYYYMMDD_主题.md`。
- 旧 `flux/intake` 已通过 `migrate-flux-intake` 迁入 `网页剪藏/`，并保留 manifest。

## 工具动作

- `route-create`：按意图创建收件箱文件。
- `migrate-flux-intake`：迁移旧 `flux/intake`，重写图片链接，并生成 manifest。

## 规范化动作

1. 补齐 Frontmatter。
2. 将 `source` 设置为 `obsidian-clipper`、`web` 或 `manual`。
3. 判断目标工作区。
4. 写入 normalization queue。

## 自治维护回路

1. 接收输入后先判断来源：网页剪藏、临时想法、素材暂存或待整理。
2. 补齐 `type=clipping|note`、`source`、`status=draft`、`workspace=01-收件箱`。
3. 粗分目标工作区：知识、项目、资源、输出或日记。
4. 不直接长期沉淀，处理建议写入 `.thirdspace/queues/normalization-queue.yaml`。
5. 对已处理文件设置 `status=processed` 或迁移时写 trace。

## 审计项

- 是否存在长期滞留的 `draft`。
- 是否有缺 Frontmatter 的 Markdown。
- 是否出现多层目录。
- 是否存在已判断归属但未写入流转队列的文件。

## 修复策略

- 可自动修复：补 `workspace/source/status`、规范文件名、创建缺失入口目录。
- 写队列：建议目标工作区和处理理由。
- 必须 trace：跨工作区移动文件。

## 禁止

- 不在收件箱长期沉淀。
- 不创建多层分类树。
