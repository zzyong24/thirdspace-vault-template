"""Article Engine — 文章生成引擎.

从知识卡片、反思、笔记中聚合素材，
为 AI 提供结构化的原材料来生成成型文章。

工具只负责 IO（聚合素材），智能创作交给 AI。
支持通过 prompt_name 引入 Prompt 库中的风格模板。
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class ArticleEngine:
    """文章引擎 — 聚合知识素材生成文章草稿."""

    def __init__(self, context_dir: Path, flux_dir: Path | None = None):
        """初始化.

        Args:
            context_dir: vault/space 目录路径
            flux_dir: vault/flux 目录路径（可选）
        """
        self.context_dir = Path(context_dir)
        self.flux_dir = Path(flux_dir) if flux_dir else self.context_dir.parent / "flux"
        
        # 关键目录
        self.found_dir = self.context_dir / "found"
        self.reflections_dir = self.context_dir / "crafted" / "reflections"
        self.writing_dir = self.context_dir / "crafted" / "writing"
        self.prompts_dir = self.context_dir / "crafted" / "prompts"

    def get_prompt_style(self, prompt_name: str) -> Optional[str]:
        """从 Prompt 库中读取指定风格模板.
        
        Args:
            prompt_name: Prompt 名称，格式为 "category/name" 或 "name"
            
        Returns:
            Prompt 内容，如果不存在则返回 None
        """
        if not prompt_name:
            return None
            
        # 支持 category/name 或直接 name
        if "/" in prompt_name:
            category, name = prompt_name.split("/", 1)
            filepath = self.prompts_dir / category / f"{name}.md"
            if filepath.exists():
                try:
                    return filepath.read_text(encoding="utf-8")
                except Exception:
                    pass
        else:
            # 搜索所有分类
            for cat_dir in self.prompts_dir.iterdir():
                if cat_dir.is_dir():
                    filepath = cat_dir / f"{prompt_name}.md"
                    if filepath.exists():
                        try:
                            return filepath.read_text(encoding="utf-8")
                        except Exception:
                            pass
        return None

    def draft_article(
        self,
        topic: str = "",
        focus: str = "",
        style: str = "insight",
        days: int = 30,
        prompt_name: str = "",
    ) -> dict:
        """聚合相关素材，为 AI 生成文章提供原材料.

        Args:
            topic: 主题过滤（如 reading, ai）
            focus: 关注方向/关键词
            style: 文章风格 (insight | tutorial | story | listicle)
            days: 回溯天数
            prompt_name: 可选的 Prompt 风格模板名称

        Returns:
            dict 包含素材汇总和风格指引
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        result = {
            "topic": topic,
            "focus": focus,
            "style": style,
            "style_description": self._get_style_description(style),
            "knowledge_cards": [],
            "reflections": [],
            "notes": [],
            "related_articles": [],
            "prompt_style": None,
        }
        
        # 1. 聚合知识卡片
        result["knowledge_cards"] = self._gather_knowledge_cards(
            topic=topic, focus=focus, cutoff=cutoff,
        )
        
        # 2. 聚合反思记录
        result["reflections"] = self._gather_reflections(
            focus=focus, cutoff=cutoff,
        )
        
        # 3. 聚合笔记
        result["notes"] = self._gather_notes(
            topic=topic, focus=focus, cutoff=cutoff,
        )
        
        # 4. 查找相关已有文章（避免重复）
        result["related_articles"] = self._find_related_articles(
            topic=topic, focus=focus,
        )
        
        # 5. 读取风格模板
        if prompt_name:
            result["prompt_style"] = self.get_prompt_style(prompt_name)
        
        return result

    def _get_style_description(self, style: str) -> str:
        """获取文章风格的描述."""
        try:
            from ts.prompts import load_prompt
            return load_prompt(f"styles/{style}", skill="article")
        except (FileNotFoundError, ImportError):
            pass
        # Fallback: inline styles
        rich_media_hint = (
            "\n"
            "💡 **富媒体建议**：根据内容需要，可适当使用：\n"
            "  - 图片：`![描述](URL)` 展示示意图、截图、效果图\n"
            "  - Mermaid 图表：流程图 `graph`、数据饼图 `pie`\n"
            "  - LaTeX 公式：行内 `$公式$` 或块级 `$$公式$$`\n"
            "  - 表格：结构化数据对比\n"
            "  - Infographic：数据可视化\n"
            "  *按需使用，不强制，参考：crafted/prompts/tools/markdown-rich-media.md*"
        )
        styles = {
            "insight": (
                "**洞察型**：以观点为核心，论据支撑。\n"
                "- 开头：抛出核心观点或发现\n"
                "- 中间：用案例、数据、引用支撑\n"
                "- 结尾：回归观点，升华意义\n"
                "- 语言：犀利、简洁、有力"
                + rich_media_hint
            ),
            "tutorial": (
                "**教程型**：以实操为核心，步骤清晰。\n"
                "- 开头：说明目标读者和学习收益\n"
                "- 中间：分步骤讲解，配代码/截图\n"
                "- 结尾：总结要点，延伸阅读\n"
                "- 语言：清晰、准确、友好"
                + rich_media_hint
            ),
            "story": (
                "**叙事型**：以经历为核心，观点穿插。\n"
                "- 开头：引入场景，制造共鸣\n"
                "- 中间：时间线叙述，关键节点突出\n"
                "- 结尾：升华主题，引发思考\n"
                "- 语言：生动、真实、有温度"
                + rich_media_hint
            ),
            "listicle": (
                "**清单型**：以要点为核心，并列展开。\n"
                "- 开头：说明清单的价值和适用场景\n"
                "- 中间：N 个并列要点，各自独立成章\n"
                "- 结尾：总结清单，行动号召\n"
                "- 语言：简洁、实用、易扫读"
                + rich_media_hint
            ),
        }
        return styles.get(style, styles["insight"])

    def _gather_knowledge_cards(
        self, topic: str, focus: str, cutoff: datetime,
    ) -> list[dict]:
        """聚合知识卡片."""
        cards = []
        
        if not self.found_dir.exists():
            return cards
            
        # 确定搜索目录
        search_dirs = []
        if topic:
            topic_dir = self.found_dir / topic
            if topic_dir.exists():
                search_dirs.append(topic_dir)
        else:
            for d in self.found_dir.iterdir():
                if d.is_dir():
                    search_dirs.append(d)
        
        for search_dir in search_dirs:
            for md_file in search_dir.rglob("*.md"):
                try:
                    mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                    if mtime < cutoff:
                        continue
                        
                    content = md_file.read_text(encoding="utf-8")
                    
                    # 如果有 focus，检查内容是否相关
                    if focus and focus.lower() not in content.lower():
                        continue
                    
                    # 提取标题
                    title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
                    title = title_match.group(1).strip() if title_match else md_file.stem
                    
                    # 提取摘要
                    summary_match = re.search(
                        r"## 摘要\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL,
                    )
                    summary = summary_match.group(1).strip()[:500] if summary_match else ""
                    
                    # 提取关键要点
                    points_match = re.search(
                        r"## 关键要点\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL,
                    )
                    key_points = []
                    if points_match:
                        items = re.findall(r"^\d+\.\s*(.+)", points_match.group(1), re.MULTILINE)
                        key_points = [item.strip()[:200] for item in items]
                    
                    # 提取思考问题
                    thinking_match = re.search(
                        r"## 深度思考\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL,
                    )
                    thinking = []
                    if thinking_match:
                        items = re.findall(r"^-\s*\[[ x]\]\s*(.+)", thinking_match.group(1), re.MULTILINE)
                        thinking = [item.strip()[:200] for item in items]
                    
                    cards.append({
                        "title": title,
                        "date": mtime.strftime("%Y-%m-%d"),
                        "topic": search_dir.name,
                        "summary": summary,
                        "key_points": key_points,
                        "thinking_questions": thinking,
                        "file_path": str(md_file),
                    })
                except Exception:
                    continue
        
        # 按相关度排序（如果有 focus）
        if focus:
            cards.sort(
                key=lambda x: (
                    focus.lower() in x.get("title", "").lower(),
                    x.get("date", ""),
                ),
                reverse=True,
            )
        else:
            cards.sort(key=lambda x: x.get("date", ""), reverse=True)
            
        return cards[:15]  # 限制数量

    def _gather_reflections(
        self, focus: str, cutoff: datetime,
    ) -> list[dict]:
        """聚合反思记录."""
        reflections = []
        
        if not self.reflections_dir.exists():
            return reflections
            
        for md_file in self.reflections_dir.rglob("*.md"):
            try:
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                if mtime < cutoff:
                    continue
                    
                content = md_file.read_text(encoding="utf-8")
                
                # 如果有 focus，检查相关性
                if focus and focus.lower() not in content.lower():
                    continue
                
                # 提取标题
                title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else md_file.stem
                
                # 提取 Mirror
                mirror_match = re.search(
                    r"## Mirror[^\n]*\n(.*?)(?=\n## |\Z)", content, re.DOTALL,
                )
                mirror = mirror_match.group(1).strip()[:500] if mirror_match else ""
                
                # 提取 Bridge
                bridge_match = re.search(
                    r"## Bridge[^\n]*\n(.*?)(?=\n## |\Z)", content, re.DOTALL,
                )
                bridge = bridge_match.group(1).strip()[:500] if bridge_match else ""
                
                reflections.append({
                    "title": title,
                    "date": mtime.strftime("%Y-%m-%d"),
                    "mirror": mirror,
                    "bridge": bridge,
                    "file_path": str(md_file),
                })
            except Exception:
                continue
        
        reflections.sort(key=lambda x: x.get("date", ""), reverse=True)
        return reflections[:10]

    def _gather_notes(
        self, topic: str, focus: str, cutoff: datetime,
    ) -> list[dict]:
        """聚合笔记."""
        notes = []
        
        # 搜索 crafted 目录下的笔记
        for subdir in self.context_dir.joinpath("crafted").iterdir():
            if not subdir.is_dir():
                continue
            if topic and subdir.name != topic:
                continue
                
            for md_file in subdir.rglob("*.md"):
                # 跳过特定目录
                if any(skip in str(md_file) for skip in ["worklog", "prompts", "reflections", "reviews"]):
                    continue
                    
                try:
                    mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                    if mtime < cutoff:
                        continue
                        
                    content = md_file.read_text(encoding="utf-8")
                    
                    # 如果有 focus，检查相关性
                    if focus and focus.lower() not in content.lower():
                        continue
                    
                    # 提取标题
                    title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
                    title = title_match.group(1).strip() if title_match else md_file.stem
                    
                    # 提取正文摘要（跳过 frontmatter）
                    body_match = re.search(r"^---\s*\n.*?\n---\s*\n(.+)", content, re.DOTALL)
                    if body_match:
                        body = body_match.group(1).strip()[:500]
                    else:
                        body = content[:500]
                    
                    notes.append({
                        "title": title,
                        "date": mtime.strftime("%Y-%m-%d"),
                        "topic": subdir.name,
                        "excerpt": body,
                        "file_path": str(md_file),
                    })
                except Exception:
                    continue
        
        notes.sort(key=lambda x: x.get("date", ""), reverse=True)
        return notes[:10]

    def _find_related_articles(
        self, topic: str, focus: str,
    ) -> list[dict]:
        """查找相关已有文章."""
        articles = []
        
        if not self.writing_dir.exists():
            return articles
            
        for md_file in self.writing_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                
                # 检查相关性
                relevant = False
                if topic and topic.lower() in content.lower():
                    relevant = True
                if focus and focus.lower() in content.lower():
                    relevant = True
                    
                if not relevant:
                    continue
                
                # 提取标题
                title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else md_file.stem
                
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                
                articles.append({
                    "title": title,
                    "date": mtime.strftime("%Y-%m-%d"),
                    "file_path": str(md_file),
                })
            except Exception:
                continue
        
        articles.sort(key=lambda x: x.get("date", ""), reverse=True)
        return articles[:5]

    def save_article(
        self,
        title: str,
        content: str,
        topic: str = "",
        tags: list[str] | None = None,
        sources: list[str] | None = None,
        publish_to: str = "",
    ) -> str:
        """保存文章.

        Args:
            title: 文章标题
            content: 文章内容
            topic: 文章主题
            tags: 标签列表
            sources: 引用源列表（文件路径）
            publish_to: 发布目标（可选：iwiki, wechat_draft）

        Returns:
            保存的文件路径
        """
        self.writing_dir.mkdir(parents=True, exist_ok=True)
        
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # 安全文件名
        safe_title = "".join(
            c if c.isalnum() or c in "_-" or "\u4e00" <= c <= "\u9fff" else "_"
            for c in title
        )[:40]
        filename = f"{date_str}_{safe_title}.md"
        filepath = self.writing_dir / filename
        
        # 避免同名覆盖
        counter = 1
        while filepath.exists():
            filename = f"{date_str}_{safe_title}_{counter}.md"
            filepath = self.writing_dir / filename
            counter += 1
        
        # 构建 tags
        all_tags = ["article"]
        if topic:
            all_tags.append(topic)
        if tags:
            all_tags.extend(t for t in tags if t not in all_tags)
        # 确保包含必要标签
        if "article" not in all_tags:
            all_tags.append("article")
        if "crafted" not in all_tags:
            all_tags.append("crafted")
        tags_str = ", ".join(f'"{t}"' for t in all_tags)
        
        # 构建源引用（使用文件名而非绝对路径）
        source_links = ""
        if sources:
            # 提取文件名（去掉路径，只保留文件名）
            source_names = []
            for s in sources:
                # 如果是绝对路径，提取文件名
                if "/" in s or "\\" in s:
                    source_names.append(Path(s).stem)  # 文件名（不含扩展名）
                else:
                    source_names.append(s)
            source_lines = "\n".join(f'  - "[[{name}]]"' for name in source_names)
            source_links = f"sources:\n{source_lines}"
        
        # 组装最终内容（遵循 vault/README.md 的 Frontmatter 规范）
        lines = [
            "---",
            'type: "article"',
            f'topic: "{topic}"' if topic else 'topic: "writing"',
            f'created: "{time_str}"',
            f'modified: "{time_str}"',
            f"tags: [{tags_str}]",
            'origin: "crafted"',
            'source: "mcp"',
            'status: "active"',
        ]
        if source_links:
            lines.append(source_links)
        if publish_to:
            lines.append(f'publish_to: "{publish_to}"')
        lines.extend([
            "---",
            "",
        ])
        
        # 添加正文
        lines.append(content)
        
        final_content = "\n".join(line for line in lines if line is not None)
        filepath.write_text(final_content, encoding="utf-8")
        
        return str(filepath)

    def list_articles(
        self,
        topic: str = "",
        days: int = 90,
    ) -> list[dict]:
        """列出已有文章.

        Args:
            topic: 主题过滤
            days: 回溯天数

        Returns:
            文章列表
        """
        articles = []
        cutoff = datetime.now() - timedelta(days=days)
        
        if not self.writing_dir.exists():
            return articles
            
        for md_file in self.writing_dir.rglob("*.md"):
            try:
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                if mtime < cutoff:
                    continue
                    
                content = md_file.read_text(encoding="utf-8")
                
                # 提取元数据
                meta = self._parse_frontmatter(content)
                
                # 主题过滤
                if topic and meta.get("topic", "") != topic:
                    continue
                
                # 提取标题
                title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else md_file.stem
                
                articles.append({
                    "title": title,
                    "date": mtime.strftime("%Y-%m-%d"),
                    "topic": meta.get("topic", ""),
                    "tags": meta.get("tags", []),
                    "file_path": str(md_file),
                })
            except Exception:
                continue
        
        articles.sort(key=lambda x: x.get("date", ""), reverse=True)
        return articles

    def _parse_frontmatter(self, content: str) -> dict:
        """简单解析 YAML frontmatter."""
        meta = {}
        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            return meta

        for line in fm_match.group(1).split("\n"):
            line = line.strip()
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            # 简单处理列表
            if value.startswith("[") and value.endswith("]"):
                items = value[1:-1].split(",")
                value = [
                    item.strip().strip('"').strip("'")
                    for item in items
                    if item.strip()
                ]

            meta[key] = value
        return meta
