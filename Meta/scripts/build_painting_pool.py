#!/usr/bin/env python3
"""重建每日画作的候选池 Meta/画作池.md(一次性,想换批再跑)。

为什么要有池:原来每天让模型上网搜一幅画、验链接、写简介,一次几千 token,
而这件事没有一处需要判断力——"有多有名"是 sitelinks、"哪个流派/哪国"是结构化
字段、"链接通不通"是 HTTP 状态码。建好池之后 pick_painting.py 纯脚本挑,
模型完全不参与。

知名度用 sitelinks(多少种语言的维基百科给这幅画写了条目)当代理:它天然把
"值得认识的名画"排在前面,不需要任何人工名单。

两条实测约束,改动前先看:
- **必须按 sitelinks 分段查**。一次拉全部绘画会 504,分段后每段约 20 秒。
- **语言变体要写 zh-hans**。只写 zh 拿回来的是繁简混杂的标签(「老彼得·布呂赫爾」),
  而台账里存的是简体,查重会因为繁简不同而漏掉同一个画家——和《三圣像》/
  《三位一体圣像》那次是同一类漏法。
- **标签要跟在同一条查询里拿**,不要事后再调 wbgetentities 补——那是几十次
  额外请求,实测直接撞速率限制,而 SERVICE wikibase:label 一次就带回来了。
"""

import json
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POOL = ROOT / "Meta" / "画作池.md"
UA = "memory-repo-painting/1.0 (github.com/jadecoltrane/memory)"
RETRIES = 2
# 段越往低命中越多、排序越贵,所以低段切得更窄,否则 WDQS 直接 502。
BANDS = [(45, None), (40, 45), (36, 40), (33, 36), (30, 33), (28, 30),
         (26, 28), (24, 26), (22, 24), (20, 22), (18, 20), (16, 18)]

QUERY = """SELECT ?itemLabel ?creatorLabel ?inception ?movementLabel ?countryLabel ?sl ?image ?zh WHERE {
  ?item wdt:P31 wd:Q3305213 ; wdt:P18 ?image ; wikibase:sitelinks ?sl .
  %s
  OPTIONAL { ?item wdt:P170 ?creator }
  OPTIONAL { ?item wdt:P571 ?inception }
  OPTIONAL { ?item wdt:P135 ?movement }
  OPTIONAL { ?item wdt:P495 ?country }
  OPTIONAL { ?zh schema:about ?item ; schema:isPartOf <https://zh.wikipedia.org/> }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "zh-hans,zh,en". }
} LIMIT 400"""


def band(lo, hi):
    flt = f"FILTER(?sl >= {lo}" + (f" && ?sl < {hi})" if hi else ")")
    for attempt in range(RETRIES + 1):
        out = subprocess.run(
            ["curl", "-sS", "--http1.1", "--max-time", "90", "-A", UA, "-G",
             "https://query.wikidata.org/sparql",
             "--data-urlencode", "query=" + QUERY % flt,
             "-H", "Accept: application/sparql-results+json"],
            capture_output=True, text=True).stdout
        try:
            return json.loads(out)["results"]["bindings"]
        except Exception:
            # WDQS 在这类扫描上会间歇 502/超时,重试通常就过;
            # 某一段彻底取不到只是这一档少几幅,不影响整池可用。
            time.sleep(4 * (attempt + 1))
    print(f"  段 {lo}-{hi} 连试 {RETRIES + 1} 次都失败,跳过", file=sys.stderr)
    return []


def to_simplified(strings):
    """把一批字符串转成简体。

    Wikidata 的 zh 标签繁简混杂,而 `zh-hans` 只在条目真有简体标签时才生效
    (实测「老彼得·布呂赫爾」照样是繁体)。zhconv/hanziconv 在有些环境编译不过,
    所以借维基百科自己的字词转换(action=parse&variant=zh-cn)——**只在建池时调**,
    日更那条路径不碰它,不给每天跑的工作流增加依赖。
    """
    out, step = [], 60
    for i in range(0, len(strings), step):
        chunk = strings[i:i + step]
        r = subprocess.run(
            ["curl", "-sS", "--max-time", "60", "-A", UA, "-G",
             "https://zh.wikipedia.org/w/api.php",
             "--data-urlencode", "action=parse", "--data-urlencode", "format=json",
             "--data-urlencode", "contentmodel=wikitext", "--data-urlencode", "prop=text",
             "--data-urlencode", "variant=zh-cn",
             "--data-urlencode", "text=" + "\n".join(chunk)],
            capture_output=True, text=True).stdout
        try:
            html = json.loads(r)["parse"]["text"]["*"]
            got = [x for x in re.sub(r"<[^>]+>", "", html).split("\n") if x.strip()]
        except Exception:
            got = []
        if len(got) == len(chunk):
            out.extend(got)
        elif len(chunk) == 1:
            # 行数对不上就放弃这一条,宁可留繁体也不要错位串行
            out.extend(chunk)
        else:
            # 二分重试:整批放弃会连累同批的几十条,拆开后失败范围收敛到单行
            mid = len(chunk) // 2
            out.extend(to_simplified(chunk[:mid]) + to_simplified(chunk[mid:]))
        time.sleep(0.3)
    return out


def simplify_rows(fields):
    """只转画名/画家/流派/国别四栏,文件名和维基标题是标识符,转了就打不开。"""
    idx = [(r, c) for r in range(len(fields)) for c in (0, 1, 3, 4) if fields[r][c]]
    conv = to_simplified([fields[r][c] for r, c in idx])
    for (r, c), v in zip(idx, conv):
        fields[r][c] = v
    return fields


def main():
    if "--convert-only" in sys.argv:
        # 只把现有池转成简体,不重新查 Wikidata(WDQS 慢且间歇失败,不值得为转换重跑)
        text = POOL.read_text(encoding="utf-8")
        head, body = text.split("\n- ", 1)
        rows = [f for f in ([x.strip() for x in ln[2:].split("|")]
                            for ln in ("- " + body).splitlines() if ln.startswith("- "))
                # 文件头的格式说明那行也以「- 」开头,靠「知名度是数字」挡掉
                if len(f) >= 8 and f[5].isdigit()]
        rows = simplify_rows(rows)
        POOL.write_text(head + "\n" + "\n".join("- " + " | ".join(f) for f in rows) + "\n",
                        encoding="utf-8")
        print(f"已转简体:{len(rows)} 幅")
        return 0

    rows = {}
    for lo, hi in BANDS:
        got = band(lo, hi)
        print(f"段 sitelinks {lo}-{hi or '∞'}: {len(got)} 条", flush=True)
        for b in got:
            g = lambda k: b.get(k, {}).get("value", "")
            name = g("itemLabel")
            # 没有标签时 itemLabel 会退化成 Q 号,那种行没法用
            if not name or name.startswith("Q") and name[1:].isdigit():
                continue
            zh = urllib.parse.unquote(g("zh").rsplit("/", 1)[-1]) if g("zh") else ""
            rows[name] = (int(g("sl") or 0), [
                name, g("creatorLabel"), g("inception").lstrip("+")[:4],
                g("movementLabel"), g("countryLabel"), g("sl"),
                urllib.parse.unquote(g("image").rsplit("/", 1)[-1]), zh])
    if not rows:
        print("一条都没取到,不覆盖现有池", file=sys.stderr)
        return 1

    ordered = sorted(rows.values(), key=lambda x: -x[0])
    print("转简体…", flush=True)
    simplify_rows([f for _, f in ordered])
    head = f"""# 每日画作候选池

`Meta/scripts/pick_painting.py` 每天从这里挑一幅,**机器读的文件,格式不能改**:

```
- 画名 | 画家 | 年份 | 流派 | 国别 | 知名度 | Commons文件名 | 中文维基标题
```

由 `build_painting_pool.py` 从 Wikidata 生成,共 {len(ordered)} 幅。**知名度**是
sitelinks——有多少种语言的维基百科给这幅画写了条目,拿它当"值不值得认识"的代理,
不需要任何人工名单。空字段表示 Wikidata 上没有这一项。

想换一批或扩容就重跑 `python3 Meta/scripts/build_painting_pool.py`;
它一条都没取到时不会覆盖现有池——宁可用旧池,也不要空池。

"""
    POOL.write_text(head + "\n".join("- " + " | ".join(f) for _, f in ordered) + "\n",
                    encoding="utf-8")
    print(f"写入 {POOL}:{len(ordered)} 幅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
