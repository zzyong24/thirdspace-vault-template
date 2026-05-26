"""Reflect Engine — 深度反思引擎.

从知识卡片中提取用户已回答的深度思考内容，
为 AI 提供结构化的素材来生成反思反馈。
新增：同时扫描用户的实际工作产出（voiceover/tutorial/writing），
让反思基于具体作品而非抽象记忆。

工具只负责 IO（读取/保存），智能分析交给 AI。
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class ReflectEngine:
    """反思引擎 — 读取知识卡片中的深度思考回答."""

    def __init__(self, context_dir: Path):
        """初始化.

        Args:
            context_dir: vault/space 目录路径
        """
        self.context_dir = Path(context_dir)
        self.reflections_dir = self.context_dir / "crafted" / "reflections"
        # Vault 根目录是 context_dir 的父目录（即 ThirdSpace/）
        self.vault_root = self.context_dir.parent

    def _to_vault_relative_path(self, path: str) -> str:
        """将路径转换为相对于 Vault 根目录的相对路径.

        Args:
            path: 输入路径（可能是绝对路径或相对路径）

        Returns:
            相对于 Vault 根目录的路径（用于 Obsidian 双向链接）
        """
        p = Path(path)

        # 如果已经是相对路径，检查是否需要调整
        if not p.is_absolute():
            # 如果路径以 space/ 开头，去掉它（因为 Vault 根在 space 的父目录）
            parts = p.parts
            if parts and parts[0] == "space":
                return str(Path(*parts[1:]))
            # 如果路径以 vault/ 开头，去掉它
            if parts and parts[0] == "vault":
                return str(Path(*parts[1:]))
            return str(p)

        # 绝对路径：尝试转换为相对路径
        try:
            rel = p.relative_to(self.vault_root)
            return str(rel)
        except ValueError:
            pass

        # 如果不在 vault_root 下，尝试其他常见前缀
        for prefix in [self.context_dir, self.context_dir.parent]:
            try:
                rel = p.relative_to(prefix)
                return str(rel)
            except ValueError:
                continue

        # 无法转换，返回原始文件名
        return p.name

    def _resolve_path(
        self, file_path: str, extra_dirs: list[Path] | None = None
    ) -> Optional[Path]:
        """通用路径解析：尝试多种方式定位文件.

        支持的路径格式：
        - 绝对路径
        - 相对于 context_dir (vault/space) 的路径，如 found/reading/...
        - 带 space/ 前缀的路径，如 space/found/reading/...
        - 相对于 vault 根目录的路径
        - 相对于 extra_dirs 的路径（如 reflections_dir）
        - 相对于 cwd 的路径

        Returns:
            解析后的绝对路径，找不到则返回 None
        """
        fp = Path(file_path)
        candidates = [fp]
        if not fp.is_absolute():
            # 额外搜索目录（如 reflections_dir）
            if extra_dirs:
                for d in extra_dirs:
                    candidates.append(d / fp)
            # context_dir (vault/space)
            candidates.append(self.context_dir / fp)
            # 兼容带 space/ 前缀的路径：context_dir 已经是 .../space，
            # 如果 file_path 以 space/ 开头则去掉前缀再拼接
            fp_str = str(fp)
            if fp_str.startswith("space/") or fp_str.startswith("space\\"):
                candidates.append(self.context_dir / fp_str[len("space/"):])
            # vault 根目录
            vault_dir = self.context_dir.parent
            candidates.append(vault_dir / fp)
            # cwd
            candidates.append(Path.cwd() / fp)

        for candidate in candidates:
            resolved = candidate.resolve()
            if resolved.exists():
                return resolved
        return None

    def scan_recent_work(self, days: int = 14) -> dict:
        """扫描用户最近的实际工作产出（voiceover/tutorial/writing）。

        这些内容让 AI 在生成反思时能结合用户的具体作品，
        而不是只基于抽象的 Q&A 回答。

        Args:
            days: 回溯天数，默认 14 天

        Returns:
            dict 包含各类作品的统计和摘要
        """
        cutoff = datetime.now() - timedelta(days=days)

        work_dirs = {
            "voiceover": self.context_dir / "crafted" / "voiceover",
            "my_tutorial": self.context_dir / "crafted" / "my-tutorial",
            "writing": self.context_dir / "crafted" / "writing",
        }

        result = {}

        for key, work_dir in work_dirs.items():
            if not work_dir.exists():
                continue

            files = []
            for md_file in work_dir.rglob("*.md"):
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                if mtime < cutoff:
                    continue
                try:
                    content = md_file.read_text(encoding="utf-8")
                    # 提取标题（第一个 # 开头的内容）
                    title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
                    title = title_match.group(1).strip() if title_match else md_file.stem
                    # 提取开头 300 字作为摘要
                    body = re.sub(r"^#.*$", "", content, flags=re.MULTILINE).strip()
                    summary = body[:300] if body else "(无正文内容)"
                    files.append({
                        "name": md_file.name,
                        "title": title,
                        "summary": summary,
                        "mtime": mtime.isoformat(),
                    })
                except Exception:
                    continue

            # 按修改时间倒序
            files.sort(key=lambda f: f["mtime"], reverse=True)
            result[key] = {
                "dir": str(work_dir.relative_to(self.context_dir)),
                "count": len(files),
                "files": files[:5],  # 最多取 5 个
            }

        return result

    def gather_reflections(
        self,
        topic: Optional[str] = None,
        days: int = 7,
        file_path: Optional[str] = None,
        include_work: bool = True,
    ) -> dict:
        """采集用户已回答的深度思考内容.

        Args:
            topic: 主题过滤（如 reading），不指定则扫描所有
            days: 回溯天数，默认 7 天
            file_path: 指定单个文件路径（优先级最高）
            include_work: 是否同时扫描用户的工作产出（voiceover/tutorial/writing）

        Returns:
            dict 包含 cards 列表、统计信息、以及可选的工作产出摘要
        """
        cards = []

        if file_path:
            # 指定单个文件：通用路径解析
            resolved = self._resolve_path(file_path)
            if resolved:
                card = self._parse_card(resolved)
                if card and card["answered_questions"]:
                    cards.append(card)
        else:
            # 扫描 found 目录
            search_dirs = []
            if topic:
                search_dirs.append(self.context_dir / "found" / topic)
            else:
                found_dir = self.context_dir / "found"
                if found_dir.exists():
                    for d in found_dir.iterdir():
                        if d.is_dir():
                            search_dirs.append(d)

            cutoff = datetime.now() - timedelta(days=days)

            for search_dir in search_dirs:
                if not search_dir.exists():
                    continue
                for md_file in search_dir.rglob("*.md"):
                    # 检查时间范围
                    mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                    if mtime < cutoff:
                        continue
                    card = self._parse_card(md_file)
                    if card and card["answered_questions"]:
                        cards.append(card)

        # 按创建时间倒序
        cards.sort(key=lambda c: c.get("created", ""), reverse=True)

        result = {
            "cards": cards,
            "total_cards": len(cards),
            "total_answered": sum(len(c["answered_questions"]) for c in cards),
            "total_unanswered": sum(len(c["unanswered_questions"]) for c in cards),
        }

        # 附加：扫描用户最近的工作产出
        if include_work:
            result["work"] = self.scan_recent_work(days=14)

        return result

    def _parse_card(self, filepath: Path) -> Optional[dict]:
        """解析单个知识卡片，提取深度思考部分.

        Returns:
            解析后的卡片字典，包含元数据和问答内容；
            如果没有深度思考部分则返回 None
        """
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception:
            return None

        # 解析 frontmatter
        meta = self._parse_frontmatter(content)

        # 提取标题
        title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else filepath.stem

        # 提取摘要
        summary = self._extract_section(content, "摘要")

        # 提取关键要点
        key_points = self._extract_section(content, "关键要点")

        # 提取深度思考部分
        thinking_section = self._extract_section(content, "深度思考")
        if not thinking_section:
            return None

        # 解析已回答和未回答的问题
        answered = []
        unanswered = []
        self._parse_questions(thinking_section, answered, unanswered)

        if not answered and not unanswered:
            return None

        # 计算相对路径
        try:
            rel_path = filepath.relative_to(self.context_dir)
        except ValueError:
            rel_path = filepath.name

        return {
            "file_path": str(filepath),
            "relative_path": str(rel_path),
            "title": title,
            "created": meta.get("created", ""),
            "tags": meta.get("tags", []),
            "source": meta.get("source", ""),
            "author": meta.get("author", ""),
            "url": meta.get("url", ""),
            "summary": summary,
            "key_points": key_points,
            "answered_questions": answered,
            "unanswered_questions": unanswered,
        }

    def _parse_questions(
        self, section: str, answered: list, unanswered: list
    ) -> None:
        """解析深度思考部分的问题和回答.

        支持格式：
        - [x] 问题文本
              回答内容（缩进行）
        - [ ] 未回答的问题
        """
        lines = section.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]

            # 匹配 checkbox 行
            checked = re.match(r"^-\s*\[x\]\s*(.+)$", line, re.IGNORECASE)
            unchecked = re.match(r"^-\s*\[\s*\]\s*(.+)$", line)

            if checked:
                question = checked.group(1).strip()
                # 收集后续缩进行作为回答
                answer_lines = []
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    # 缩进行（至少有空格/tab 前缀）或者空行
                    if next_line and (
                        next_line.startswith("      ")
                        or next_line.startswith("\t")
                    ):
                        answer_lines.append(next_line.strip())
                        i += 1
                    elif next_line.strip() == "":
                        i += 1
                        # 空行后如果下一行还是缩进，继续收集
                        if i < len(lines) and (
                            lines[i].startswith("      ")
                            or lines[i].startswith("\t")
                        ):
                            continue
                        else:
                            break
                    else:
                        break
                answered.append({
                    "question": question,
                    "answer": "\n".join(answer_lines) if answer_lines else "(已勾选但无文字回答)",
                })
            elif unchecked:
                question = unchecked.group(1).strip()
                unanswered.append({"question": question})
                i += 1
            else:
                i += 1

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

    def _extract_section(self, content: str, heading: str) -> str:
        """提取指定二级标题下的内容."""
        pattern = rf"^## {re.escape(heading)}\s*\n(.*?)(?=\n## |\n---|\Z)"
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        return match.group(1).strip() if match else ""

    def save_reflection(
        self,
        title: str,
        mirror: str,
        deepen: str,
        bridge: str,
        source_cards: list[str],
        growth_track: str = "",
        tags: list[str] | None = None,
    ) -> str:
        """保存反思内容到 crafted/reflections/ 目录.

        Args:
            title: 反思标题
            mirror: Mirror（认知照镜）部分内容
            deepen: Deepen（深度追问）部分内容
            bridge: Bridge（行动搭桥）部分内容
            source_cards: 源卡片相对路径列表
            growth_track: 成长轨迹内容（可选）
            tags: 标签列表（可选）

        Returns:
            保存的文件路径
        """
        self.reflections_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")

        safe_title = "".join(
            c if c.isalnum() or c in "_-" or "\u4e00" <= c <= "\u9fff" else "_"
            for c in title
        )[:40]
        filename = f"reflect_{date_str}_{safe_title}.md"
        filepath = self.reflections_dir / filename

        # 避免同名覆盖
        counter = 1
        while filepath.exists():
            filename = f"reflect_{date_str}_{safe_title}_{counter}.md"
            filepath = self.reflections_dir / filename
            counter += 1

        # 构建 tags
        all_tags = ["reflection", "crafted"]
        if tags:
            all_tags.extend(t for t in tags if t not in all_tags)
        tags_str = ", ".join(f'"{t}"' for t in all_tags)

        # 构建源卡片链接（转换为 Vault 相对路径）
        relative_cards = [self._to_vault_relative_path(p) for p in source_cards]
        source_links = "\n".join(f'  - "[[{p}]]"' for p in relative_cards)

        # 组装 Markdown（遵循 vault/README.md 的 Frontmatter 规范）
        lines = [
            "---",
            'type: "reflection"',
            'topic: "reflection"',
            f'created: "{time_str}"',
            f'modified: "{time_str}"',
            f"tags: [{tags_str}]",
            'origin: "crafted"',
            'source: "mcp"',
            'status: "active"',
            "source_cards:",
            source_links,
            "---",
            "",
            f"# 反思：{title}",
            "",
            "## Mirror — 认知照镜",
            "",
            mirror,
            "",
            "## Deepen — 深度追问",
            "",
            deepen,
            "",
            "## Bridge — 行动搭桥",
            "",
            bridge,
        ]

        if growth_track:
            lines.extend([
                "",
                "## 成长轨迹",
                "",
                growth_track,
            ])

        lines.extend([
            "",
            "---",
            "",
            f"*反思于 {time_str}*",
            "",
        ])

        filepath.write_text("\n".join(lines), encoding="utf-8")
        return str(filepath)

    def gather_reflection_closure(
        self,
        file_path: str,
    ) -> Optional[dict]:
        """读取反思文件中 Deepen 追问的用户回答，为闭环点评提供素材.

        Args:
            file_path: 反思文件路径

        Returns:
            dict 包含反思原文各章节和用户对追问的回答；
            如果没有找到已回答的追问则返回 None
        """
        resolved_path = self._resolve_path(
            file_path, extra_dirs=[self.reflections_dir]
        )
        if resolved_path is None:
            return None

        try:
            content = resolved_path.read_text(encoding="utf-8")
        except Exception:
            return None

        meta = self._parse_frontmatter(content)

        # 提取标题
        title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else resolved_path.stem

        # 提取各章节
        mirror = self._extract_section(content, "Mirror — 认知照镜")
        deepen = self._extract_section(content, "Deepen — 深度追问")
        bridge = self._extract_section(content, "Bridge — 行动搭桥")
        growth_track = self._extract_section(content, "成长轨迹")

        if not deepen:
            return None

        # 解析 Deepen 中已回答和未回答的追问
        answered = []
        unanswered = []
        self._parse_questions(deepen, answered, unanswered)

        if not answered:
            return None

        # 计算相对路径
        try:
            rel_path = resolved_path.relative_to(self.context_dir)
        except ValueError:
            rel_path = resolved_path.name

        return {
            "file_path": str(resolved_path),
            "relative_path": str(rel_path),
            "title": title,
            "created": meta.get("created", ""),
            "tags": meta.get("tags", []),
            "source_cards": meta.get("source_cards", []),
            "mirror": mirror,
            "deepen_raw": deepen,
            "bridge": bridge,
            "growth_track": growth_track,
            "answered_questions": answered,
            "unanswered_questions": unanswered,
        }

    def save_reflection_closure(
        self,
        file_path: str,
        closure_content: str,
    ) -> str:
        """将闭环点评追加到反思文件末尾.

        在「成长轨迹」之后、文件结尾分隔线之前，插入「## Closure — 闭环点评」章节。

        Args:
            file_path: 反思文件路径
            closure_content: AI 生成的闭环点评内容（Markdown 格式）

        Returns:
            保存的文件路径
        """
        resolved_path = self._resolve_path(
            file_path, extra_dirs=[self.reflections_dir]
        )
        if resolved_path is None:
            raise FileNotFoundError(f"找不到反思文件: {file_path}")

        content = resolved_path.read_text(encoding="utf-8")

        # 更新 modified 时间
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = re.sub(
            r'modified: ".*?"',
            f'modified: "{now_str}"',
            content,
        )

        # 如果已有 Closure 章节，替换它
        closure_section = (
            f"## Closure — 闭环点评\n\n{closure_content}"
        )

        existing = re.search(
            r"## Closure — 闭环点评\s*\n.*?(?=\n---|\Z)",
            content,
            re.DOTALL,
        )
        if existing:
            content = content[:existing.start()] + closure_section + content[existing.end():]
        else:
            # 在结尾分隔线之前插入
            # 匹配最后的 \n---\n\n*反思于...*
            tail_match = re.search(r"\n---\s*\n\s*\*反思于.*?\*\s*$", content)
            if tail_match:
                insert_pos = tail_match.start()
                content = (
                    content[:insert_pos]
                    + "\n\n"
                    + closure_section
                    + "\n"
                    + content[insert_pos:]
                )
            else:
                # fallback: 追加到末尾
                content = content.rstrip() + "\n\n" + closure_section + "\n"

        resolved_path.write_text(content, encoding="utf-8")
        return str(resolved_path)

    # ─── 建议 1：Bridge 行动追踪 ──────────────────────────

    def extract_bridge_actions(self, file_path: str) -> Optional[dict]:
        """从反思文件中提取 Bridge 行动项及其完成状态.

        扫描 Bridge 章节中的行动项（以 🔨 或 checkbox 开头），
        返回结构化数据供 AI 生成验证追问。

        Args:
            file_path: 反思文件路径

        Returns:
            dict 包含反思标题、行动项列表及完成状态；
            如果没有 Bridge 章节则返回 None
        """
        resolved_path = self._resolve_path(
            file_path, extra_dirs=[self.reflections_dir]
        )
        if resolved_path is None:
            return None

        try:
            content = resolved_path.read_text(encoding="utf-8")
        except Exception:
            return None

        meta = self._parse_frontmatter(content)
        title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else resolved_path.stem

        bridge = self._extract_section(content, "Bridge — 行动搭桥")
        if not bridge:
            return None

        # 提取行动项：匹配 🔨 行动 N、### 行动 N、最推荐/备选、- [ ] / - [x] 格式
        actions = []
        lines = bridge.split("\n")
        current_action = None
        for line in lines:
            # 匹配 ### 🔨 行动 N：标题 或 ### 行动 N：标题（兼容早期格式）
            action_match = re.match(
                r"^###?\s*(?:🔨\s*)?行动\s*\d+[：:]\s*(.+)$", line
            )
            # 也匹配 **最推荐 →「...」** 和 **备选 →「...」** 格式
            if not action_match:
                action_match = re.match(
                    r"^\*\*(?:最推荐|备选)\s*→\s*[「「](.+?)[」」]\*\*$", line
                )
            if action_match:
                if current_action:
                    actions.append(current_action)
                current_action = {
                    "title": action_match.group(1).strip(),
                    "detail": "",
                    "completed": False,
                    "verification": "",
                }
                continue

            # 匹配 checkbox 行动
            checked = re.match(r"^-\s*\[x\]\s*(.+)$", line, re.IGNORECASE)
            unchecked = re.match(r"^-\s*\[\s*\]\s*(.+)$", line)
            if checked:
                if current_action:
                    actions.append(current_action)
                current_action = {
                    "title": checked.group(1).strip(),
                    "detail": "",
                    "completed": True,
                    "verification": "",
                }
                continue
            elif unchecked:
                if current_action:
                    actions.append(current_action)
                current_action = {
                    "title": unchecked.group(1).strip(),
                    "detail": "",
                    "completed": False,
                    "verification": "",
                }
                continue

            # 收集行动描述
            if current_action and line.strip():
                current_action["detail"] += line.strip() + " "

        if current_action:
            actions.append(current_action)

        # 检查是否已有 Action Verify 章节
        verify_section = self._extract_section(content, "Action Verify — 行动验证")
        has_verification = bool(verify_section)

        # 计算相对路径
        try:
            rel_path = resolved_path.relative_to(self.context_dir)
        except ValueError:
            rel_path = resolved_path.name

        return {
            "file_path": str(resolved_path),
            "relative_path": str(rel_path),
            "title": title,
            "created": meta.get("created", ""),
            "actions": actions,
            "total_actions": len(actions),
            "has_verification": has_verification,
        }

    def save_action_verification(
        self,
        file_path: str,
        verification_content: str,
    ) -> str:
        """将行动验证结果追加到反思文件.

        在 Closure 之后（或 Bridge 之后），插入
        「## Action Verify — 行动验证」章节。

        Args:
            file_path: 反思文件路径
            verification_content: AI 生成的行动验证内容

        Returns:
            保存的文件路径
        """
        resolved_path = self._resolve_path(
            file_path, extra_dirs=[self.reflections_dir]
        )
        if resolved_path is None:
            raise FileNotFoundError(f"找不到反思文件: {file_path}")

        content = resolved_path.read_text(encoding="utf-8")

        # 更新 modified 时间
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = re.sub(
            r'modified: ".*?"',
            f'modified: "{now_str}"',
            content,
        )

        verify_section = (
            f"## Action Verify — 行动验证\n\n{verification_content}"
        )

        # 如果已有 Action Verify 章节，替换它
        existing = re.search(
            r"## Action Verify — 行动验证\s*\n.*?(?=\n## |\n---|\Z)",
            content,
            re.DOTALL,
        )
        if existing:
            content = (
                content[:existing.start()]
                + verify_section
                + content[existing.end():]
            )
        else:
            # 在尾部分隔线之前插入
            tail_match = re.search(
                r"\n---\s*\n\s*\*反思于.*?\*\s*$", content
            )
            if tail_match:
                insert_pos = tail_match.start()
                content = (
                    content[:insert_pos]
                    + "\n\n"
                    + verify_section
                    + "\n"
                    + content[insert_pos:]
                )
            else:
                content = content.rstrip() + "\n\n" + verify_section + "\n"

        resolved_path.write_text(content, encoding="utf-8")
        return str(resolved_path)

    # ─── 建议 2：跨反思模式识别（Meta-Reflection）──────────

    def gather_meta_reflection(self, limit: int = 10) -> dict:
        """扫描所有反思文件，提取 Mirror/Deepen/Bridge/Closure 的关键内容.

        为 AI 做跨反思模式识别提供素材：
        - 每篇反思的核心洞察（Mirror 关键段落）
        - 用户的 Deepen 回答（暴露深层模式）
        - Bridge 行动及执行情况
        - Closure 中的成长轨迹

        Args:
            limit: 最多读取的反思文件数

        Returns:
            dict 包含所有反思的结构化摘要
        """
        if not self.reflections_dir.exists():
            return {"reflections": [], "total": 0}

        files = sorted(
            self.reflections_dir.glob("reflect_*.md"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )[:limit]

        reflections = []
        for fp in files:
            try:
                content = fp.read_text(encoding="utf-8")
            except Exception:
                continue

            meta = self._parse_frontmatter(content)
            title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
            title = (
                title_match.group(1).strip()
                if title_match
                else fp.stem
            )

            mirror = self._extract_section(content, "Mirror — 认知照镜")
            deepen = self._extract_section(content, "Deepen — 深度追问")
            bridge = self._extract_section(content, "Bridge — 行动搭桥")
            closure = self._extract_section(content, "Closure — 闭环点评")
            growth = self._extract_section(content, "成长轨迹")
            verify = self._extract_section(
                content, "Action Verify — 行动验证"
            )

            # 提取 Deepen 中用户的回答
            answered = []
            unanswered = []
            if deepen:
                self._parse_questions(deepen, answered, unanswered)

            try:
                rel_path = fp.relative_to(self.context_dir)
            except ValueError:
                rel_path = fp.name

            reflections.append({
                "file_path": str(fp),
                "relative_path": str(rel_path),
                "title": title,
                "created": meta.get("created", ""),
                "tags": meta.get("tags", []),
                "mirror_summary": mirror[:500] if mirror else "",
                "deepen_answers": answered,
                "bridge_summary": bridge[:500] if bridge else "",
                "closure_summary": closure[:500] if closure else "",
                "growth_track": growth,
                "action_verify": verify[:300] if verify else "",
                "has_closure": bool(closure),
                "has_verification": bool(verify),
            })

        return {
            "reflections": reflections,
            "total": len(reflections),
            "total_with_closure": sum(
                1 for r in reflections if r["has_closure"]
            ),
            "total_with_verification": sum(
                1 for r in reflections if r["has_verification"]
            ),
        }

    # ─── 旧行动打卡系统已迁移到 skills/actions/scripts/action_engine.py ─
