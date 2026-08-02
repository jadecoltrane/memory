#!/usr/bin/env python3
"""记忆库体检:断链 + frontmatter + 结构性腐化(机械检查,不靠人记得)。

规则由 AI 执行,但 AI 会漏(真实案例:supersede 删旧文件后忘了更新引用它的双链;
2026-08-02 一天写了 100 条 note→note 链,把 hub-and-spoke 结构写成了网)。
这里做机器能做的兜底检查,错误退出码 1 让 CI 亮红灯,警告只提示。

错误(阻断):
- 断链:双链指向的文件必须存在。例外:[[concepts/xxx]] 允许是幽灵节点(懒加载设计),
  但幽灵可以命中概念页的 aliases;裸名链接按 basename 或 aliases 解析。
- frontmatter:concepts 必须有 type: concept;profile 必须有 type: profile 和 updated。

警告(只提示,给 GC 排队):
- notes/ 缺 frontmatter:用户手写笔记允许没有,GC 时才补齐。
- note→note 超标:单篇 > MAX_NOTE_LINKS 条,且超出部分没标"上下篇"。防网状化。
- 概念裸奔:已有概念页的名字/别名在正文里出现 ≥2 次却一次双链都没打。防图谱连不上。
- 文件夹膨胀:单个文件夹 > MAX_FOLDER_NOTES 篇。防下一个"社会学 28 篇"。
- 概念页延伸超限:延伸区 > MAX_EXTENSIONS 条,该做晋升(定论折进定义,其余进已探讨)。
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LINK_CHECK_FILES = ["工作台.md"]  # CLAUDE/RESOLVER 里是示例链接,不查
WIKILINK = re.compile(r"\[\[([^\]|#^]+)")

MAX_NOTE_LINKS = 2  # 单篇 note→note 上限;标了"上下篇"的那行不计入
MAX_FOLDER_NOTES = 12  # 单个 notes/ 子文件夹的笔记数上限
MAX_EXTENSIONS = 6  # 概念页「延伸」区条目上限
SERIES_MARK = re.compile(r"上下篇|上篇|下篇")  # 豁免标记:写在含该链接的同一行里

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
    if top == "concepts":
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


def collect_concept_names() -> dict:
    """概念页 → 它的所有可识别称呼(文件名 + aliases)。用于「裸奔」检查。"""
    names = {}
    d = ROOT / "concepts"
    if not d.is_dir():
        return names
    for p in sorted(d.glob("*.md")):
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        al = fm.get("aliases", [])
        if isinstance(al, str):
            al = [al]
        names[f"concepts/{p.stem}"] = [p.stem] + [a for a in al if a]
    return names


def check_note_links(path: Path):
    """note→note 密度。CONCEPTS.md 规定笔记之间不直接互链,走概念页中转;
    真的是同一论证上下篇时,在那一行里写上「上下篇」豁免。"""
    rel = path.relative_to(ROOT).as_posix()
    plain = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        hits = [t for t in WIKILINK.findall(line) if t.strip().startswith("notes/")]
        if hits and not SERIES_MARK.search(line):
            plain += len(hits)
    if plain > MAX_NOTE_LINKS:
        warnings.append(
            f"{rel}: note→note 双链 {plain} 条(上限 {MAX_NOTE_LINKS})"
            f"——改走概念页中转(另一篇写成纯文本路径),或在那一行写明「上下篇/上篇/下篇」"
        )


def check_naked_concepts(path: Path, concept_names: dict):
    """已有概念页的名字在正文里裸文本反复出现,却一次双链都没打 → 图谱连不上。"""
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8")
    linked = {t.strip() for t in WIKILINK.findall(text)}
    stripped = WIKILINK.sub("", text)  # 去掉双链本身,只看裸文本
    for cpath, names in concept_names.items():
        if cpath in linked or cpath.split("/")[-1] in linked:
            continue
        if any(n in linked for n in names):
            continue
        for n in names:
            if stripped.count(n) >= 2:
                warnings.append(f"{rel}: 「{n}」出现 {stripped.count(n)} 次但没挂 [[{cpath}]]")
                break


def check_folder_sizes():
    counts = defaultdict(int)
    for p in (ROOT / "notes").rglob("*.md"):
        counts[p.parent.relative_to(ROOT).as_posix()] += 1
    for folder, n in sorted(counts.items()):
        if n > MAX_FOLDER_NOTES:
            warnings.append(f"{folder}/: {n} 篇(上限 {MAX_FOLDER_NOTES})——该拆分了")


def check_extension_cap(path: Path):
    """概念页延伸区的晋升机制:超过上限说明该做一次收敛,而不是继续堆。"""
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^## 延伸.*$", text, re.M)
    if not m:
        return
    rest = text[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    body = rest[: nxt.start()] if nxt else rest
    n = len([ln for ln in body.splitlines() if ln.startswith("- ")])
    if n > MAX_EXTENSIONS:
        warnings.append(
            f"{rel}: 延伸 {n} 条(上限 {MAX_EXTENSIONS})"
            f"——按 meta/CONCEPTS.md 的晋升机制收敛:已成定论的折进定义,存疑的移进已探讨"
        )


def main():
    paths, basenames, aliases = collect_pages()
    concept_names = collect_concept_names()
    for top in ["notes", "concepts", "profile"]:
        d = ROOT / top
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.md")):
            check_links(p, paths, basenames, aliases)
            check_frontmatter(p)
            if top == "notes":
                check_note_links(p)
                check_naked_concepts(p, concept_names)
            elif top == "concepts":
                check_extension_cap(p)
    check_folder_sizes()
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
