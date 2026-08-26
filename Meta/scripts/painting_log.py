#!/usr/bin/env python3
"""工作台每日画作的台账:选画前查重,写完机器校验。

为什么不继续用 git 历史查重:原来的命令是 `git log -- Home.md | grep painting-title`,
而 `git log -- <路径>` **不跨改名**。2026-08-16 把 工作台.md 改名成 Home.md 之后,
这条命令只看得见改名之后的十天,7 月那五十多幅在它眼里不存在——查重从那天起就是
空跑,而且不报错、静默通过,六天里放进来四幅重复的。台账是纯文本文件,改名、
换目录、换执行器都不影响。

三重比对,单独任何一条都漏:
- URL:同一幅画在 Commons 上常有多个文件(不同扫描版本),URL 只拦得住原样复制的。
- 画名:实测《三位一体圣像》和《三圣像》是同一幅画的两个译名,字面比对为零。
- 画家:同一幅画换个译名也换不掉画家,所以画家撞车一律拦。半年内本来也不该
  连着用同一个画家(规则要求时代/地域/风格轮换),误伤的代价只是换一幅。

用法:
  painting_log.py            打印近 180 天用过的画(选画前必读)
  painting_log.py --check    校验 Home.md 当期画作没重复(CI 兜底,不通过退出码 1)
  painting_log.py --record   把 Home.md 当期画作追加进台账(--check 通过之后再跑)
"""

import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "Meta" / "画作台账.md"
HOME = ROOT / "Home.md"
WINDOW_DAYS = 180
SIM_THRESHOLD = 0.75


def norm(s):
    """比对用的规范化:去掉括号注释、书名号、空白和标点。

    同一幅画在不同期的 painting-title 里,括号里的内容每次都不一样
    (「(1942)」vs「(美国写实主义,1942年)」),不去掉就永远比不出重复。
    """
    s = re.split(r"[(（]", s, 1)[0]
    return re.sub(r"[\s·、,，.。《》〈〉\"'\-—]", "", s)


def dice(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    ga = {a[i:i + 2] for i in range(len(a) - 1)} or {a}
    gb = {b[i:i + 2] for i in range(len(b) - 1)} or {b}
    return 2 * len(ga & gb) / (len(ga) + len(gb))


def split_title(title):
    """把 `画家《画名》(注释)` 拆成 (画家, 画名)。拆不开就整串当画名。"""
    m = re.match(r"^(.*?)[《〈](.+?)[》〉]", title.strip())
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return "", re.split(r"[(（]", title, 1)[0].strip()


def read_ledger():
    rows = []
    if not LEDGER.exists():
        return rows
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^-\s*(\d{4}-\d{2}-\d{2})\s*\|(.*?)\|(.*?)\|(.*)$", line)
        if m:
            rows.append({
                "date": m.group(1),
                "artist": m.group(2).strip(),
                "name": m.group(3).strip(),
                "url": m.group(4).strip(),
            })
    return rows


def read_home():
    fm = {}
    for line in HOME.read_text(encoding="utf-8").splitlines()[1:40]:
        if line.strip() == "---":
            break
        m = re.match(r"^(generated|painting-url|painting-title):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    artist, name = split_title(fm.get("painting-title", ""))
    return {
        "date": fm.get("generated", ""),
        "artist": artist,
        "name": name,
        "url": fm.get("painting-url", ""),
        "title": fm.get("painting-title", ""),
    }


def recent(rows, today):
    try:
        cutoff = datetime.date.fromisoformat(today) - datetime.timedelta(days=WINDOW_DAYS)
    except ValueError:
        return rows
    return [r for r in rows if r["date"] >= cutoff.isoformat()]


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    rows = read_ledger()

    if arg == "":
        today = datetime.date.today().isoformat()
        window = recent(rows, today)
        print(f"近 {WINDOW_DAYS} 天用过 {len(window)} 幅(共 {len(rows)} 幅),别再挑这些:")
        for r in sorted(window, key=lambda x: x["date"], reverse=True):
            print(f"  {r['date']}  {r['artist']}《{r['name']}》")
        artists = sorted({r["artist"] for r in window if r["artist"]})
        print(f"\n窗口内出现过的画家({len(artists)}):{'、'.join(artists)}")
        return 0

    cur = read_home()
    if not cur["title"]:
        print("✗ Home.md 里没有 painting-title", file=sys.stderr)
        return 1

    if arg == "--check":
        window = recent(rows, cur["date"])
        hits = []
        for r in window:
            # 同一天的那行是自己(重跑时台账里已经有了),不算重复
            if r["date"] == cur["date"]:
                continue
            if cur["url"] and r["url"] == cur["url"]:
                hits.append((r, "URL 相同"))
            elif norm(r["name"]) == norm(cur["name"]):
                hits.append((r, "画名相同"))
            elif cur["artist"] and norm(r["artist"]) == norm(cur["artist"]):
                hits.append((r, "画家相同"))
            elif dice(r["name"], cur["name"]) >= SIM_THRESHOLD:
                hits.append((r, f"画名相似度 {dice(r['name'], cur['name']):.2f}"))
        if hits:
            print(f"✗ 今日画作重复:{cur['title']}", file=sys.stderr)
            for r, why in hits:
                print(f"    ← {r['date']} {r['artist']}《{r['name']}》({why})", file=sys.stderr)
            print(f"  近 {WINDOW_DAYS} 天用过的画见 Meta/画作台账.md,换一幅重跑。", file=sys.stderr)
            return 1
        print(f"✓ 画作查重通过:{cur['title']}")
        return 0

    if arg == "--record":
        if any(r["date"] == cur["date"] and r["url"] == cur["url"] for r in rows):
            print(f"台账里已有 {cur['date']} 这行,跳过")
            return 0
        with LEDGER.open("a", encoding="utf-8") as f:
            f.write(f"- {cur['date']} | {cur['artist']} | {cur['name']} | {cur['url']}\n")
        print(f"已记入台账:{cur['date']} {cur['artist']}《{cur['name']}》")
        return 0

    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
