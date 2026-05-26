# 全局路由与 Hook 事件采集规范

## 目标

让 Agent 在任何目录都能操作 ThirdSpace 知识库，并让 Git Hook、Agent Hook、定时任务自动记录高价值工作日志。

这不是流水账系统，而是工作记忆系统：

- Git Hook 记录“提交了什么”。
- Agent Hook 记录“产出了什么重大内容、基于什么决策、为什么这样决策”。
- 定时任务保证每天都有工作日志文件。
- 全局路由保证在任意 `pwd` 都能找到知识库并把内容写到正确工作区。

## 四层流程

```text
任何目录触发
  -> resolve-vault 找到 ThirdSpace
  -> intent-router 判断意图和目标工作区
  -> workspace/subsystem skill 应用规范
  -> create/worklog/event 命令落盘
```

## Vault Resolver

知识库路径查找顺序：

1. 从当前 `pwd` 向上查找 `.thirdspace/workspace-index.yaml`。
2. 读取环境变量 `THIRDSPACE_VAULT`。
3. 读取 `~/.thirdspace/config.yaml`。
4. 无可用配置时报错退出（不设硬编码 fallback，避免在错误路径写入）。

## Intent Router

常见意图路由：

| 意图 | 目标 |
|---|---|
| 记录内容创作数据、发布复盘、tracker | `04-项目/内容创作` |
| 写开发文档、技术方案、部署手册 | `03-知识/开发` |
| 写工具方法论、CLI 使用说明 | `03-知识/开发工具` 或 `05-资源/CLI工具` |
| 写可发布文章、教程 | `06-输出/文章` |
| 写口播稿 | `06-输出/口播稿` |
| 写项目计划、需求、复盘 | `04-项目` |
| 记录工作日志 | `02-日记/工作日志` |
| 暂时无法判断 | `01-收件箱/待整理` |

路由落盘必须写入 Frontmatter：

- `origin_cwd`
- `route_intent`
- `route_reason`
- `source`

## 工作日志文件

每日工作日志路径：

```text
02-日记/工作日志/YYYYMMDD_工作日志_周X.md
```

固定章节：

```markdown
## 今日重点
## 今日Todo
## Git 提交
## 重点记录
## 关键决策
## 问题与风险
## 明日计划
```

定时任务每天只需要调用 `ensure-worklog`，存在则不重复创建。

定时任务规格必须在 vault 内留存：

```text
00-系统/运行时/crontab/thirdspace-worklog.cron
```

## Git Hook

Git Hook 只记录提交事实，不做长篇解释：

- repo 路径
- branch
- commit hash
- commit subject
- changed files
- commit time

写入工作日志的 `## Git 提交`。

## Agent Hook

Agent Hook 记录语义产出，不记录每一步操作：

- 重大产出：产出了什么
- 决策：选择了什么方案
- 理由：为什么这样选
- 证据：改了哪些文件、生成了哪些报告、跑了哪些验证
- 来源目录：`origin_cwd`

写入工作日志的 `## 重点记录` section，格式为结构化条目：

```markdown
### HH:MM — 标题

**为什么做**：...
**怎么做的**：...
**改了什么**：...
```

重大决策同步写入 `## 关键决策`。

## 初始化与自注册

初始化新知识库时必须具备：

- `.thirdspace/schema/event-capture.yaml`
- `.thirdspace/events/`
- `02-日记/工作日志/`
- `thirdspace-vault.mjs ensure-worklog`
- `thirdspace-vault.mjs record-agent-event`
- `thirdspace-vault.mjs capture-git-commit`
- `thirdspace-vault.mjs register-hooks`

任意 Git 仓库执行 `register-hooks --repo <repo>` 后，会安装 post-commit hook。注册时必须尊重 Git 实际使用的 `core.hooksPath`；若未配置则写入仓库 `.git/hooks`。若目标位置已有自定义 hook，不覆盖，只生成待人工合并的 hook 文件。

全局 Git Hook 的源模板必须保存在：

```text
00-系统/运行时/hooks/global-post-commit.sh
```

换电脑时，Agent 应调用：

```bash
node 00-系统/Skills/thirdspace-vault/scripts/thirdspace-vault.mjs install-runtime --vault <vault> --all
```

该命令从 vault 内模板恢复本机 `core.hooksPath` 和每日工作日志 crontab。

## 防噪音原则

- Git Hook 只记录 commit 级事件。
- Agent Hook 只记录重大产出和关键决策。
- 不记录每次 shell 命令。
- 不记录纯读取、纯搜索、无产出的探索。
- 同一个 commit hash 不重复写入。
