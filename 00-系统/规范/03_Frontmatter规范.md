# Frontmatter 规范

## 必填字段

```yaml
---
title: "标题"
type: "note"
topic: "ai"
workspace: "03-知识"
created: "2026-05-24 10:00:00"
modified: "2026-05-24 10:00:00"
tags: ["ai", "note", "active"]
source: "manual"
status: "active"
---
```

## 字段说明

- `title`：人类可读标题。
- `type`：内容类型，见 `.thirdspace/schema/taxonomy.yaml`。
- `topic`：主题 key。
- `workspace`：当前工作区目录名。
- `created`：首次创建时间。
- `modified`：最后修改时间。
- `tags`：类型、状态、来源和补充语义。
- `source`：来源。
- `status`：`draft`、`active`、`processed`、`archived`。

## 自动修复

Agent 规范化文件时，优先补齐缺失字段，不删除正文。
