#!/usr/bin/env python3
"""额度流水报表:按年算 Profile/财务.md「想要」那张表里每一格还剩多少。

为什么余额不存进文件:手填的余额会和流水对不上,而且对不上的时候没有任何信号。
所以这里每次现算,文件里只留原始流水。

为什么格式坏掉就退出而不是跳过:一笔金额记错格子名、或者行写坏了,
静默跳过的话那笔钱就凭空消失,事后没法从余额反推是哪一笔。宁可吵,不可漏。
"""
import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "Profile" / "额度流水.md"

BUDGET_RE = re.compile(r"^-\s*(.+?)\s*\|\s*(-?\d+)\s*$")
FLOW_RE = re.compile(r"^-\s*(\d{4})-(\d{2})-(\d{2})\s*\|\s*(.+?)\s*\|\s*(-?\d+)\s*\|\s*(.*?)\s*$")


def section(text: str, name: str) -> list:
    """取 ## <name> 到下一个 ## 之间的非空行。"""
    m = re.search(rf"^## {re.escape(name)}\s*$", text, re.M)
    if not m:
        sys.exit(f"✗ {SRC.name} 里找不到「## {name}」区")
    rest = text[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    body = rest[: nxt.start()] if nxt else rest
    return [ln.strip() for ln in body.splitlines() if ln.strip()]


def main():
    if not SRC.exists():
        sys.exit(f"✗ 找不到 {SRC}")
    text = SRC.read_text(encoding="utf-8")
    year = sys.argv[1] if len(sys.argv) > 1 else str(datetime.date.today().year)

    budgets, errors = {}, []
    for ln in section(text, "额度"):
        m = BUDGET_RE.match(ln)
        if not m:
            errors.append(f"「额度」区这行格式不对,应为 `- 名称 | 数字`:{ln}")
            continue
        budgets[m.group(1)] = int(m.group(2))
    if not budgets:
        sys.exit("✗ 「额度」区是空的,没法算")

    today = datetime.date.today()
    used = {k: 0 for k in budgets}
    rows = 0
    for ln in section(text, "流水"):
        if ln.startswith("("):
            continue
        m = FLOW_RE.match(ln)
        if not m:
            errors.append(f"「流水」区这行格式不对,应为 `- YYYY-MM-DD | 格子 | 金额 | 说明`:{ln}")
            continue
        y, mo, d, bucket, amount, _note = m.groups()
        try:
            when = datetime.date(int(y), int(mo), int(d))
        except ValueError:
            errors.append(f"日期不存在:{ln}")
            continue
        if when > today:
            errors.append(f"日期在未来({when}),是不是记错年份了:{ln}")
            continue
        if bucket not in budgets:
            errors.append(f"格子名「{bucket}」不在「额度」区里(写错了这笔钱会落空):{ln}")
            continue
        if y != year:
            continue
        used[bucket] += int(amount)
        rows += 1

    if errors:
        print(f"✗ {len(errors)} 处问题,先修掉再看报表:\n")
        for e in errors:
            print("  - " + e)
        sys.exit(1)

    width = max(len(k) for k in budgets)
    print(f"📒 {year} 年额度流水({rows} 笔)\n")
    print(f"  {'格子'.ljust(width)}   额度      已用      剩余")
    print("  " + "─" * (width + 28))
    over = []
    for name, quota in budgets.items():
        left = quota - used[name]
        flag = ""
        if left < 0:
            flag, over = "  ⚠️ 超支", over + [name]
        elif quota and used[name] / quota >= 0.8:
            flag = "  ⚠️ 已用八成"
        print(f"  {name.ljust(width)}  {quota:>6}  {used[name]:>8}  {left:>8}{flag}")
    tq, tu = sum(budgets.values()), sum(used.values())
    print("  " + "─" * (width + 28))
    print(f"  {'合计'.ljust(width)}  {tq:>6}  {tu:>8}  {tq - tu:>8}")

    if over:
        print(f"\n⚠️ 超支的格子:{'、'.join(over)}。**从别的格子挪,不要直接抬总额**——")
        print("   抬总额等于把应急金的进度让出去(见 Profile/财务「分配」)。")


if __name__ == "__main__":
    main()
