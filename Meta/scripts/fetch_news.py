#!/usr/bin/env python3
"""工作台「📰 简讯」的候选清单:日更里 Claude 开工之前,用纯脚本拉固定几家新闻源的 RSS。

原来让模型自己 WebSearch + 一篇篇 WebFetch 找新闻,一次几十次抓取、上万 token,
而且搜索对"当天新闻"很弱(常返回旧闻、日期不明),AP/BBC/路透还常常抓不开。
RSS 把标题、链接、发布时间、摘要都给好了——哪条是 48 小时内的是时间戳比较,
不需要判断力,和挑画作同一个思路:机械的部分不交给模型。

产物 `.news-candidates.md`(仓库根目录,不入库):按「国际/中国/财经/科技/汽车」分组,
每条一行。Claude 只从这里挑(选中的再打开正文读),**链接只能用清单里的**——
check_news_brief.py 会逐条对账,清单外的链接直接拦,编链接这条路就堵死了。

某个源挂了只跳过它,不让整轮日更失败;全挂了退出码 1(工作流里 continue-on-error,
简讯那天写「今日未抓到可靠新闻」)。

用法:fetch_news.py [--hours 48]
"""

from __future__ import annotations

import datetime as dt
import email.utils
import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / ".news-candidates.md"

# 固定来源。改这里就是改简讯的视野;每组几家互相补位,一家挂了不至于整组空掉。
# 入选标准是两条都过:RSS 拉得到,而且 read_article.py 能从文章页抽出完整正文
# (2026-10-21 实测:SCMP 只给导语、正文在付费墙后;NPR、CNBC、France 24、FT 整页 403;
# The Verge 抽出来夹着大量订阅按钮文字——都删了。WebFetch 对卫报、DW、CNA 直接拒抓,
# 所以读正文走 read_article.py,不走 WebFetch)。加新源前先用它试三篇。
# 汽车组只占简讯 1 条(用户明确说过汽车别多),所以只留两家。
FEEDS = {
    "国际": [
        ("BBC", "https://feeds.bbci.co.uk/news/world/rss.xml"),
        ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
        ("DW", "https://rss.dw.com/rdf/rss-en-all"),
        ("德国之声中文", "https://rss.dw.com/rdf/rss-chi-all"),
        ("CNA Asia", "https://www.channelnewsasia.com/rssfeeds/8395744"),
    ],
    # 简讯固定要 1 条中国新闻,check_news_brief.py 认的就是这一组的链接,所以这组只放中国。
    # 一家外媒视角、一家官方视角,互相补位。
    "中国": [
        ("Guardian China", "https://www.theguardian.com/world/china/rss"),
        ("CGTN China", "https://www.cgtn.com/subscribe/rss/section/china.xml"),
    ],
    "财经": [
        ("Guardian Business", "https://www.theguardian.com/business/rss"),
        ("BBC Business", "https://feeds.bbci.co.uk/news/business/rss.xml"),
        ("CNA Business", "https://www.channelnewsasia.com/rssfeeds/8395954"),
    ],
    "科技": [
        ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
        ("BBC Tech", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ],
    "汽车": [
        ("CnEVPost", "https://cnevpost.com/feed/"),
        ("electrive", "https://www.electrive.com/feed/"),
    ],
}
PER_FEED = 8  # 每家最多几条:候选太多,读清单本身就成了 token 大头
SUMMARY_CHARS = 140


def text_of(el, *names):
    for n in names:
        for child in el:
            if child.tag.split("}")[-1] == n and (child.text or child.attrib.get("href")):
                return (child.text or child.attrib.get("href") or "").strip()
    return ""


def parse_date(s: str) -> dt.datetime | None:
    if not s:
        return None
    try:
        d = email.utils.parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def clean(s: str) -> str:
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    s = re.sub(r"\s+", " ", s).strip()
    return s[:SUMMARY_CHARS] + ("…" if len(s) > SUMMARY_CHARS else "")


def fetch(url: str) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (memory-workbench)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        root = ET.fromstring(r.read())
    items = []
    for el in root.iter():
        if el.tag.split("}")[-1] not in ("item", "entry"):
            continue
        link = text_of(el, "link")
        if not link:
            for child in el:
                if child.tag.split("}")[-1] == "link" and child.attrib.get("href"):
                    link = child.attrib["href"]
        items.append({
            "title": clean(text_of(el, "title")),
            "link": link.strip(),
            "date": parse_date(text_of(el, "pubDate", "date", "published", "updated")),
            "summary": clean(text_of(el, "description", "summary", "encoded")),
        })
    return items


def main() -> int:
    hours = int(sys.argv[sys.argv.index("--hours") + 1]) if "--hours" in sys.argv else 48
    now = dt.datetime.now(dt.timezone.utc)
    cutoff = now - dt.timedelta(hours=hours)
    seen, out, ok, dead = set(), [], 0, []
    bj = dt.timezone(dt.timedelta(hours=8))

    out.append(f"# 简讯候选 · 拉取于 {now.astimezone(bj):%Y-%m-%d %H:%M} 北京时间 · 近 {hours} 小时\n")
    out.append("只从这里挑;链接原样用,check_news_brief.py 会对账。格式:时间 | 来源 | 标题 | 链接 | 摘要\n")
    for group, feeds in FEEDS.items():
        out.append(f"\n## {group}\n")
        for name, url in feeds:
            try:
                items = fetch(url)
            except Exception as e:  # 一家挂了跳过,别让整轮失败
                dead.append(f"{name}({type(e).__name__})")
                continue
            ok += 1
            fresh = [i for i in items if i["link"] and i["date"] and i["date"] >= cutoff]
            fresh.sort(key=lambda i: i["date"], reverse=True)
            for i in fresh[:PER_FEED]:
                if i["link"] in seen:
                    continue
                seen.add(i["link"])
                out.append(
                    f"- {i['date'].astimezone(bj):%m-%d %H:%M} | {name} | {i['title']} | {i['link']} | {i['summary']}"
                )
    if dead:
        out.append(f"\n> 今天没拉到:{'、'.join(dead)}")
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"简讯候选 {len(seen)} 条,{ok} 个源可用" + (f",挂了:{'、'.join(dead)}" if dead else ""))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
