#!/usr/bin/env python3
"""工作台「📰 简讯」的机器体检:日更提交之前跑,不过退出码 1。

简讯是工作台里唯一一块内容来自库外、而且每天都会过期的东西,最怕的是两种静默坏法:
- **链接是编的**。模型凭记忆写一条"像新闻"的标题配一个像样的 URL,页面上看不出来。
  机器验不了真假,但能逼格式:每条必须有来源链接,没链接的条直接拦。
- **天天同一批**。生成是冷启动,搜不到新东西时最省事的是把昨天的几条换个说法再写一遍。
  拿上一版 Home.md 的链接对一遍,撞了就拦。

版面也一起查,因为 workbench.css 是按结构认的(第一段粗体=标题行,其余段=正文),
结构一歪样式就跟着歪,而且不报错:
  > [!feed] 📰 简讯
  > **原文标题**
  > 中文标题 · [来源](https://...)
  >
  > 据报道……影响:……
  >
  > ---
  > (下一条)

链接还要和 `.news-candidates.md`(fetch_news.py 拉的固定源 RSS)对账:
简讯里每个链接都必须在清单里。清单不在时本地只警告;CI 里清单不在还写了链接,
说明没走固定源,直接拦。

位置也查:用户要它排在 ✅ 每日习惯卡正上方,夹在两个 dataviewjs 块中间,
AI 重写页面时最容易把它挪到底下和其他 callout 待在一起。

「影响:」讲这事会带来什么变化,每条必须有(用户靠它看懂国家大事)。落在国家、社会、
国际格局还是普通人看情况——它的前身「对你:」先被写成每条都硬扯到车,改成"对普通人"
之后又每条硬找一条传导到老百姓的路,所以标签改成中性的「影响」。
车那条坑还在,另拦「影响」提到车的超过 1 条。

用户要每期 4 条、其中固定 1 条中国的:清单「## 中国」那组有候选时,
简讯里至少一个链接得来自那一组,一条都没有就拦。

用法:check_news_brief.py   (读仓库根目录 Home.md)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
HOME = ROOT / "Home.md"
CANDIDATES = ROOT / ".news-candidates.md"

TITLE_RE = re.compile(r"^> \[!feed\][+-]? 📰 简讯")
HABITS_RE = re.compile(r"^```dataviewjs\n// ✅ 每日习惯", re.M)
SOURCE_RE = re.compile(r"^.+ · \[[^\]]+\]\((https?://[^)\s]+)\)\s*$")
URL_RE = re.compile(r"\]\((https?://[^)\s]+)\)")
EMPTY_MARK = "今日未抓到"
MAX_ITEMS = 4
CAR_RE = re.compile(r"汽车|车企|车市|车机|车型|电动车|新能源车|中国车|买车|座舱|HMI|智驾|出海")  # 行业词;「打车」这类日常出行不算


def group_links(pool: str, group: str) -> set[str]:
    """候选清单里某一组(## 标题)下的全部链接。"""
    m = re.search(rf"^## {group}\n(.*?)(?=^## |\Z)", pool, re.M | re.S)
    return set(re.findall(r"\| (https?://\S+) \|", m.group(1))) if m else set()


def feed_block(text: str) -> tuple[int, int, list[str]] | None:
    """返回 (起始行号, 结束行号, 去掉 '> ' 前缀的正文行)。"""
    lines = text.split("\n")
    starts = [i for i, l in enumerate(lines) if TITLE_RE.match(l)]
    if len(starts) != 1:
        return None
    s = starts[0]
    e = s + 1
    while e < len(lines) and lines[e].startswith(">"):
        e += 1
    body = [re.sub(r"^> ?", "", l) for l in lines[s + 1 : e]]
    return s, e, body


def split_items(body: list[str]) -> list[list[str]]:
    items, cur = [], []
    for l in body:
        if l.strip() == "---":
            items.append(cur)
            cur = []
        else:
            cur.append(l)
    items.append(cur)
    return [[l for l in it] for it in items if any(x.strip() for x in it)]


def check_item(n: int, item: list[str]) -> list[str]:
    errs = []
    lines = [l for l in item]
    while lines and not lines[0].strip():
        lines.pop(0)
    if len(lines) < 2:
        return [f"第 {n} 条太短:至少要有粗体标题行和「中文标题 · [来源](链接)」行"]
    if not re.fullmatch(r"\*\*[^*].*\*\*\s*", lines[0]):
        errs.append(f"第 {n} 条第一行不是 **粗体标题**:{lines[0][:40]}")
    if not SOURCE_RE.match(lines[1]):
        errs.append(f"第 {n} 条第二行不是「中文标题 · [来源](https://…)」:{lines[1][:60]}")
    paras = "\n".join(lines[2:]).split("\n\n")
    paras = [p.strip() for p in paras if p.strip()]
    if not paras:
        errs.append(f"第 {n} 条没有正文段")
    else:
        if any(p.startswith("**") for p in paras):
            errs.append(f"第 {n} 条正文段不能以粗体开头(CSS 会把它当成标题行)")
        if not re.search(r"影响[::]", "\n".join(paras)):
            errs.append(f"第 {n} 条正文里没有「影响:」那句(这事会带来什么变化)")
    return errs


def links_to_car(item: list[str]) -> bool:
    """这条的「影响:」那句有没有往车上扯。"""
    m = re.search(r"影响[::]([^\n]*)", "\n".join(item))
    return bool(m and CAR_RE.search(m.group(1)))


def previous_urls(text: str) -> set[str]:
    """上一版(HEAD)Home.md 简讯里的链接;同一天重跑时 HEAD 就是今天自己,不比。"""
    try:
        old = subprocess.run(
            ["git", "-c", "core.quotepath=false", "show", "HEAD:Home.md"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()
    gen = lambda t: (re.search(r"^generated:\s*(\S+)", t, re.M) or [None, None])[1]
    if gen(old) == gen(text):
        return set()
    blk = feed_block(old)
    return set(URL_RE.findall("\n".join(blk[2]))) if blk else set()


def main() -> int:
    text = HOME.read_text(encoding="utf-8")
    blk = feed_block(text)
    if blk is None:
        n = sum(1 for l in text.split("\n") if TITLE_RE.match(l))
        print(f"✗ Home.md 里 `> [!feed] 📰 简讯` 应该正好一张,现在 {n} 张", file=sys.stderr)
        return 1
    s, e, body = blk
    errs = []

    after = "\n".join(text.split("\n")[e:]).lstrip("\n")
    if not HABITS_RE.match(after):
        errs.append("简讯卡必须紧挨在 ✅ 每日习惯那个 dataviewjs 块正上方(中间只许空行)")

    items = split_items(body)
    joined = "\n".join(body)
    if EMPTY_MARK in joined and not URL_RE.search(joined):
        print(f"⚠ 简讯今天是空的(写了「{EMPTY_MARK}」),放行")
    else:
        if not 1 <= len(items) <= MAX_ITEMS:
            errs.append(f"简讯应为 1–{MAX_ITEMS} 条(平时正好 4 条),现在 {len(items)} 条")
        for i, it in enumerate(items, 1):
            errs += check_item(i, it)
        car = [i for i, it in enumerate(items, 1) if links_to_car(it)]
        if len(car) > 1:
            errs.append(f"第 {car} 条的「影响」都扯到了车——「影响」讲这事本身带来的变化,别往车上扯(用户:不要强行关联)")
        if len(items) < MAX_ITEMS:
            print(f"⚠ 简讯只有 {len(items)} 条(平时 4 条);搜不到就少写是对的,别硬凑")

        urls = URL_RE.findall(joined)
        dup = [u for u in set(urls) if urls.count(u) > 1]
        if dup:
            errs.append(f"同一个链接出现了不止一次:{dup}")
        if CANDIDATES.exists():
            pool = CANDIDATES.read_text(encoding="utf-8")
            outside = [u for u in urls if u not in pool]
            if outside:
                errs.append(f"这些链接不在今天的候选清单 .news-candidates.md 里(只许从清单挑):{outside}")
            china = group_links(pool, "中国")
            if china and not china & set(urls):
                errs.append("没有中国的新闻:候选清单「## 中国」那组有候选,简讯里至少要有 1 条来自那组")
        elif os.environ.get("GITHUB_ACTIONS") == "true":
            errs.append("CI 里找不到 .news-candidates.md,简讯却写了链接——没走固定源")
        else:
            print("⚠ 本地没有 .news-candidates.md,跳过链接对账(先跑 fetch_news.py 才能对)")
        stale = set(urls) & previous_urls(text)
        if stale:
            errs.append(f"和上一期简讯撞了链接(天天同一批):{sorted(stale)}")

    if errs:
        for x in errs:
            print("✗ " + x, file=sys.stderr)
        return 1
    print(f"✓ 简讯 {len(items)} 条,版式和位置都对")
    return 0


if __name__ == "__main__":
    sys.exit(main())
