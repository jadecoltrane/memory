#!/usr/bin/env python3
"""扫描仓库根目录的四类记忆,生成 index.md — 每条记忆一行,文件名即结论。"""
import datetime
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = [
    ("decisions", "决策与约定"),
    ("pitfalls", "踩坑记录"),
    ("insights", "判断与洞察"),
    ("questions", "未解问题"),
    ("notes", "我的收藏"),
]


def frontmatter(path: Path) -> dict:
    meta = {}
    m = re.match(r"^---\n(.*?)\n---", path.read_text(encoding="utf-8"), re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta


lines = [
    "# 记忆索引",
    "",
    f"> 自动生成于 {datetime.date.today()},勿手改;运行 `python3 scripts/build_memory_index.py` 更新。",
    "",
]
total = 0
for dirname, title in SECTIONS:
    files = sorted((ROOT / dirname).rglob("*.md")) if (ROOT / dirname).exists() else []
    if not files:
        continue
    lines += [f"## {title}", ""]
    for f in files:
        meta = frontmatter(f)
        extras = [
            f"{label}: {meta[key]}"
            for key, label in (("confidence", "confidence"), ("last-verified", "verified"))
            if meta.get(key)
        ]
        suffix = f" ({', '.join(extras)})" if extras else ""
        rel = f.relative_to(ROOT).with_suffix("").as_posix()
        lines.append(f"- [[{rel}|{f.stem}]]{suffix}")
        total += 1
    lines.append("")
lines.append(f"共 {total} 条记忆。")

(ROOT / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"index.md 已更新,共 {total} 条记忆")
