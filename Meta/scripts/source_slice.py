#!/usr/bin/env python3
"""只取原文里要看的那几轮 —— 别整份读进上下文。

存原文是 0 token(躺着不被读的文件没有成本),**读原文才是真花钱**:
库里两份导出加起来约 9.3 万字,整份读进来就是几万 token。
2026-08-02 那次审计我是分块整份读完的,现在回头看大部分块根本不需要。

所以规矩是:**先列目录,再切片,永远不要整份 Read。**

用法:
  python3 Meta/scripts/source_slice.py <文件>              # 列出所有轮次(便宜,只出标题行)
  python3 Meta/scripts/source_slice.py <文件> 19           # 只打印第 19 轮
  python3 Meta/scripts/source_slice.py <文件> 19-21        # 打印 19 到 21 轮
  python3 Meta/scripts/source_slice.py <文件> -g 苏格拉底   # 搜关键词,只出命中的轮次号
"""

import re
import signal
import sys
from pathlib import Path

signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # 被 head 截断时安静退出

MARK = re.compile(r"^message time: (.+)$")


def rounds(path: Path):
    """切成 [(轮次号, 时间, 起始行, 正文)] """
    lines = path.read_text(encoding="utf-8").splitlines()
    marks = [(i, m.group(1)) for i, l in enumerate(lines) if (m := MARK.match(l))]
    out = []
    for n, (i, ts) in enumerate(marks, 1):
        end = marks[n][0] if n < len(marks) else len(lines)
        out.append((n, ts, i + 1, lines[i + 1:end]))
    return out


def first_line(body):
    for l in body:
        if l.strip() and not l.startswith("---"):
            return l.strip()
    return ""


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    rs = rounds(path)
    args = sys.argv[2:]

    if not args:  # 目录模式
        total = sum(len("\n".join(b)) for *_, b in rs)
        print(f"# {path.name} — {len(rs)} 轮,全文约 {total} 字(整份读 ≈ 同量级 token)\n")
        for n, ts, ln, body in rs:
            print(f"{n:3d} | L{ln:<5d} | {ts} | {first_line(body)[:70]}")
        print("\n只看某几轮:加轮次号,例 `19` 或 `19-21`;搜关键词:`-g 关键词`")
        return

    if args[0] == "-g":  # 搜索模式:只回轮次号,不回正文
        kw = args[1]
        hits = [(n, ts, first_line(b)[:60]) for n, ts, _, b in rs if kw in "\n".join(b)]
        print(f"「{kw}」命中 {len(hits)} 轮:")
        for n, ts, q in hits:
            print(f"  {n:3d} | {ts} | {q}")
        return

    a, _, b = args[0].partition("-")  # 切片模式
    lo, hi = int(a), int(b or a)
    for n, ts, ln, body in rs:
        if lo <= n <= hi:
            print(f"\n{'=' * 20} 第 {n} 轮 | {ts} | 原文 L{ln}\n")
            print("\n".join(body).strip())


if __name__ == "__main__":
    main()
