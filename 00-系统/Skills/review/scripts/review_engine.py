"""Review Engine — 周/月复盘引擎.

全量扫描 vault 中所有 .md 文件，按 Frontmatter 中的 created/modified
时间戳筛选目标周期内的文件，按 type/topic 自动分类聚合。

**设计哲学：不硬编码任何目录列表，新增 topic/type 自动被覆盖。**

工具只负责 IO（聚合数据），智能分析交给 AI。
支持通过 prompt_name 引入 Prompt 库中的风格模板。
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import yaml


# 不需要出现在周报素材中的文件类型/路径
_SKIP_PATTERNS = {
    "README.md", "INDEX.md", "daily-template.md",
}

# 文件类型的展示名称和图标
_TYPE_DISPLAY = {
    "reflection": ("💭", "深度反思"),
    "card": ("📚", "知识卡片"),
    "note": ("📝", "笔记"),
    "worklog": ("📋", "工作日志"),
    "article": ("✍️", "文章"),
    "plan": ("🚀", "学习计划"),
    "event": ("📌", "LifeOS 事件"),
    "tracker": ("📊", "创作追踪"),
    "project": ("🏗️", "项目文档"),
    "prompt": ("🤖", "Prompt"),
    "review": ("📅", "复盘"),
}

# topic 展示名
_TOPIC_DISPLAY = {
    "creation": "🎬 创作",
    "reading": "📖 阅读",
    "thinking": "🧠 思维",
    "practice": "⚡ 实践",
    "wellness": "🧘 身心",
    "work": "💼 工作",
    "dev": "💻 开发",
    "product": "📱 产品",
    "business": "💰 商业",
    "market": "📣 营销",
    "AI": "🤖 AI",
}


class ReviewEngine:
    """复盘引擎 — 全量扫描 vault，按时间范围聚合所有内容."""

    def __init__(self, context_dir: Path, flux_dir: Path | None = None):
        """初始化.

        Args:
            context_dir: vault/space 目录路径
            flux_dir: vault/flux 目录路径（可选）
        """
        self.context_dir = Path(context_dir)
        self.flux_dir = Path(flux_dir) if flux_dir else self.context_dir.parent / "flux"

        # 关键目录（仅用于保存和特殊查询）
        self.prompts_dir = self.context_dir / "crafted" / "prompts"
        self.reviews_dir = self.context_dir / "crafted" / "reviews"
        self.worklog_dir = self.context_dir / "crafted" / "work" / "worklog"

    def get_real_date(self) -> datetime:
        """通过系统命令获取真实日期."""
        try:
            result = subprocess.run(
                ["date", "+%Y-%m-%d"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                return datetime.strptime(result.stdout.strip(), "%Y-%m-%d")
        except Exception:
            pass
        return datetime.now()

    def get_prompt_style(self, prompt_name: str) -> Optional[str]:
        """从 Prompt 库中读取指定风格模板.

        Args:
            prompt_name: Prompt 名称，格式为 "category/name" 或 "name"

        Returns:
            Prompt 内容，如果不存在则返回 None
        """
        if not prompt_name:
            return None

        filepath = None
        # 支持 category/name 或直接 name
        if "/" in prompt_name:
            category, name = prompt_name.split("/", 1)
            filepath = self.prompts_dir / category / f"{name}.md"
        else:
            # 搜索所有分类
            if self.prompts_dir.exists():
                for cat_dir in self.prompts_dir.iterdir():
                    if cat_dir.is_dir():
                        candidate = cat_dir / f"{prompt_name}.md"
                        if candidate.exists():
                            filepath = candidate
                            break

        if filepath and filepath.exists():
            try:
                return filepath.read_text(encoding="utf-8")
            except Exception:
                pass
        return None

    # ─────────────────────────────────────────────────
    # 核心：全量扫描
    # ─────────────────────────────────────────────────

    def _parse_frontmatter(self, content: str) -> dict:
        """解析 Markdown 文件的 YAML Frontmatter.

        Returns:
            dict，解析失败则返回空 dict
        """
        if not content.startswith("---"):
            return {}
        end = content.find("---", 3)
        if end == -1:
            return {}
        try:
            fm = yaml.safe_load(content[3:end])
            return fm if isinstance(fm, dict) else {}
        except Exception:
            return {}

    def _parse_datetime(self, value) -> Optional[datetime]:
        """将 Frontmatter 中的时间值转为 datetime."""
        if isinstance(value, datetime):
            return value
        if not isinstance(value, str):
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(value.strip('"').strip("'"), fmt)
            except ValueError:
                continue
        return None

    def _extract_title(self, content: str, stem: str) -> str:
        """从内容中提取标题."""
        match = re.search(r"^# (.+)$", content, re.MULTILINE)
        return match.group(1).strip() if match else stem

    def _extract_summary(self, content: str, file_type: str) -> str:
        """从内容中提取摘要（根据类型使用不同策略）."""
        # 反思：提取 Mirror 章节
        if file_type == "reflection":
            match = re.search(
                r"## Mirror[^\n]*\n(.*?)(?=\n## |\Z)", content, re.DOTALL,
            )
            if match:
                return match.group(1).strip()[:500]

        # 知识卡片：提取摘要章节
        if file_type == "card":
            match = re.search(
                r"## 摘要\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL,
            )
            if match:
                return match.group(1).strip()[:300]

        # 工作日志：提取重点
        if file_type == "worklog":
            return self._extract_worklog_highlights_text(content)

        # 通用：取 Frontmatter 之后、第一个 ## 之前的内容
        body = content
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                body = content[end + 3:].strip()
        # 跳过标题行
        lines = body.split("\n")
        summary_lines = []
        for line in lines:
            if line.startswith("# "):
                continue
            if line.startswith("## "):
                break
            stripped = line.strip()
            if stripped:
                summary_lines.append(stripped)
            if len(summary_lines) >= 3:
                break
        return " ".join(summary_lines)[:300]

    def _extract_worklog_highlights_text(self, content: str) -> str:
        """从工作日志中提取重点记录文本."""
        highlights = []

        for section_name in ("重点记录", "今日工作内容"):
            match = re.search(
                rf"## {section_name}[^\n]*\n(.*?)(?=\n## |\Z)",
                content, re.DOTALL,
            )
            if match:
                items = re.findall(r"^- (.+)", match.group(1), re.MULTILINE)
                highlights.extend(
                    item.strip()[:100] for item in items if item.strip()
                )

        return "; ".join(highlights[:8])

    def _should_skip(self, md_file: Path) -> bool:
        """判断文件是否应跳过."""
        if md_file.name in _SKIP_PATTERNS:
            return True
        # 跳过 .obsidian / .trash 等隐藏目录下的文件
        for part in md_file.parts:
            if part.startswith("."):
                return True
        return False

    def _scan_vault_files(
        self,
        start: datetime,
        end: datetime,
    ) -> list[dict]:
        """全量扫描 vault/space 下所有 .md 文件，返回时间范围内的条目.

        筛选逻辑（优先级）：
        1. 优先使用 Frontmatter 中的 created 字段
        2. 备用 modified 字段
        3. 最后使用文件系统的 mtime

        Returns:
            list[dict]，每个 dict 包含文件元信息和摘要
        """
        items = []
        # 扩展 end 到当天 23:59:59
        end_inclusive = end.replace(hour=23, minute=59, second=59)

        # 扫描 space/crafted 和 space/found
        scan_dirs = []
        crafted_dir = self.context_dir / "crafted"
        found_dir = self.context_dir / "found"
        if crafted_dir.exists():
            scan_dirs.append(crafted_dir)
        if found_dir.exists():
            scan_dirs.append(found_dir)

        for base_dir in scan_dirs:
            origin = "crafted" if "crafted" in str(base_dir) else "found"

            for md_file in base_dir.rglob("*.md"):
                if self._should_skip(md_file):
                    continue

                try:
                    content = md_file.read_text(encoding="utf-8")
                except Exception:
                    continue

                fm = self._parse_frontmatter(content)

                # 确定时间
                file_date = None
                for field in ("created", "modified"):
                    dt = self._parse_datetime(fm.get(field))
                    if dt:
                        file_date = dt
                        break
                if file_date is None:
                    # 从文件名提取日期（如 20260318_xxx.md 或 2026-03-18-xxx.md）
                    date_match = re.match(
                        r"(\d{4})[-_]?(\d{2})[-_]?(\d{2})", md_file.stem,
                    )
                    if date_match:
                        try:
                            file_date = datetime(
                                int(date_match.group(1)),
                                int(date_match.group(2)),
                                int(date_match.group(3)),
                            )
                        except ValueError:
                            pass
                if file_date is None:
                    # 最后用文件系统 mtime
                    file_date = datetime.fromtimestamp(md_file.stat().st_mtime)

                if not (start <= file_date <= end_inclusive):
                    continue

                # 确定类型
                file_type = fm.get("type", "")
                if not file_type:
                    # 根据路径推断类型
                    rel = md_file.relative_to(base_dir)
                    parts = rel.parts
                    if origin == "found":
                        file_type = "card"
                    elif "reflections" in parts:
                        file_type = "reflection"
                    elif "worklog" in parts:
                        file_type = "worklog"
                    elif "reviews" in parts:
                        file_type = "review"
                    elif "prompts" in parts:
                        file_type = "prompt"
                    elif "tracker" in parts:
                        file_type = "tracker"
                    elif "plans" in parts:
                        file_type = "plan"
                    elif "writing" in parts:
                        file_type = "article"
                    elif "lifeos" in parts and "events" in parts:
                        file_type = "event"
                    elif "project" in parts:
                        file_type = "project"
                    else:
                        file_type = "note"

                # 确定 topic
                topic = fm.get("topic", "")
                if not topic:
                    # 根据路径推断 topic
                    rel = md_file.relative_to(base_dir)
                    parts = rel.parts
                    if len(parts) >= 2:
                        # crafted/{topic}/... 或 found/{topic}/...
                        candidate = parts[0]
                        # 跳过一些特殊目录
                        if candidate not in ("work", "lifeos", "prompts"):
                            topic = candidate
                        elif candidate == "work":
                            topic = "work"
                        elif candidate == "lifeos":
                            topic = "lifeos"
                        elif candidate == "prompts":
                            topic = "prompts"
                    else:
                        topic = "other"

                # 标准化 topic：复数目录名归一化
                _topic_normalize = {
                    "reflections": "reflection",
                    "reviews": "review",
                    "actions": "action",
                }
                topic = _topic_normalize.get(topic, topic)

                # 跳过已有的周/月报文件（不把自身纳入素材）
                if file_type == "review":
                    continue

                title = self._extract_title(content, md_file.stem)
                summary = self._extract_summary(content, file_type)
                tags = fm.get("tags", [])
                if isinstance(tags, str):
                    tags = [t.strip() for t in tags.split(",")]

                items.append({
                    "title": title,
                    "type": file_type,
                    "topic": topic,
                    "origin": origin,
                    "date": file_date.strftime("%Y-%m-%d"),
                    "datetime": file_date,
                    "summary": summary,
                    "tags": tags,
                    "file_path": str(md_file),
                    "file_name": md_file.name,
                })

        # 按日期倒序排列
        items.sort(key=lambda x: x["datetime"], reverse=True)
        return items

    def _group_by_type(self, items: list[dict]) -> dict[str, list[dict]]:
        """按 type 分组."""
        groups: dict[str, list[dict]] = {}
        for item in items:
            t = item["type"]
            groups.setdefault(t, []).append(item)
        return groups

    def _group_by_topic(self, items: list[dict]) -> dict[str, list[dict]]:
        """按 topic 分组."""
        groups: dict[str, list[dict]] = {}
        for item in items:
            t = item["topic"]
            groups.setdefault(t, []).append(item)
        return groups

    def _calc_stats(self, items: list[dict]) -> dict:
        """计算统计概览."""
        type_counts: dict[str, int] = {}
        topic_counts: dict[str, int] = {}
        origin_counts = {"crafted": 0, "found": 0}

        for item in items:
            type_counts[item["type"]] = type_counts.get(item["type"], 0) + 1
            topic_counts[item["topic"]] = topic_counts.get(item["topic"], 0) + 1
            origin_counts[item["origin"]] = origin_counts.get(item["origin"], 0) + 1

        return {
            "total": len(items),
            "by_type": dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True)),
            "by_topic": dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)),
            "crafted_count": origin_counts["crafted"],
            "found_count": origin_counts["found"],
        }

    # ─────────────────────────────────────────────────
    # 公开方法：weekly / monthly
    # ─────────────────────────────────────────────────

    def weekly_review(
        self,
        week_offset: int = 0,
        prompt_name: str = "",
    ) -> dict:
        """聚合本周数据，返回给 AI 生成周报.

        扫描 vault/space 下所有 .md 文件，按 created/modified 时间筛选
        本周范围内的内容，自动分类返回。

        Args:
            week_offset: 周偏移量，0 表示本周，-1 表示上周
            prompt_name: 可选的 Prompt 风格模板名称

        Returns:
            dict 包含本周所有内容的分类汇总
        """
        today = self.get_real_date()

        # 计算周的起止日期（周一到周日）
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday + (-week_offset * 7))
        week_end = week_start + timedelta(days=6)

        # 格式化周数
        week_number = week_start.isocalendar()[1]
        year = week_start.year
        week_label = f"{year}-W{week_number:02d}"

        # 全量扫描
        all_items = self._scan_vault_files(week_start, week_end)

        result = {
            "week_label": week_label,
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "stats": self._calc_stats(all_items),
            "items_by_type": self._group_by_type(all_items),
            "items_by_topic": self._group_by_topic(all_items),
            "all_items": all_items,
            "prompt_style": None,
        }

        # 读取风格模板
        if prompt_name:
            result["prompt_style"] = self.get_prompt_style(prompt_name)

        return result

    def monthly_review(
        self,
        month_offset: int = 0,
        prompt_name: str = "",
    ) -> dict:
        """聚合本月数据，返回给 AI 生成月报.

        Args:
            month_offset: 月偏移量，0 表示本月，-1 表示上月
            prompt_name: 可选的 Prompt 风格模板名称

        Returns:
            dict 包含本月所有内容的分类汇总
        """
        today = self.get_real_date()

        # 计算月的起止日期
        target_month = today.month + month_offset
        target_year = today.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        while target_month > 12:
            target_month -= 12
            target_year += 1

        month_start = datetime(target_year, target_month, 1)
        if target_month == 12:
            month_end = datetime(target_year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(target_year, target_month + 1, 1) - timedelta(days=1)

        month_label = month_start.strftime("%Y-%m")

        # 全量扫描
        all_items = self._scan_vault_files(month_start, month_end)

        # 聚合已有周报摘要
        weekly_summaries = self._gather_weekly_summaries(month_start, month_end)

        result = {
            "month_label": month_label,
            "month_start": month_start.strftime("%Y-%m-%d"),
            "month_end": month_end.strftime("%Y-%m-%d"),
            "stats": self._calc_stats(all_items),
            "items_by_type": self._group_by_type(all_items),
            "items_by_topic": self._group_by_topic(all_items),
            "all_items": all_items,
            "weekly_summaries": weekly_summaries,
            "prompt_style": None,
        }

        if prompt_name:
            result["prompt_style"] = self.get_prompt_style(prompt_name)

        return result

    def _gather_weekly_summaries(self, start: datetime, end: datetime) -> list[dict]:
        """聚合指定日期范围内的周报摘要."""
        summaries = []

        if not self.reviews_dir.exists():
            return summaries

        end_inclusive = end.replace(hour=23, minute=59, second=59)

        for md_file in self.reviews_dir.glob("weekly_*.md"):
            try:
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                if not (start <= mtime <= end_inclusive):
                    continue

                content = md_file.read_text(encoding="utf-8")

                title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else md_file.stem

                highlights_match = re.search(
                    r"## 本周亮点\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL,
                )
                highlights = highlights_match.group(1).strip()[:500] if highlights_match else ""

                summaries.append({
                    "title": title,
                    "date": mtime.strftime("%Y-%m-%d"),
                    "highlights": highlights,
                    "file_path": str(md_file),
                })
            except Exception:
                continue

        summaries.sort(key=lambda x: x["date"])
        return summaries

    # ─────────────────────────────────────────────────
    # 保存方法（不变）
    # ─────────────────────────────────────────────────

    def save_weekly_review(
        self,
        week_label: str,
        highlights: list[str],
        knowledge_summary: str,
        practice_progress: str,
        insights: str,
        next_focus: list[str],
        content: str = "",
    ) -> str:
        """保存周报.

        Args:
            week_label: 周标签（如 2026-W11）
            highlights: 本周亮点列表
            knowledge_summary: 知识摄入总结
            practice_progress: 实践进度
            insights: 思考沉淀
            next_focus: 下周聚焦
            content: 完整内容（可选，用于自定义格式）

        Returns:
            保存的文件路径
        """
        self.reviews_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now()
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")

        filename = f"weekly_{week_label}.md"
        filepath = self.reviews_dir / filename

        if content:
            final_content = content
        else:
            lines = [
                "---",
                'type: "review"',
                'topic: "work"',
                f'created: "{time_str}"',
                f'modified: "{time_str}"',
                'tags: ["review", "weekly", "work", "crafted"]',
                'origin: "crafted"',
                'source: "mcp"',
                'status: "active"',
                f'week: "{week_label}"',
                "---",
                "",
                f"# 周报：{week_label}",
                "",
                "## 本周亮点",
                "",
            ]
            for h in highlights:
                lines.append(f"- {h}")
            lines.extend([
                "",
                "## 知识摄入",
                "",
                knowledge_summary,
                "",
                "## 实践进度",
                "",
                practice_progress,
                "",
                "## 思考沉淀",
                "",
                insights,
                "",
                "## 下周聚焦",
                "",
            ])
            for f in next_focus:
                lines.append(f"- [ ] {f}")
            lines.extend([
                "",
                "---",
                "",
                f"*生成于 {time_str}*",
            ])
            final_content = "\n".join(lines)

        filepath.write_text(final_content, encoding="utf-8")
        return str(filepath)

    def save_monthly_review(
        self,
        month_label: str,
        theme: str,
        achievements: list[str],
        knowledge_graph: str,
        growth_track: str,
        next_okr: list[str],
        content: str = "",
    ) -> str:
        """保存月报.

        Args:
            month_label: 月标签（如 2026-03）
            theme: 本月主题
            achievements: 主要成就
            knowledge_graph: 知识图谱变化
            growth_track: 成长轨迹
            next_okr: 下月 OKR
            content: 完整内容（可选）

        Returns:
            保存的文件路径
        """
        self.reviews_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now()
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")

        filename = f"monthly_{month_label}.md"
        filepath = self.reviews_dir / filename

        if content:
            final_content = content
        else:
            lines = [
                "---",
                'type: "review"',
                'topic: "work"',
                f'created: "{time_str}"',
                f'modified: "{time_str}"',
                'tags: ["review", "monthly", "work", "crafted"]',
                'origin: "crafted"',
                'source: "mcp"',
                'status: "active"',
                f'month: "{month_label}"',
                "---",
                "",
                f"# 月报：{month_label}",
                "",
                "## 本月主题",
                "",
                theme,
                "",
                "## 主要成就",
                "",
            ]
            for a in achievements:
                lines.append(f"- {a}")
            lines.extend([
                "",
                "## 知识图谱变化",
                "",
                knowledge_graph,
                "",
                "## 成长轨迹",
                "",
                growth_track,
                "",
                "## 下月 OKR",
                "",
            ])
            for o in next_okr:
                lines.append(f"- [ ] {o}")
            lines.extend([
                "",
                "---",
                "",
                f"*生成于 {time_str}*",
            ])
            final_content = "\n".join(lines)

        filepath.write_text(final_content, encoding="utf-8")
        return str(filepath)

    def save_weekly_review(
        self,
        week_label: str,
        highlights: list[str],
        knowledge_summary: str,
        practice_progress: str,
        insights: str,
        next_focus: list[str],
        content: str = "",
    ) -> str:
        """保存周报.

        Args:
            week_label: 周标签（如 2026-W11）
            highlights: 本周亮点列表
            knowledge_summary: 知识摄入总结
            practice_progress: 实践进度
            insights: 思考沉淀
            next_focus: 下周聚焦
            content: 完整内容（可选，用于自定义格式）

        Returns:
            保存的文件路径
        """
        self.reviews_dir.mkdir(parents=True, exist_ok=True)
        
        now = datetime.now()
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        filename = f"weekly_{week_label}.md"
        filepath = self.reviews_dir / filename
        
        if content:
            # 使用自定义内容
            final_content = content
        else:
            # 使用模板生成（遵循 vault/README.md 的 Frontmatter 规范）
            lines = [
                "---",
                'type: "review"',
                'topic: "work"',
                f'created: "{time_str}"',
                f'modified: "{time_str}"',
                'tags: ["review", "weekly", "work", "crafted"]',
                'origin: "crafted"',
                'source: "mcp"',
                'status: "active"',
                f'week: "{week_label}"',
                "---",
                "",
                f"# 周报：{week_label}",
                "",
                "## 本周亮点",
                "",
            ]
            for h in highlights:
                lines.append(f"- {h}")
            lines.extend([
                "",
                "## 知识摄入",
                "",
                knowledge_summary,
                "",
                "## 实践进度",
                "",
                practice_progress,
                "",
                "## 思考沉淀",
                "",
                insights,
                "",
                "## 下周聚焦",
                "",
            ])
            for f in next_focus:
                lines.append(f"- [ ] {f}")
            lines.extend([
                "",
                "---",
                "",
                f"*生成于 {time_str}*",
            ])
            final_content = "\n".join(lines)
        
        filepath.write_text(final_content, encoding="utf-8")
        return str(filepath)

    def save_monthly_review(
        self,
        month_label: str,
        theme: str,
        achievements: list[str],
        knowledge_graph: str,
        growth_track: str,
        next_okr: list[str],
        content: str = "",
    ) -> str:
        """保存月报.

        Args:
            month_label: 月标签（如 2026-03）
            theme: 本月主题
            achievements: 主要成就
            knowledge_graph: 知识图谱变化
            growth_track: 成长轨迹
            next_okr: 下月 OKR
            content: 完整内容（可选）

        Returns:
            保存的文件路径
        """
        self.reviews_dir.mkdir(parents=True, exist_ok=True)
        
        now = datetime.now()
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        filename = f"monthly_{month_label}.md"
        filepath = self.reviews_dir / filename
        
        if content:
            final_content = content
        else:
            # 遵循 vault/README.md 的 Frontmatter 规范
            lines = [
                "---",
                'type: "review"',
                'topic: "work"',
                f'created: "{time_str}"',
                f'modified: "{time_str}"',
                'tags: ["review", "monthly", "work", "crafted"]',
                'origin: "crafted"',
                'source: "mcp"',
                'status: "active"',
                f'month: "{month_label}"',
                "---",
                "",
                f"# 月报：{month_label}",
                "",
                "## 本月主题",
                "",
                theme,
                "",
                "## 主要成就",
                "",
            ]
            for a in achievements:
                lines.append(f"- {a}")
            lines.extend([
                "",
                "## 知识图谱变化",
                "",
                knowledge_graph,
                "",
                "## 成长轨迹",
                "",
                growth_track,
                "",
                "## 下月 OKR",
                "",
            ])
            for o in next_okr:
                lines.append(f"- [ ] {o}")
            lines.extend([
                "",
                "---",
                "",
                f"*生成于 {time_str}*",
            ])
            final_content = "\n".join(lines)
        
        filepath.write_text(final_content, encoding="utf-8")
        return str(filepath)
