# 如何更新

用户的 vault 是从模板 fork 出来的个人知识库，包含你自己的笔记、日记等个人内容。**不能直接 `git pull`**——那会覆盖你的内容。

正确的做法是只更新"系统目录"（Skills、规范、schema、插件），完全不碰你的个人内容。

---

## 第一次配置上游（只做一次）

```bash
cd your-vault
git remote add upstream https://github.com/zzyong24/thirdspace-vault-template
git fetch upstream
```

---

## 查看有哪些更新

```bash
git fetch upstream

# 查看上游改了什么（只看系统目录）
git diff HEAD upstream/main -- 00-系统/Skills/
git diff HEAD upstream/main -- .thirdspace/schema/
git diff HEAD upstream/main -- CLAUDE.md AGENTS.md
```

---

## 执行更新

只更新系统文件，个人内容（日记、笔记、项目等）完全不动：

```bash
git fetch upstream

# 更新 Skills（核心）
git checkout upstream/main -- 00-系统/Skills/

# 更新 schema
git checkout upstream/main -- .thirdspace/schema/

# 更新规范文档
git checkout upstream/main -- 00-系统/规范/

# 更新运行时模板
git checkout upstream/main -- 00-系统/运行时/

# 更新入口文件
git checkout upstream/main -- CLAUDE.md AGENTS.md

# 更新 Dashboard 插件
git checkout upstream/main -- .obsidian/plugins/thirdspace-dashboard/

# 提交
git add -A
git commit -m "chore: sync from upstream template"
```

> **安全**：以上命令绝不会碰 `01-收件箱/`、`02-日记/`、`03-知识/`、`04-项目/`、`05-资源/`、`06-输出/`、`99-归档/` 这些你的个人内容目录。

---

## 更新 Dashboard 插件（单独）

插件更新不需要 git，直接替换文件：

1. 下载 [最新 Release](https://github.com/zzyong24/thirdspace-dashboard/releases) 的 `main.js` / `styles.css`
2. 覆盖 `.obsidian/plugins/thirdspace-dashboard/` 下的文件
3. 在 Obsidian 中重载插件（`Cmd+P` → Reload app without saving）

---

## 个人扩展 Skills 怎么管理

模板只包含通用 Skills。你自己的领域 Skills（如写作流程、个人方法论等）放在：

```
00-系统/Skills/   ← 你的个人 Skills 也放这里，不影响更新
```

执行系统 Skills 更新时（`git checkout upstream/main -- 00-系统/Skills/`），只会更新模板里存在的 Skill 目录，**你自己新增的 Skill 不会被删除**。
