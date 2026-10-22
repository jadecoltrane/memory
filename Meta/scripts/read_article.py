#!/usr/bin/env python3
"""工作台「📰 简讯」读正文:日更里模型挑好 4 条后,用它把每条的正文抽成纯文本。

为什么不用 WebFetch:实测它对卫报、DW、CNA、海峡时报直接拒抓,SCMP 回 403——
挑出来的新闻有一半读不到,"读正文"就成了空话。这里用普通浏览器 UA 直接取网页,
只留像正文的长段落(<p> 里够长的),导航、推荐、版权声明这些短段落自然掉了。
固定源都在 fetch_news.py 的 FEEDS 里,是挑过"这样能抽出正文"的。

只许读 `.news-candidates.md` 里的链接:模型不能借它满网乱抓,和 check_news_brief.py
的链接对账是一个口子。输出截到 --max 字(默认 4000),新闻是倒金字塔,
关键事实都在前面,再长就是在花 token 读细节。

抽不出正文(付费墙、改版)时打印一行说明、退出码 1,模型照清单摘要写。

用法:read_article.py <链接> [--max 4000]
"""

from __future__ import annotations

import html
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CANDIDATES = ROOT / ".news-candidates.md"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
CJK = re.compile(r"[一-鿿]")
# 段落里出现这些就是页面杂项,不是正文
JUNK = re.compile(r"cookie|subscribe|newsletter|sign up|all rights reserved|copyright|©|版权所有|订阅", re.I)


def paragraphs(page: str) -> list[str]:
    out = []
    for raw in re.findall(r"<p\b[^>]*>(.*?)</p>", page, re.S | re.I):
        p = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", raw))).strip()
        # 中文段落 30 字、英文 80 字以下多半是图注、署名、按钮;太长的是塞进 <p> 的脚本数据
        if len(p) < (30 if CJK.search(p) else 80) or len(p) > 3000 or JUNK.search(p):
            continue
        if p not in out:
            out.append(p)
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    url = sys.argv[1]
    limit = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 4000
    if not CANDIDATES.exists() or url not in CANDIDATES.read_text(encoding="utf-8"):
        print("✗ 这个链接不在 .news-candidates.md 里,只许读清单里的", file=sys.stderr)
        return 2
    req = urllib.request.Request(urllib.parse.quote(url, safe=":/?&=%#+,;@"), headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            page = r.read().decode(r.headers.get_content_charset() or "utf-8", "ignore")
    except Exception as e:
        print(f"✗ 打不开({type(e).__name__} {getattr(e, 'code', '')}),照清单摘要写", file=sys.stderr)
        return 1
    ps = paragraphs(page)
    text = "\n\n".join(ps)
    if len(text) < 400:
        print(f"✗ 抽不出正文(只有 {len(text)} 字,多半是付费墙或页面改版),照清单摘要写", file=sys.stderr)
        return 1
    print(text[:limit] + ("\n\n……(后文截断)" if len(text) > limit else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
