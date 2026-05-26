"""LifeOS Engine - 人际建模与事件决策辅助系统.

核心功能:
- 人物画像管理 (people.json CRUD)
- 事件创建 (基于模板自动生成 Markdown)
- 事件分析上下文准备 (读取事件+关联人物画像)
- 事件分析写入 (AI 生成的分析保存到事件文档)
- 事件复盘 (读取完整事件上下文供 AI 复盘)
- 事件搜索 (多维度搜索历史事件)
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class LifeOSEngine:
    """LifeOS 核心引擎."""

    def __init__(self, raw_dir: Path, context_dir: Path) -> None:
        self.raw_dir = raw_dir
        self.context_dir = context_dir
        vault_root = context_dir.parent if context_dir.name == "space" else context_dir
        new_people_file = vault_root / "05-资源" / "人物档案" / "people.json"
        new_events_dir = vault_root / "02-日记" / "人际事件" / "事件"
        self.people_file = new_people_file if new_people_file.exists() else raw_dir / "lifeos" / "people.json"
        self.machine_people_file = vault_root / ".thirdspace" / "data" / "lifeos" / "people.json"
        self.events_dir = new_events_dir if new_events_dir.exists() else context_dir / "crafted" / "lifeos" / "events"
        self.events_dir.mkdir(parents=True, exist_ok=True)

    # ──────────────────────────────────────
    # People CRUD
    # ──────────────────────────────────────

    def _load_people(self) -> dict[str, Any]:
        if self.people_file.exists():
            try:
                with open(self.people_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, KeyError) as e:
                raise RuntimeError(f"people.json 解析失败: {e}")
        return {"version": "1.0", "people": []}

    def _save_people(self, data: dict[str, Any]) -> None:
        self.people_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.people_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.machine_people_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.machine_people_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _find_person(self, people: list[dict], person_id: str) -> dict | None:
        for p in people:
            if p.get("id") == person_id:
                return p
        return None

    def list_people(self) -> str:
        data = self._load_people()
        people = data.get("people", [])
        if not people:
            return "📋 人物库为空，暂无人物记录。"

        lines = [f"📋 **人物列表**（共 {len(people)} 人）\n"]
        for p in people:
            rel_types = ", ".join(p.get("relation", {}).get("types", []))
            org = p.get("org", {})
            dept = org.get("department", "")
            title = org.get("title", "")
            traits_str = "、".join(p.get("traits", [])[:3])
            if len(p.get("traits", [])) > 3:
                traits_str += "..."
            lines.append(
                f"- **{p['name']}** (`{p['id']}`) — {rel_types}\n"
                f"  {dept} / {title}\n"
                f"  特征: {traits_str or '暂无'}"
            )
        return "\n".join(lines)

    def get_person(self, person_id: str) -> str:
        data = self._load_people()
        person = self._find_person(data.get("people", []), person_id)
        if not person:
            return f"❌ 未找到人物: {person_id}"
        return f"📄 **{person['name']}** 完整画像\n\n```json\n{json.dumps(person, ensure_ascii=False, indent=2)}\n```"

    def add_person(self, person_data: dict[str, Any]) -> str:
        data = self._load_people()
        people = data.get("people", [])
        person_id = person_data.get("id")
        if not person_id:
            return "❌ 缺少必填字段: id"
        if self._find_person(people, person_id):
            return f"❌ 人物已存在: {person_id}，请使用 update 操作"

        # 设置默认值
        person_data.setdefault("aliases", [])
        person_data.setdefault("domain", "work")
        person_data.setdefault("org", {})
        person_data.setdefault("relation", {"types": [], "closeness": 1, "trust": 1, "influence": 1})
        person_data.setdefault("traits", [])
        person_data.setdefault("notes", "")
        person_data.setdefault("interaction_summary", "")
        person_data.setdefault("history", [])
        person_data.setdefault("tags", [])
        person_data["updated"] = datetime.now().strftime("%Y-%m-%d")

        people.append(person_data)
        self._save_people(data)
        return f"✅ 人物已添加: **{person_data.get('name', person_id)}** (`{person_id}`)"

    def update_person(self, person_id: str, updates: dict[str, Any]) -> str:
        data = self._load_people()
        people = data.get("people", [])
        person = self._find_person(people, person_id)
        if not person:
            return f"❌ 未找到人物: {person_id}"

        changes = []
        for key, value in updates.items():
            if key == "id":
                continue
            if key == "traits" and isinstance(value, list):
                # traits 追加模式
                existing = set(person.get("traits", []))
                new_traits = [t for t in value if t not in existing]
                if new_traits:
                    person["traits"] = person.get("traits", []) + new_traits
                    changes.append(f"traits +{len(new_traits)}")
            elif key == "history" and isinstance(value, list):
                # history 追加模式
                person.setdefault("history", [])
                person["history"].extend(value)
                changes.append(f"history +{len(value)}")
            elif key == "interaction_summary" and isinstance(value, str):
                # interaction_summary 追加模式
                existing = person.get("interaction_summary", "")
                if existing:
                    person["interaction_summary"] = existing + "\n" + value
                else:
                    person["interaction_summary"] = value
                changes.append("interaction_summary")
            elif key == "relation" and isinstance(value, dict):
                # relation 合并更新
                person.setdefault("relation", {})
                person["relation"].update(value)
                changes.append("relation")
            elif key == "org" and isinstance(value, dict):
                person.setdefault("org", {})
                person["org"].update(value)
                changes.append("org")
            elif key == "tags" and isinstance(value, list):
                existing = set(person.get("tags", []))
                new_tags = [t for t in value if t not in existing]
                if new_tags:
                    person["tags"] = person.get("tags", []) + new_tags
                    changes.append(f"tags +{len(new_tags)}")
            else:
                person[key] = value
                changes.append(key)

        person["updated"] = datetime.now().strftime("%Y-%m-%d")
        self._save_people(data)
        return f"✅ 已更新 **{person.get('name', person_id)}**: {', '.join(changes)}"

    def delete_person(self, person_id: str) -> str:
        data = self._load_people()
        people = data.get("people", [])
        person = self._find_person(people, person_id)
        if not person:
            return f"❌ 未找到人物: {person_id}"
        name = person.get("name", person_id)
        data["people"] = [p for p in people if p.get("id") != person_id]
        self._save_people(data)
        return f"✅ 已删除人物: **{name}** (`{person_id}`)"

    def search_people(self, query: str) -> str:
        data = self._load_people()
        people = data.get("people", [])
        query_lower = query.lower()
        results = []
        for p in people:
            searchable = json.dumps(p, ensure_ascii=False).lower()
            if query_lower in searchable:
                results.append(p)

        if not results:
            return f"🔍 未找到匹配「{query}」的人物"

        lines = [f"🔍 搜索「{query}」找到 {len(results)} 人\n"]
        for p in results:
            rel_types = ", ".join(p.get("relation", {}).get("types", []))
            lines.append(f"- **{p['name']}** (`{p['id']}`) — {rel_types}")
        return "\n".join(lines)

    # ──────────────────────────────────────
    # Event Creation
    # ──────────────────────────────────────

    FULL_TEMPLATE = """---
created: "{created}"
tags: ["event", "{domain}", "{event_type}"]
domain: {domain}
event_type: {event_type}
urgency: {urgency}
status: new
people: {people_yaml}
related_events: []
---

# 事件：{title}

## 📋 事件描述

{description}

### 我的情绪状态

- **当前情绪**：{emotion}
- **情绪来源**：*（待 AI 分析）*
- **情绪对判断的影响**：*（待 AI 分析）*

> 💡 让 AI 知道你当前的情绪状态很重要——"很上头"和"很冷静"时，AI 给出的建议策略会完全不同。

---

## 🔍 事件剖析（AI 生成）

*（待 AI 分析）*

---

## 📐 处理原则（AI 生成）

*（待 AI 分析）*

---

## 💡 处理建议（AI 生成）

*（待 AI 分析）*

---

## 🎯 预演模拟（AI 生成）

*（待 AI 分析）*

---

## ✅ 实操 Checklist（AI 生成）

*（待 AI 分析）*

---

## 📝 执行记录（用户自行更新）

### {date_today}

（待记录）

---

## 🔄 事件复盘（事件结束后，AI 辅助生成）

*（待事件结束后复盘）*

---

## 关联

- 相关人物：{people_links}
- 前序事件：（待补充）
- 后续事件：（待补充）

---
"""

    LIGHT_TEMPLATE = """---
created: "{created}"
tags: ["event", "{domain}", "{event_type}"]
domain: {domain}
event_type: {event_type}
urgency: low
status: new
people: {people_yaml}
related_events: []
---

# 事件：{title}

## 📋 事件描述

{description}

## 我的情绪状态

{emotion}

---

## 💡 AI 建议

*（待 AI 分析）*

---

## 📝 结果

（待记录）

---
"""

    def create_event(
        self,
        title: str,
        description: str,
        domain: str = "work",
        event_type: str = "routine",
        urgency: str = "medium",
        people: list[str] | None = None,
        emotion: str = "平静",
    ) -> str:
        people = people or []
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        created = now.strftime("%Y-%m-%d %H:%M:%S")
        date_today = now.strftime("%Y-%m-%d")

        # 安全文件名
        safe_title = re.sub(r'[^\w\u4e00-\u9fff-]', '_', title)[:50]
        filename = f"event_{date_str}_{safe_title}.md"
        filepath = self.events_dir / filename

        # 检查同名文件
        if filepath.exists():
            suffix = 1
            while filepath.exists():
                filename = f"event_{date_str}_{safe_title}_{suffix}.md"
                filepath = self.events_dir / filename
                suffix += 1

        people_yaml = json.dumps(people, ensure_ascii=False)
        people_links = " ".join(f"[[{pid}]]" for pid in people) if people else "（无）"

        # preparation 类型始终用完整模板
        use_full = urgency in ("high", "medium") or event_type == "preparation"

        template = self.FULL_TEMPLATE if use_full else self.LIGHT_TEMPLATE
        content = template.format(
            created=created,
            domain=domain,
            event_type=event_type,
            urgency=urgency,
            people_yaml=people_yaml,
            title=title,
            description=description,
            emotion=emotion,
            date_today=date_today,
            people_links=people_links,
        )

        filepath.write_text(content, encoding="utf-8")

        return (
            f"✅ 事件已创建\n"
            f"📄 文件: `{filepath}`\n"
            f"📋 类型: {event_type} / {urgency}\n"
            f"👥 关联人物: {', '.join(people) or '无'}\n\n"
            f"💡 下一步: AI 应调用 `analyze_event` 读取上下文并生成分析"
        )

    # ──────────────────────────────────────
    # Event Analysis Context
    # ──────────────────────────────────────

    def analyze_event(self, event_path: str) -> str:
        filepath = Path(event_path)
        if not filepath.exists():
            return f"❌ 事件文件不存在: {event_path}"

        event_content = filepath.read_text(encoding="utf-8")

        # 提取 people 列表
        people_ids = self._extract_people_from_frontmatter(event_content)

        # 读取关联人物画像
        people_profiles = []
        data = self._load_people()
        all_people = data.get("people", [])
        for pid in people_ids:
            person = self._find_person(all_people, pid)
            if person:
                people_profiles.append(person)

        # 搜索相关历史事件
        frontmatter = self._parse_frontmatter(event_content)
        event_type = frontmatter.get("event_type", "")
        related_events = self._find_related_events(filepath, event_type, people_ids)

        # 组装上下文
        sections = []
        sections.append("# 📎 事件分析上下文\n")

        sections.append("## 事件原文\n")
        sections.append(event_content)
        sections.append("\n---\n")

        if people_profiles:
            sections.append("## 关联人物画像\n")
            for p in people_profiles:
                sections.append(f"### {p['name']} (`{p['id']}`)\n")
                sections.append(f"```json\n{json.dumps(p, ensure_ascii=False, indent=2)}\n```\n")
            sections.append("---\n")

        if related_events:
            sections.append("## 相关历史事件（摘要）\n")
            for evt in related_events[:5]:
                sections.append(f"- **{evt['title']}** ({evt['date']}) — {evt['type']}\n")
            sections.append("---\n")

        sections.append(
            "\n## AI 分析指引\n\n"
            "请基于以上事件内容和人物画像，生成以下分析章节：\n"
            "1. **🔍 事件剖析** — 各方立场分析、核心矛盾、利益分析、我的处境\n"
            "2. **📐 处理原则** — 明确边界和底线\n"
            "3. **💡 处理建议** — 短期和中期行动方案\n"
            "4. **🎯 预演模拟** — 关键场景的对话预演\n"
            "5. **✅ 实操 Checklist** — 可执行的步骤清单\n\n"
            "分析完成后，请调用 `save_event_analysis` 将分析写入事件文档。"
        )

        return "\n".join(sections)

    def _extract_people_from_frontmatter(self, content: str) -> list[str]:
        match = re.search(r'^people:\s*\[([^\]]*)\]', content, re.MULTILINE)
        if match:
            raw = match.group(1)
            return [s.strip().strip('"').strip("'") for s in raw.split(",") if s.strip()]
        return []

    def _parse_frontmatter(self, content: str) -> dict[str, str]:
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {}
        fm = {}
        for line in match.group(1).splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                fm[key.strip()] = val.strip().strip('"').strip("'")
        return fm

    def _find_related_events(
        self, current_file: Path, event_type: str, people_ids: list[str]
    ) -> list[dict[str, str]]:
        results = []
        for f in self.events_dir.glob("event_*.md"):
            if f == current_file:
                continue
            try:
                content = f.read_text(encoding="utf-8")
                fm = self._parse_frontmatter(content)
                evt_people = self._extract_people_from_frontmatter(content)

                # 匹配：类型相同 或 有共同人物
                type_match = fm.get("event_type") == event_type
                people_overlap = bool(set(evt_people) & set(people_ids))

                if type_match or people_overlap:
                    # 提取标题
                    title_match = re.search(r'^# 事件：(.+)$', content, re.MULTILINE)
                    title = title_match.group(1) if title_match else f.stem

                    results.append({
                        "title": title,
                        "date": fm.get("created", "")[:10],
                        "type": fm.get("event_type", "unknown"),
                        "file": str(f),
                    })
            except Exception:
                continue

        results.sort(key=lambda x: x["date"], reverse=True)
        return results

    # ──────────────────────────────────────
    # Save Event Analysis
    # ──────────────────────────────────────

    def save_event_analysis(self, event_path: str, section: str, content: str) -> str:
        filepath = Path(event_path)
        if not filepath.exists():
            return f"❌ 事件文件不存在: {event_path}"

        event_content = filepath.read_text(encoding="utf-8")

        # 定义可替换的占位符模式
        section_map = {
            "事件剖析": "🔍 事件剖析（AI 生成）",
            "处理原则": "📐 处理原则（AI 生成）",
            "处理建议": "💡 处理建议（AI 生成）",
            "预演模拟": "🎯 预演模拟（AI 生成）",
            "实操checklist": "✅ 实操 Checklist（AI 生成）",
            "checklist": "✅ 实操 Checklist（AI 生成）",
            "情绪来源": "情绪来源",
            "情绪对判断的影响": "情绪对判断的影响",
            "复盘": "🔄 事件复盘（事件结束后，AI 辅助生成）",
            "ai建议": "💡 AI 建议",
        }

        section_lower = section.lower().replace(" ", "")
        target_header = section_map.get(section_lower, section)

        # 尝试通过精确查找 + 字符串拼接替换，避免 re.sub 对 content 中
        # 反斜杠/特殊字符的错误解释（这是 JSON 编码内容经常触发的问题）
        lines = event_content.split("\n")
        header_idx = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            # 匹配 ## 开头，且包含目标标题关键文字（去掉 emoji 和空格后模糊匹配）
            if stripped.startswith("## "):
                header_text = stripped[3:].strip()
                # 精确匹配
                if header_text == target_header:
                    header_idx = i
                    break
                # 模糊匹配：去掉 emoji 和括号后比较核心文字
                import unicodedata
                def _strip_decorators(s: str) -> str:
                    """去掉 emoji、括号说明、空格，保留核心中文/英文。"""
                    result = []
                    skip_paren = False
                    for ch in s:
                        if ch in ("（", "("):
                            skip_paren = True
                            continue
                        if ch in ("）", ")"):
                            skip_paren = False
                            continue
                        if skip_paren:
                            continue
                        cat = unicodedata.category(ch)
                        if cat.startswith("So"):  # Symbol, other (emoji)
                            continue
                        if ch in (" ", "\t", "—", "-", "_"):
                            continue
                        result.append(ch.lower())
                    return "".join(result)

                if _strip_decorators(header_text) == _strip_decorators(target_header):
                    header_idx = i
                    break

        if header_idx is None:
            return f"❌ 未找到章节: {section}（目标标题: {target_header}）"

        # 检查标题下方是否有占位符 *（待...）*
        placeholder_idx = None
        for j in range(header_idx + 1, min(header_idx + 5, len(lines))):
            if lines[j].strip().startswith("*（待") and lines[j].strip().endswith("）*"):
                placeholder_idx = j
                break
            if lines[j].strip().startswith("## "):
                break  # 遇到下一个章节标题，停止

        if placeholder_idx is not None:
            # 替换占位符行为实际内容
            lines[placeholder_idx] = "\n" + content
        else:
            # 在标题后追加内容
            lines.insert(header_idx + 1, "\n" + content + "\n")

        new_content = "\n".join(lines)
        filepath.write_text(new_content, encoding="utf-8")
        return f"✅ 已写入「{target_header}」章节 → `{filepath.name}`"

    def save_event_analysis_batch(self, event_path: str, analyses: dict[str, str]) -> str:
        """批量写入多个章节的分析结果."""
        results = []
        for section, content in analyses.items():
            result = self.save_event_analysis(event_path, section, content)
            results.append(result)

        # 更新 status
        filepath = Path(event_path)
        if filepath.exists():
            event_content = filepath.read_text(encoding="utf-8")
            event_content = re.sub(
                r'status:\s*new',
                'status: analyzing',
                event_content,
            )
            filepath.write_text(event_content, encoding="utf-8")

        return "\n".join(results)

    # ──────────────────────────────────────
    # Event Review (复盘)
    # ──────────────────────────────────────

    def review_event(self, event_path: str) -> str:
        filepath = Path(event_path)
        if not filepath.exists():
            return f"❌ 事件文件不存在: {event_path}"

        event_content = filepath.read_text(encoding="utf-8")
        people_ids = self._extract_people_from_frontmatter(event_content)

        # 读取关联人物画像
        people_profiles = []
        data = self._load_people()
        all_people = data.get("people", [])
        for pid in people_ids:
            person = self._find_person(all_people, pid)
            if person:
                people_profiles.append(person)

        sections = []
        sections.append("# 📎 事件复盘上下文\n")
        sections.append("## 完整事件记录\n")
        sections.append(event_content)
        sections.append("\n---\n")

        if people_profiles:
            sections.append("## 关联人物当前画像\n")
            for p in people_profiles:
                sections.append(f"### {p['name']} (`{p['id']}`)\n")
                sections.append(f"```json\n{json.dumps(p, ensure_ascii=False, indent=2)}\n```\n")
            sections.append("---\n")

        sections.append(
            "\n## AI 复盘指引\n\n"
            "请基于完整事件记录（包括执行记录），生成以下复盘内容：\n\n"
            "### 1. 复盘内容（写入事件文档「🔄 事件复盘」章节）\n"
            "- **结果评估**：事件最终结果如何\n"
            "- **经验提取**：做对了什么、可以改进什么、意外发现\n"
            "- **认知升级**：这件事改变/强化了什么认知\n"
            "- **模式识别**：是否有类似模式反复出现\n\n"
            "### 2. 人物画像更新（调用 `manage_people` 更新）\n"
            "对每个关联人物，基于事件中的**具体行为证据**，更新以下字段：\n"
            "- `interaction_summary`：追加本次互动模式\n"
            "- `traits`：新发现的行为特征\n"
            "- `relation`：如信任度/亲密度有明显变化则调整（单次最多±1）\n"
            "- `notes`：新的重要认知\n"
            "- `history`：关系变化记录\n\n"
            "**更新原则**：有证据才更新、追加而非覆盖、变化需标注来源事件。\n\n"
            "完成后：\n"
            "1. 调用 `save_event_analysis(section='复盘')` 保存复盘内容\n"
            "2. 对每个需要更新的人物调用 `manage_people(action='update')` 更新画像"
        )

        return "\n".join(sections)

    # ──────────────────────────────────────
    # Event Search
    # ──────────────────────────────────────

    def search_events(
        self,
        query: str | None = None,
        event_type: str | None = None,
        domain: str | None = None,
        people: list[str] | None = None,
        status: str | None = None,
        days: int | None = None,
    ) -> str:
        results = []
        cutoff_date = None
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)

        for f in sorted(self.events_dir.glob("event_*.md"), reverse=True):
            try:
                content = f.read_text(encoding="utf-8")
                fm = self._parse_frontmatter(content)
                evt_people = self._extract_people_from_frontmatter(content)

                # 过滤条件
                if event_type and fm.get("event_type") != event_type:
                    continue
                if domain and fm.get("domain") != domain:
                    continue
                if status and fm.get("status") != status:
                    continue
                if people and not (set(people) & set(evt_people)):
                    continue
                if cutoff_date:
                    created = fm.get("created", "")[:10]
                    try:
                        if datetime.strptime(created, "%Y-%m-%d") < cutoff_date:
                            continue
                    except ValueError:
                        pass
                if query:
                    if query.lower() not in content.lower():
                        continue

                # 提取标题和摘要
                title_match = re.search(r'^# 事件：(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else f.stem

                results.append({
                    "title": title,
                    "date": fm.get("created", "")[:10],
                    "type": fm.get("event_type", "unknown"),
                    "urgency": fm.get("urgency", ""),
                    "status": fm.get("status", ""),
                    "people": evt_people,
                    "file": str(f),
                })
            except Exception:
                continue

        if not results:
            filters = []
            if query:
                filters.append(f"关键词={query}")
            if event_type:
                filters.append(f"类型={event_type}")
            if people:
                filters.append(f"人物={','.join(people)}")
            return f"🔍 未找到匹配的事件（过滤: {', '.join(filters) or '无'}）"

        lines = [f"🔍 **搜索结果**（共 {len(results)} 个事件）\n"]
        for evt in results:
            people_str = ", ".join(evt["people"]) if evt["people"] else "无"
            lines.append(
                f"### {evt['title']}\n"
                f"- 📅 {evt['date']} | 📋 {evt['type']} | ⚡ {evt['urgency']} | 🔖 {evt['status']}\n"
                f"- 👥 {people_str}\n"
                f"- 📄 `{evt['file']}`\n"
            )
        return "\n".join(lines)

    # ──────────────────────────────────────
    # Update event status
    # ──────────────────────────────────────

    def update_event_status(self, event_path: str, new_status: str) -> str:
        filepath = Path(event_path)
        if not filepath.exists():
            return f"❌ 事件文件不存在: {event_path}"

        valid_statuses = ["new", "analyzing", "in_progress", "resolved", "reviewed"]
        if new_status not in valid_statuses:
            return f"❌ 无效状态: {new_status}，可选: {', '.join(valid_statuses)}"

        content = filepath.read_text(encoding="utf-8")
        content = re.sub(r'status:\s*\S+', f'status: {new_status}', content)
        filepath.write_text(content, encoding="utf-8")
        return f"✅ 事件状态已更新为: {new_status}"

    # ──────────────────────────────────────
    # Append execution record
    # ──────────────────────────────────────

    def append_execution_record(self, event_path: str, record: str) -> str:
        filepath = Path(event_path)
        if not filepath.exists():
            return f"❌ 事件文件不存在: {event_path}"

        content = filepath.read_text(encoding="utf-8")
        today = datetime.now().strftime("%Y-%m-%d")

        # 找到「执行记录」章节，在其中追加
        exec_pattern = re.compile(
            r'(## 📝 执行记录（用户自行更新）\s*\n)',
        )
        if exec_pattern.search(content):
            new_record = f"\n### {today}\n\n{record}\n"
            # 在已有执行记录章节的末尾（下一个 ## 之前）插入
            parts = content.split("## 📝 执行记录（用户自行更新）")
            if len(parts) == 2:
                after_section = parts[1]
                # 找到下一个 ## 标题
                next_section = re.search(r'\n## ', after_section)
                if next_section:
                    insert_pos = next_section.start()
                    new_after = after_section[:insert_pos] + new_record + after_section[insert_pos:]
                else:
                    new_after = after_section + new_record
                content = parts[0] + "## 📝 执行记录（用户自行更新）" + new_after
                filepath.write_text(content, encoding="utf-8")
                return f"✅ 执行记录已追加 ({today})"

        return "❌ 未找到「📝 执行记录」章节"
