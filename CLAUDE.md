# ThirdSpace Claude Code 入口

## Bootstrap（新用户 / 任意机器）

**当 Claude Code 在 vault 根目录（含 `.thirdspace/workspace-index.yaml` 的目录）打开时，按顺序读取：**

1. `./00-系统/Skills/thirdspace-vault/SKILL.md`（Skill 定义 + 初始化流程）
2. `.thirdspace/workspace-index.yaml`（工作区索引）
3. `.thirdspace/schema/subsystems.yaml`（工作区契约）
4. `.thirdspace/schema/event-capture.yaml`（Agent 事件采集规格）
5. `.thirdspace/schema/workspace-tools.yaml`（工作区→Skill 绑定）
6. 当前工作区的 `WORKSPACE.md`

> 所有路径相对于 vault 根。不写任何绝对路径。

## 初始化指令

用户说「初始化」「帮我配置知识库」「setup」时，Agent 执行 SKILL.md 中的
**Delivery Checklist（新仓库初始化流程）**，顺序完成：
1. 结构验证（schema 文件是否完整）
2. 运行时安装（git hook + crontab）
3. Claude Code Stop Hook 安装（`~/.claude/hooks/session-stop.sh`）
4. Skill 全局注册（`~/.claude/skills/thirdspace-vault` 软链）
5. 打印 Obsidian 插件启用说明

## 操作规则

- 新 Markdown 文件命名：`YYYYMMDD_主题.md`。
- 每个 Markdown 文件必须有完整 Frontmatter（9 字段）。
- `workspace` 字段等于当前工作区目录名（如 `"03-知识"`）。
- 不确定归属时写入 `01-收件箱/待整理/`。
- Obsidian Web Clipper 内容写入 `01-收件箱/网页剪藏/`。
- 任何写入操作先 resolve vault 根，再按意图路由到工作区。
- Git Hook 只记录提交事实；Agent Hook 只记录重大产出和关键决策。
- 工作日志写入 `02-日记/工作日志/YYYYMMDD_工作日志_周X.md`。
- 批量操作先写 manifest 到 `.thirdspace/manifests/`，不直接移动。
- `flux/`、`space/crafted/` 等旧路径只用于迁移追溯，不作为新内容入口。
