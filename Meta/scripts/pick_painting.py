#!/usr/bin/env python3
"""每天从 Meta/画作池.md 挑一幅画写进 Home.md。纯脚本,不消耗任何模型 token。

原来这件事是让模型上网搜、验链接、写简介,一次几千 token,而其中没有一处需要
判断力:"有多有名"是 sitelinks、"哪个流派/哪国"是结构化字段、"链接通不通"是
HTTP 状态码、"一句话简介"中文维基第一句就是。所以整件事下放到脚本。

三层过滤,前两层是规则、第三层是现实:
- 半年内用过的画/画家不许再出(判据复用 painting_log,和机器校验同一套,不会出现
  "挑的时候合规、校验时被打回"的自相矛盾)。
- 流派和国别各有自己的冷却期:这是原来写在 prompt 里的"时代/地域/风格轮换",
  改成机械执行——模型做这件事既贵又不稳。
- 图片当场验:HTTP 200 + 体积在区间内才算数。一幅不行就换下一幅。
"""

import datetime
import hashlib
import json
import re
import subprocess
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import painting_log as PL  # noqa: E402  判据必须和机器校验共用一份

ROOT = Path(__file__).resolve().parents[2]
POOL = ROOT / "Meta" / "画作池.md"
HOME = ROOT / "Home.md"
UA = "memory-repo-painting/1.0 (github.com/jadecoltrane/memory)"
MOVEMENT_COOLDOWN = 6      # 天:同一流派
COUNTRY_COOLDOWN = 4       # 天:同一国别
TOP_K = 50                 # 在符合条件的前 K 名里随机,而不是永远取最有名的那幅
MIN_BYTES, MAX_BYTES = 60_000, 6_000_000
MAX_TRIES = 8


def read_pool():
    rows = []
    if not POOL.exists():
        return rows
    for line in POOL.read_text(encoding="utf-8").splitlines():
        if not line.startswith("- "):
            continue
        f = [x.strip() for x in line[2:].split("|")]
        # 文件头的格式说明那一行也以「- 」开头,靠「知名度必须是数字」把它挡掉
        if len(f) >= 8 and f[0] and f[6] and f[5].isdigit():
            # 显示名优先用中文维基条目名:Wikidata 的 zh 标签繁简混杂(「基督變容」),
            # 而条目名通常是简体(「耶稣显圣容_(拉斐尔)」)。括号里的消歧后缀要去掉。
            disp = re.sub(r"[_ ]?[((][^)）]*[)）]$", "", f[7].replace("_", " ")).strip() or f[0]
            rows.append({"name": disp, "artist": f[1], "year": f[2], "movement": f[3],
                         "country": f[4], "sl": int(f[5] or 0), "file": f[6], "zh": f[7]})
    return rows


def curl(url, args=()):
    return subprocess.run(["curl", "-sS", "--http1.1", "--max-time", "40", "-A", UA, *args, url],
                          capture_output=True, text=True).stdout


def image_url(fname):
    from urllib.parse import quote
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{quote(fname)}?width=1280"


def verify(url):
    out = subprocess.run(
        ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code} %{size_download} %{content_type}",
         "-L", "--max-time", "45", "-A", UA, url], capture_output=True, text=True).stdout.split()
    if len(out) < 3 or out[0] != "200":
        return False, " ".join(out) or "无响应"
    size = int(out[1])
    if not (MIN_BYTES <= size <= MAX_BYTES) or not out[2].startswith("image/"):
        return False, f"{out[0]} {size}B {out[2]}"
    return True, f"{size}B"


def intro_of(cand):
    """中文维基第一段当简介;没有中文条目就用结构化字段拼一句,不留空。"""
    if cand["zh"]:
        from urllib.parse import quote
        text = ""
        # 抓不到就只能退化成拼接的一句话,那是明显更差的结果,值得重试
        for _ in range(3):
            raw = curl(f"https://zh.wikipedia.org/api/rest_v1/page/summary/{quote(cand['zh'])}")
            try:
                text = json.loads(raw).get("extract", "").strip()
            except Exception:
                text = ""
            if text:
                break
            time.sleep(2)
        text = re.sub(r"\s+", "", text)
        if len(text) > 30:
            # 截到第二个句号:第一句常常只是"《X》是一幅画",信息量不够
            parts = re.split(r"(?<=[。!?])", text)
            out = "".join(parts[:2])[:160]
            return out or text[:160]
    bits = [b for b in (cand["country"], cand["movement"], cand["year"]) if b]
    return f"{cand['artist']}的作品" + ("(" + "、".join(bits) + ")" if bits else "") + "。"


def title_of(cand):
    tail = "、".join(b for b in (cand["movement"], cand["year"] and cand["year"] + "年") if b)
    return f"{cand['artist']}《{cand['name']}》" + (f"({tail})" if tail else "")


def recent_field(ledger_titles, pool, field, days, today):
    """台账只存画家和画名,流派/国别得回池里查。查不到的当作没有冲突。"""
    by_name = {PL.norm(r["name"]): r for r in pool}
    cutoff = (datetime.date.fromisoformat(today) - datetime.timedelta(days=days)).isoformat()
    out = set()
    for row in ledger_titles:
        if row["date"] >= cutoff:
            hit = by_name.get(PL.norm(row["name"]))
            if hit and hit[field]:
                out.add(hit[field])
    return out


def main():
    dry = "--dry-run" in sys.argv
    today = datetime.date.today().isoformat()
    pool, ledger = read_pool(), PL.read_ledger()
    if not pool:
        print("画作池是空的,先跑 build_painting_pool.py", file=sys.stderr)
        return 1
    window = PL.recent(ledger, today)
    hot_mv = recent_field(ledger, pool, "movement", MOVEMENT_COOLDOWN, today)
    hot_ct = recent_field(ledger, pool, "country", COUNTRY_COOLDOWN, today)

    def eligible(c):
        if c["movement"] and c["movement"] in hot_mv:
            return False
        if c["country"] and c["country"] in hot_ct:
            return False
        for r in window:
            if PL.norm(r["name"]) == PL.norm(c["name"]):
                return False
            if c["artist"] and PL.norm(r["artist"]) == PL.norm(c["artist"]):
                return False
            if PL.dice(r["name"], c["name"]) >= PL.SIM_THRESHOLD:
                return False
        return True

    cands = [c for c in pool if eligible(c)]
    if not cands:
        print("池里没有符合条件的画了——冷却期太长或池太小,扩容池或调冷却期", file=sys.stderr)
        return 1
    cands.sort(key=lambda c: -c["sl"])
    # 在最有名的 TOP_K 幅里按日期定序打乱:既不会天天挑同一档冷门,也不会
    # 严格按名气递减导致头两个月全是教科书封面款。同一天重跑结果一致。
    head = cands[:TOP_K]
    head.sort(key=lambda c: hashlib.sha1((today + c["name"]).encode()).hexdigest())

    for cand in head[:MAX_TRIES]:
        url = image_url(cand["file"])
        ok, why = verify(url)
        if not ok:
            print(f"  跳过 {cand['name']}:图片验证失败({why})")
            continue
        title, intro = title_of(cand), intro_of(cand)
        if dry:
            print(f"[dry-run] {title}\n  {url}\n  {intro}\n  ({why},候选 {len(cands)} 幅)")
            return 0
        s = HOME.read_text(encoding="utf-8")
        s = re.sub(r"^painting-url:.*$", "painting-url: " + url, s, count=1, flags=re.M)
        s = re.sub(r"^painting-title:.*$", "painting-title: " + title, s, count=1, flags=re.M)
        s = re.sub(r"^painting-intro:.*$", "painting-intro: " + intro, s, count=1, flags=re.M)
        HOME.write_text(s, encoding="utf-8")
        print(f"✓ 今日画作:{title}  ({why},候选池 {len(cands)} 幅可选)")
        return 0
    print(f"连试 {MAX_TRIES} 幅图片都验证失败,保留前一天的画", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
