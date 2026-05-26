---
name: knowledge
description: Use when turning collected web, video, Feishu, or reading material into ThirdSpace knowledge cards, study notes, or long-term topic notes.
triggers:
  - "知识卡片"
  - "整理成知识"
  - "做成笔记"
  - "知识沉淀"
  - "study note"
  - "学习文档"
---

# Knowledge Skill

## Scope

This is a domain Skill loaded after `thirdspace-vault` and `workspace-knowledge`. It handles processed knowledge, not raw capture.

## Current Paths

- Raw or unprocessed capture: `{VAULT}/01-收件箱/网页剪藏` or `{VAULT}/01-收件箱/待整理`
- Knowledge cards and notes: `{VAULT}/03-知识/<一级主题>/YYYYMMDD_主题.md`
- Study notes and book notes: `{VAULT}/03-知识/书籍笔记/YYYYMMDD_主题.md`

## Rules

- Do not save raw webpage全文 directly into `03-知识`.
- Choose an existing first-level knowledge directory; do not create temporary nested categories.
- New knowledge files must use `workspace: "03-知识"` and `type: "note"` or `type: "card"`.
- If content is still unprocessed, route it to `01-收件箱/待整理`.

## Prompts

- `prompts/knowledge-card.md`
- `prompts/study-doc.md`

