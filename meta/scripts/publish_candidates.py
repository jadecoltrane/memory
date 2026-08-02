#!/usr/bin/env python3
"""挑出「可以发出去」的候选笔记 —— 机械筛选,不靠人想得起来。

背景(2026-08-02):库里从来只有入口没有出口。同一天写的
notes/动机与自我改变/大量输入没有输出 给了三个练习,但那三个全是私下的,
没有一个会让东西离开硬盘。这个脚本补的就是最后那一步。

筛选标准(三个都要满足):
- tier: 核心 —— 只有自己的判断值得发,外部知识发出去没有辨识度
- 有「开放问题」或 ⚠️ 张力标记 —— 用户的写作定位是「从冲突开始,不要从观点开始」
  (notes/写作/小红书写作定位),而张力/未解问题天生就是冲突形状的
- published 为空 —— 发过的不再进候选

概念页单独列一组:一个概念页的「定义 + 开放问题」本身就是一篇短文的骨架,
而且「同一个概念被我自己评价了三次、三次相反」这种东西全网只有这个库里有。

用法:python3 meta/scripts/publish_candidates.py [--all]
      --all 连同已发布的一起列出,用来回看发过什么
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


def main():
    show_all = "--all" in sys.argv
    notes, published, concepts = [], [], []

    for p in sorted((ROOT / "notes").rglob("*.md")):
        text = p.read_text(encoding="utf-8")
        fm = frontmatter(text)
        rel = p.relative_to(ROOT).as_posix()
        if fm.get("published"):
            published.append((rel, fm["published"]))
            continue
        if fm.get("tier") != "核心" or not TENSION.search(text):
            continue
        notes.append((rel, hooks(text)))

    for p in sorted((ROOT / "concepts").glob("*.md")):
        text = p.read_text(encoding="utf-8")
        if frontmatter(text).get("published"):
            continue
        m = re.search(r"^## 开放问题.*$", text, re.M)
        if not m:
            continue
        rest = text[m.end():]
        nxt = re.search(r"^## ", rest, re.M)
        qs = [ln.strip()[2:] for ln in (rest[: nxt.start()] if nxt else rest).splitlines() if ln.startswith("- ")]
        if qs:
            concepts.append((p.relative_to(ROOT).as_posix(), qs))

    print(f"\n🧠 核心层里带冲突、还没发过的笔记({len(notes)} 篇)\n")
    for rel, hs in notes:
        print(f"  {rel}")
        for h in hs:
            print(f"      ↳ {h[:110]}")
    print(f"\n💥 概念页的开放问题({len(concepts)} 页,一条就是一个选题)\n")
    for rel, qs in concepts:
        print(f"  {rel}")
        for q in qs[:2]:
            print(f"      ↳ {q[:110]}")

    if show_all or published:
        print(f"\n✅ 已发布({len(published)} 篇)\n")
        for rel, where in published:
            print(f"  {where}  {rel}")
    print("\n发出去之后在那篇 frontmatter 加一行,例:published: 小红书 2026-08-10\n")


if __name__ == "__main__":
    main()
