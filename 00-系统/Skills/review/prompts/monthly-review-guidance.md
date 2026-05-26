## 月报生成指引

收到 `monthly_review` 返回的全部素材后，生成月报并调用 `save_monthly_review` 保存。

### 需要生成的字段

1. `month_label`: 月标签（从素材元数据获取）
2. `theme`: 本月主题（一句话概括）
3. `achievements`: 主要成就列表（覆盖各维度）
4. `knowledge_graph`: 知识图谱变化描述
5. `growth_track`: 成长轨迹
6. `next_okr`: 下月 OKR 列表

### 关键要求

- 素材覆盖了 vault 中所有本月变更的文件，请**全面整合**
- 月报比周报视角更高：关注趋势、模式和战略方向
- 下月 OKR 要具体可衡量
