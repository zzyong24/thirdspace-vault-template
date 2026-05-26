# ThirdSpace Vault 使用手册

> **定位**：一个由 AI Agent 驱动的个人知识库操作系统。不是 App，不需要配置界面——打开 AI Agent，直接说话就能用。

---

## 目录

1. [准备工作](#1-准备工作)
2. [第一次初始化](#2-第一次初始化)
3. [工作区介绍](#3-工作区介绍)
4. [功能模块（Skills）](#4-功能模块skills)
5. [日常使用场景](#5-日常使用场景)
6. [控制台插件（Dashboard）](#6-控制台插件dashboard)
7. [自动化功能](#7-自动化功能)
8. [个性化](#8-个性化)
9. [常见问题](#9-常见问题)

---

## 1. 准备工作

### 必须安装

| 工具 | 用途 | 下载 |
|------|------|------|
| **Git** | 版本控制 | 系统自带或 git-scm.com |
| **Obsidian** | 查看和编辑知识库文件 | obsidian.md |
| **AI Agent** | 驱动所有知识库操作 | 见下方 |

### 支持的 AI Agent

**所有主流 Agent 均支持**——只要 Agent 能读取 `CLAUDE.md` / `AGENTS.md` 或自身规则文件，就能驱动本知识库系统。Skills 内置在 vault 的 `00-系统/Skills/` 目录，初始化时由 Agent 自动完成软链，**无需任何外部工具**。

| Agent | 读取的规则文件 | Skill 安装路径 |
|-------|--------------|----------------|
| Claude Code | `CLAUDE.md` | `~/.claude/skills/` |
| Cursor | `CLAUDE.md` | `.cursor/rules/` |
| Windsurf | `CLAUDE.md` | `.windsurf/rules/` |
| OpenCode | `AGENTS.md` · `opencode.json` | `~/.opencode/skills/` |
| Codex (OpenAI) | `AGENTS.md` | `~/.codex/skills/` |
| Amp | `AGENTS.md` | `~/.amp/skills/` |
| Kilo Code | `AGENTS.md` | `.kilocode/rules/` |
| Roo Code | `AGENTS.md` | `.roo/rules/` |
| Goose | `AGENTS.md` | `~/.goose/skills/` |
| Gemini CLI | `GEMINI.md` | `~/.gemini/skills/` |
| GitHub Copilot | `.github/copilot-instructions.md` | — |
| TRAE IDE | `AGENTS.md` | — |
| Antigravity / Clawdbot / Droid | `AGENTS.md` | — |

> **Skill 不需要手动安装**：执行初始化时，Agent 读取 `init-vault` Skill 后，会根据当前使用的 Agent 平台自动创建对应的软链或复制文件，无需用户干预。hooks、crontab 同理——Agent 自行感知 OS 和平台决定安装方式。

### 可选

- **Node.js 18+**：供部分脚本使用（如 `thirdspace-vault.mjs`）
- **Python 3.10+**：供 worklog、review、reflect 等 Skill 的脚本使用

---

## 2. 第一次初始化

### Step 1：Clone

```bash
git clone https://github.com/your-org/thirdspace-vault-template my-vault
cd my-vault
```

### Step 2：打开 AI Agent，说一句话

```
帮我初始化这个知识库
```

Agent 会自动读取 `CLAUDE.md` → 加载 `init-vault` Skill → 根据你的环境完成：

**Agent 会做的事：**

| 操作 | 说明 | 可跳过 |
|------|------|--------|
| ✅ 结构验证 | 确认 `.thirdspace/schema/` 6 个文件完整 | 否 |
| 🔧 Stop Hook 安装 | 每次 Agent session 结束自动提示记工作日志 | 可选 |
| 🔧 Git Hook 安装 | 每次 `git commit` 后自动记录提交到工作日志 | 可选 |
| 🔧 Crontab 注册 | 定时任务（如每日工作日志初始化） | 可选 |
| 🔧 Skill 全局注册 | 让 Agent 从任意目录都能识别知识库 | 推荐 |

> **注意**：Agent 会自动感知你的操作系统（macOS / Linux / Windows）和当前使用的 Agent 平台，自行选择安装方式。你不需要手动执行命令。

### Step 3：启用 Obsidian 插件

用 Obsidian 打开 `my-vault` 目录：

1. 设置（左下角齿轮）→ 第三方插件
2. 关闭「安全模式」
3. 在已安装插件列表找到 **ThirdSpace Dashboard** → 启用

### 初始化完成 ✓

现在可以在 vault 目录打开 Agent 说任何话了。

---

## 3. 工作区介绍

知识库由 8 个工作区组成，每个工作区有明确的职责边界：

```
my-vault/
├── 01-收件箱/    ← 所有新内容的入口
├── 02-日记/      ← 工作日志、反思、复盘
├── 03-知识/      ← 沉淀后的知识卡片和笔记
├── 04-项目/      ← 项目、产品 Roadmap
├── 05-资源/      ← 图片、附件、参考资料
├── 06-输出/      ← 文章、口播稿等发布内容
├── 99-归档/      ← 归档内容（只读）
└── 00-系统/      ← 规范、Skills、运行时（不放内容）
```

### 01-收件箱：入口

**放什么**：所有来不及归类的内容——随手记录的想法、网页剪藏、待处理的信息

**常用说法**：
- "帮我记一个想法：……"
- "把这篇文章存进来"
- "临时记一下：……"

**流转**：收件箱的内容处理后流向 03-知识、04-项目 或 06-输出。

---

### 02-日记：时间线

**放什么**：工作日志（每天）、反思（不定期）、复盘（每周/月）、人际事件

**子目录**：

| 目录 | 内容 | 触发方式 |
|------|------|---------|
| `工作日志/` | 每日工作记录，git commit 自动写入 | `git commit` 自动 / "今天做了……" |
| `反思/` | 深度反思文章（Mirror-Deepen-Bridge 结构） | "我想反思一下……" |
| `复盘/` | 周报、月报 | "帮我写周报" / "生成月报" |
| `人际事件/` | 重要人际互动记录 | "记录一个人际事件" |
| `todos/` | 每日 Todo 文件 | Dashboard "记TODO" 按钮 |

---

### 03-知识：知识库核心

**放什么**：经过处理的知识——读完一篇文章后的卡片、某个主题的系统笔记、技术文档

**常用说法**：
- "帮我整理一下关于 XX 的笔记"
- "把这篇文章做成知识卡片"
- "记录一下我对 XX 的理解"

---

### 04-项目：项目管理

**放什么**：正在推进的项目的 Roadmap、规格文档、状态看板

**常用说法**：
- "帮我新建一个项目文档"
- "更新一下 XX 项目的进展"
- "看看我的项目状态"

---

### 06-输出：对外发布

**放什么**：准备发布的文章、视频口播稿、课程脚本

**流程**：03-知识 → 06-输出 → 发布

**常用说法**：
- "帮我把这篇笔记改成文章"
- "写一篇关于 XX 的文章"

---

## 4. 功能模块（Skills）

Skill 是 AI Agent 的能力模块，按需加载，不会在无关操作时占用 token。

### 核心 Skill

| Skill | 触发词（对 Agent 说） | 功能 |
|-------|----------------------|------|
| `thirdspace-vault` | "知识库"、"ThirdSpace"、"vault" | 主入口，路由到具体工作区和子 Skill |
| `init-vault` | "初始化"、"setup"、"第一次使用" | 新机器初始化，安装 hooks、注册 Skill |

### 工作区 Skills（自动加载）

进入对应工作区时自动激活，无需手动触发：

| Skill | 激活场景 |
|-------|---------|
| `workspace-inbox` | 整理收件箱、网页剪藏、待整理内容 |
| `workspace-journal` | 写日记、工作日志、反思 |
| `workspace-knowledge` | 知识卡片、主题笔记、知识沉淀 |
| `workspace-projects` | 项目管理、Roadmap、任务看板 |
| `workspace-outputs` | 写文章、发布内容 |
| `workspace-resources` | 管理参考资料、图片、素材 |
| `workspace-archive` | 归档内容管理 |
| `workspace-system` | 系统配置、规范维护（一般不手动触发） |

### 领域 Skills（意图触发）

| Skill | 触发词 | 功能 |
|-------|--------|------|
| `worklog` | "工作日志"、"补充日志"、"今天做了" | 创建/更新工作日志 |
| `review` | "周报"、"月报"、"周复盘"、"月复盘" | 生成周/月报告 |
| `reflect` | "反思"、"复盘思考" | 结构化反思（Mirror-Deepen-Bridge） |
| `lifeos` | "人际事件"、"记录关系"、"人物档案" | 人际互动记录和分析 |
| `article` | "写文章"、"发布文章" | 文章创作和发布流程 |
| `knowledge` | "知识卡片"、"整理成知识" | 知识加工和沉淀 |

---

## 5. 日常使用场景

### 场景一：记录一个想法

**你说**：
> 刚想到一个关于 XX 的想法，帮我记下来

**Agent 做**：
1. 创建 `01-收件箱/YYYYMMDD_想法.md`
2. 写入完整 Frontmatter（9 字段）
3. 记录想法内容

---

### 场景二：保存一篇文章

**你说**：
> 帮我把这篇文章（粘贴内容）保存到知识库，做成知识卡片

**Agent 做**：
1. 加载 `knowledge` Skill
2. 提炼核心观点、关键词
3. 创建 `03-知识/主题/YYYYMMDD_文章标题.md`，格式化为知识卡片

---

### 场景三：写今日工作日志

**你说**：
> 帮我把今天做的事情记录一下

**Agent 做**：
1. 加载 `worklog` Skill
2. 找到或创建今日工作日志 `02-日记/工作日志/YYYYMMDD_工作日志_周X.md`
3. 询问你今天做了什么，写入「重点记录」章节

**或者**：直接点 Dashboard 的「今日志」按钮打开今日文件手写。

---

### 场景四：生成周报

**你说**：
> 帮我写本周的周报

**Agent 做**：
1. 加载 `review` Skill
2. 扫描本周 `02-日记/工作日志/` 下的文件
3. 生成结构化周报，存入 `02-日记/复盘/`

---

### 场景五：管理项目

**你说**：
> 帮我创建一个新项目"XX App"，包含 Roadmap 和任务列表

**Agent 做**：
1. 加载 `workspace-projects` Skill
2. 在 `04-项目/` 下创建项目文件夹
3. 生成 Roadmap 文件和任务看板

---

### 场景六：整理收件箱

**你说**：
> 帮我整理收件箱，把里面的内容分类到对应工作区

**Agent 做**：
1. 扫描 `01-收件箱/` 下的文件
2. 根据内容类型判断目标工作区
3. 逐个询问确认后移动（不自动批量移动）

---

## 6. 控制台插件（Dashboard）

在 Obsidian 侧边栏点击 📊 图标（或 `Cmd+P` 搜索 ThirdSpace）打开控制台。

### 面板功能

| 区域 | 功能 |
|------|------|
| **顶部统计** | 总文件数 / 本周新增 / 本月新增 / 活跃天数 |
| **ACTIVITY** | 过去一年的贡献热力图（GitHub 贪吃蛇风格） |
| **WORKSPACES** | 8 个工作区的文件数量和最近活跃时间，点击打开 |
| **TODOS** | 今日 Todo 文件的待办事项，可直接勾选完成 |
| **TODAY** | 今日工作日志的重点和决策 |
| **PRODUCTS** | 产品/项目状态看板（读取 `04-项目/product-status.md`） |
| **QUICK** | 快捷操作按钮（见下表） |
| **RECENT** | 最近 7 天修改的文件列表 |

### 快捷操作按钮

| 按钮 | 操作 |
|------|------|
| ✎ 新笔记 | 在收件箱创建新笔记并打开（含完整 Frontmatter） |
| ◈ 今日志 | 打开今日工作日志文件 |
| ☐ 记TODO | 打开/创建今日 Todo 文件（`02-日记/todos/`） |
| ⊕ 搜索 | 打开全局搜索 |
| ↓ 收件箱 | 打开收件箱工作区 |

---

## 7. 自动化功能

### Git Hook（自动记录提交）

每次执行 `git commit`，钩子自动：
1. 检测当前 repo 所在的 vault 根
2. 将提交信息追加到今日工作日志的 `## Git 提交` 章节

**格式**：
```
- [14:30] `项目名/main` `a1b2c3`: feat: 新增XX功能 (5文件: src/...)
```

不需要手动操作，每次 commit 自动执行。

---

### Stop Hook（AI 会话结束提示）

每次关闭 AI Agent session 时，钩子检测本次是否有重大产出（代码提交、完成任务等），如果有：

- Agent 被要求在停止前记录工作日志
- 格式：`### HH:MM — 标题 / **为什么做** / **怎么做的** / **改了什么**`
- 写入今日工作日志的 `## 重点记录` 章节

---

## 8. 个性化

### 修改工作区名称

编辑 `.thirdspace/workspace-index.yaml`，修改 `desc` 字段（保持 `dir` 不变）：

```yaml
- dir: "03-知识"
  desc: "我的知识库"    # 改这里
  skill: workspace-knowledge
```

### 添加自己的触发词

编辑 `00-系统/Skills/thirdspace-vault/SKILL.md`，在 `triggers:` 下添加：

```yaml
triggers:
  - "知识库"
  - "我的项目名"    # ← 添加你的项目名，让 Agent 自动识别
```

### 添加产品状态看板

创建 `04-项目/product-status.md`，Dashboard 的 PRODUCTS 区域会自动读取：

```markdown
## 🟢 进行中

### 项目名称
- 当前里程碑：v1.0 发布
```

状态图标：`🟢` 活跃 / `🟡` 关注 / `🔴` 暂停

### 调整 Frontmatter 规范

编辑 `.thirdspace/schema/taxonomy.yaml` 添加自定义 topic：

```yaml
topic_values:
  - ai
  - dev
  - my-topic    # ← 添加你自己的主题
```

---

## 9. 常见问题

**Q：Agent 说找不到知识库**

在 vault 根目录（含 `.thirdspace/` 的目录）打开 Agent。或者：

```bash
export THIRDSPACE_VAULT=/path/to/my-vault
```

---

**Q：Dashboard 工作区文件数显示为 0**

在 Obsidian 中 `Cmd+P` → `Reload app without saving` 重新加载插件。

---

**Q：Git Hook 没有写入工作日志**

检查 hook 是否已安装：

```bash
ls ~/.config/git/hooks/post-commit    # macOS/Linux
```

未安装则让 Agent 重新初始化：`帮我重新安装 git hook`

---

**Q：想在已有的 Obsidian Vault 上使用**

将以下内容复制到你的 vault：
1. `.thirdspace/` 目录（含所有 schema）
2. `00-系统/Skills/` 目录
3. `CLAUDE.md` 和 `AGENTS.md`
4. `.obsidian/plugins/thirdspace-dashboard/`

然后告诉 Agent："帮我初始化这个知识库"。

---

**Q：能在 Windows 上用吗？**

可以，但 Stop Hook 和 Git Hook 需要 WSL 或 Git Bash。初始化时告诉 Agent 你的环境，它会选择合适的安装方式。

---

## 附录：Frontmatter 字段说明

所有 Markdown 文件必须包含这 9 个字段（Agent 创建文件时自动填写）：

| 字段 | 说明 | 示例值 |
|------|------|--------|
| `title` | 文档标题 | `"我的笔记"` |
| `type` | 内容类型 | `note` / `worklog` / `article` / `card` ... |
| `topic` | 主题 | `ai` / `dev` / `work` / `life` ... |
| `workspace` | 所在工作区 | `"03-知识"` |
| `created` | 创建时间 | `"2026-05-26 10:00:00"` |
| `modified` | 修改时间 | `"2026-05-26 10:00:00"` |
| `tags` | 标签列表 | `["note", "ai", "draft"]` |
| `source` | 来源 | `manual` / `agent` / `web` |
| `status` | 状态 | `draft` / `active` / `processed` / `archived` |
