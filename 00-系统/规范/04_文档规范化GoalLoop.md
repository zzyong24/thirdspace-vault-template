# 文档规范化 Goal Loop

## 目标

对一个工作区内的 Markdown 文件逐个规范化，使其符合全局 schema 和当前工作区 `WORKSPACE.md`。

## 输入

- 工作区路径
- `.thirdspace/queues/normalization-queue.yaml` 中对应文件列表
- `.thirdspace/schema/`
- 当前工作区 `WORKSPACE.md`

## Loop

对每个文件执行：

1. 读取文件。
2. 判断是否缺少 Frontmatter。
3. 判断文件名是否符合 `YYYYMMDD_主题.md` 或项目内局部命名。
4. 判断 `workspace` 是否等于当前工作区。
5. 判断 `type`、`topic`、`source`、`status` 是否符合 schema。
6. 修复单文件。
7. 记录修复摘要。
8. 运行当前工作区审计。
9. 文件通过后处理下一个。

## 禁止

- 不跨工作区批量移动文件。
- 不删除正文。
- 不把 prompts 迁回全局 prompts 目录。
- 不新增超过一层的主题子目录。

## 输出

- 修改后的文件
- 工作区修复报告
- 剩余问题列表
