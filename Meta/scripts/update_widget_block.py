#!/usr/bin/env python3
"""把当天工作台压成几行纯文本,写进 Home.md 顶部的 %% 注释块,给 iOS 主屏小组件看。

Obsidian 的小组件跑在独立的系统扩展进程里,不加载插件、不套主题 CSS,只把笔记原始
文本切一段显示——所以 Home.md 开头的 dataviewjs 代码块就是小组件上那一屏代码。
解法是让小组件读到的第一段是人话:纯文本放文件最前面,用 `%%` 注释包起来,
Obsidian 自己就会在阅读视图和实时预览里隐藏它,页面视觉一点不变。

用 `%%` 而不是 <div>+CSS 隐藏:CSS 方案要么依赖片段被启用、要么依赖 :has() 支持,
任何一条不成立,页面顶部就会露出一块裸文本;`%%` 是 Obsidian 原生语法,没有依赖。

机械生成而不是让日更的 AI 顺手写:小组件是"系统还活着"的外部信号之一(第一行带
日期,手机上一眼能看出同步有没有停),这类兜底不挂在 prompt 遵守上。
块不存在就自动补,所以哪天被误删也能自愈。
"""

import re
import sys
from pathlib import Path

HOME = Path(__file__).resolve().parents[2] / "Home.md"

# 小组件小尺寸大约只放得下 5~6 行折行后的文本,所以每行都压到一句话以内
LIMIT_DRAW_TITLE = 30
LIMIT_DRAW_HINT = 30
LIMIT_QUESTION = 28


def clean(text: str) -> str:
    text = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", text)  # [[路径|显示名]] → 显示名
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"[*`]", "", text)
    return text.strip()


def cut(text: str, limit: int) -> str:
    """截断到 limit 字并加省略号;没截断的原样返回(调用方靠这个判断要不要补问号)。"""
    text = clean(text)
    if len(text) <= limit:
        return text
    return text[:limit].rstrip("　 ,,、。;;::—-(()") + "…"


def question_gist(body: str) -> str:
    """压成一行:取第一个问句,并把"XX这个概念页提到一种说法"这类套话压成"XX:"。

    不取最后那个问句——它常以"还是说……"开头,单独拎出来是个没有主语的残句;
    第一句反而带着题目出自哪个概念,而那正是小组件上一眼要看的东西。
    """
    body = re.sub(r"[((][^))]*[))]", "", clean(body))  # 括号补充说明在小组件上只占地方
    body = re.sub(
        r"^(.{2,12}?)(这[个篇])?(概念页|笔记)[里中]?(提到|讲到|说过|说)(过)?(一[种个条])?(说法|观点|判断)?[::,,]\s*",
        r"\1:",
        body,
    )
    first = re.split(r"[??]", body)[0].strip()
    gist = cut(first or body, LIMIT_QUESTION)
    return gist if gist.endswith("…") else gist + "?"


def build_lines(text: str, date: str) -> list[str]:
    lines: list[str] = []

    draw = re.search(r"^> \[!draw\][^\n]*", text, re.M)
    if draw:
        title = draw.group(0).split("] ", 1)[1]
        title = title.split(" · ", 1)[1] if " · " in title else title
        lines.append(f"🎴 {date} 抽卡 · {cut(title, LIMIT_DRAW_TITLE)}")
        block = text[draw.end():].split("\n\n", 1)[0]
        hint = re.search(r"^> \d+\.\s*(.+)$", block, re.M)
        if hint:
            lines.append("· " + cut(hint.group(1), LIMIT_DRAW_HINT))

    for n in ("1", "2"):
        ask = re.search(rf"^> \[!ask\|{n}\][^\n]*\n((?:^>.*\n)+?)(?=^> ?> |\Z)", text, re.M)
        if ask:
            body = " ".join(l.lstrip("> ").strip() for l in ask.group(1).splitlines())
            lines.append(f"❓ 问{n} {question_gist(body)}")

    return lines


def main() -> int:
    text = HOME.read_text(encoding="utf-8")
    gen = re.search(r"^generated:\s*(\d{4})-(\d{2})-(\d{2})", text, re.M)
    date = f"{int(gen.group(2))}/{int(gen.group(3))}" if gen else ""

    lines = build_lines(text, date)
    if not lines:
        print("✗ Home.md 里既找不到 🎴 抽卡也找不到 ❓ 问题卡,小组件块没法生成", file=sys.stderr)
        return 1

    block = "%%\n" + "\n".join(lines) + "\n%%"
    # 只认 frontmatter 之后、第一个代码块之前的那个 %% 块,免得动到正文里的注释
    head = re.match(r"\A(---\n.*?\n---\n)(\n*)(%%\n.*?\n%%\n)?", text, re.S)
    if head is None:
        print("✗ Home.md 开头不是 frontmatter,不敢改", file=sys.stderr)
        return 1
    new = head.group(1) + "\n" + block + "\n" + text[head.end():].lstrip("\n")

    if new == text:
        print("小组件块无变化")
        return 0
    HOME.write_text(new, encoding="utf-8")
    print("✓ 已更新 Home.md 小组件块:\n" + "\n".join("  " + l for l in lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
