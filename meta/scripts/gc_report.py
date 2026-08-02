#!/usr/bin/env python3
"""GC 的机械工单 —— lint 管不到的那些。

分工:
  lint_memory.py  管**结构正确性**(断链、frontmatter、图谱形状),会亮红灯
  gc_report.py    管**时间和规模**(过期、积压、该合并了、该瘦身了),只报数

设计原则和 lint 一样:便宜、机械、不靠人记得。**只报事实,不替用户做判断**——
尤其不主动建议删除任何 🧠 核心层内容。

用法:python3 meta/scripts/gc_report.py
"""

import datetime
import difflib
import re
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TODAY = datetime.date.today()
WIKILINK = re.compile(r"\[\[([^\]|#^]+)")

PROFILE_STALE_DAYS = 90   # 画像页多久没动就提一句
MAX_NOTE_LINES = 150      # 超过就提示瘦身或拆分
MERGE_SHARED_CONCEPTS = 3 # 同文件夹内共享这么多概念 → 同族合并候选
OPEN_Q_BACKLOG = 4        # 单个概念页开放问题堆到这个数 → 提示挑一条推进
STALE_SURFACED_DAYS = 120 # 这么久没被工作台抽中过 → 列出来(不建议删,只是让它被看见)
NAME_SIMILARITY = 0.5     # 概念名相似度超过这个 → 提示考虑 aliases 收编

# profile 正文里的时间承诺。只认真正的截止表达——"(2026-07-25)"那种出处日期
# 满仓都是,当承诺抓会把这一节淹掉,不如不做。
DEADLINE = re.compile(
    r"(窗口|截止|deadline|之前完成|前完成|计划于|预计.{0,4}完成|目标日期)[^。;\n]{0,40}?"
    r"(20\d{2})[-年](\d{1,2})[-月](\d{1,2})?"
    r"|(20\d{2})[-年](\d{1,2})[-月](\d{1,2})?[^。;\n]{0,20}?(窗口|截止|之前完成|前完成)"
)


def fm(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    out = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line and not line[:1].isspace():
                k, _, v = line.partition(":")
                out[k.strip()] = v.strip()
    return out


def date_of(s):
    try:
        return datetime.date.fromisoformat(s.strip()[:10])
    except Exception:
        return None


def section(title, rows, hint=""):
    print(f"\n## {title}({len(rows)})")
    if hint and rows:
        print(f"   {hint}")
    for r in rows:
        print(f"   - {r}")
    if not rows:
        print("   (无)")


def main():
    notes = sorted((ROOT / "notes").rglob("*.md"))
    print(f"# GC 机械工单 · {TODAY}")

    # 1. 画像过期
    stale = []
    for p in sorted((ROOT / "profile").glob("*.md")):
        d = date_of(fm(p.read_text(encoding="utf-8")).get("updated", ""))
        if d and (TODAY - d).days > PROFILE_STALE_DAYS:
            stale.append(f"{p.name}:{(TODAY - d).days} 天没动(updated: {d})")
    section("画像页可能过期", stale, "只是提醒去看一眼,没变化就把 updated 往前挪,不用硬改内容")

    # 2. 参考层到期
    expired, no_exp = [], []
    for p in notes:
        f = fm(p.read_text(encoding="utf-8"))
        rel = p.relative_to(ROOT).as_posix()
        if f.get("tier") != "参考":
            continue
        d = date_of(f.get("expires", ""))
        if d is None:
            no_exp.append(rel)
        elif d <= TODAY:
            expired.append(f"{rel}(expires: {d})")
    section("📖 参考层已到期", expired, "问用户一句「这条还要吗」;要就把 expires 往后推,不要就归档。核心/方法层不进这个名单")
    section("📖 参考层还没设 expires", no_exp, "补一个日期即可,不用现在判断内容")

    # 3. 超长笔记
    fat = []
    for p in notes:
        n = len(p.read_text(encoding="utf-8").splitlines())
        if n > MAX_NOTE_LINES:
            fat.append(f"{p.relative_to(ROOT).as_posix()}:{n} 行")
    section("笔记偏长,考虑瘦身或拆分", fat,
            "瘦身规则:保留用户原话/结论/⚠️张力,把 AI 的论证过程压成一句。手册型笔记可以豁免")

    # 4. 同族合并候选
    by_folder = defaultdict(list)
    for p in notes:
        cs = {t.strip().split("|")[0] for t in WIKILINK.findall(p.read_text(encoding="utf-8"))
              if t.strip().startswith("concepts/")}
        by_folder[p.parent.relative_to(ROOT).as_posix()].append((p, cs))
    pairs = []
    for folder, items in sorted(by_folder.items()):
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                shared = items[i][1] & items[j][1]
                if len(shared) >= MERGE_SHARED_CONCEPTS:
                    pairs.append(f"{items[i][0].stem} × {items[j][0].stem} "
                                 f"(共享 {len(shared)} 个概念:{', '.join(sorted(x.split('/')[-1] for x in shared))})")
    section("同族合并候选", pairs,
            "共享概念多 ≠ 该合并。先读一遍:真重复就合并成主笔记+差异点,只是同主题就别动")

    # 5. 开放问题积压
    backlog = []
    for p in sorted((ROOT / "concepts").glob("*.md")):
        t = p.read_text(encoding="utf-8")
        m = re.search(r"^## 开放问题.*$", t, re.M)
        if not m:
            continue
        rest = t[m.end():]
        nxt = re.search(r"^## ", rest, re.M)
        n = len([l for l in (rest[:nxt.start()] if nxt else rest).splitlines() if l.startswith("- ")])
        if n >= OPEN_Q_BACKLOG:
            backlog.append(f"{p.stem}:{n} 条")
    section("概念页开放问题积压", backlog, "挑一条丢进工作台碰撞,不要一次清空——问题区本来就只增不减")

    # 5b. 画像正文里已经过期的时间承诺
    promises = []
    for p in sorted((ROOT / "profile").glob("*.md")):
        for line in p.read_text(encoding="utf-8").splitlines():
            m = DEADLINE.search(line)
            if not m:
                continue
            g = [x for x in m.groups() if x and x.isdigit()]
            if len(g) < 2:
                continue
            dt = date_of(f"{g[0]}-{int(g[1]):02d}-{int(g[2]) if len(g) > 2 else 1:02d}")
            if dt and dt < TODAY:
                promises.append(f"{p.name}:{line.strip()[:90]}…(锚点 {dt},已过)")
    section("画像里已经过期的时间承诺", promises,
            "updated 是新的不代表正文里写的窗口没过期。只问一句现在什么情况,不替用户改结论")

    # 5c. source 外链存活(默认跳过,--net 才真去访问)
    urls = {}
    for p in notes + sorted((ROOT / "sources").glob("*.md")):
        f = fm(p.read_text(encoding="utf-8"))
        for v in (f.get("source", ""), f.get("原文位置", "")):
            for u in re.findall(r"https?://[^\s,,)]+", v):
                urls.setdefault(u, p.relative_to(ROOT).as_posix())
    if "--net" in sys.argv:
        dead = []
        for u, owner in urls.items():
            try:
                req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "memory-gc"})
                code = urllib.request.urlopen(req, timeout=10).status
                if code >= 400:
                    dead.append(f"{code} {u} ← {owner}")
            except Exception as e:
                dead.append(f"访问失败({type(e).__name__}) {u} ← {owner}")
        section("source 外链已失效", dead,
                "别删链接,在 source 后面标注「原链接已失效(日期)」——出处失效本身是要记录的事实")
    else:
        print(f"\n## source 外链({len(urls)} 条)")
        print("   加 --net 才真去访问(GC 里跑,平时别跑,慢)")

    # 5d. 久未被工作台抽中
    cold = []
    for p in notes:
        f = fm(p.read_text(encoding="utf-8"))
        d = date_of(f.get("last-surfaced", ""))
        if d is None or (TODAY - d).days > STALE_SURFACED_DAYS:
            cold.append((p.relative_to(ROOT).as_posix(), (TODAY - d).days if d else None))
    if all(n is None for _, n in cold) and len(cold) == len(notes):
        print(f"\n## 久未在工作台露面(—)")
        print("   last-surfaced 字段刚引入,工作台还没写过。等抽过几轮才有意义,本期跳过")
    else:
        shown = [f"{r}({n} 天没抽中)" if n else f"{r}(还没被抽中过)" for r, n in cold[:15]]
        if len(cold) > 15:
            shown.append(f"…还有 {len(cold) - 15} 篇")
        section("久未在工作台露面", shown,
                "⚠️ 这不是删除名单。目的是让沉底的笔记被看见——抽卡时优先从这里挑")

    # 5e. 概念名近义
    names = {}
    for p in sorted((ROOT / "concepts").glob("*.md")):
        f = fm(p.read_text(encoding="utf-8"))
        al = f.get("aliases", "")
        al = [a.strip() for a in al.strip("[]").split(",") if a.strip()] if al else []
        names[p.stem] = [p.stem] + al
    close = []
    keys = sorted(names)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            best = max(difflib.SequenceMatcher(None, a, b).ratio()
                       for a in names[keys[i]] for b in names[keys[j]])
            if best >= NAME_SIMILARITY:
                close.append(f"{keys[i]} × {keys[j]}(相似度 {best:.2f})")
    section("概念名近义,考虑 aliases 收编", close,
            "像 ≠ 是同一个。真是同义 → 合并进一页的 aliases 并改写旧链接;是对立面/子集 → 什么都不做,在「相关概念」互相指一下就够")

    # 6. sources 覆盖
    srcs = {p.stem for p in (ROOT / "sources").glob("*.md") if p.stem != "README"}
    print(f"\n## sources 映射表({len(srcs)} 份)")
    print("   本周如果用户发过导出原文,检查有没有建对照表;没有就补(见 sources/README.md)")

    # 7. 分层与出口
    tiers = defaultdict(int)
    published = 0
    for p in notes:
        f = fm(p.read_text(encoding="utf-8"))
        tiers[f.get("tier", "未分层")] += 1
        if f.get("published"):
            published += 1
    print(f"\n## 分层与出口")
    print(f"   🧠核心 {tiers['核心']} / 🔧方法 {tiers['方法']} / 📖参考 {tiers['参考']}"
          + (f" / ⚠️未分层 {tiers['未分层']}" if tiers["未分层"] else ""))
    print(f"   已发布 {published} 篇;可发候选跑 publish_candidates.py 看")
    arch = len([p for p in (ROOT / "archive").glob("*.md") if p.stem != "README"]) if (ROOT / "archive").is_dir() else 0
    print(f"   已归档 {arch} 篇")

    # 8. 杂物
    junk = [p.name for p in (ROOT / ".trash").glob("*") ] if (ROOT / ".trash").is_dir() else []
    section(".trash 残留", junk, "Obsidian 的回收站,清不清由用户定;conflict-files-* 是两端撞车的物证,别急着删")


if __name__ == "__main__":
    main()
