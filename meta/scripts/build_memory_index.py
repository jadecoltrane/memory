#!/usr/bin/env python3
"""扫描仓库根目录的各类记忆,生成 meta/index.md — 每条记忆一行,文件名即结论。"""
import datetime
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SECTIONS = [
    ("profile", "用户画像"),
    ("concepts", "概念"),
    ("notes", "我的收藏"),
]


# 分层(meta/RESOLVER.md 定义):核心=我自己的判断和立场,方法=可执行做法,
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
    f"> 自动生成于 {datetime.date.today()},勿手改;运行 `python3 meta/scripts/build_memory_index.py` 更新。",
    "",
]
total = 0
for dirname, title in SECTIONS:
    files = sorted((ROOT / dirname).rglob("*.md")) if (ROOT / dirname).exists() else []
    if not files:
        continue
    lines += [f"## {title}", ""]
    if dirname == "notes":
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
    lines.append("")
lines.append(f"共 {total} 条记忆。")

(ROOT / "meta" / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"meta/index.md 已更新,共 {total} 条记忆")
