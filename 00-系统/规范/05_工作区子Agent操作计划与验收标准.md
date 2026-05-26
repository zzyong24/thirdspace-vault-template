# 工作区子 Agent 操作计划与验收标准

> **路径约定（所有人适用）**
> - `{VAULT}` = vault 根目录，即包含 `.thirdspace/workspace-index.yaml` 的目录
> - `{SKILLS}` = ThirdSpace skills 根目录（可选，未安装时跳过 CLI 脚本步骤）
> - bash 代码块中已替换为 `$VAULT` / `$SKILLS` 变量
> - 在 vault 根目录执行命令时：`VAULT="."` 即可；跨目录时向上遍历找到 `.thirdspace/workspace-index.yaml` 所在位置

## 目标

把历史目录中的内容按工作区逐批迁移、规范化，并让之后的新增和更新都由 Agent-native Skill 维护。

本计划用于给子 Agent 派发任务。每个子 Agent 只负责一个工作区，按照 `goal + loop + acceptance` 执行，不跨区抢任务。

## 总原则

1. 先读根协议，再读工作区协议。
2. 单个 Agent 只处理一个工作区。
3. 每次处理前先生成候选清单，不直接整树搬。
4. 不删除正文。
5. 不删除用户未确认的历史文件。
6. 不打散项目资产。
7. 跨工作区移动必须记录 `source -> target`。
8. 每个工作区独立报告、独立验收。
9. 新 Markdown 必须使用 `YYYYMMDD_主题.md`，项目内部约定文件除外。
10. 所有 Markdown 必须补齐 Frontmatter。

## 必读文件

每个子 Agent 开始前必须读取：

```text
{VAULT}/AGENTS.md
{VAULT}/.thirdspace/workspace-index.yaml
{VAULT}/.thirdspace/schema/frontmatter.yaml
{VAULT}/.thirdspace/schema/taxonomy.yaml
{VAULT}/.thirdspace/queues/normalization-queue.yaml
{VAULT}/00-系统/规范/01_文件命名与目录规范.md
{VAULT}/00-系统/规范/02_主题与标签规范.md
{VAULT}/00-系统/规范/03_Frontmatter规范.md
{VAULT}/00-系统/规范/04_文档规范化GoalLoop.md
```

然后读取自己负责的：

```text
{VAULT}/<工作区>/WORKSPACE.md
{SKILLS}/<workspace-skill>/SKILL.md
```

## 派发顺序

推荐按这个顺序执行：

1. `01-收件箱`
2. `02-日记`
3. `03-知识`
4. `06-输出`
5. `05-资源`
6. `04-项目`
7. `99-归档`
8. `00-系统`

原因：

- 收件箱先清，避免新输入继续污染。
- 日记和知识是结构最明确的两类。
- 输出和资源相对容易分流。
- 项目最复杂，最后处理，避免破坏活跃上下文。
- 系统最后复核，确保规则和实际迁移结果一致。

## 子 Agent 通用执行 Loop

每个工作区使用同一个 Loop：

1. 读取任务配置。
2. 列出 source/current paths 中的候选文件。
3. 先生成本工作区候选清单。
4. 对每个 Markdown 文件：
   - 读取正文。
   - 判断是否应进入本工作区。
   - 判断目标子目录。
   - 生成目标文件名。
   - 补齐或修正 Frontmatter。
   - 保留正文。
   - 写入目标文件。
   - 记录 `source -> target`。
5. 对非 Markdown 文件：
   - 判断是否为资源或资产。
   - 不强制改名。
   - 必要时创建 Markdown 索引。
6. 生成工作区报告。
7. 输出剩余问题。

## 全局 Frontmatter 验收

每个迁移后的 Markdown 必须包含：

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

字段要求：

| 字段 | 验收标准 |
|---|---|
| `title` | 非空，和文件主题一致 |
| `type` | 必须在 `.thirdspace/schema/taxonomy.yaml` 中 |
| `topic` | 必须在 `.thirdspace/schema/taxonomy.yaml` 中，或在报告中声明新增建议 |
| `workspace` | 必须等于目标工作区目录名 |
| `created` | 格式为 `YYYY-MM-DD HH:MM:SS` |
| `modified` | 格式为 `YYYY-MM-DD HH:MM:SS` |
| `tags` | 至少包含 topic、type、status |
| `source` | 必须在 `.thirdspace/schema/frontmatter.yaml` 的 source_values 中 |
| `status` | 必须为 `draft`、`active`、`processed` 或 `archived` |

## 全局报告格式

每个子 Agent 必须创建报告：

```text
{VAULT}/.thirdspace/reports/YYYYMMDD_<工作区>_规范化报告.md
```

报告模板：

```markdown
# <工作区> 规范化报告

## 摘要

- 工作区：
- Skill：
- 开始时间：
- 结束时间：
- 处理文件数：
- 新建文件数：
- 移动文件数：
- 更新 Frontmatter 数：
- 跳过文件数：
- 剩余问题数：

## 输入路径

列出本次处理的 source_paths 或 current_paths。

## 迁移记录

| Source | Target | Action | Reason |
|---|---|---|---|

## Frontmatter 修复记录

| File | 修复字段 |
|---|---|

## 跳过记录

| File | Reason |
|---|---|

## 剩余问题

| File | Problem | Suggested next action |
|---|---|---|

## 验收结论

- [ ] 工作区 `WORKSPACE.md` 已读取
- [ ] 所有新增 Markdown 文件有 Frontmatter
- [ ] 所有新增 Markdown 文件命名合规
- [ ] 没有删除正文
- [ ] 跨工作区移动已记录
- [ ] 剩余问题已列出
```

## 01-收件箱

### 目标

规范化网页剪藏和临时输入，补齐 Frontmatter，判断后续目标工作区。

### 输入

```text
{VAULT}/01-收件箱/网页剪藏
```

### 输出

保持在：

```text
{VAULT}/01-收件箱/网页剪藏
```

### 规则

- 文件名改为 `YYYYMMDD_主题.md`。
- `type` 设置为 `clipping`。
- `workspace` 设置为 `01-收件箱`。
- `source` 设置为 `obsidian-clipper` 或 `web`。
- `status` 设置为 `draft`。
- 不直接迁移到其他工作区，只在报告里建议目标工作区。

### 验收标准

- 所有网页剪藏都有 Frontmatter。
- 所有网页剪藏保留正文。
- 所有网页剪藏文件名合规，或在报告中列出无法改名原因。
- 报告中包含每个剪藏的建议目标工作区。

### 子 Agent 命令

```text
你负责规范化 01-收件箱。

只处理 {VAULT}/01-收件箱/网页剪藏。
逐个文件执行 Goal Loop。
补齐 Frontmatter，规范命名，保留正文。
不要跨工作区移动，只在报告中建议目标工作区。
完成后写入 {VAULT}/.thirdspace/reports/YYYYMMDD_01-收件箱_规范化报告.md。
```

## 02-日记

### 目标

迁移并规范化工作日志、反思和复盘。

### 输入

```text
{VAULT}/space/crafted/work
{VAULT}/space/crafted/reflections
{VAULT}/space/crafted/reviews
```

### 输出

```text
{VAULT}/02-日记/工作日志
{VAULT}/02-日记/反思
{VAULT}/02-日记/复盘
```

### 规则

- 工作日志 `type=worklog`。
- 反思 `type=reflection`。
- 复盘 `type=review`。
- `workspace=02-日记`。
- 原路径中有年月层级时，允许在目标目录保留 `YYYY/MM` 两层；如果造成过深，改用文件名承载日期。

### 验收标准

- 工作日志、反思、复盘分流正确。
- Markdown 文件均有 Frontmatter。
- 正文完整。
- 移动记录完整。
- 旧目录中未迁移文件都有跳过原因。

### 子 Agent 命令

```text
你负责规范化 02-日记。

source_paths：
- {VAULT}/space/crafted/work
- {VAULT}/space/crafted/reflections
- {VAULT}/space/crafted/reviews

target_paths：
- {VAULT}/02-日记/工作日志
- {VAULT}/02-日记/反思
- {VAULT}/02-日记/复盘

逐个文件迁移，补齐 Frontmatter，保留正文，记录 source -> target。
完成后写入 {VAULT}/.thirdspace/reports/YYYYMMDD_02-日记_规范化报告.md。
```

## 03-知识

### 目标

迁移并规范化知识卡片、阅读笔记、学科笔记和主题知识。

### 输入

```text
{VAULT}/space/found
{VAULT}/space/crafted/AI
{VAULT}/space/crafted/ai-engineering
{VAULT}/space/crafted/dev
{VAULT}/space/crafted/dev-note
{VAULT}/space/crafted/reading
{VAULT}/space/crafted/study
{VAULT}/space/found/subject
```

### 输出

```text
{VAULT}/03-知识/AI工程
{VAULT}/03-知识/开发
{VAULT}/03-知识/书籍笔记
{VAULT}/03-知识/AI工具学习
```

### 规则

- 已处理知识卡片 `type=card`。
- 普通知识笔记 `type=note`。
- `workspace=03-知识`。
- 只保留一层主题目录。
- 原始网页全文不进入 `03-知识`，应留在 `01-收件箱` 或 `05-资源`。

### 验收标准

- 目标目录最多一层主题子目录。
- 每个 Markdown 有 Frontmatter。
- `topic` 合理，不能把来源当 topic。
- 原始剪藏和已处理知识分开。
- 学科类长文可先保留系列目录，但必须在报告中说明。

### 子 Agent 命令

```text
你负责规范化 03-知识。

source_paths：
- {VAULT}/space/found
- {VAULT}/space/crafted/AI
- {VAULT}/space/crafted/ai-engineering
- {VAULT}/space/crafted/dev
- {VAULT}/space/crafted/dev-note
- {VAULT}/space/crafted/reading
- {VAULT}/space/crafted/study
- {VAULT}/space/found/subject

target_paths：
- {VAULT}/03-知识/AI工程
- {VAULT}/03-知识/开发
- {VAULT}/03-知识/书籍笔记
- {VAULT}/03-知识/AI工具学习

逐个文件迁移，补齐 Frontmatter，最多保留一层主题目录。
完成后写入 {VAULT}/.thirdspace/reports/YYYYMMDD_03-知识_规范化报告.md。
```

## 04-项目

### 目标

迁移并规范化活跃项目、创作项目和知识星球运营项目。

### 输入

```text
{VAULT}/04-项目/内容创作/20260415_创作
{VAULT}/04-项目/运营增长/202605211200_知识星球
{VAULT}/04-项目/产品系统/20260430_短视频创作者AI知识库
{VAULT}/04-项目/产品系统/20260509_MoonOS
{VAULT}/04-项目/商业合作/20260430_声文智汇
{VAULT}/04-项目/实验原型/20260415_AI童伴
```

### 输出

```text
{VAULT}/04-项目/内容创作
{VAULT}/04-项目/运营增长
{VAULT}/04-项目/产品系统
{VAULT}/04-项目/商业合作
{VAULT}/04-项目/研究验证
{VAULT}/04-项目/实验原型
```

### 规则

- 项目目录使用 `YYYYMMDDHHMM_项目名/`。
- 不打散项目资产。
- 项目内允许局部 `AGENTS.md` 或 `CLAUDE.md`。
- 对正在修改、含大量媒体、含渲染产物的项目，只生成迁移建议，不强制移动。
- `workspace=04-项目`。
- 项目内 Markdown 必须有 `project` 字段。

### 验收标准

- 活跃项目不被破坏。
- 每个移动的项目有完整目录。
- 媒体资产相对引用不失效，或报告中列出需要人工复核的引用。
- 复杂项目可先只建立索引文件，不移动资产。

### 子 Agent 命令

```text
你负责规范化 04-项目。

source_paths：
- {VAULT}/04-项目/内容创作/20260415_创作
- {VAULT}/04-项目/运营增长/202605211200_知识星球
- {VAULT}/04-项目/产品系统/20260430_短视频创作者AI知识库
- {VAULT}/04-项目/产品系统/20260509_MoonOS
- {VAULT}/04-项目/商业合作/20260430_声文智汇
- {VAULT}/04-项目/实验原型/20260415_AI童伴

target_paths：
- {VAULT}/04-项目/内容创作
- {VAULT}/04-项目/运营增长
- {VAULT}/04-项目/产品系统
- {VAULT}/04-项目/商业合作
- {VAULT}/04-项目/研究验证
- {VAULT}/04-项目/实验原型

不要打散项目资产。对复杂项目先写迁移建议和项目索引。
完成后写入 {VAULT}/.thirdspace/reports/YYYYMMDD_04-项目_规范化报告.md。
```

## 05-资源

### 目标

迁移并规范化长期参考资料、模板、附件和工具资料。

### 输入

```text
{VAULT}/99-归档/旧结构/top-level-tools/CLI-tools
{VAULT}/space/templates
{VAULT}/space/workflow
{VAULT}/99-归档/旧结构/top-level-tools/Excalidraw
{VAULT}/99-归档/旧结构/flux
{VAULT}/05-资源/图片/flux-intake-assets
```

### 输出

```text
{VAULT}/05-资源/CLI工具
{VAULT}/05-资源/模板
{VAULT}/05-资源/工作流
{VAULT}/05-资源/附件
{VAULT}/05-资源/图片
{VAULT}/05-资源/人物档案
```

### 规则

- 二进制文件不强制改名。
- 资源需要 Markdown 索引。
- Excalidraw 文件可保留原名。
- 工具说明类 Markdown 可进入 `05-资源/CLI工具`。
- 资源目录只保留一层类型目录，不再使用 `参考资料/xxx` 二级嵌套。
- `workspace=05-资源`。

### 验收标准

- 非 Markdown 资源没有被破坏。
- 每类资源有索引或报告。
- Markdown 资源说明有 Frontmatter。
- 附件和图片不混入知识笔记目录。

### 子 Agent 命令

```text
你负责规范化 05-资源。

source_paths：
- {VAULT}/99-归档/旧结构/top-level-tools/CLI-tools
- {VAULT}/space/templates
- {VAULT}/space/workflow
- {VAULT}/99-归档/旧结构/top-level-tools/Excalidraw
- {VAULT}/99-归档/旧结构/flux
- {VAULT}/05-资源/图片/flux-intake-assets

target_paths：
- {VAULT}/05-资源/CLI工具
- {VAULT}/05-资源/模板
- {VAULT}/05-资源/工作流
- {VAULT}/05-资源/附件
- {VAULT}/05-资源/图片
- {VAULT}/05-资源/人物档案

二进制文件不要强制改名。必要时创建 Markdown 索引。
完成后写入 {VAULT}/.thirdspace/reports/YYYYMMDD_05-资源_规范化报告.md。
```

## 06-输出

### 目标

迁移并规范化文章、口播稿、视频脚本和发布稿。

### 输入

```text
{VAULT}/space/crafted/writing
{VAULT}/space/crafted/voiceover
{VAULT}/space/crafted/tracker
{VAULT}/space/found/writing
```

### 输出

```text
{VAULT}/06-输出/文章
{VAULT}/06-输出/口播稿
{VAULT}/06-输出/视频脚本
{VAULT}/06-输出/发布稿
```

### 规则

- 文章 `type=article`。
- 口播稿 `type=voiceover`。
- 视频脚本 `type=script`。
- 未完成草稿 `status=draft`。
- 已发布内容保留发布信息。
- `workspace=06-输出`。

### 验收标准

- 输出成品与素材分开。
- 草稿和已发布状态清晰。
- 每个 Markdown 有 Frontmatter。
- 文件命名合规。

### 子 Agent 命令

```text
你负责规范化 06-输出。

source_paths：
- {VAULT}/space/crafted/writing
- {VAULT}/space/crafted/voiceover
- {VAULT}/space/crafted/tracker
- {VAULT}/space/found/writing

target_paths：
- {VAULT}/06-输出/文章
- {VAULT}/06-输出/口播稿
- {VAULT}/06-输出/视频脚本
- {VAULT}/06-输出/发布稿

区分草稿和成品，补齐 Frontmatter，记录 source -> target。
完成后写入 {VAULT}/.thirdspace/reports/YYYYMMDD_06-输出_规范化报告.md。
```

## 99-归档

### 目标

整理旧结构、旧审计和迁移前备份。

### 输入

```text
{VAULT}/99-归档/旧结构
{VAULT}/99-归档/旧审计
```

### 规则

- `status=archived`。
- 不再活跃的旧文件保留原始内容。
- 只补 Frontmatter 和索引，不做内容重写。

### 验收标准

- 归档内容不影响当前 Agent 上下文。
- 旧结构可追溯。
- 旧审计可追溯。
- 不误删。

## 00-系统

### 目标

最后复核系统工作区，确保系统区只保留当前规则、Schema、Agent 入口、Skills 索引和当前审计。

### 输入

```text
{VAULT}/00-系统
```

### 规则

- 不保留旧 `ai-context` 运行时文件。
- 不保留旧 prompt 机制说明。
- 不保留二进制资源。
- 不保留过期 vault-map 作为当前索引。
- 当前运行入口是 `00-系统/Agent/README.md`。

### 验收标准

- `00-系统/Agent/` 只保留运行时必需文件。
- `00-系统/规范/` 只保留当前规范。
- `00-系统/Skills/` 指向当前 Skill 体系。
- `00-系统/审计/` 只保留当前清理和验证报告。

### 子 Agent 命令

```text
你负责复核 00-系统。

目标：
确认系统工作区只保留当前有效规则、Schema、Agent 入口、Skills 索引和当前审计。

不要删除文件。对不该常驻 00-系统 的文件，移动到 99-归档 或 05-资源，并记录 source -> target。
完成后写入 {VAULT}/.thirdspace/reports/YYYYMMDD_00-系统_复核报告.md。
```

## 最终全库验收

所有工作区完成后，主 Agent 执行最终验收：

```bash
find $VAULT -maxdepth 2 -name WORKSPACE.md | sort
find $VAULT/.thirdspace -maxdepth 3 -type f | sort
test ! -d $VAULT/Clippings && echo "Clippings 已迁移"
test ! -d $VAULT/ai-context && echo "ai-context 已迁移"
find $VAULT/.thirdspace/reports -maxdepth 1 -type f | sort
```

全库通过标准：

- 8 个工作区都有 `WORKSPACE.md`。
- 每个已处理工作区都有报告。
- 顶层没有 `Clippings`。
- 顶层没有 `ai-context`。
- 新增 Markdown 文件均有 Frontmatter。
- 旧结构仍可在 `99-归档` 或迁移报告中追溯。
- `README.md`、`AGENTS.md`、`CLAUDE.md` 与实际结构一致。
