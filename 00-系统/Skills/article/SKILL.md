# Article Skill — 文章生成引擎

## 功能概述

从知识卡片、反思记录、笔记中聚合素材，为 AI 撰写成型文章提供结构化原材料。

## 工具清单

| 工具 | 说明 |
|------|------|
| `draft_article(topic, focus, style, days, prompt_name)` | 聚合素材，返回给 AI 撰写文章 |
| `save_article(title, content, topic, tags, sources)` | 保存 AI 生成的文章 |
| `list_articles(topic, days)` | 列出已有文章 |

## 设计原则

遵循 **Tool → AI → Tool** 模式：
1. `draft_article` 只负责聚合素材（IO）
2. AI 基于素材撰写文章（智能）
3. `save_article` 保存结果（IO）

## 文章风格

| 风格 | 说明 |
|------|------|
| `insight` | 洞察型：观点先行，论据支撑，语言犀利 |
| `tutorial` | 教程型：步骤清晰，实操为主，语言准确 |
| `story` | 叙事型：以经历串联观点，语言生动 |
| `listicle` | 清单型：N 个要点并列，易于扫读 |

## 支持 Prompt 风格调整

通过 `prompt_name` 参数引入 Prompt 库中的风格模板：

```python
draft_article(focus="AI", prompt_name="tools/犀利文风")
```

模板位置：对应 Skill 的 `prompts/`、`templates/` 或 `references/`。

## 素材聚合范围

- **知识卡片**：摘要、关键要点、思考问题
- **反思记录**：Mirror（认知）、Bridge（行动）
- **笔记**：`03-知识` 中的长期知识笔记
- **已有文章**：避免重复创作

## 输出位置

文章：`{VAULT}/06-输出/文章/YYYYMMDD_文章标题.md`

## 引用追踪

通过 `sources` 参数记录引用的素材来源，自动生成 Obsidian 双链：

```yaml
sources:
  - "[[03-知识/AI工程/xxx.md]]"
  - "[[02-日记/反思/xxx.md]]"
```
