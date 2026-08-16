#!/usr/bin/env python3
"""扫描仓库根目录的各类记忆,生成 Meta/index.md — 每条记忆一行,文件名即结论。"""
import datetime
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SECTIONS = [
    ("Profile", "用户画像"),
    ("Concepts", "概念"),
    ("Notes", "我的收藏"),
    # 日记进索引是 2026-08-16 用户明确要的:让 AI 看得见、能据此了解和分析用户。
    # 一月一个文件所以一年只多 12 行。Works/ 和 Archive/ 不进(它们不是给 AI 读的)。
    ("Diary", "日记"),
]
SKIP_NAMES = {"README.md"}  # 目录说明文件不是记忆


# 分层(Meta/RESOLVER.md 定义):核心=我自己的判断和立场,方法=可执行做法,
# 参考=外部知识,过时了换一份就行——只有参考层适合被淡出/折叠,核心层永不自动降级。
TIERS = {"核心": "🧠", "方法": "🔧", "参考": "📖"}


def frontmatter(path: Path) -> dict:
    meta = {}
    m = re.match(r"^---\n(.*?)\n---", path.read_text(encoding="utf-8"), re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta


def entry(f: Path) -> str:
    meta = frontmatter(f)
    extras = [
        f"{label}: {meta[key]}"
        for key, label in (
            ("confidence", "confidence"),
            ("last-verified", "verified"),
            ("verified", "verified"),
            ("last-checked", "checked"),
        )
        if meta.get(key)
    ]
    suffix = f" ({', '.join(extras)})" if extras else ""
    rel = f.relative_to(ROOT).with_suffix("").as_posix()
    return f"[[{rel}|{f.stem}]]{suffix}"


lines = [
    "# 记忆索引",
    "",
    f"> 自动生成于 {datetime.date.today()},勿手改;运行 `python3 Meta/scripts/build_memory_index.py` 更新。",
    "",
]
total = 0
for dirname, title in SECTIONS:
    files = sorted((ROOT / dirname).rglob("*.md")) if (ROOT / dirname).exists() else []
    files = [f for f in files if f.name not in SKIP_NAMES]
    if not files:
        continue
    older = []
    if dirname == "Diary":
        # 2026-08-16 用户要求:索引里只列最近一个月。日记按 年/年-月.md 命名,
        # 文件名排序即时间序,取最后一个。更早的不列但要留一句话说明它们存在,
        # 否则"日记进索引"就退化成"只有这个月的日记存在过"。
        older, files = files[:-1], files[-1:]
    lines += [f"## {title}", ""]
    if dirname == "Notes":
        # 分层展示:🧠 核心先行,📖 参考垫底——想淡出参考层时,直接从最后一段往下看/折叠
        buckets = {t: [] for t in TIERS}
        for f in files:
            buckets.setdefault(frontmatter(f).get("tier", "未分层"), []).append(f)
        for tier in list(TIERS) + [t for t in buckets if t not in TIERS]:
            group = buckets.get(tier) or []
            if not group:
                continue
            lines += [f"### {TIERS.get(tier, '❓')} {tier}({len(group)})", ""]
            for f in group:
                lines.append(f"- {entry(f)}")
                total += 1
            lines.append("")
        continue
    for f in files:
        meta = frontmatter(f)
        extras = [
            f"{label}: {meta[key]}"
            for key, label in (
                ("confidence", "confidence"),
                ("last-verified", "verified"),
                ("verified", "verified"),
                ("last-checked", "checked"),
            )
            if meta.get(key)
        ]
        suffix = f" ({', '.join(extras)})" if extras else ""
        rel = f.relative_to(ROOT).with_suffix("").as_posix()
        lines.append(f"- [[{rel}|{f.stem}]]{suffix}")
        total += 1
    if older:
        lines.append(
            f"- *更早的 {len(older)} 个月在 `Diary/` 下(最早 {older[0].stem}),"
            "刻意不列进索引;要看更早的自己去翻那个目录。*"
        )
    lines.append("")
lines.append(f"共 {total} 条记忆。")

(ROOT / "Meta" / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Meta/index.md 已更新,共 {total} 条记忆")
