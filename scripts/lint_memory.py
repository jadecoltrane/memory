#!/usr/bin/env python3
"""记忆库体检:断链 + frontmatter 完整性。

规则由 AI 执行,但 AI 会漏(真实案例:supersede 删旧文件后忘了更新 SUMMARY 里的双链)。
这里做机器能做的兜底检查,错误时退出码 1 让 CI 亮红灯。

- 断链:双链指向的文件必须存在。例外:[[concepts/xxx]] 允许是幽灵节点(懒加载设计),
  但幽灵可以命中概念页的 aliases;裸名链接按 basename 或 aliases 解析。
- frontmatter:decisions/pitfalls/insights/questions 必须有 type 和 created,
  insight 必须有 confidence;concepts 必须有 type: concept。
- notes/ 只给警告不报错:用户手写笔记允许没有 frontmatter,GC 时才补齐。
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIMELINE_DIRS = ["decisions", "pitfalls", "insights", "questions"]
LINK_CHECK_FILES = ["meta/SUMMARY.md", "工作台.md"]  # CLAUDE/RESOLVER 里是示例链接,不查
WIKILINK = re.compile(r"\[\[([^\]|#^]+)")

errors, warnings = [], []


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm, key = {}, None
    for line in text[4:end].splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and key:
            fm.setdefault(key, [])
            if isinstance(fm[key], list):
                fm[key].append(stripped[2:].strip())
        elif ":" in line and not line[:1].isspace():
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip()
            if val.startswith("[") and val.endswith("]"):
                fm[key] = [v.strip() for v in val[1:-1].split(",") if v.strip()]
            elif val:
                fm[key] = val
            else:
                fm[key] = []
    return fm


def collect_pages():
    """全库 md 文件 → (相对路径集合, basename 集合, 别名集合)"""
    paths, basenames, aliases = set(), set(), set()
    for p in ROOT.rglob("*.md"):
        if any(part.startswith(".") for part in p.relative_to(ROOT).parts):
            continue
        rel = p.relative_to(ROOT).as_posix()[:-3]
        paths.add(rel)
        basenames.add(p.stem)
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        al = fm.get("aliases", [])
        if isinstance(al, str):
            al = [al]
        aliases.update(a for a in al if a)
    return paths, basenames, aliases


def check_links(path: Path, paths, basenames, aliases):
    rel = path.relative_to(ROOT).as_posix()
    for target in WIKILINK.findall(path.read_text(encoding="utf-8")):
        target = target.strip()
        if not target or target.startswith("concepts/"):
            continue  # 幽灵概念是设计允许的
        if "/" in target:
            if target not in paths:
                errors.append(f"{rel}: 断链 [[{target}]]")
        elif target not in basenames and target not in aliases:
            errors.append(f"{rel}: 断链 [[{target}]](按文件名和 aliases 都没找到)")


def check_frontmatter(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    top = rel.split("/")[0]
    fm = parse_frontmatter(path.read_text(encoding="utf-8"))
    if top in TIMELINE_DIRS:
        for field in ("type", "created"):
            if field not in fm:
                errors.append(f"{rel}: frontmatter 缺 {field}")
        if top == "insights" and "confidence" not in fm:
            errors.append(f"{rel}: insight 必须标 confidence")
    elif top == "concepts":
        if fm.get("type") != "concept":
            errors.append(f"{rel}: 概念页 frontmatter 必须是 type: concept")
    elif top == "profile":
        if fm.get("type") != "profile":
            errors.append(f"{rel}: 画像页 frontmatter 必须是 type: profile")
        if "updated" not in fm:
            errors.append(f"{rel}: 画像页必须有 updated 日期")
    elif top == "notes":
        if "type" not in fm:
            warnings.append(f"{rel}: 还没有 frontmatter(手写笔记?等 GC 补齐)")


def main():
    paths, basenames, aliases = collect_pages()
    for top in TIMELINE_DIRS + ["notes", "concepts", "profile"]:
        d = ROOT / top
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.md")):
            check_links(p, paths, basenames, aliases)
            check_frontmatter(p)
    for name in LINK_CHECK_FILES:
        p = ROOT / name
        if p.exists():
            check_links(p, paths, basenames, aliases)

    for w in warnings:
        print(f"⚠️  {w}")
    for e in errors:
        print(f"❌ {e}")
    if errors:
        print(f"\n体检不通过:{len(errors)} 个错误,{len(warnings)} 个警告")
        sys.exit(1)
    print(f"体检通过:0 个错误,{len(warnings)} 个警告")


if __name__ == "__main__":
    main()
