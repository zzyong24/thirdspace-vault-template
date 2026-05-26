# ThirdSpace Vault Template

一个可直接 clone 使用的知识库操作系统模板。

📖 **[完整使用手册 → MANUAL.md](./MANUAL.md)**

## 设计理念

- **Agent-native**：所有知识库操作由 AI Agent 驱动，无需手动维护
- **全 Agent 兼容**：支持 Claude Code、Cursor、Windsurf、OpenCode、Codex、Amp、Roo Code、Goose、Gemini CLI 等所有主流 Agent。Skills 内置在 vault 内，初始化时由 Agent 自动完成，无需外部工具
- **自描述（Self-contained）**：vault 根目录存在 `.thirdspace/workspace-index.yaml` 即代表"这里是知识库"，无需任何外部配置
- **路径无关**：任何人 clone 到任意目录均可直接使用，零硬编码绝对路径
- **渐进式加载**：Skill 按需加载，日常操作不浪费 token

## 快速开始

### 1. Clone 或使用模板

```bash
# 方式 A：直接 clone
git clone https://github.com/zzyong24/thirdspace-vault-template my-vault
cd my-vault

# 方式 B：点击页面上方 "Use this template" 创建你自己的 repo
```

### 2. 初始化（由 Agent 完成）

在 vault 目录打开任意 AI Agent，说：

> 帮我初始化这个知识库

Agent 读取 `CLAUDE.md` / `AGENTS.md` → 加载 `init-vault` Skill → 根据当前环境（OS、Agent 平台）自动完成：
- 结构验证
- Hook 安装（git hook / Agent stop hook）
- 定时任务注册
- Skill 全局注册

### 3. 启用 Obsidian 插件（可选）

用 Obsidian 打开 vault 目录：
- 设置 → 第三方插件 → 关闭安全模式 → 启用 **ThirdSpace Dashboard**

插件提供：工作区文件统计、GitHub 贪吃蛇热力图、Todos 管理、快捷操作面板。

---

## 目录结构

```
.thirdspace/              ← vault 根锚点 + schema 规范
00-系统/
  Skills/                 ← Agent Skill 定义（thirdspace-vault + 16 个通用 Skill）
  规范/                   ← Frontmatter、工作区、路由等规范文档
  运行时/                 ← hooks 脚本模板（git hook、Claude stop hook、crontab）
01-收件箱/                ← 所有未分类内容入口
02-日记/                  ← 工作日志、反思、复盘、Todos
03-知识/                  ← 知识卡片、主题笔记
04-项目/                  ← Roadmap、项目文档
05-资源/                  ← 图片、附件
06-输出/                  ← 对外发布内容
99-归档/                  ← 已归档内容
.obsidian/plugins/        ← ThirdSpace Dashboard 插件
```

## Skill 体系

| Skill | 触发场景 |
|-------|---------|
| `thirdspace-vault` | 任何知识库操作（主 Skill） |
| `init-vault` | "初始化" / "setup" / 第一次使用 |
| `workspace-*` | 进入对应工作区时自动加载 |
| `worklog` | 工作日志相关 |
| `review` | 周报 / 月报 / 复盘 |
| `reflect` | 反思 |
| `lifeos` | 人际事件 / 人物画像 |
| `article` | 写文章 / 发布 |
| `knowledge` | 知识整理 |

## 个性化

clone 后按需修改：
- `.thirdspace/workspace-index.yaml`：调整工作区名称和描述
- `00-系统/Skills/thirdspace-vault/SKILL.md`：添加你的触发词
- 各工作区 `WORKSPACE.md`：定义你的工作区规范

## 许可

MIT
