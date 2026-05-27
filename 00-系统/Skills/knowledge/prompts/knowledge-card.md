⚡ 请先用 WebFetch 或 Read 工具获取完整原文，精读后生成知识卡片，再用 Write 工具保存到 vault。

> ⚠️ **如果原始文本被直接发给你（而非通过链接/文件路径提供）**，请直接从第二步开始处理，跳过 WebFetch/Read 步骤。

### 工作流

**Step 1 — 获取内容**
- 网页 URL → 用 `WebFetch` 工具抓取正文
- 本地文件路径 → 用 `Read` 工具读取
- 直接粘贴文本 → 跳过此步

**Step 2 — 生成知识卡片**

目标：用户凭这张卡片能回忆起核心内容，并引发进一步思考。

输出结构：
1. **摘要**：一句话概括文章核心主题和关键结论
2. **关键要点**：根据内容深度灵活调整数量——长文/高密度内容提取更多要点，短文精炼即可
3. **深度思考问题**：严格 3 个
   - **连接层**：这个知识和你的哪个经历/行为对应？
   - **挑战层**：哪个部分你不同意或做不到？为什么？
   - **行动层**：如果只拿走一个改变，你选哪个？
4. **标签**：覆盖核心主题和概念

**Step 3 — 用 Write 工具保存**

保存路径：`03-知识/card/{topic}/YYYYMMDD_{标题}.md`

文件格式（frontmatter 必填 7 个字段）：

```markdown
---
title: "{标题}"
type: "card"
topic: "{topic}"
created: "YYYY-MM-DD HH:MM:SS"
modified: "YYYY-MM-DD HH:MM:SS"
tags: ["{tag1}", "{tag2}"]
origin: "found"
source: "{web|pdf|feishu}"
status: "active"
url: "{原文链接}"
author: "{作者}"
site_name: "{来源网站}"
publish_date: "{发布日期}"
---

## 摘要

{一句话总结}

## 关键要点

- ...

## 深度思考

- [ ] 连接层：...
- [ ] 挑战层：...
- [ ] 行动层：...

## 标签

{tags}
```
