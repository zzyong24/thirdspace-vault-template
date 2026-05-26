# 05-资源 工作区规范

## 用途

保存长期参考资料、CLI 工具、工作流、模板、附件、图片、人物档案和可复用素材。

## 允许

- CLI 工具说明
- 工作流说明
- 模板说明
- 图片和附件索引
- 人物档案索引

## 禁止

- 临时收件箱文件
- 日记
- 发布成品

## 命名

文档使用 `YYYYMMDD_资源主题.md`。资源目录只保留一层类型目录，例如 `图片/`、`附件/`、`CLI工具/`、`模板/`、`工作流/`、`人物档案/`，并用根层 Markdown 索引描述。

图片和附件允许为了保持引用关系保留一层资产包目录，例如 `图片/flux-intake-assets/` 和 `附件/flux-intake-data/`，但必须有 README 或 manifest 说明来源。

## Frontmatter

`workspace` 必须为 `05-资源`，`type` 使用 `resource`、`note`、`asset`、`workflow` 或 `profile-data`。

## 子 Skill

使用 `workspace-resources`。

## 人物档案

- `人物档案/people.json` 是 LifeOS 的人类可见人物画像数据。
- `.thirdspace/data/lifeos/people.json` 是机器副本。
- 处理人物画像时加载 `lifeos` Skill。
