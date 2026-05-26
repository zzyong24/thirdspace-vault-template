---
name: workspace-projects
description: Use when working inside ThirdSpace `04-项目`, creating or updating project files, auditing project categories, or deciding where an active project belongs.
triggers:
  - "项目"
  - "roadmap"
  - "产品"
  - "04-项目"
  - "项目分类"
  - "project"
---

# Workspace Projects Skill

## 工作区

`{VAULT}/04-项目`

## 规则来源

先读：

1. `{VAULT}/04-项目/WORKSPACE.md`
2. `{VAULT}/00-系统/规范/06_项目工作区分类治理规则.md`
3. `{VAULT}/.thirdspace/schema/subsystems.yaml`

## 一级分类

按项目意图分类，而不是按历史来源分类：

| 分类 | project_type | 何时使用 |
|---|---|---|
| `内容创作` | `content` | 视频、文章、课程、栏目、选题、发布包 |
| `产品系统` | `product` | 软件、工具、系统、插件、技术产品 |
| `运营增长` | `operations` | 知识星球、社群、运营 SOP、内容矩阵、增长飞轮、数据追踪 |
| `研究验证` | `research` | 阶段性调研、技术验证、方案探索 |
| `实验原型` | `experiment` | MVP、原型、低成本试验、方向未定项目 |

## 文件创建

- 项目目录使用 `YYYYMMDDHHMM_项目名/`。
- 项目内允许 `brief.md`、`plan.md`、`assets.md`、`review.md`。
- 项目内核心 Markdown 必须包含 `project` 字段。
- 项目入口或核心文档应包含 `project_type`、`project_category`、`stage`。

## 分类审计

当用户说“项目分类不对”“重新整理项目”“这个项目该放哪”时：

1. 不要立即移动目录。
2. 运行或要求运行：

```bash
node {SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs audit-projects --vault {VAULT} --write-report
```

3. 先输出建议表：

```text
当前路径 | 建议分类 | 建议路径 | 置信度 | 理由 | 是否需要人工确认
```

4. `confidence >= 0.8` 可以进入待执行清单。
5. `confidence < 0.8` 必须人工确认。

## 跨分类移动

- 只能移动完整项目目录。
- 不移动项目内部零散文件。
- 必须写 trace：原路径、目标路径、理由、时间、执行者。
- 正在活跃的复杂项目优先保留原内部结构。

## 自治维护回路

1. 先判断项目类型：内容创作、产品系统、运营增长、研究验证或实验原型。
2. 读取项目内 `AGENTS.md`、`CLAUDE.md` 或局部 `.codex/skills`，如果存在。
3. 创建或更新项目文件时补 `workspace=04-项目`、`project`、`project_type`、`project_category`、`stage`。
4. 产出类文件流向 `06-输出`，可复用知识流向 `03-知识`，长期资产索引流向 `05-资源`。
5. 完结项目进入 `99-归档/完结项目`，并保留项目 trace。

## 审计项

- 项目一级分类是否和项目意图一致。
- 项目核心 Markdown 是否缺 `project` 字段。
- 跨分类移动是否写入 trace。
- 局部 Skill 和脚本路径是否失效。

## 修复策略

- 可自动修复：补 `workspace/project` 字段，生成分类审计。
- 写队列：低置信度分类建议、缺失项目索引。
- 必须 trace：移动完整项目目录、项目归档。

## 子 Skill

按项目类型渐进式加载：

- 内容创作：`creative-video-workflow`、`moonlit-video-draft-pipeline`
- 产品系统 / 实验原型：`mvp-project`
- 运营增长：`review`、`mvp-project`
- 研究验证：`workspace-knowledge`
