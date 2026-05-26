---
name: review
description: >-
  周/月复盘引擎。用户说"做周报"、"周复盘"、"月复盘"、"复盘一下"、"这周做了什么"时触发。
  全量扫描 vault .md 文件，按时间过滤，聚合内容，生成结构化复盘报告。
triggers:
  - "周报"
  - "月报"
  - "周复盘"
  - "月复盘"
  - "复盘"
  - "这周做了什么"
  - "上周总结"
---

# Review Skill — 周/月复盘引擎

## 核心设计原则

不硬编码目录列表。全量扫描 `{VAULT}` 下所有 `.md`，按 Frontmatter 时间戳筛选，自动覆盖所有 workspace / type / topic。

---

## 执行流程

### Step 1 — 确定时间范围

```bash
# 本周（周一到周日）
python3 -c "
from datetime import date, timedelta
today = date.today()
monday = today - timedelta(days=today.weekday())
sunday = monday + timedelta(days=6)
print(f'本周: {monday} ~ {sunday}')
print(f'周标签: {monday.isocalendar()[0]}-W{monday.isocalendar()[1]:02d}')
"

# 本月
python3 -c "
from datetime import date
today = date.today()
print(f'本月: {today.year}-{today.month:02d}')
"
```

### Step 2 — 扫描并过滤 vault 文件

```bash
VAULT=$(cat ~/.thirdspace/config.yaml 2>/dev/null | grep "^vault:" | awk '{print $2}')
# 按 created/modified 日期过滤（提取 frontmatter）
python3 - "$VAULT" "$START_DATE" "$END_DATE" <<'EOF'
import sys, os, re, json
from pathlib import Path

vault = Path(sys.argv[1])
start = sys.argv[2]
end   = sys.argv[3]

items = []
for md in vault.rglob("*.md"):
    # 跳过 _legacy、.thirdspace、WORKSPACE.md 等
    if any(p in str(md) for p in ["_legacy", ".thirdspace", "WORKSPACE", "AGENTS", "CLAUDE"]):
        continue
    text = md.read_text(errors='ignore')
    # 提取 frontmatter
    fm = {}
    m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            kv = line.split(':', 1)
            if len(kv) == 2:
                fm[kv[0].strip()] = kv[1].strip().strip('"')
    # 提取日期
    date_str = fm.get('created') or fm.get('modified', '')[:10]
    if not date_str:
        name_m = re.match(r'(\d{8})', md.stem)
        if name_m:
            d = name_m.group(1)
            date_str = f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    if start <= date_str[:10] <= end:
        items.append({
            "path": str(md.relative_to(vault)),
            "title": fm.get('title', md.stem),
            "type": fm.get('type', ''),
            "topic": fm.get('topic', ''),
            "workspace": fm.get('workspace', str(md.parts[0]) if md.parts else ''),
            "date": date_str[:10],
            "status": fm.get('status', ''),
        })

items.sort(key=lambda x: x['date'], reverse=True)
print(json.dumps(items, ensure_ascii=False, indent=2))
EOF
```

### Step 3 — Claude 生成报告

拿到 JSON 数据后，Claude 按以下结构生成报告：

**周报结构：**
```markdown
# 周报：{YYYY}-W{WW}

## 本周亮点
（3-5 条最有价值的产出/进展）

## 知识摄入
（03-知识 + 01-收件箱 处理的内容）

## 实践进度
（04-项目 的推进）

## 内容产出
（06-输出 的文章/口播稿）

## 思考沉淀
（02-日记/反思 的核心洞察）

## 下周聚焦
（3 条具体方向）
```

**月报结构：**在周报基础上增加：
- 月度主题词
- 知识图谱变化
- 下月 OKR（3 条）

### Step 4 — 写入 vault

**周报**：`{VAULT}/02-日记/复盘/{YYYY}W{WW}_weekly.md`
**月报**：`{VAULT}/02-日记/复盘/{YYYYMM}_monthly.md`

Frontmatter 模板：
```yaml
---
title: "周报：{YYYY}-W{WW}"
type: "review"
topic: "work"
workspace: "02-日记"
created: "{今日时间}"
modified: "{今日时间}"
tags: ["work", "review", "active"]
source: "manual"
status: "active"
week: "{YYYY}-W{WW}"
---
```

---

## 快速触发示例

```
用户：帮我做本周复盘
Agent：
  1. 计算本周时间范围
  2. 扫描 vault 筛选本周文件
  3. 按 type/topic 分组展示给用户确认
  4. 生成周报正文
  5. 写入 02-日记/复盘/
```
