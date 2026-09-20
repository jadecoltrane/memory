#!/usr/bin/env python3
"""还有没有到期未做的 notes 复核?给 weekly-gc.yml 的省成本闸门用。

闸门原来只看"这周有没有新提交",但复核是**按时间**到期的,和有没有新内容无关。
两个条件必须是或的关系,否则安静的一周会把到期的复核一起顺延,一路积压下去。

输出一行 `due=N`,退出码恒为 0。
"""
import datetime
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TODAY = datetime.date.today()

FIRST_CHECK_DAYS = 30    # 从没复核过的,建库 30 天内必查
SUPPORTED_DAYS = 180     # 上次结论「支持」,180 天后再查
# 「存疑」「找不到依据」不设间隔:下次 GC 就该继续查(Meta/GC.md)

REC = re.compile("^- (\\d{4}-\\d{2}-\\d{2})[:\uff1a](.*)$", re.M)
# 复核记录按 Meta/GC.md 要求会写一句「下次复核约 X」——那是上一轮自己排的期,
# 比任何启发式都准,优先认它
NEXT = re.compile("下次复核约?\\s*[(\uff08]?(\\d{4})[-\u5e74\\.]?\\s*(\\d{1,2})?")


def frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    out = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith((" ", "-")):
                k, _, v = line.partition(":")
                out[k.strip()] = v.strip()
    return out


def due_notes() -> list:
    out = []
    for p in sorted((ROOT / "Notes").rglob("*.md")):
        text = p.read_text(encoding="utf-8")
        fm = frontmatter(text)
        if str(fm.get("checkable", "")).lower() != "true":
            continue
        if str(fm.get("verified", "")).lower() == "true":
            continue  # 已核实的不做真实性复核
        i = text.find("## 复核记录")
        if i < 0:
            # 从没复核过:按 created 起算,没有 created 就当立刻到期
            d = fm.get("created", "")
            try:
                start = datetime.date.fromisoformat(d)
            except ValueError:
                out.append(p)
                continue
            if (TODAY - start).days >= FIRST_CHECK_DAYS:
                out.append(p)
            continue
        recs = REC.findall(text[i:])
        if not recs:
            out.append(p)
            continue
        last_date, last_body = recs[-1]
        try:
            last = datetime.date.fromisoformat(last_date)
        except ValueError:
            out.append(p)
            continue
        m = NEXT.search(last_body)
        if m:
            y, mo = int(m.group(1)), int(m.group(2) or 1)
            if (y, mo) > (TODAY.year, TODAY.month):
                continue          # 上一轮排的下次复核时间还没到
            out.append(p)
            continue
        # 没写下次时间才用启发式:「用户裁决」和「结论支持」都算这一轮结束
        # (Meta/GC.md:存疑要一直查到用户裁决或转为支持),之后按 180 天再排
        # 结论词必须锚定在这条记录的开头(格式是"- 日期:结论,依据..."),
        # 否则"不再支持该理论"这类正文里的"支持"会被误判成结论本身
        closed = last_body.strip().startswith("支持") or any(
            w in last_body for w in ("裁决", "完结", "修正", "已改正")
        )
        if closed:
            if (TODAY - last).days >= SUPPORTED_DAYS:
                out.append(p)
        else:
            out.append(p)  # 存疑 / 找不到依据 → 下次就查
    return out


if __name__ == "__main__":
    d = due_notes()
    print(f"due={len(d)}")
    for p in d:
        print(f"  {p.relative_to(ROOT).as_posix()}")
