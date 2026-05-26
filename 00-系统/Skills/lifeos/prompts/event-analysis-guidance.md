## LifeOS 事件分析指引

### 事件创建

使用 `create_event` 创建事件文档，系统自动从模板生成结构化文件，包含：事件描述、关联人物、情绪标记、分析框架。

### 事件分析流程

1. 调用 `analyze_event(event_path)` 读取事件上下文（包含关联人物画像）
2. AI 基于上下文生成分析，调用 `save_event_analysis(event_path, section, content)` 分章节保存
3. 可分析的章节：利益格局、信息差、决策选项、风险评估等

### 事件复盘

调用 `review_event(event_path)` 读取事件全貌（含已写入的分析），生成复盘总结。

### 人物画像

- `manage_people(action="add", data="{...}")`: 新增人物档案
- `manage_people(action="get", person_id="xxx")`: 查看人物详情
- `manage_people(action="search", data="关键词")`: 搜索人物

### 关键原则

- 事件分析要结合关联人物的画像和历史互动
- 分析要直白，不回避冲突和利益矛盾
- 复盘重在提炼可复用的决策模式
