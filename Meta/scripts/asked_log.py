#!/usr/bin/env python3
"""工作台每日提问的台账:出题前查重,出题后机器校验。

问题重复是靠"我记得问过"防不住的:每天的生成是一次无记忆的冷启动,
上一期问了什么只有翻 Home.md 的 git 历史才知道,而问题正文是长段落、
翻起来贵。所以把每道题压成一行(日期|编号|来源|轴|主旨|状态)存进
Meta/问题台账.md,读一行就够判断重不重。

三张网互补,单独任何一张都漏:
- 来源窗口:同一个概念页/笔记 SOURCE_WINDOW_DAYS 天内不许再出题。
  防的是措辞完全不同、但绕着同一篇打转的题。
- 主旨相似度:字符 Dice 系数 ≥ SIM_THRESHOLD 判为同题。
  防的是换了来源、问的还是同一件事。
- 轴:两道题可以一个字都不重叠、来源也不同,问的还是同一件事(实测:
  "事后如释重负分不分得出真逃避" 和 "当下爽不爽还是交出去被检验更说明在往前走"
  字面相似度只有 0.1,是同一个问题的两种问法)。字面比对到此为止,所以每道题
  必须自报一个轴,同轴 AXIS_WINDOW_DAYS 天内不许再出,同轴的旧题一律打印出来
  让出题人自己比。

用法:
  asked_log.py            打印近 90 天台账 + 轴的冷热 + 禁用来源/封存主旨(出题前必读)
  asked_log.py --check    校验 Home.md 当期的两行台账(CI 兜底,不通过退出码 1)
"""

import datetime
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LEDGER = ROOT / "Meta" / "问题台账.md"
HOME = ROOT / "Home.md"

LIST_WINDOW_DAYS = 90  # 打印和查重的回看窗口
SOURCE_WINDOW_DAYS = 14  # 同一来源的冷却期
# 轴的冷却期比来源短得多:一天两道、轴表十几个,按 7 天算槽位刚好卡死,
# 5 天才留得出余量。轴不是用来卡死出题的,是用来把"又绕回这一片"变得看得见。
AXIS_WINDOW_DAYS = 5
AXIS_BUSY_30D = 3  # 近 30 天同轴到这个数就提醒(不阻断)
AXIS_MAX_30D = 6  # 近 30 天同轴到这个数就阻断:轴表十几个还能吃掉六格,是真偏食了
# 轴表是活的:库长出新主题就该加轴,种子那批只是从既有的题倒推出来的起步集合。
# 但"加轴"同时也是绕开同轴查重最省事的路(每道题都起个新轴,就永远撞不上车),
# 所以放开加、卡住加的速度:一个月新起三个轴以上,基本只可能是在绕路。
AXIS_NEW_MAX_30D = 3
# 阈值按现有台账实测标定:真正重复的两道(2026-08-13/08-20 那对情绪分析题、
# 08-04/08-06 那对天赋题)落在 0.49~0.61,不相干的最高只到 0.33。定在 0.45 是
# 这两堆之间那道缝;抬高就漏、压低就开始误伤正常出题。
SIM_THRESHOLD = 0.45
# 这两类来源不占冷却期:自由题本来就不绑定某篇,日记每天都是新内容。
# 留这个豁免是为了保证「合法的下一步」永远存在——所有概念页都在冷却期里时,
# 出题人还有路可走,不会被逼到只能重复(死锁时唯一的出口就是复读)。
EXEMPT_SOURCES = ("自由题", "Diary")
STATUSES = ("待答", "已答", "未答", "封存")

ROW = re.compile(
    r"^-\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(问题[12])\s*\|(.+?)\|(.+?)\|(.+?)\|(.+?)$"
)
# 轴表:文件里「## 轴表」那节的 `- 轴名:说明` 行。轴名从文件读、不写死在这里,
# 是为了让加轴这个动作必须落在台账上——出题时临时造一个轴名就绕开了同轴查重。
AXIS_DEF = re.compile(r"^-\s*([^:：\n]+)[:：]\s*(.*)$")


class Entry:
    def __init__(self, date, num, source, axis, gist, status, lineno):
        self.date, self.num = date, num
        self.source, self.axis = source, axis
        self.gist, self.status = gist, status
        self.lineno = lineno


def axis_table() -> dict:
    """轴名 -> (说明, 在台账里的行号)。行号是给 git blame 用的。"""
    if not LEDGER.exists():
        return {}
    text = LEDGER.read_text(encoding="utf-8")
    if "## 轴表" not in text:
        return {}
    offset = text[: text.index("## 轴表")].count("\n") + 1
    table = {}
    # split 后的第一段是「## 轴表」这行的残余,所以从标题行本身的行号数起
    for i, line in enumerate(text.split("## 轴表", 1)[1].splitlines(), start=offset):
        if line.startswith("## ") or line.startswith("- 20"):
            break
        m = AXIS_DEF.match(line.strip())
        if m:
            table[m.group(1).strip()] = (m.group(2).strip(), i)
    return table


def axis_added_on(table: dict) -> dict:
    """每个轴是哪天进的表——问 git blame,不设"加入日期"字段。

    字段要靠出题人自己填,而这里恰恰是他有动机填错的地方(把新起的轴写成老轴,
    加轴限速就形同虚设)。blame 记的是这一行真正进仓库的时间,填不了。"""
    if not table:
        return {}
    lines = sorted(v[1] for v in table.values())
    # quotepath=false:台账的文件名是中文,不关的话 blame 输出里的路径会被转义
    cmd = ["git", "-c", "core.quotepath=false", "blame", "--date=short", "-p",
           f"-L{lines[0]},{lines[-1]}", "--", str(LEDGER.relative_to(ROOT))]
    try:
        out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return {}
    if out.returncode != 0:
        return {}  # 没有 git 历史(浅克隆、新仓库)就不做限速,别把日更卡死
    added, cur = {}, None
    for line in out.stdout.splitlines():
        if line.startswith("author-time "):
            cur = datetime.date.fromtimestamp(int(line.split()[1]))
        elif line.startswith("\t") and cur:
            m = AXIS_DEF.match(line[1:].strip())
            if m and m.group(1).strip() in table:
                added[m.group(1).strip()] = cur
    # 起步那批轴是一次性倒推出来的,不算"新起的轴";只有后来加的才受限速管
    if added:
        founding = min(added.values())
        added = {k: v for k, v in added.items() if v > founding}
    return added


def load() -> list:
    if not LEDGER.exists():
        return []
    entries, bad = [], []
    for i, line in enumerate(LEDGER.read_text(encoding="utf-8").splitlines(), 1):
        # 只有「- 四位年份开头」的行才是台账行,文件顶上的说明列表照样用 - 开头
        if not re.match(r"^-\s*\d{4}", line):
            continue
        m = ROW.match(line.strip())
        if not m:
            bad.append(f"{i}: {line.strip()[:60]}")
            continue
        d, num, source, axis, gist, status = m.groups()
        try:
            date = datetime.date.fromisoformat(d)
        except ValueError:
            bad.append(f"{i}: 日期不合法 {d}")
            continue
        entries.append(
            Entry(date, num, source.strip(), axis.strip(), gist.strip(), status.strip(), i)
        )
    if bad:
        print("⚠️  台账里有解析不了的行(格式:- 日期 | 问题N | 来源 | 轴 | 主旨 | 状态):")
        for b in bad:
            print(f"    {b}")
    return entries


def norm(text: str) -> str:
    """归一化:去标点空白、全角转半角、字母转小写,只留能承载语义的字符。"""
    text = unicodedata.normalize("NFKC", text).lower()
    return "".join(c for c in text if c.isalnum())


def dice(a: str, b: str, n: int) -> float:
    ga = {a[i : i + n] for i in range(len(a) - n + 1)}
    gb = {b[i : i + n] for i in range(len(b) - n + 1)}
    return 2 * len(ga & gb) / (len(ga) + len(gb)) if ga and gb else 0.0


def similarity(a: str, b: str) -> float:
    """单字和二元组各算一次 Dice,取大的那个。

    只用二元组会漏掉换语序的改写(中文一个字就是一个词素,"情绪被分析掉"和
    "分析完情绪还在不在"共享的是字不是相邻字对);只用单字会被"是不是/有没有"
    这类高频虚字抬高底噪。取 max 两头都收。"""
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    return max(dice(a, b, 1), dice(a, b, 2))


def sources(entry) -> list:
    """一道题常常同时挂着概念页和笔记(答案两边都要归档),来源栏用 + 并列写。
    冷却期按每一个来源单独算——只认第一个的话,换个写法就能绕过去。"""
    return [s.strip() for s in entry.source.split("+") if s.strip()]


def exempt(source: str) -> bool:
    return any(source == e or source.startswith(e + "/") for e in EXEMPT_SOURCES)


def today() -> datetime.date:
    """当期日期以 Home.md 的 generated: 为准 —— 日更的 runner 跑在 UTC,
    generated 是前置步骤按北京时间写好的,拿它当"今天"才和当期产物对得上。"""
    if HOME.exists():
        m = re.search(r"^generated:\s*(\d{4}-\d{2}-\d{2})", HOME.read_text(encoding="utf-8"), re.M)
        if m:
            return datetime.date.fromisoformat(m.group(1))
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).date()


def do_list(entries: list) -> None:
    now = today()
    recent = [e for e in entries if (now - e.date).days <= LIST_WINDOW_DAYS]
    print(f"# 近 {LIST_WINDOW_DAYS} 天问过的题(当期 {now},共 {len(recent)} 道)\n")
    for e in sorted(recent, key=lambda x: (x.date, x.num)):
        print(f"{e.date} {e.num} [{e.status}] {e.source} —— {e.gist}")

    blocked = sorted(
        {
            s
            for e in entries
            if (now - e.date).days < SOURCE_WINDOW_DAYS
            for s in sources(e)
            if not exempt(s)
        }
    )
    print(f"\n# 轴的冷热(挑定轴之后,把该轴下面那几道旧题逐条读一遍,读着像就换)")
    for axis in axis_table():
        same = [e for e in entries if e.axis == axis]
        last = max((e.date for e in same), default=None)
        d30 = len([e for e in same if (now - e.date).days < 30])
        if last is None:
            print(f"- {axis}:没问过")
            continue
        gap = (now - last).days
        flag = "🚫 冷却中" if gap < AXIS_WINDOW_DAYS else ("⚠️ 近 30 天偏多" if d30 >= AXIS_BUSY_30D else "")
        print(f"- {axis}:近 30 天 {d30} 次,最近 {last}({gap} 天前){' ' + flag if flag else ''}")
        for e in sorted(same, key=lambda x: x.date)[-4:]:
            print(f"    · {e.date} {e.gist}")

    table = axis_table()
    used = {e.axis for e in entries}
    added = axis_added_on(table)
    unused = [a for a in table if a not in used]
    once = sorted({e.axis for e in entries if len([x for x in entries if x.axis == e.axis]) == 1})
    fresh = sorted(k for k, v in added.items() if (now - v).days < 30)
    print("\n# 轴表卫生(轴表是活的:库长出新主题就加轴,重了就合并——每周 GC 顺手看一眼)")
    print(f"- 表里共 {len(table)} 个轴,近 30 天新加 {len(fresh)} 个"
          f"{'(' + '、'.join(fresh) + ')' if fresh else ''},上限 {AXIS_NEW_MAX_30D}")
    print(f"- 还没用过的轴:{'、'.join(unused) if unused else '(无)'}")
    print(f"- 只用过一次的轴:{'、'.join(once) if once else '(无)'}"
          "  ← 堆多了通常是在给同一件事换名字,GC 时合并")

    print(f"\n# 禁用来源(近 {SOURCE_WINDOW_DAYS} 天出过题,今天不许再用)")
    print("\n".join(f"- {s}" for s in blocked) if blocked else "-(无)")

    sealed = [e for e in entries if e.status == "封存"]
    print("\n# 封存主旨(已经问透,永久不再问)")
    print("\n".join(f"- {e.gist}" for e in sealed) if sealed else "-(无)")

    pending = [e for e in entries if e.status == "待答" and e.date < now]
    if pending:
        print("\n# 状态还没结的旧题(处理完上一期回答后要改成 已答/未答/封存)")
        for e in pending:
            print(f"- 第 {e.lineno} 行:{e.date} {e.num} {e.gist}")

    print(f"\n# 规矩:同一来源 {SOURCE_WINDOW_DAYS} 天内不重出;同一个轴 {AXIS_WINDOW_DAYS} 天内不重出;")
    print(f"#       主旨和上面任何一条撞车都作废;字面查重是下限不是上限,同轴旧题自己再比一遍;")
    print(f"#       轮不开就出 自由题 / Diary(不占来源冷却期);写完跑 asked_log.py --check")


def do_check(entries: list) -> int:
    now = today()
    errors, warnings = [], []

    cur = [e for e in entries if e.date == now]
    nums = sorted(e.num for e in cur)
    if nums != ["问题1", "问题2"]:
        errors.append(f"{now} 的台账应该正好两行(问题1、问题2),现在是 {nums or '空'} —— 出了题就要记账")

    for e in cur:
        if e.status not in STATUSES:
            errors.append(f"{now} {e.num} 状态 '{e.status}' 不在 {STATUSES} 里")
        if not e.source or not e.gist:
            errors.append(f"{now} {e.num} 来源或主旨是空的")

    past = [e for e in entries if e.date < now]
    for e in cur:
        for s in sources(e):
            if exempt(s):
                continue
            clash = [
                p for p in past if s in sources(p) and (now - p.date).days < SOURCE_WINDOW_DAYS
            ]
            if clash:
                last = max(clash, key=lambda x: x.date)
                errors.append(
                    f"{e.num} 来源 {s} 在 {last.date} 刚出过题({(now - last.date).days} 天前,"
                    f"冷却 {SOURCE_WINDOW_DAYS} 天):换个来源,或出自由题"
                )

    table = axis_table()
    added = axis_added_on(table)
    fresh = [k for k, v in added.items() if (now - v).days < 30]
    for e in cur:
        if e.axis not in table:
            errors.append(
                f"{e.num} 的轴「{e.axis}」还不在 Meta/问题台账.md 的轴表里。"
                f"库里长出新主题时加轴是正常的:先往《轴表》补一行(轴名 + 一句说明),再用它出题。"
                f"但先确认它不是已有轴换个名——同轴查重全靠这一栏"
            )
            continue
        if e.axis not in [p.axis for p in past]:  # 这个轴第一次被用来出题
            for name, (desc, _) in table.items():
                if name == e.axis:
                    continue
                sim = similarity(f"{e.axis}{table[e.axis][0]}", f"{name}{desc}")
                if sim >= SIM_THRESHOLD:
                    warnings.append(
                        f"{e.num} 新用的轴「{e.axis}」和已有的「{name}」说明高度重合"
                        f"(相似度 {sim:.2f}):确认这不是同一个轴换了名字,是的话合并掉"
                    )
            if len(fresh) >= AXIS_NEW_MAX_30D:
                errors.append(
                    f"近 30 天已经新起了 {len(fresh)} 个轴({'、'.join(fresh)}),"
                    f"上限 {AXIS_NEW_MAX_30D}:这道题先归到已有的轴,轴表要动留给每周 GC 统一整理"
                )
        same = [p for p in past if p.axis == e.axis]
        recent = [p for p in same if (now - p.date).days < AXIS_WINDOW_DAYS]
        if recent:
            last = max(recent, key=lambda x: x.date)
            errors.append(
                f"{e.num} 的轴「{e.axis}」{last.date} 刚问过({(now - last.date).days} 天前,"
                f"冷却 {AXIS_WINDOW_DAYS} 天):{last.gist}"
            )
        d30 = len([p for p in same if (now - p.date).days < 30]) + 1
        if d30 >= AXIS_MAX_30D:
            errors.append(f"{e.num} 的轴「{e.axis}」近 30 天已经是第 {d30} 道:换个轴,问得太偏食了")
        elif d30 >= AXIS_BUSY_30D:
            warnings.append(
                f"{e.num} 的轴「{e.axis}」近 30 天第 {d30} 道:"
                f"把同轴那几道旧题读一遍,确认这道真问的不是同一件事"
            )
    if len(cur) == 2 and cur[0].axis == cur[1].axis:
        errors.append(f"今天两道题在同一个轴「{cur[0].axis}」上:两道题要问不同的方面")

    # 封存的不受窗口限制:那是"问透了"的结论,永久有效
    pool = [p for p in past if (now - p.date).days <= LIST_WINDOW_DAYS or p.status == "封存"]
    for e in cur:
        for p in pool:
            s = similarity(e.gist, p.gist)
            if s >= SIM_THRESHOLD:
                errors.append(
                    f"{e.num}「{e.gist}」和 {p.date} {p.num}「{p.gist}」相似度 {s:.2f}"
                    f"(阈值 {SIM_THRESHOLD}):换一道"
                )
    if len(cur) == 2:
        s = similarity(cur[0].gist, cur[1].gist)
        if s >= SIM_THRESHOLD:
            errors.append(f"今天两道题自己就撞了(相似度 {s:.2f}):两道题要来自不同概念/笔记")

    stale = [p for p in past if p.status == "待答"]
    for p in stale:
        warnings.append(f"{p.date} {p.num} 还挂在「待答」:处理上一期回答时忘了结状态(第 {p.lineno} 行)")

    for w in warnings:
        print(f"⚠️  {w}")
    for e in errors:
        print(f"❌ {e}")
    if errors:
        print(f"\n提问查重不通过:{len(errors)} 个错误,{len(warnings)} 个警告")
        return 1
    print(f"提问查重通过:0 个错误,{len(warnings)} 个警告")
    return 0


if __name__ == "__main__":
    data = load()
    sys.exit(do_check(data) if "--check" in sys.argv[1:] else (do_list(data) or 0))
