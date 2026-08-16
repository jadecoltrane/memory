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
- 出现在漏收:笔记挂了 [[concepts/X]],X 的「出现在」区却没收录它。防枢纽不认识自己的辐条。
- 文件夹膨胀:单个文件夹 > MAX_FOLDER_NOTES 篇。防下一个"社会学 28 篇"。
  FOLDER_CAP_EXEMPT 里的流水型目录(书影音)不查——按条目自然增长的东西,按数量拆没意义。
- 顶层过宽:notes/ 直属子文件夹 > MAX_TOP_FOLDERS 个。上面那条只封单个文件夹的宽度,
  不封文件夹**数量**——一路平铺拆下去文件树会比笔记还难翻,所以拆分往深里走。
- 概念页延伸超限:延伸区 > MAX_EXTENSIONS 条,该做晋升(定论折进定义,其余进已探讨)。
- 指向 archive/ 的双链:归档的东西不该还挂在图谱上,改成纯文本路径。
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LINK_CHECK_FILES = ["工作台.md"]  # CLAUDE/RESOLVER 里是示例链接,不查
WIKILINK = re.compile(r"\[\[([^\]|#^]+)")

MAX_NOTE_LINKS = 2  # 单篇 note→note 上限;标了"上下篇"的那行不计入
MAX_FOLDER_NOTES = 12  # 单个 notes/ 子文件夹的笔记数上限(按直接父目录计,嵌套不受罚)
MAX_TOP_FOLDERS = 10  # notes/ 直属子文件夹数上限;2026-08-16 定,当时 8 个
# 12 篇上限不查的目录(前缀匹配)。判据是"流水型 vs 观点型":
# 观点型笔记堆到 12 条同级结论就说明该分层了,警告有意义;书影音这种按条目自然增长的,
# 一年几十本,按数量拆只会拆出一堆没有意义的文件夹——它们该按年份/门类分。
# 而且找一本书是靠书名找的,不靠翻文件夹,"翻不动"这个原始问题在这里不成立。
FOLDER_CAP_EXEMPT = ("notes/书影音",)
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
        rel_parts = p.relative_to(ROOT).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
        if rel_parts[:2] == ("sources", "raw"):
            continue  # 导出原文不是记忆,不该成为可解析的链接目标(链进去就该报断链)
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
        if target.startswith("archive/"):
            # 归档的东西不该还留在图谱里。按 archive/README.md,归档前要先把
            # 指向它的双链改成纯文本路径——这条就是那一步的守门员。
            warnings.append(f"{rel}: 双链指向已归档的 [[{target}]],改成纯文本路径并注明「已归档」")
            continue
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


def check_concept_backlinks(concept_names: dict):
    """反向检查:笔记挂了 [[concepts/X]],X 的「出现在」区却没收录这篇。
    Obsidian 的反链面板能看到,但 AI 读的是概念页正文——出现在漏收 = 枢纽自己不知道谁连着它。"""
    for cpath in concept_names:
        p = ROOT / f"{cpath}.md"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        m = re.search(r"^## 出现在.*$", text, re.M)
        listed = set()
        if m:
            rest = text[m.end():]
            nxt = re.search(r"^## ", rest, re.M)
            for x in WIKILINK.findall(rest[: nxt.start()] if nxt else rest):
                listed.add(x.strip().split("|")[0].rsplit("/", 1)[-1])
        miss = []
        for n in sorted((ROOT / "notes").rglob("*.md")):
            targets = [x.strip().split("|")[0] for x in WIKILINK.findall(n.read_text(encoding="utf-8"))]
            if (cpath in targets or cpath.split("/")[-1] in targets) and n.stem not in listed:
                miss.append(n.stem)
        if miss:
            warnings.append(f"{cpath}.md: 「出现在」漏收 {len(miss)} 篇 → {miss[0]} 等")


def check_folder_sizes():
    counts = defaultdict(int)
    for p in (ROOT / "notes").rglob("*.md"):
        counts[p.parent.relative_to(ROOT).as_posix()] += 1
    for folder, n in sorted(counts.items()):
        if folder.startswith(FOLDER_CAP_EXEMPT):
            continue
        if n > MAX_FOLDER_NOTES:
            warnings.append(
                f"{folder}/: {n} 篇(上限 {MAX_FOLDER_NOTES})——该拆了,"
                "**在这个文件夹里面开子文件夹**,别在 notes/ 下平铺出新顶层"
            )


def check_top_folder_count():
    """顶层宽度上限。MAX_FOLDER_NOTES 只封了单个文件夹能有多宽,不封文件夹**数量**:
    每满 12 篇就在 notes/ 下平铺一个新文件夹,一年后文件树比笔记本身还难翻
    (2026-08-16 按当时 9 篇/周算过,一年 ~470 篇 = 40 个顶层文件夹)。
    lint 数的是直接父目录,所以嵌套天然不受罚——拆分往深里走,顶层锁在这个数。"""
    d = ROOT / "notes"
    if not d.is_dir():
        return
    tops = sorted(x.name for x in d.iterdir() if x.is_dir())
    if len(tops) > MAX_TOP_FOLDERS:
        warnings.append(
            f"notes/ 顶层 {len(tops)} 个文件夹(上限 {MAX_TOP_FOLDERS})——"
            f"该把近邻主题合并、或收进同一个大类下面了:{'、'.join(tops)}"
        )


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
    check_concept_backlinks(concept_names)
    check_folder_sizes()
    check_top_folder_count()
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
