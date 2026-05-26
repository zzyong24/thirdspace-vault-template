"""工作日志管理器 - 生成、追加、索引重建."""

from __future__ import annotations

import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


# 星期映射
WEEKDAY_MAP = {
    0: "周一", 1: "周二", 2: "周三", 3: "周四",
    4: "周五", 5: "周六", 6: "周日",
}

# 日志模板
WORKLOG_TEMPLATE = """---
title: "{date_str} {weekday} 工作日志"
type: "worklog"
topic: "work"
created: "{created_time}"
modified: "{created_time}"
tags: ["worklog", "work", "crafted"]
origin: "crafted"
source: "mcp"
status: "active"
---

# {date_str} {weekday}

## 今日工作内容

{initial_content}

## 重点记录（可直接粘贴）

-

## 问题 & 解决方案



## 参考 / 链接

-

## 明日计划

"""

# 内容分类关键词
SECTION_KEYWORDS: dict[str, list[str]] = {
    "问题 & 解决方案": [
        "问题", "bug", "报错", "异常", "错误", "error", "issue",
        "解决", "修复", "fix", "处理", "排查",
    ],
    "重点记录（可直接粘贴）": [
        "完成", "实现", "开发", "重点", "要点", "上线", "部署",
        "联调", "评审", "需求", "设计", "优化",
    ],
    "参考 / 链接": [
        "链接", "参考", "文档", "http://", "https://", "wiki",
    ],
    "明日计划": [
        "明天", "明日", "计划", "待办", "todo", "下一步",
    ],
}


class WorklogManager:
    """工作日志管理器."""

    def __init__(self, worklog_dir: str | Path):
        """初始化.

        Args:
            worklog_dir: worklog 根目录路径
                         (即 vault/02-日记/工作日志/)
        """
        self.worklog_dir = Path(worklog_dir)
        self.worklog_dir.mkdir(parents=True, exist_ok=True)

    def get_real_date(self) -> tuple[str, str]:
        """通过系统命令获取真实日期.

        Returns:
            (日期字符串 YYYY-MM-DD, 星期中文名)
        """
        try:
            result = subprocess.run(
                ["date", "+%Y-%m-%d %u"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split()
                date_str = parts[0]
                weekday_num = int(parts[1]) - 1  # 1=Mon -> 0
                weekday = WEEKDAY_MAP.get(weekday_num, "周一")
                return date_str, weekday
        except Exception:
            pass

        # Fallback
        now = datetime.now()
        return now.strftime("%Y-%m-%d"), WEEKDAY_MAP[now.weekday()]

    def create_worklog(self, content: str = "") -> tuple[str, str]:
        """生成今日工作日志.

        Args:
            content: 可选的初始内容

        Returns:
            (结果消息, 文件路径)
        """
        date_str, weekday = self.get_real_date()
        year, month, _ = date_str.split("-")

        # 创建目录
        month_dir = self.worklog_dir / year / month
        month_dir.mkdir(parents=True, exist_ok=True)

        # 文件路径
        filename = f"{date_str}-{weekday}.md"
        filepath = month_dir / filename

        # 检查是否已存在
        if filepath.exists():
            return f"今日日志已存在: {filepath}\n如需追加内容，请使用 append_worklog", str(filepath)

        # 在创建前，处理前一天日志的索引更新
        self._update_previous_log_index()

        # 生成日志
        created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_content = WORKLOG_TEMPLATE.format(
            date_str=date_str,
            weekday=weekday,
            created_time=created_time,
            initial_content=content or "（简要描述今天完成的主要工作）",
        )
        filepath.write_text(log_content, encoding="utf-8")

        return f"✅ 已创建今日工作日志: {date_str} {weekday}", str(filepath)

    def append_worklog(self, content: str) -> tuple[str, str]:
        """智能追加内容到今日工作日志.

        Args:
            content: 要追加的内容

        Returns:
            (结果消息, 文件路径)
        """
        date_str, weekday = self.get_real_date()
        year, month, _ = date_str.split("-")

        filename = f"{date_str}-{weekday}.md"
        filepath = self.worklog_dir / year / month / filename

        if not filepath.exists():
            return (
                f"今日日志不存在，请先使用 create_worklog 创建\n"
                f"期望路径: {filepath}",
                "",
            )

        # 读取现有内容
        existing = filepath.read_text(encoding="utf-8")

        # 判断内容类别
        section = self._classify_content(content)

        # 追加到对应章节
        updated = self._append_to_section(existing, section, content)
        filepath.write_text(updated, encoding="utf-8")

        return f"✅ 已追加到「{section}」章节", str(filepath)

    def append_to_section(self, content: str, section: str) -> tuple[str, str]:
        """将已格式化的内容直接写入指定章节（AI 已完成分类和格式化）.

        Args:
            content: 已格式化好的内容（AI 负责格式化）
            section: 目标章节名

        Returns:
            (结果消息, 文件路径)
        """
        date_str, weekday = self.get_real_date()
        year, month, _ = date_str.split("-")

        filename = f"{date_str}-{weekday}.md"
        filepath = self.worklog_dir / year / month / filename

        if not filepath.exists():
            return (
                f"今日日志不存在，请先使用 create_worklog 创建\n"
                f"期望路径: {filepath}",
                "",
            )

        existing = filepath.read_text(encoding="utf-8")

        # 直接写入指定章节，不做额外格式化
        updated = self._insert_raw_to_section(existing, section, content)
        filepath.write_text(updated, encoding="utf-8")

        return f"✅ 已追加到「{section}」章节", str(filepath)

    def _insert_raw_to_section(self, existing: str, section: str, content: str) -> str:
        """将原始内容直接插入到指定章节（不做格式化处理）."""
        section_pattern = re.compile(rf"^## {re.escape(section)}", re.MULTILINE)
        match = section_pattern.search(existing)

        if not match:
            return existing.rstrip() + f"\n\n## {section}\n\n{content}\n"

        next_section = re.search(r"\n## ", existing[match.end():])
        if next_section:
            insert_pos = match.end() + next_section.start()
        else:
            insert_pos = len(existing)

        before = existing[:insert_pos].rstrip()
        after = existing[insert_pos:]

        return before + "\n" + content + "\n" + after

    def rebuild_index(self) -> tuple[str, str]:
        """重建日志索引.

        Returns:
            (结果消息, INDEX.md 路径)
        """
        index_path = self.worklog_dir / "INDEX.md"
        entries: list[dict[str, Any]] = []

        # 扫描所有日志文件
        for md_file in sorted(self.worklog_dir.rglob("*.md"), reverse=True):
            if md_file.name == "INDEX.md":
                continue

            # 解析文件名: YYYY-MM-DD-周X.md
            match = re.match(r"(\d{4}-\d{2}-\d{2})-(周.+)\.md", md_file.name)
            if not match:
                continue

            date_str = match.group(1)
            year_month = date_str[:7]  # YYYY-MM

            # 提取关键词
            try:
                content = md_file.read_text(encoding="utf-8")
                keywords = self._extract_keywords(content)
            except Exception:
                keywords = []

            # 构建相对链接
            rel_path = md_file.relative_to(self.worklog_dir)

            entries.append({
                "date": date_str,
                "year_month": year_month,
                "year": date_str[:4],
                "keywords": ", ".join(keywords),
                "link": f"[{md_file.stem}](./{rel_path})",
            })

        # 按年月分组生成索引
        lines = ["# 工作日志索引", ""]
        current_year = ""
        current_ym = ""

        for entry in entries:
            if entry["year"] != current_year:
                current_year = entry["year"]
                lines.append(f"## {current_year}年")
                lines.append("")

            if entry["year_month"] != current_ym:
                current_ym = entry["year_month"]
                lines.append(f"### {current_ym}")
                lines.append("")
                lines.append("| 日期 | 关键词 | 链接 |")
                lines.append("|------|--------|------|")

            lines.append(
                f"| {entry['date']} | {entry['keywords']} | {entry['link']} |"
            )
            # 检查下一个是否换组
            idx = entries.index(entry)
            if idx < len(entries) - 1 and entries[idx + 1]["year_month"] != current_ym:
                lines.append("")

        lines.append("")
        index_content = "\n".join(lines)
        index_path.write_text(index_content, encoding="utf-8")

        return f"✅ 索引已重建，共 {len(entries)} 篇日志", str(index_path)

    def _classify_content(self, content: str) -> str:
        """对内容进行分类，判断应追加到哪个章节."""
        content_lower = content.lower()

        # 检查用户是否显式指定了章节
        explicit_map = {
            "重点记录": "重点记录（可直接粘贴）",
            "问题": "问题 & 解决方案",
            "解决方案": "问题 & 解决方案",
            "参考": "参考 / 链接",
            "链接": "参考 / 链接",
            "明日计划": "明日计划",
            "计划": "明日计划",
        }
        for keyword, section in explicit_map.items():
            if content_lower.startswith(f"补充到{keyword}") or content_lower.startswith(keyword + "："):
                return section

        # 基于关键词自动分类
        scores: dict[str, int] = {}
        for section, keywords in SECTION_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in content_lower)
            if score > 0:
                scores[section] = score

        if scores:
            return max(scores, key=scores.get)

        # 默认归到今日工作内容
        return "今日工作内容"

    def _append_to_section(self, existing: str, section: str, content: str) -> str:
        """将内容追加到指定章节."""
        # 格式化追加内容
        formatted = self._format_for_section(section, content)

        # 查找章节位置
        section_pattern = re.compile(rf"^## {re.escape(section)}", re.MULTILINE)
        match = section_pattern.search(existing)

        if not match:
            # 章节不存在，追加到文件末尾
            return existing.rstrip() + f"\n\n## {section}\n\n{formatted}\n"

        # 找到下一个 ## 章节的位置
        next_section = re.search(r"\n## ", existing[match.end():])
        if next_section:
            insert_pos = match.end() + next_section.start()
        else:
            insert_pos = len(existing)

        # 在章节末尾追加（在下一个章节前）
        before = existing[:insert_pos].rstrip()
        after = existing[insert_pos:]

        return before + "\n" + formatted + "\n" + after

    def _format_for_section(self, section: str, content: str) -> str:
        """根据章节格式化追加内容."""
        # 清理可能的前缀
        content = re.sub(r'^(补充到\S+[:：]\s*|重点记录[:：]\s*|问题[:：]\s*)', '', content).strip()

        if section == "问题 & 解决方案":
            # 尝试拆分问题和解决方案
            if "解决" in content or "fix" in content.lower():
                parts = re.split(r'[,，;；]?\s*(?:解决|修复|fix)[：:]\s*', content, maxsplit=1)
                if len(parts) == 2:
                    return f"问题：{parts[0].strip()}\n\n解决：{parts[1].strip()}\n"
            return f"问题：{content}\n\n解决：\n"

        if section == "参考 / 链接":
            return self._format_list_items(content, prefix="- ")

        if section == "明日计划":
            return self._format_list_items(content, prefix="- [ ] ")

        # 重点记录 / 今日工作内容
        return self._format_list_items(content, prefix="- ")

    def _format_list_items(self, content: str, prefix: str = "- ") -> str:
        """将多行/多段内容格式化为列表项.

        逻辑：
        - 按空行分割为多个段落，每个段落作为一个顶级列表项
        - 段落内如果有多行，首行为列表项，后续行缩进为子项
        - 已有 `- ` 前缀的行保持原样（避免重复加前缀）
        """
        # 按连续空行分段
        paragraphs = re.split(r'\n\s*\n', content.strip())
        result_lines = []

        for para in paragraphs:
            lines = [l.strip() for l in para.strip().splitlines() if l.strip()]
            if not lines:
                continue

            if len(lines) == 1:
                line = lines[0]
                # 已有列表前缀则保持
                if re.match(r'^[-*] ', line) or re.match(r'^- \[[ x]\] ', line):
                    result_lines.append(line)
                else:
                    result_lines.append(f"{prefix}{line}")
            else:
                # 多行：首行作为主项，后续行缩进为子项
                first = lines[0]
                if re.match(r'^[-*] ', first) or re.match(r'^- \[[ x]\] ', first):
                    result_lines.append(first)
                else:
                    result_lines.append(f"{prefix}{first}")

                for sub in lines[1:]:
                    if re.match(r'^[-*] ', sub):
                        # 已有前缀的子项，加缩进
                        result_lines.append(f"  {sub}")
                    else:
                        result_lines.append(f"  - {sub}")

        return "\n".join(result_lines)

    def _extract_keywords(self, content: str) -> list[str]:
        """从日志内容中提取关键词摘要.
        
        扫描多个章节，提取有实际内容的列表项作为关键词。
        """
        keywords = []
        
        # 定义要扫描的章节优先级（按重要性排序）
        sections_to_scan = [
            # (章节标题正则, 最大提取数)
            (r"## 完成事项", 3),
            (r"## 今日重点", 3),
            (r"## 今日工作内容", 3),
            (r"## 重点记录[^\n]*", 3),
            (r"## 工作记录", 2),
            (r"## 思考沉淀", 1),
        ]
        
        for section_pattern, max_items in sections_to_scan:
            if len(keywords) >= 5:  # 总共最多 5 条
                break
                
            match = re.search(
                rf"{section_pattern}\n(.*?)(?=\n## |\Z)",
                content, re.DOTALL,
            )
            if not match:
                continue
                
            section_content = match.group(1)
            
            # 提取列表项（支持 - 和数字列表，只匹配顶级列表项，跳过缩进的子项）
            items = re.findall(r"^[-\d.]+\s*(.+)", section_content, re.MULTILINE)
            
            for item in items[:max_items * 2]:  # 多取一些，因为会过滤
                if len(keywords) >= 5:
                    break
                    
                # 清理并截取
                clean = item.strip()
                
                # 跳过空内容、占位符
                if not clean or clean == "":
                    continue
                if clean in ("（简要描述今天完成的主要工作）", ""):
                    continue
                
                # 去掉内容中的链接部分（保留链接前的描述文字）
                clean = re.sub(r"[：:]\s*https?://\S+", "", clean)
                clean = re.sub(r"https?://\S+", "", clean)
                clean = clean.strip()
                
                # 跳过纯链接行（去掉链接后为空）
                if not clean:
                    continue
                    
                # 跳过待办项标记（但保留内容）
                clean = re.sub(r"^\[[ x]\]\s*", "", clean)
                
                # 去掉 Markdown 加粗/斜体标记
                clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", clean)  # **bold** -> bold
                clean = re.sub(r"^\*+\s*", "", clean)  # 开头的 * 标记
                
                # 跳过只有标点或只有几个字的行（如 "根因分析：" "问题：" 等）
                if len(clean) < 5 or clean.endswith("："):
                    continue
                
                # 去掉子列表的缩进标记
                clean = re.sub(r"^\s*[-*]\s*", "", clean)
                
                # 截取前 50 字符，智能截断（不在单词/汉字中间断开）
                if len(clean) > 50:
                    clean = clean[:50] + "..."
                    
                if clean and clean not in keywords:
                    keywords.append(clean)
        
        # 补充：从问题行提取
        if len(keywords) < 5:
            problem_match = re.findall(r"问题[：:]\s*(.+)", content)
            for p in problem_match[:2]:
                if len(keywords) >= 5:
                    break
                clean = p.strip()
                # 去掉链接
                clean = re.sub(r"https?://\S+", "", clean).strip()
                if len(clean) > 50:
                    clean = clean[:50] + "..."
                if clean and len(clean) >= 5 and clean not in keywords:
                    keywords.append(clean)

        return keywords

    def _update_previous_log_index(self) -> None:
        """更新前一个日志的索引关键词."""
        # 找到最近的日志文件
        all_logs = sorted(self.worklog_dir.rglob("*.md"))
        logs = [f for f in all_logs if f.name != "INDEX.md" and re.match(r"\d{4}-\d{2}-\d{2}", f.name)]

        if not logs:
            return

        latest = logs[-1]
        try:
            content = latest.read_text(encoding="utf-8")
            keywords = self._extract_keywords(content)
            if not keywords:
                return

            # 更新 INDEX.md 中该日期的关键词
            index_path = self.worklog_dir / "INDEX.md"
            if not index_path.exists():
                return

            index_content = index_path.read_text(encoding="utf-8")
            date_str = latest.name[:10]  # YYYY-MM-DD

            # 查找并更新该日期行
            pattern = rf"(\| {re.escape(date_str)} \|) [^|]* (\|)"
            # 转义 keywords 中可能存在的反斜杠等特殊字符，
            # 避免被 re.sub 当作反向引用解释
            safe_keywords = re.escape(', '.join(keywords))
            replacement = rf"\1 {safe_keywords} \2"
            updated = re.sub(pattern, replacement, index_content)

            if updated != index_content:
                index_path.write_text(updated, encoding="utf-8")
        except Exception:
            pass
