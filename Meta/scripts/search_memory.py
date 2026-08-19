#!/usr/bin/env python3
"""全库搜索 —— 按相关度排序,不是 grep 那种"有没有出现过"。

为什么不是 grep:grep 只会告诉你"这个词在不在",一个词命中 20 个文件时
它把 20 行平铺给你,你还是不知道该看哪篇。这个脚本用 BM25 给每篇打分:
罕见词权重高、命中多次加分、长文件不因为字多就占便宜,然后按分数排序。

为什么不是向量语义搜索:向量要么调 API(要 key、要钱、要联网,而且这个库的
设计前提是纯 Markdown + Git、任何 AI 都能接入,不该多一个外部依赖),要么本地
跑模型(要装几百 MB 的东西)。库到几百条之前,BM25 + 概念别名扩展的效果和
向量差不了多少,而依赖是零。真到了需要向量的规模,升级路径写在文件末尾。

"语义"这一半靠概念页做:查询词命中某个概念页的名字或 aliases 时,自动把
它的其他别名一起加进查询。所以搜"怕气氛尴尬"能带出挂着 [[间歇性强化]]、
[[客服模式]] 的笔记,而不只是字面出现过这四个字的。

用法:
    python3 Meta/scripts/search_memory.py 查询词
    python3 Meta/scripts/search_memory.py "怕气氛尴尬" -n 10
    python3 Meta/scripts/search_memory.py 边界 --all      # 连 Archive/ 一起搜
"""

import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DIRS = ["Notes", "Concepts", "Profile", "Diary"]
CJK = re.compile(r"[一-鿿]")
WORD = re.compile(r"[a-zA-Z][a-zA-Z0-9_.-]*")
FM = re.compile(r"^---\n(.*?)\n---", re.S)


def tokens(text: str) -> list:
    """中文切二元组、英文按词切。

    中文没有空格,按单字切会让"的""是"这种字淹没一切,按二元组切("边界感"
    → 边界/界感)不需要分词库就能保住大部分词的形状,对这个体量足够用。
    """
    out = [w.lower() for w in WORD.findall(text)]
    cjk = CJK.findall(text)
    # 逐字扫,只在相邻两个字都是中文时才成组,避免把跨标点的两个字粘起来
    chars = [c if CJK.match(c) else " " for c in text]
    for a, b in zip(chars, chars[1:]):
        if a != " " and b != " ":
            out.append(a + b)
    out.extend(cjk)
    return out


def concept_expansion() -> dict:
    """{名字或别名: [该概念的全部叫法]} —— 查询扩展用。"""
    table = {}
    d = ROOT / "Concepts"
    if not d.is_dir():
        return table
    for p in sorted(d.glob("*.md")):
        names = [p.stem]
        m = FM.match(p.read_text(encoding="utf-8"))
        if m:
            for line in m.group(1).splitlines():
                if line.startswith("aliases:"):
                    raw = line.partition(":")[2].strip().strip("[]")
                    names += [x.strip().strip("\"'") for x in raw.split(",") if x.strip()]
        for n in names:
            table.setdefault(n, set()).update(names)
    return {k: sorted(v) for k, v in table.items()}


def collect(include_archive: bool) -> list:
    dirs = DIRS + (["Archive"] if include_archive else [])
    docs = []
    for d in dirs:
        base = ROOT / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            if p.name == "README.md":
                continue
            text = p.read_text(encoding="utf-8")
            docs.append((p.relative_to(ROOT).as_posix(), text, tokens(text)))
    return docs


def best_line(text: str, terms: set) -> str:
    """挑一行最能说明为什么命中的原文,而不是从头截一段。"""
    best, score = "", 0
    for line in text.splitlines():
        s = line.strip().lstrip("#->*| ").strip()
        if len(s) < 10 or s.startswith("---"):
            continue
        hit = sum(1 for t in terms if t in s)
        if hit > score:
            best, score = s, hit
    return best


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print(__doc__)
        return
    topn = 8
    if "-n" in sys.argv:
        topn = int(sys.argv[sys.argv.index("-n") + 1])
        args = [a for a in args if a != str(topn)]
    query = " ".join(args)

    expand = concept_expansion()
    extra = []
    for name, group in expand.items():
        if name in query:
            extra += [g for g in group if g not in query]
    if extra:
        print(f"(顺着概念页扩展了查询:{'、'.join(sorted(set(extra)))})")

    q = tokens(query + " " + " ".join(extra))
    docs = collect("--all" in sys.argv)
    if not docs:
        print("没有可搜索的文件")
        return

    # BM25:df 越小的词权重越高,tf 有饱和(k1),长文件被 b 折价
    N = len(docs)
    avg = sum(len(t) for _, _, t in docs) / N
    df = Counter()
    for _, _, t in docs:
        df.update(set(t))
    k1, b = 1.5, 0.75

    scored = []
    for rel, text, toks in docs:
        tf = Counter(toks)
        s = 0.0
        for term in set(q):
            if term not in tf:
                continue
            idf = math.log(1 + (N - df[term] + 0.5) / (df[term] + 0.5))
            f = tf[term]
            s += idf * f * (k1 + 1) / (f + k1 * (1 - b + b * len(toks) / avg))
        if s > 0:
            scored.append((s, rel, text))
    scored.sort(reverse=True, key=lambda x: x[0])

    if not scored:
        print(f"没搜到:{query}")
        return
    qset = {t for t in q if len(t) >= 2}
    print(f"\n🔎 {query} —— {len(scored)} 篇命中,按相关度前 {min(topn, len(scored))} 篇\n")
    for s, rel, text in scored[:topn]:
        print(f"  {s:5.1f}  {rel}")
        line = best_line(text, qset)
        if line:
            print(f"         ↳ {line[:110]}")
    print()


# 什么时候该换成向量语义搜索:
# 当"我记得写过一个意思,但想不起用了哪个词"这件事反复发生,而且换词重搜也搜不到
# 的时候。那说明字面重合已经不够用了。届时的最小改法是加一个 --semantic 开关,
# 用嵌入模型把每篇算成一个向量存进 Meta/.embeddings.json,查询时算余弦相似度,
# 和上面的 BM25 分数加权合并(混合检索通常比纯向量更稳)。BM25 这条路留着别删。

if __name__ == "__main__":
    main()
