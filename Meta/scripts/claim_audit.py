#!/usr/bin/env python3
"""回声审计:查这个库有多少"库外知识"其实只是 AI 转述,以及哪些引用从没被核实过。

要防的是一个闭环:AI 说 → 记成笔记 → AI 读笔记 → 再说给用户听 → 听起来像被两个
独立来源确认过。第二次说出口时,"AI 转述、未核实"这个标签已经掉了,一条模型回忆
就洗成了一条有出处的事实。这个脚本把标签捡回来。

两件事机器能做,所以在这里做(不靠 AI 记得在回答里主动声明):
1. 按 frontmatter 的 source: 给每篇笔记分来源档,统计 AI 转述占比。
2. 把正文里所有"引用状"的字符串(人名+年份、《书名》、et al.)连同宿主笔记列成队列,
   标出哪些明确写了未核实。这是一份可以逐条去查证的工单,不是一个提醒。

引用形态只认硬特征(年份、et al.、书名号),宁可漏掉也不虚报——一份混进噪音的工单
没人会真去查。

用法:python3 Meta/scripts/claim_audit.py [--queue]
      不带参数只出汇总;--queue 打印完整待核实队列。
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCAN_DIRS = ["Notes", "Concepts"]

# 来源分档:按 source: 那行的关键词。顺序即优先级,先命中先算。
ORIGIN_RULES = [
    # 「用户手写」必须排在最前:这几条正文里也常提 AI,先判来源作者是谁。
    ("用户手写", re.compile(r"用户手写|自己提出|会话追问")),
    ("外部一手", re.compile(r"《|论文|文献|https?://(?!chatgpt|gemini)")),
    ("迁移存量", re.compile(r"迁移")),
    # 裸「对话」也算:这个库里的对话对象只有 AI,不写模型名不等于来源变了。
    ("AI 转述", re.compile(r"Gemini|ChatGPT|Claude|Fable|AI\b|陪练|工作台问答|命理|对话|会话")),
]

# 引用状字符串:只认硬特征,避免把普通括号当引用
# 括号里必须同时有「年份或 et al.」和「一个拉丁姓氏」,否则 2026-08-02 这种日期会淹掉队列。
CITATION = re.compile(
    r"(?:（|\()((?=[^）)]*(?:et al\.?|\b(?:1[89]|20)\d{2}\b))"
    r"(?=[^）)]*[A-Z][a-zA-Z]{2,})[^）)]{3,70})(?:）|\))"
    r"|(?:《([^》]{1,40})》)"
)
# 笔记自己承认没核实的措辞
UNVERIFIED = re.compile(r"未联网核查|未交叉核实|未经核实|未核实|未实测")


def origin_of(source_line: str) -> str:
    for label, pat in ORIGIN_RULES:
        if pat.search(source_line):
            return label
    return "未标来源" if not source_line else "其他"


def front(text: str, key: str) -> str:
    m = re.search(rf"^{key}:\s*(.+)$", text, re.M)
    return m.group(1).strip() if m else ""


def main() -> int:
    show_queue = "--queue" in sys.argv
    tally: dict[str, int] = {}
    queue: list[tuple[str, str, str, str, bool]] = []  # tier, note, origin, claim, flagged
    total = 0

    for d in SCAN_DIRS:
        for path in sorted((ROOT / d).rglob("*.md")):
            if path.name == "README.md":
                continue
            text = path.read_text(encoding="utf-8")
            total += 1
            source = front(text, "source")
            origin = origin_of(source)
            tally[origin] = tally.get(origin, 0) + 1
            tier = front(text, "tier") or "—"
            rel = str(path.relative_to(ROOT))
            seen = set()
            for m in CITATION.finditer(text):
                claim = (m.group(1) or m.group(2) or "").strip()
                if not claim or claim in seen:
                    continue
                seen.add(claim)
                # 同一行或紧邻是否已标未核实
                line_start = text.rfind("\n", 0, m.start()) + 1
                line_end = text.find("\n", m.end())
                line = text[line_start: line_end if line_end != -1 else len(text)]
                flagged = bool(UNVERIFIED.search(line) or UNVERIFIED.search(source))
                queue.append((tier, rel, origin, claim, flagged))

    print(f"📚 扫描 {total} 篇(Notes/ + Concepts/)\n")
    print("来源分档:")
    for label, n in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"  {label:<6} {n:>3} 篇  {n * 100 // total:>3}%")

    ai = tally.get("AI 转述", 0)
    print(f"\n⚠️  {ai} 篇({ai * 100 // total}%)的来源是 AI 对话。"
          f"引用这些笔记时必须连来源一起报,否则等于把模型回忆洗成事实。")

    unver = [q for q in queue if q[4]]
    core = [q for q in queue if q[0] == "核心"]
    print(f"\n🔍 引用状主张 {len(queue)} 条,其中 {len(unver)} 条所在笔记/行明确写了未核实;"
          f"{len(core)} 条落在 🧠 核心层(错了代价最大,优先核)。")

    if show_queue:
        print("\n待核实队列(核心层在前):")
        for tier, rel, origin, claim, flagged in sorted(
                queue, key=lambda q: (q[0] != "核心", q[1])):
            mark = "未核实" if flagged else "  ?  "
            print(f"  [{mark}] {tier:<3} {claim[:56]:<56} ← {rel}")
    else:
        print("   加 --queue 打印完整队列。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
