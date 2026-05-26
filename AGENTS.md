# ThirdSpace Agent 入口

## 读取顺序

0. 如果当前目录不在知识库内，向上遍历父目录直到找到 `.thirdspace/workspace-index.yaml`，该目录即为 vault 根。也可通过 `$THIRDSPACE_VAULT` 环境变量或 `~/.thirdspace/config.yaml` 指定（可选）。
1. 读取 `.thirdspace/workspace-index.yaml`，先根据用户意图判断目标工作区；如果当前 `pwd` 在 vault 内，再把 `pwd` 作为辅助信号校准。
2. 读取 `.thirdspace/schema/taxonomy.yaml`，确认当前工作区允许的 type/topic 枚举。
3. 读取 `.thirdspace/schema/subsystems.yaml`，确认当前工作区的自治子系统契约。
4. 读取 `.thirdspace/schema/event-capture.yaml`，确认全局路由和 Hook 事件采集规则。
5. 读取 `.thirdspace/schema/workspace-tools.yaml`，确认当前工作区可用工具 Skill 和领域 Skill。
6. 读取当前工作区的 `WORKSPACE.md`。
7. 按 `workspace-index.yaml` 中的 `skill` 加载对应子 Skill。
8. 仅在意图命中时加载领域 Skill，例如 `lifeos`、`worklog`、`article`。
9. 创建、更新或整理文件前，检查 `.thirdspace/schema/`。

## 全局规则

- 新 Markdown 文件默认使用 `YYYYMMDD_主题.md`。
- 每个 Markdown 文件必须有 Frontmatter。
- `workspace` 字段必须等于当前工作区目录名。
- 不确定归属时，写入 `01-收件箱/待整理/`。
- 不直接批量删除历史内容。
- 大规模迁移先写入 `.thirdspace/manifests/`。
- Prompt 能力统一进入 Skills，不再维护全局 prompts 目录。
- 每个工作区都是自治子系统，必须遵守输入、输出、状态、审计和修复边界。
- 任意目录触发知识库操作时，先 resolve vault，再按意图 route-create。
- Git Hook 记录提交事实；Agent Hook 记录重大产出、关键决策和理由，不记录流水账。
- CLI 不作为用户入口；旧 CLI 能力必须迁入 Skill，脚本只作为 Skill 内部实现。
- `flux/`、`space/crafted/lifeos` 等旧路径只能作为 legacy source，不能作为新内容入口。
- 人际事件写入 `02-日记/人际事件/`；人物档案由 `lifeos` Skill 管理。

## 工作区切换

当前目录只在位于 vault 内时辅助决定工作状态；外部目录触发知识库操作时，以用户意图和工作区规范为准：

- `00-系统`：规范、Schema、Skills、Agent、审计。
- `01-收件箱`：接收、粗分、生成整理队列。
- `02-日记`：记录、反思、复盘。
- `03-知识`：沉淀知识卡片和主题笔记。
- `04-项目`：推进项目，项目内可有局部 `AGENTS.md` 或 `CLAUDE.md`。
- `05-资源`：保存长期参考资料和附件。
- `06-输出`：维护可发布成品。
- `99-归档`：保存迁移记录、废弃系统、废弃工具、完结项目和非活跃内容。

## 验收

结构迁移后至少检查：

```bash
# 在 vault 根目录执行
find . -maxdepth 2 -name WORKSPACE.md | sort
find .thirdspace -maxdepth 3 -type f | sort
# 如已配置 $THIRDSPACE_SKILLS，运行 CLI 脚本验收：
# node ${THIRDSPACE_SKILLS}/thirdspace-vault/scripts/thirdspace-vault.mjs audit-subsystems --vault . --write-report
```
