#!/usr/bin/env python3
"""挑出「可以发出去」的候选笔记 —— 机械筛选,不靠人想得起来。

一条笔记有三种状态,这个脚本把它们分开:
- **未动**:符合筛选标准、`Works/` 里没有稿子、也没发过 → 真正的候选
- **在写**:`Works/` 里已经有稿子引用了它 → 从候选池里挪走,不再重复提醒
- **已发**:frontmatter 有 `published:` → 不再进候选

「在写」怎么认出来:扫 `Works/**/*.md` 正文里出现的 `Notes/xxx.md`、
`Concepts/xxx.md` 纯文本路径(Works/ 引用笔记本来就是这个写法,见
`Works/README.md`);笔记那侧也可以主动写一行 `draft: Works/xxx.md`,两边都认。

筛选标准:
- tier: 核心 —— 只有自己的判断值得发,外部知识发出去没有辨识度
- 没在写、也没发过

张力不再是硬门槛,只做排序:带「开放问题」或 ⚠️ 张力标记的排在前面、并挑出钩子,
因为写作定位是「从冲突开始,不要从观点开始」,张力天生是冲突形状、最好起笔。
没张力的核心笔记照样进池子(排在后面、不给钩子),只是选题卡里「冲突在哪」那栏会空,
开头得自己找 —— 由用户手动决定要不要写。

概念页单独列一组:一个概念页的「定义 + 开放问题」本身就是一篇短文的骨架。

`Works/选题/` 是每周机器人推的选题卡,不算稿子——它引用来源笔记只是为了说明推荐理由,
**不能当成"在写"**。否则机器人每推一条,候选池就少一条,推满一年池子自己空了,
而用户一个字都没写。它要变成"在写",得由用户把文件 `git mv` 出这个目录(见 Works/README.md)。

用法:python3 Meta/scripts/publish_candidates.py [--all|--sync|--count]
      --all   连同已发布的一起列出,用来回看发过什么
      --count 只吐 `notes=N concepts=M`,给 weekly-writing-pick.yml 判断池子空没空。
              有这个口子是因为拿 grep 去匹配上面那些人读的标题,标题一改就静默失灵
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TENSION = re.compile(r"⚠️|张力|开放问题|只列不调和|评价相反")


def frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line[:1].isspace():
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def hooks(text: str) -> list:
    """把能直接当开头用的那几句挑出来——不是摘要,是钩子。"""
    out = []
    for line in text.splitlines():
        s = line.strip().lstrip("-•* ").strip()
        if len(s) < 12 or s.startswith("#"):
            continue
        if TENSION.search(s):
            out.append(re.sub(r"\[\[([^\]|#^]+)\|?([^\]]*)\]\]", lambda m: m.group(2) or m.group(1).rsplit("/", 1)[-1], s))
        if len(out) >= 2:
            break
    return out


REF = re.compile(r"(?:Notes|Concepts)/[^\s)）】」』,,;;、\]]+\.md")

PICKS = "Works/选题"  # 机器人推的选题卡,不是稿子;理由见模块开头


def works_md():
    """Works/ 下算作「稿子」的文件 —— 排除 README 和机器人的选题卡。"""
    works = ROOT / "Works"
    if not works.exists():
        return
    for w in sorted(works.rglob("*.md")):
        rel = w.relative_to(ROOT).as_posix()
        if w.name == "README.md" or rel.startswith(PICKS + "/"):
            continue
        yield w, rel


def drafted() -> dict:
    """Works/ 里每篇稿子引用了哪些笔记 —— 返回 {笔记路径: [稿子路径, ...]}。"""
    out = {}
    for w, rel in works_md():
        for ref in set(REF.findall(w.read_text(encoding="utf-8"))):
            out.setdefault(ref, []).append(rel)
    return out


# 冒号后面只吃空格和 tab,不吃换行:原来写 \s* 时,一行空的 `published:` 会让它
# 跨行吃到下一行,把 frontmatter 的结束符 `---` 当成渠道名,--sync 时静默写进
# 来源笔记的 frontmatter。开头要求 \S 保证空值不匹配
PUB = re.compile(r"^(?:published|已发)[::][ \t]*(\S.*?)[ \t]*$", re.M)


def works_published() -> dict:
    """稿子里写了 `published: 渠道 日期` 的,把它带给这篇稿子的所有来源笔记。

    返回 {笔记路径: (渠道日期, 稿子路径)} —— 让用户只在稿子那边标一次。
    """
    out = {}
    for w, rel in works_md():
        text = w.read_text(encoding="utf-8")
        m = PUB.search(text)
        if not m:
            continue
        for ref in set(REF.findall(text)):
            out.setdefault(ref, (m.group(1), rel))
    return out


def write_published(note: str, value: str) -> bool:
    """往笔记 frontmatter 补一行 published:。已经有了就不动。"""
    p = ROOT / note
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return False
    end = text.index("\n---", 4)
    if re.search(r"^published[::]", text[4:end], re.M):
        return False
    p.write_text(text[:end] + f"\npublished: {value}" + text[end:], encoding="utf-8")
    return True


def orphan_works() -> list:
    """没标任何来源笔记的稿子 —— 不是错,但值得看得见。"""
    return [rel for w, rel in works_md() if not REF.search(w.read_text(encoding="utf-8"))]


def main():
    show_all = "--all" in sys.argv
    do_sync = "--sync" in sys.argv
    count_only = "--count" in sys.argv

    pending = {n: v for n, v in works_published().items()
               if not frontmatter((ROOT / n).read_text(encoding="utf-8")).get("published")
               and (ROOT / n).exists()}
    if pending and not count_only:
        print(f"\n🔁 稿子里标了已发、笔记还没同步({len(pending)} 篇)\n")
        for note, (value, src) in pending.items():
            done = write_published(note, value) if do_sync else False
            print(f"  {'✅ 已写入' if done else '待写入'}  {note}  ← {value}  ({src})")
        if not do_sync:
            print("\n  加 --sync 把这些写进笔记 frontmatter")

    notes, published, concepts, writing = [], [], [], []
    drafts = drafted()

    for p in sorted((ROOT / "Notes").rglob("*.md")):
        text = p.read_text(encoding="utf-8")
        fm = frontmatter(text)
        rel = p.relative_to(ROOT).as_posix()
        if fm.get("published"):
            published.append((rel, fm["published"]))
            continue
        # 笔记自己写的 draft: 和 Works/ 里扫出来的引用,合成一份去向
        where = list(drafts.get(rel, []))
        if fm.get("draft") and fm["draft"] not in where:
            where.append(fm["draft"])
        if where:
            writing.append((rel, where))
            continue
        if fm.get("tier") != "核心":
            continue
        notes.append((rel, hooks(text), bool(TENSION.search(text))))

    # 带张力的排前面(有现成钩子、最好起笔),其余按路径。张力不再是门槛、只是优先级
    notes.sort(key=lambda x: (not x[2], x[0]))

    for p in sorted((ROOT / "Concepts").glob("*.md")):
        text = p.read_text(encoding="utf-8")
        rel = p.relative_to(ROOT).as_posix()
        if frontmatter(text).get("published"):
            continue
        if rel in drafts:
            writing.append((rel, drafts[rel]))
            continue
        m = re.search(r"^## 开放问题.*$", text, re.M)
        if not m:
            continue
        rest = text[m.end():]
        nxt = re.search(r"^## ", rest, re.M)
        qs = [ln.strip()[2:] for ln in (rest[: nxt.start()] if nxt else rest).splitlines() if ln.startswith("- ")]
        if qs:
            concepts.append((p.relative_to(ROOT).as_posix(), qs))

    if count_only:
        print(f"notes={len(notes)} concepts={len(concepts)}")
        return

    print(f"\n🧠 核心层里还没发过的笔记({len(notes)} 篇,带 ⚠️ 的有现成冲突、优先写)\n")
    for rel, hs, ten in notes:
        print(f"  {'⚠️ ' if ten else '   '}{rel}")
        for h in hs:
            print(f"      ↳ {h[:110]}")
    print(f"\n💥 概念页的开放问题({len(concepts)} 页,一条就是一个选题)\n")
    for rel, qs in concepts:
        print(f"  {rel}")
        for q in qs[:2]:
            print(f"      ↳ {q[:110]}")

    print(f"\n✍️ 在写:Works/ 里已经有稿子({len(writing)} 篇,不用再提醒)\n")
    for rel, where in writing:
        print(f"  {rel}")
        for w in where:
            print(f"      → {w}")

    loose = orphan_works()
    if loose:
        print(f"\n📄 Works/ 里没标来源笔记的稿子({len(loose)} 篇)\n")
        for w in loose:
            print(f"  {w}")

    if show_all or published:
        print(f"\n✅ 已发布({len(published)} 篇)\n")
        for rel, where in published:
            print(f"  {where}  {rel}")
    print("\n开始写就在稿子里写一行来源路径(例:Notes/思考/xxx.md),那篇笔记会从候选挪进「在写」;")
    print("发出去之后在笔记 frontmatter 加一行,例:published: 小红书 2026-08-10\n")


if __name__ == "__main__":
    main()
