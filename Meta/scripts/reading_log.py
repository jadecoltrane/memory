#!/usr/bin/env python3
"""工作台「📖 今日一读」的台账:挑体裁前查冷热,出稿后机器校验。

这一块的前身是每天两道提问。停掉它的直接原因是回答率——台账最后三周有 21 道
挂着「未答」,占了当期的一多半;而没被回答的题,第二天的生成又不许原样再问,
于是每天真正的产出是"再找两个还没问过的角度",不是内容。**只读不写之后,
重复的代价从"要不要答"变成"读着眼熟",防重复反而更要靠机器,不是更不用。**

一天一行(日期|体裁|素材|主旨),三张网:

- 体裁轮换:六个体裁 GENRE_WINDOW_DAYS 天内不重出、14 天内同一个最多 GENRE_MAX_14D 次。
  防的是全都滑向最好写的那一个(纯外部知识那种),其余五个名存实亡。
  体裁是**闭集**,写死在这里而不是像旧轴表那样放在台账里让当期临时加——加体裁是
  改版面,不是当天的选择;要加就改这个文件和 Meta/WORKBENCH.md,两边一起动。
- 素材冷却:同一篇笔记/概念页 SOURCE_WINDOW_DAYS 天内不许再当素材。
- 主旨相似度:字符 Dice ≥ SIM_THRESHOLD 判为同稿,换了体裁讲同一件事也拦得住。

用法:
  reading_log.py          打印近 90 天读过什么 + 体裁冷热 + 今天该出哪个体裁(选材前必读)
  reading_log.py --check  校验当期这一行 + Home.md 的卡片对不对得上(CI 兜底,不过退出码 1)
"""

import datetime
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LEDGER = ROOT / "Meta" / "阅读台账.md"
HOME = ROOT / "Home.md"

# 六个体裁。说明是给出题人看的一句话,详细规矩在 Meta/WORKBENCH.md。
# 三个朝库外(核查/复核/反例)、三个朝库内(对撞/串线/旧信),对半开是有意的:
# 全朝外就成了每天一条科普,和 🌱 延伸重复;全朝内就是 CLAUDE.md 反信息茧房
# 第 3 条点名的那种"所有论据都能在本库 grep 到"。
GENRES = {
    "对撞": "库里两条判断打架:摆出来、说清分歧在哪、给立场",
    "核查": "从 claim_audit 队列取一条引用状主张,当场联网核实,回写宿主笔记的标注",
    "复核": "从 review_due 取一篇到期的 checkable 笔记,重验主结论,写 ## 复核记录",
    "串线": "把散在三四篇里的同一条线索连起来讲一遍,够格就提名概念",
    "反例": "给库里一条判断找外部最强的反驳或边界条件",
    "旧信": "回放一段 Diary/ 或用户自己写下的原话,配一句现在读出来的东西",
}
# 外部锚点是硬要求的那几个体裁:卡里必须出现 [事实]/[推论]/[观点] 标记。
# 机器只查得到标记在不在,查不了标记后面那句是不是真的库外知识——所以它是
# 下限不是上限,和主旨查重一样。
NEEDS_ANCHOR = ("对撞", "核查", "复核", "反例")

LIST_WINDOW_DAYS = 90
GENRE_WINDOW_DAYS = 3  # 六个体裁,卡 3 天:连着三天不重样,又不至于把选择逼死
GENRE_MAX_14D = 3  # 14 天内同一个体裁最多三次 —— 超了就是在偏食
SOURCE_WINDOW_DAYS = 14
SIM_THRESHOLD = 0.45  # 阈值沿用旧提问台账实测标定的那道缝(真重复 0.49+,不相干 ≤0.33)
# 这两类素材不占冷却期:日记每天都是新内容,纯外部素材本来就不绑定库里某一篇。
# 留豁免是为了保证"合法的下一步"永远存在——所有相关笔记都在冷却期时还有路可走,
# 不至于被逼到只能复读。
EXEMPT_SOURCES = ("Diary", "外部")
# 素材写的是仓库路径就顺手查一下文件在不在:选材阶段最容易出的错是路径记岔了,
# 卡片里的双链跟着一起断,而断链在 Home.md 上看不出来(工作台不进 lint)。
PATH_PREFIXES = ("Notes/", "Concepts/", "Profile/", "Works/", "Archive/")

ROW = re.compile(r"^-\s*(\d{4}-\d{2}-\d{2})\s*\|([^|]+)\|(.+?)\|(.+?)$")
CARD = re.compile(r"^> \[!read\][^\n]*?今日一读\s*·\s*([^\s·]+)\s*·[^\n]*\n((?:^>.*\n?)*)", re.M)
ANCHOR = re.compile(r"\[(事实|推论|观点)")


class Entry:
    def __init__(self, date, genre, source, gist, lineno):
        self.date, self.genre = date, genre
        self.source, self.gist = source, gist
        self.lineno = lineno


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
        d, genre, source, gist = m.groups()
        try:
            date = datetime.date.fromisoformat(d)
        except ValueError:
            bad.append(f"{i}: 日期不合法 {d}")
            continue
        entries.append(Entry(date, genre.strip(), source.strip(), gist.strip(), i))
    if bad:
        print("⚠️  台账里有解析不了的行(格式:- 日期 | 体裁 | 素材 | 主旨):")
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

    只用二元组会漏掉换语序的改写(中文一个字就是一个词素);只用单字会被
    "是不是/有没有"这类高频虚字抬高底噪。取 max 两头都收。"""
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    return max(dice(a, b, 1), dice(a, b, 2))


def sources(entry) -> list:
    """一篇一读常常同时用到几篇(对撞至少两篇,串线三四篇),素材栏用 + 并列写。
    冷却期按每一个单独算——只认第一个的话,换个写法就能绕过去。"""
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


def genre_state(entries: list, now: datetime.date) -> dict:
    """体裁 -> (上次用是哪天, 近 14 天用了几次, 冷却中/超额的原因)。"""
    state = {}
    for g in GENRES:
        same = [e for e in entries if e.genre == g and e.date < now]
        last = max((e.date for e in same), default=None)
        d14 = len([e for e in same if (now - e.date).days < 14])
        why = ""
        if last is not None and (now - last).days < GENRE_WINDOW_DAYS:
            why = f"冷却中(还差 {GENRE_WINDOW_DAYS - (now - last).days} 天)"
        elif d14 >= GENRE_MAX_14D:
            why = f"近 14 天已经 {d14} 次(上限 {GENRE_MAX_14D})"
        state[g] = (last, d14, why)
    return state


def suggest(entries: list, now: datetime.date) -> list:
    """今天该出哪个体裁:可用的里面挑最久没出过的(没出过的排最前)。

    只是建议不是命令 —— 挑中的体裁当天可能没素材(claim 队列清空了、没有到期的
    复核),硬绑就会变成"为了体裁硬凑一篇"。--check 只管冷却和配额,不管是不是
    这一个,所以永远有合法的下一步。"""
    state = genre_state(entries, now)
    free = [g for g, (_, _, why) in state.items() if not why]
    return sorted(free, key=lambda g: (state[g][0] is not None, state[g][0] or now))


def do_list(entries: list) -> None:
    now = today()
    recent = [e for e in entries if (now - e.date).days <= LIST_WINDOW_DAYS]
    print(f"# 近 {LIST_WINDOW_DAYS} 天出过的一读(当期 {now},共 {len(recent)} 篇)\n")
    for e in sorted(recent, key=lambda x: x.date):
        print(f"{e.date} [{e.genre}] {e.source} —— {e.gist}")

    state = genre_state(entries, now)
    print("\n# 体裁冷热(挑定之后,把同体裁那几篇旧稿读一遍,读着像同一篇就换)")
    for g, desc in GENRES.items():
        last, d14, why = state[g]
        when = f"最近 {last}({(now - last).days} 天前)" if last else "还没出过"
        print(f"- {g}:{when},近 14 天 {d14} 次{'  🚫 ' + why if why else ''}")
        print(f"    {desc}")
        for e in sorted([x for x in entries if x.genre == g], key=lambda x: x.date)[-2:]:
            print(f"    · {e.date} {e.gist}")

    order = suggest(entries, now)
    print(f"\n# 今天建议的体裁:{' > '.join(order) if order else '(全在冷却里,按上面的冷热自己挑最松的那个)'}")
    print("#   建议不是命令:挑中的体裁今天没素材(队列空了、没有到期复核)就换下一个,别硬凑。")

    blocked = sorted(
        {
            s
            for e in entries
            if (now - e.date).days < SOURCE_WINDOW_DAYS
            for s in sources(e)
            if not exempt(s)
        }
    )
    print(f"\n# 禁用素材(近 {SOURCE_WINDOW_DAYS} 天用过,今天不许再用)")
    print("\n".join(f"- {s}" for s in blocked) if blocked else "-(无)")

    print("\n# 选材入口:")
    print("#   核查 → python3 Meta/scripts/claim_audit.py --queue(核心层排在前面)")
    print("#   复核 → python3 Meta/scripts/review_due.py")
    print("#   对撞/串线 → Meta/index.md + python3 Meta/scripts/search_memory.py 关键词")
    print("#   旧信 → Diary/<年>/ 最近几个月,或某篇笔记的「原话」段")
    print(f"\n# 规矩:同一体裁 {GENRE_WINDOW_DAYS} 天内不重出、14 天内最多 {GENRE_MAX_14D} 次;")
    print(f"#       同一素材 {SOURCE_WINDOW_DAYS} 天内不重用;主旨和上面任何一条撞车都作废;")
    print("#       写完跑 reading_log.py --check")


def read_card() -> tuple:
    """从 Home.md 取当期那张 [!read] 卡:(体裁, 正文)。没有就 (None, '')。"""
    if not HOME.exists():
        return None, ""
    m = CARD.search(HOME.read_text(encoding="utf-8"))
    return (m.group(1), m.group(2)) if m else (None, "")


def do_check(entries: list) -> int:
    now = today()
    errors, warnings = [], []

    cur = [e for e in entries if e.date == now]
    if len(cur) != 1:
        errors.append(f"{now} 的台账应该正好一行,现在是 {len(cur)} 行 —— 出了稿就要记账")
    past = [e for e in entries if e.date < now]
    state = genre_state(entries, now)

    card_genre, card_body = read_card()
    if card_genre is None:
        errors.append("Home.md 里找不到 `> [!read] 📖 今日一读 · <体裁> · <标题>` 这张卡")

    for e in cur:
        if e.genre not in GENRES:
            errors.append(f"体裁「{e.genre}」不在 {list(GENRES)} 里 —— 要加体裁得同时改 "
                          f"reading_log.py 和 Meta/WORKBENCH.md,不是当天临时起一个")
            continue
        if card_genre and card_genre != e.genre:
            errors.append(f"台账写的体裁是「{e.genre}」,Home.md 卡片标题上写的是「{card_genre}」:两边对不上")
        if state[e.genre][2]:
            errors.append(f"体裁「{e.genre}」{state[e.genre][2]}:换一个,建议 {' / '.join(suggest(entries, now)) or '(自己挑最松的)'}")
        if e.genre in NEEDS_ANCHOR and card_body and not ANCHOR.search(card_body):
            errors.append(
                f"「{e.genre}」这一篇卡里一个 [事实]/[推论]/[观点] 标记都没有 —— "
                f"这几个体裁的正文必须有库外的支点,标记是它唯一的机器信号"
            )
        if not e.source or not e.gist:
            errors.append("素材或主旨是空的")

        for s in sources(e):
            if exempt(s):
                continue
            if s.startswith(PATH_PREFIXES) and not (ROOT / (s + ".md")).exists():
                errors.append(f"素材 {s} 在仓库里找不到(路径记岔了?卡片里的双链多半也是断的)")
            clash = [
                p for p in past if s in sources(p) and (now - p.date).days < SOURCE_WINDOW_DAYS
            ]
            if clash:
                last = max(clash, key=lambda x: x.date)
                errors.append(
                    f"素材 {s} 在 {last.date} 刚用过({(now - last.date).days} 天前,"
                    f"冷却 {SOURCE_WINDOW_DAYS} 天):换一篇"
                )

        for p in past:
            if (now - p.date).days > LIST_WINDOW_DAYS:
                continue
            s = similarity(e.gist, p.gist)
            if s >= SIM_THRESHOLD:
                errors.append(
                    f"主旨「{e.gist}」和 {p.date}「{p.gist}」相似度 {s:.2f}"
                    f"(阈值 {SIM_THRESHOLD}):换一篇"
                )

    same_genre_recent = [p for p in past if cur and p.genre == cur[0].genre][-2:]
    if same_genre_recent:
        warnings.append(
            "同体裁最近两篇:"
            + ";".join(f"{p.date} {p.gist}" for p in same_genre_recent)
            + " —— 字面查重拦不住换套说法讲同一件事,自己再比一遍"
        )

    for w in warnings:
        print(f"⚠️  {w}")
    for e in errors:
        print(f"❌ {e}")
    if errors:
        print(f"\n一读查重不通过:{len(errors)} 个错误,{len(warnings)} 个警告")
        return 1
    print(f"一读查重通过:0 个错误,{len(warnings)} 个警告")
    return 0


if __name__ == "__main__":
    data = load()
    sys.exit(do_check(data) if "--check" in sys.argv[1:] else (do_list(data) or 0))
