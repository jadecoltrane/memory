#!/usr/bin/env python3
"""记忆库体检:断链 + frontmatter + 结构性腐化(机械检查,不靠人记得)。

规则由 AI 执行,但 AI 会漏(真实案例:supersede 删旧文件后忘了更新引用它的双链;
2026-08-02 一天写了 100 条 note→note 链,把 hub-and-spoke 结构写成了网)。
这里做机器能做的兜底检查,错误退出码 1 让 CI 亮红灯,警告只提示。

错误(阻断):
- 断链:双链指向的文件必须存在。例外:[[Concepts/xxx]] 允许是幽灵节点(懒加载设计),
  但幽灵可以命中概念页的 aliases;裸名链接按 basename 或 aliases 解析。
- frontmatter:concepts 必须有 type: concept;profile 必须有 type: profile 和 updated。

警告(只提示,给 GC 排队):
- Notes/ 缺 frontmatter:用户手写笔记允许没有,GC 时才补齐。
- note→note 超标:单篇 > MAX_NOTE_LINKS 条,且超出部分没标"上下篇"。防网状化。
- 概念裸奔:已有概念页的名字/别名在正文里出现 ≥2 次却一次双链都没打。防图谱连不上。
- 出现在漏收:笔记挂了 [[Concepts/X]],X 的「出现在」区却没收录它。防枢纽不认识自己的辐条。
- 顶层过宽:Notes/ 直属子文件夹 > MAX_TOP_FOLDERS 个。上面那条只封单个文件夹的宽度,
  不封文件夹**数量**——一路平铺拆下去文件树会比笔记还难翻,所以拆分往深里走。
- 概念页延伸超限:延伸区 > MAX_EXTENSIONS 条,该做晋升(定论折进定义,其余进已探讨)。
- 指向 Archive/ 的双链:归档的东西不该还挂在图谱上,改成纯文本路径。
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LINK_CHECK_FILES = ["Home.md"]  # CLAUDE/RESOLVER 里是示例链接,不查
# 排除反斜杠:表格单元格里的双链必须把竖线转义成 [[目标\|别名]],不排掉会把 \ 当成目标的一部分而误报断链
WIKILINK = re.compile(r"\[\[([^\]|#^\\]+)")

MAX_NOTE_LINKS = 2  # 单篇 note→note 上限;标了"上下篇"的那行不计入
MAX_TOP_FOLDERS = 10  # Notes/ 直属子文件夹数上限;2026-08-16 定,当时 8 个
MAX_EXTENSIONS = 6  # 概念页「延伸」区条目上限
SERIES_MARK = re.compile(r"上下篇|上篇|下篇")  # 豁免标记:写在含该链接的同一行里

errors, warnings = [], []


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm, key = {}, None
    for line in text[4:end].splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and key:
            fm.setdefault(key, [])
            if isinstance(fm[key], list):
                fm[key].append(stripped[2:].strip())
        elif ":" in line and not line[:1].isspace():
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip()
            if val.startswith("[") and val.endswith("]"):
                fm[key] = [v.strip() for v in val[1:-1].split(",") if v.strip()]
            elif val:
                fm[key] = val
            else:
                fm[key] = []
    return fm


def collect_pages():
    """全库 md 文件 → (相对路径集合, basename 集合, 别名集合)"""
    paths, basenames, aliases = set(), set(), set()
    for p in ROOT.rglob("*.md"):
        rel_parts = p.relative_to(ROOT).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
        if rel_parts[:2] == ("Sources", "raw"):
            continue  # 导出原文不是记忆,不该成为可解析的链接目标(链进去就该报断链)
        rel = p.relative_to(ROOT).as_posix()[:-3]
        paths.add(rel)
        basenames.add(p.stem)
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        al = fm.get("aliases", [])
        if isinstance(al, str):
            al = [al]
        aliases.update(a for a in al if a)
    return paths, basenames, aliases


def archived_pages() -> set:
    """Archive/ 里的文件名 —— 用来认出"短写法双链其实指着归档件"。"""
    d = ROOT / "Archive"
    return {q.stem for q in d.rglob("*.md") if q.name != "README.md"} if d.is_dir() else set()


def check_git_quotepath():
    """脚本里调 git 却没加 core.quotepath=false —— 这类失败是无声的。

    本库文件名基本全是中文,git 默认把路径转义成 "Notes/\346\200\235…"(带引号),
    于是所有按路径前缀判断的逻辑一律失配:不抛异常、不报错,只是一条都匹配不上,
    脚本照常跑完并输出"0 个"。靠人记得加参数守不住,交给这条机械检查。
    """
    d = ROOT / "Meta" / "scripts"
    if not d.is_dir():
        return
    for q in sorted(d.glob("*.py")):
        text = q.read_text(encoding="utf-8")
        calls = re.findall(r"\[\s*[\"']git[\"'][^\]]*\]", text)
        for call in calls:
            if "quotepath" not in call and "quotepath" not in text:
                warnings.append(
                    f"{q.relative_to(ROOT).as_posix()}: 调 git 没加 "
                    f"`-c core.quotepath=false`,中文路径会被转义成 \\346… 而静默失配")
                break


def check_archive_frontmatter():
    """手动拖进 Archive/ 的文件不会有 archived 字段 —— 这条把它捞出来。

    Obsidian 里直接拖动是零成本的,但归档动作要求补 archived / archived-reason,
    否则事后没人说得清它是哪天为什么退役的,也分不清是归档还是随手挪错了。
    """
    d = ROOT / "Archive"
    if not d.is_dir():
        return
    for q in sorted(d.rglob("*.md")):
        if q.name == "README.md":
            continue
        fm = parse_frontmatter(q.read_text(encoding="utf-8"))
        missing = [k for k in ("archived", "archived-reason") if not fm.get(k)]
        if missing:
            rel = q.relative_to(ROOT).as_posix()
            warnings.append(f"{rel}: 在 Archive/ 里但缺 {'、'.join(missing)}(手动挪进来的?补上再提交)")


def check_links(path: Path, paths, basenames, aliases, archived=frozenset()):
    rel = path.relative_to(ROOT).as_posix()
    for target in WIKILINK.findall(path.read_text(encoding="utf-8")):
        target = target.strip()
        if not target or target.startswith("Concepts/"):
            continue  # 幽灵概念是设计允许的
        if target.startswith("Archive/"):
            # 归档的东西不该还留在图谱里。按 Archive/README.md,归档前要先把
            # 指向它的双链改成纯文本路径——这条就是那一步的守门员。
            warnings.append(f"{rel}: 双链指向已归档的 [[{target}]],改成纯文本路径并注明「已归档」")
            continue
        if "/" in target:
            if target not in paths:
                errors.append(f"{rel}: 断链 [[{target}]]")
        elif target in archived and target not in aliases:
            # 短写法([[某笔记]] 不带目录)照样能解析到 Archive/ 里,上面那条只拦得住
            # 写全路径的。Obsidian 默认就用最短写法,不补这条,手动归档是完全静默的。
            warnings.append(f"{rel}: 双链 [[{target}]] 指着 Archive/ 里的文件,改成纯文本路径并注明「已归档」")
        elif target not in basenames and target not in aliases:
            errors.append(f"{rel}: 断链 [[{target}]](按文件名和 aliases 都没找到)")


def check_frontmatter(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    top = rel.split("/")[0]
    fm = parse_frontmatter(path.read_text(encoding="utf-8"))
    if top == "Concepts":
        if fm.get("type") != "concept":
            errors.append(f"{rel}: 概念页 frontmatter 必须是 type: concept")
    elif top == "Profile":
        # Profile/ 下允许放 type: data 的数据文件(习惯打卡这类),它们不是画像页,
        # 没有 updated 语义也不该被催更新——只有真画像页才吃下面两条
        if fm.get("type") == "data":
            return
        if fm.get("type") != "profile":
            errors.append(f"{rel}: 画像页 frontmatter 必须是 type: profile")
        if "updated" not in fm:
            errors.append(f"{rel}: 画像页必须有 updated 日期")
    elif top == "Notes":
        if "type" not in fm:
            warnings.append(f"{rel}: 还没有 frontmatter(手写笔记?等 GC 补齐)")
        elif "created" not in fm:
            # Home.md 的「最近 7 天」只认 frontmatter 的 created,而且故意不退回 file.ctime
            # (clone/checkout 会把 ctime 整批刷成"刚才")。所以漏写 created 的后果是
            # 这篇在统计里永远不存在——不报错、不断链、症状只是数字偏小,没人会去查。
            # 这正是需要机器兜底的那类静默失败,所以报出来。
            warnings.append(f"{rel}: 缺 created: YYYY-MM-DD,「最近 7 天」统计会看不见它")


def collect_concept_names() -> dict:
    """概念页 → 它的所有可识别称呼(文件名 + aliases)。用于「裸奔」检查。"""
    names = {}
    d = ROOT / "Concepts"
    if not d.is_dir():
        return names
    for p in sorted(d.glob("*.md")):
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        al = fm.get("aliases", [])
        if isinstance(al, str):
            al = [al]
        names[f"Concepts/{p.stem}"] = [p.stem] + [a for a in al if a]
    return names


def check_note_links(path: Path):
    """note→note 密度。CONCEPTS.md 规定笔记之间不直接互链,走概念页中转;
    真的是同一论证上下篇时,在那一行里写上「上下篇」豁免。"""
    rel = path.relative_to(ROOT).as_posix()
    plain = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        hits = [t for t in WIKILINK.findall(line) if t.strip().startswith("Notes/")]
        if hits and not SERIES_MARK.search(line):
            plain += len(hits)
    if plain > MAX_NOTE_LINKS:
        warnings.append(
            f"{rel}: note→note 双链 {plain} 条(上限 {MAX_NOTE_LINKS})"
            f"——改走概念页中转(另一篇写成纯文本路径),或在那一行写明「上下篇/上篇/下篇」"
        )


def check_naked_concepts(path: Path, concept_names: dict):
    """已有概念页的名字在正文里裸文本反复出现,却一次双链都没打 → 图谱连不上。"""
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8")
    linked = {t.strip() for t in WIKILINK.findall(text)}
    stripped = WIKILINK.sub("", text)  # 去掉双链本身,只看裸文本
    for cpath, names in concept_names.items():
        if cpath in linked or cpath.split("/")[-1] in linked:
            continue
        if any(n in linked for n in names):
            continue
        for n in names:
            if stripped.count(n) >= 2:
                warnings.append(f"{rel}: 「{n}」出现 {stripped.count(n)} 次但没挂 [[{cpath}]]")
                break


def check_concept_backlinks(concept_names: dict):
    """反向检查:笔记挂了 [[Concepts/X]],X 的「出现在」区却没收录这篇。
    Obsidian 的反链面板能看到,但 AI 读的是概念页正文——出现在漏收 = 枢纽自己不知道谁连着它。"""
    for cpath in concept_names:
        p = ROOT / f"{cpath}.md"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        m = re.search(r"^## 出现在.*$", text, re.M)
        listed = set()
        if m:
            rest = text[m.end():]
            nxt = re.search(r"^## ", rest, re.M)
            for x in WIKILINK.findall(rest[: nxt.start()] if nxt else rest):
                listed.add(x.strip().split("|")[0].rsplit("/", 1)[-1])
        miss = []
        for n in sorted((ROOT / "Notes").rglob("*.md")):
            targets = [x.strip().split("|")[0] for x in WIKILINK.findall(n.read_text(encoding="utf-8"))]
            if (cpath in targets or cpath.split("/")[-1] in targets) and n.stem not in listed:
                miss.append(n.stem)
        if miss:
            warnings.append(f"{cpath}.md: 「出现在」漏收 {len(miss)} 篇 → {miss[0]} 等")


def check_top_folder_count():
    """顶层宽度上限。2026-08-17 撤掉了"单个文件夹 > 12 篇就报警"那条(用户决定:
    文件夹按需再建,不按数量凑),但顶层**数量**这条留着——一路在 Notes/ 下平铺新文件夹,
    一年后文件树比笔记本身还难翻(2026-08-16 按 9 篇/周算过,一年 ~470 篇 = 40 个顶层)。
    要拆就往深里拆,顶层锁在这个数。"""
    d = ROOT / "Notes"
    if not d.is_dir():
        return
    tops = sorted(x.name for x in d.iterdir() if x.is_dir())
    if len(tops) > MAX_TOP_FOLDERS:
        warnings.append(
            f"Notes/ 顶层 {len(tops)} 个文件夹(上限 {MAX_TOP_FOLDERS})——"
            f"该把近邻主题合并、或收进同一个大类下面了:{'、'.join(tops)}"
        )


def check_extension_cap(path: Path):
    """概念页延伸区的晋升机制:超过上限说明该做一次收敛,而不是继续堆。"""
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^## 延伸.*$", text, re.M)
    if not m:
        return
    rest = text[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    body = rest[: nxt.start()] if nxt else rest
    n = len([ln for ln in body.splitlines() if ln.startswith("- ")])
    if n > MAX_EXTENSIONS:
        warnings.append(
            f"{rel}: 延伸 {n} 条(上限 {MAX_EXTENSIONS})"
            f"——按 Meta/CONCEPTS.md 的晋升机制收敛:已成定论的折进定义,存疑的移进已探讨"
        )


# 「X 月 X 日补」这类词是"只在末尾接一段、没重读全文"留下的疤。补内容本身没问题,
# 问题是补完不重排——同一个判断散在三处、后面那段推翻前面那段还都留着。
# 词表只收那些除了交代"这个文件怎么长出来的"之外没有别的意思的说法。
APPEND_SCAR = re.compile(
    r"后续扩编|未改名|已删(?![除掉])|"
    r"(?:当天|同日|后来|之后|随后|次日)补(?![充偿])|"
    r"再补一?[条句段]|新增[::]|补记[::]"
)
# 「这段对话的核心是…」这类词把笔记锚在一场读者接触不到的会话上,是"对着来源写、
# 没有为只有这一篇的读者重写"留下的疤。词表只收指向会话本身的说法——「原文」不收,
# 因为它绝大多数时候指的是一部能查到的外部作品或本篇内已转录的内容,收了全是误报。
# 只收「这/那/本+段次场条+对话」这一档指示代词——它才是"指着笔记自己的出身"。「上一次对话」
# 「这一轮」不收:前者常指跟某人上次聊天(是内容),后者常指本篇里的上一轮推理(是篇内自指)。
# 抓不住的那一半在 CLAUDE.md:笔记的小标题和来源的段落一一对应,一个可疑词都不会留。
SOURCE_POINTER = re.compile(r"(?:这|那|本)(?:段|次|场|条)对话|同一天的对话")

# Profile/ 的规矩最严:只写结论本身,不写依据、日期、出处(CLAUDE.md「Profile/」)。
# 这里只查日期,因为只有它是机器认得准的;依据和出处交给 GC 人工看
BODY_DATE = re.compile(r"20\d{2}\s*[-/年]\s*\d{1,2}\s*[-/月]\s*\d{1,2}")


def strip_frontmatter(text: str) -> str:
    m = re.match(r"^---\n.*?\n---\n", text, re.S)
    return text[m.end():] if m else text


def check_append_scars(path: Path):
    """全库通用:正文里的追加痕迹。"""
    rel = path.relative_to(ROOT).as_posix()
    body = strip_frontmatter(path.read_text(encoding="utf-8"))
    hits = sorted(set(APPEND_SCAR.findall(body)))
    if hits:
        warnings.append(
            f"{rel}: 正文有追加痕迹「{'」「'.join(hits)}」——补完要重读全文重排,"
            f"不是在末尾接一段(CLAUDE.md「只记内容」)"
        )
    ptrs = sorted(set(SOURCE_POINTER.findall(body)))
    if ptrs:
        warnings.append(
            f"{rel}: 正文指向一场读者看不到的会话「{'」「'.join(ptrs)}」——"
            f"改成直接陈述,留判断本身、去掉它当初在回应谁(CLAUDE.md「只记内容」)"
        )


# 「AI 推的…落空了」「AI 别把那句当成…」这类句子记的是 AI 自己,不是用户
# (CLAUDE.md 判据:去掉"AI"两个字这句还成不成立)。只匹配 AI 后面直接跟动词/限定词
# 的写法——画像里「AI 交互设计师」「AI 辅助合规审查」是她的岗位和经历,不能误伤。
AI_SELF = re.compile(
    r"\bAI\s*(?:推|别|已|当时|之前|那个|这个|说的|的框架|的判断|的推断|的看法|自己)"
    r"|Claude\s*(?:代写|说|推|问|提|建议)"
    r"|上一(?:期|版)(?:给出|说|推|的推论)"
)


def check_profile_ai_traces(path: Path):
    """只管 Profile/:画像里出现"AI 当时怎么想的"就报,那不是用户画像。"""
    rel = path.relative_to(ROOT).as_posix()
    hits = sorted(set(AI_SELF.findall(strip_frontmatter(path.read_text(encoding="utf-8")))))
    if hits:
        warnings.append(
            f"{rel}: 画像里记了 AI 自己(「{'」「'.join(h.strip() for h in hits)}」)"
            f"——把「AI」两个字去掉这句还成立吗?不成立就重写"
        )


def check_profile_body_dates(path: Path):
    """只管 Profile/:画像页正文一个日期都不该有,frontmatter 的 updated 除外。"""
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8")
    if parse_frontmatter(text).get("type") == "data":
        return  # 习惯打卡那种数据文件,整篇都是日期
    n = len(BODY_DATE.findall(strip_frontmatter(text)))
    if n:
        warnings.append(f"{rel}: 画像正文里有 {n} 处日期——画像只写结论本身,不写依据、日期、出处")


def check_dataviewjs_blocks(path: Path) -> None:
    """dataviewjs 代码块不能以行注释结尾。

    2026-08-16 真实踩到:dataview 把代码包成 `(async () => { 代码 })()`,而它从
    markdown 拿到的代码块末尾没有换行,那句 ` })()` 就直接接在最后一行 `//` 后面被
    注释吃掉,整块报 Unexpected end of input。单看代码块本身语法完全正确,node --check
    也过,只有连包装一起看才暴露——所以必须机器查,靠人记得肯定要再犯。
    """
    rel = path.relative_to(ROOT).as_posix()
    for i, block in enumerate(re.findall(r"```dataviewjs\n(.*?)```", path.read_text(encoding="utf-8"), re.S), 1):
        lines = [ln for ln in block.rstrip().splitlines() if ln.strip()]
        if lines and lines[-1].lstrip().startswith("//"):
            errors.append(
                f"{rel}: 第 {i} 个 dataviewjs 块以行注释结尾——"
                f"dataview 追加的 `}})()` 会被这行 // 吃掉,整块报 Unexpected end of input。"
                f"把注释挪到代码上方,或改成 /* */"
            )


def main():
    paths, basenames, aliases = collect_pages()
    concept_names = collect_concept_names()
    archived = archived_pages()
    check_archive_frontmatter()
    check_git_quotepath()
    for top in ["Notes", "Concepts", "Profile"]:
        d = ROOT / top
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.md")):
            check_links(p, paths, basenames, aliases, archived)
            check_frontmatter(p)
            check_append_scars(p)
            if top == "Profile":
                check_profile_body_dates(p)
                check_profile_ai_traces(p)
            if top == "Notes":
                check_note_links(p)
                check_naked_concepts(p, concept_names)
            elif top == "Concepts":
                check_extension_cap(p)
    check_concept_backlinks(concept_names)
    check_top_folder_count()
    for name in LINK_CHECK_FILES:
        p = ROOT / name
        if p.exists():
            check_links(p, paths, basenames, aliases, archived)
            check_dataviewjs_blocks(p)

    for w in warnings:
        print(f"⚠️  {w}")
    for e in errors:
        print(f"❌ {e}")
    if errors:
        print(f"\n体检不通过:{len(errors)} 个错误,{len(warnings)} 个警告")
        sys.exit(1)
    print(f"体检通过:0 个错误,{len(warnings)} 个警告")


if __name__ == "__main__":
    main()
