#!/usr/bin/env python3
"""一次性(或偶尔)重建每日画作的候选池 Meta/画作池.md。

为什么要有池:原来每天让模型上网搜一幅画、验链接、写简介,一次要烧掉几千 token,
而这件事没有一处需要判断力——"有多有名""哪个流派""哪国"全是结构化数据。
建好池之后 pick_painting.py 纯脚本挑,模型完全不参与。

知名度用 Wikidata 的 sitelinks(有多少种语言的维基百科给它写了条目)当代理:
它天然把"值得认识的名画"排在前面,而且不需要任何人工名单。

**必须分段查**:WDQS 对"全部绘画 + sitelinks"这种全表扫描会 504,
按 sitelinks 分几段、每段 ORDER BY + LIMIT 才跑得完(实测单段 ~20 秒)。
"""

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POOL = ROOT / "Meta" / "画作池.md"
UA = "memory-repo-painting/1.0 (github.com/jadecoltrane/memory)"
# 段越往低命中越多、排序越贵,所以低段必须切得更窄,否则 WDQS 直接 502。
BANDS = [(45, None), (40, 45), (36, 40), (33, 36), (30, 33), (28, 30),
         (26, 28), (24, 26), (22, 24), (20, 22), (19, 20), (18, 19)]
RETRIES = 3


def curl(url, args=()):
    r = subprocess.run(["curl", "-sS", "--http1.1", "--max-time", "150", "-A", UA, *args, url],
                       capture_output=True, text=True)
    return r.stdout


def sparql(lo, hi):
    flt = f"FILTER(?sl >= {lo}" + (f" && ?sl < {hi})" if hi else ")")
    q = ("SELECT ?item ?sl ?image WHERE { ?item wdt:P31 wd:Q3305213 ; wdt:P18 ?image ; "
         f"wikibase:sitelinks ?sl . {flt} }} ORDER BY DESC(?sl) LIMIT 300")
    for attempt in range(RETRIES):
        out = curl("https://query.wikidata.org/sparql",
                   ["-G", "--data-urlencode", "query=" + q,
                    "-H", "Accept: application/sparql-results+json"])
        try:
            return json.loads(out)["results"]["bindings"]
        except Exception:
            # WDQS 在这类扫描上会间歇 502/超时,重试通常就过了;
            # 一段彻底取不到只是这一档少几幅,不影响整池可用。
            time.sleep(5 * (attempt + 1))
    print(f"  段 {lo}-{hi} 连试 {RETRIES} 次都失败,跳过", file=sys.stderr)
    return []


def entities(qids):
    """wbgetentities 一次最多 50 个,比 SPARQL 稳得多,用它补元数据。"""
    out = {}
    for i in range(0, len(qids), 50):
        chunk = "|".join(qids[i:i + 50])
        url = ("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json"
               f"&ids={chunk}&props=labels|claims|sitelinks&languages=zh|zh-hans|en&sitefilter=zhwiki")
        try:
            out.update(json.loads(curl(url)).get("entities", {}))
        except Exception as e:
            print(f"  实体批次 {i} 失败: {e}", file=sys.stderr)
        time.sleep(0.3)
    return out


def label(ent, qid):
    ls = ent.get(qid, {}).get("labels", {})
    for k in ("zh", "zh-hans", "en"):
        if k in ls:
            return ls[k]["value"]
    return ""


def claim_qid(ent, qid, prop):
    for c in ent.get(qid, {}).get("claims", {}).get(prop, []):
        v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
        if isinstance(v, dict) and "id" in v:
            return v["id"]
    return ""


def year(ent, qid):
    for c in ent.get(qid, {}).get("claims", {}).get("P571", []):
        t = c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("time", "")
        if t:
            return t.lstrip("+")[:4]
    return ""


def main():
    seen = {}
    for lo, hi in BANDS:
        rows = sparql(lo, hi)
        print(f"段 sitelinks {lo}-{hi or '∞'}: {len(rows)} 条")
        for b in rows:
            qid = b["item"]["value"].rsplit("/", 1)[-1]
            seen[qid] = (int(b["sl"]["value"]),
                         b["image"]["value"].rsplit("/", 1)[-1])
    if not seen:
        print("一条都没取到,不覆盖现有池", file=sys.stderr)
        return 1
    print(f"共 {len(seen)} 幅,开始补元数据…")

    ents = entities(list(seen))
    refs = set()
    for qid in seen:
        for p in ("P170", "P135", "P495"):
            r = claim_qid(ents, qid, p)
            if r:
                refs.add(r)
    ref_ents = entities(sorted(refs))

    rows = []
    for qid, (sl, fname) in seen.items():
        name = label(ents, qid)
        if not name:
            continue
        zh = ents.get(qid, {}).get("sitelinks", {}).get("zhwiki", {}).get("title", "")
        parts = [name,
                 label(ref_ents, claim_qid(ents, qid, "P170")),
                 year(ents, qid),
                 label(ref_ents, claim_qid(ents, qid, "P135")),
                 label(ref_ents, claim_qid(ents, qid, "P495")),
                 str(sl), fname, zh]
        rows.append((sl, "- " + " | ".join(parts)))
    rows.sort(key=lambda x: -x[0])

    head = f"""# 每日画作候选池

`Meta/scripts/pick_painting.py` 每天从这里挑一幅,**机器读的文件,格式不能改**:

```
- 画名 | 画家 | 年份 | 流派 | 国别 | 知名度 | Commons文件名 | 中文维基标题
```

由 `build_painting_pool.py` 从 Wikidata 生成,共 {len(rows)} 幅。**知名度**是
sitelinks——有多少种语言的维基百科给这幅画写了条目,拿它当"值不值得认识"的
代理,不需要任何人工名单。空字段表示 Wikidata 上没有这项。

想换一批或扩容就重跑 `python3 Meta/scripts/build_painting_pool.py`;
它一条都没取到时不会覆盖现有池(宁可用旧池,也不要空池)。

"""
    POOL.write_text(head + "\n".join(r for _, r in rows) + "\n", encoding="utf-8")
    print(f"写入 {POOL}:{len(rows)} 幅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
