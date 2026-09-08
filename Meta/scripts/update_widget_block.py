#!/usr/bin/env python3
"""把当天工作台压成几行纯文本,写进 Home.md 顶部,给 iOS 主屏小组件看。

Obsidian 的小组件跑在独立的系统扩展进程里,不加载插件、不套主题 CSS,只把笔记原始
文本切一段显示——所以 Home.md 开头的 dataviewjs 代码块就是小组件上那一屏代码。
解法是让小组件读到的第一段是人话:纯文本放文件最前面,页面里由 workbench.css
认出来整段藏掉,视觉一点不变。

**行数写死 WIDGET_LINES 行**:小组件是"有多少空间就往下念多少",速览只占三行的话,
剩下的空间它接着念 ```dataviewjs——所以文本不光要好看,还得把那一屏占满。不够的行数
用只含零宽空格的占位行补齐(在 Obsidian 里不可见,对小组件是空行,把代码顶出可视区)。
写死行数是因为 workbench.css 那条实时预览的选择器靠 `+ .cm-line` 一级级往下数,
数几级和这里的行数是死绑的:**改 WIDGET_LINES 必须同步改 CSS 里的链长**,
否则要么漏藏一行、要么把正文第一块一起藏掉。

标签放第一行行尾:CSS 只有"往后数"的兄弟选择器,没有往前数的,所以认路的那行必须最靠前。
用行尾标签而不是 `%%` 注释:`%%` 得单独占一行,小组件统共只放得下五六行折行后的文本。

机械生成而不是让日更的 AI 顺手写:小组件带日期,是"日更还在跑 + 手机同步没停"
在手机上唯一看得见的信号,这类兜底不挂在 prompt 遵守上。行被删了会自动补回。
"""

import re
import sys
from pathlib import Path

HOME = Path(__file__).resolve().parents[2] / "Home.md"
TAG = "#工作台"  # CSS 靠它认出这段,别改成别的词——workbench.css 里写死了
WIDGET_LINES = 5  # 改这个必须同步改 workbench.css 里 `+ .cm-line` 的链长
PAD = "​"  # 零宽空格:Obsidian 里不可见,小组件当空行,用来把代码顶出可视区

# 小组件小尺寸一行大约放得下 10 个汉字,三行内容加两行占位刚好铺满一屏
LIMIT_DRAW = 20
LIMIT_HINT = 22
LIMIT_READ = 16  # 体裁两个字 + 分隔符之后还剩这么多位置


def clean(text: str) -> str:
    text = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", text)  # [[路径|显示名]] → 显示名
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"[*`]", "", text)
    return text.strip()


def cut(text: str, limit: int) -> str:
    text = clean(text)
    if len(text) <= limit:
        return text
    return text[:limit].rstrip("　 ,,、。;;::—-(()") + "…"


def draw_block(text: str) -> tuple[str, str] | None:
    """抽卡那张卡取(被抽中的笔记名, 第一道回忆提示)——笔记名是线索,提示是真正的题。"""
    m = re.search(r"^> \[!draw\][^\n]*\n((?:^>.*\n)+)", text, re.M)
    if not m:
        return None
    body = m.group(1)
    link = re.search(r"\[\[[^\]|]*\|([^\]]*)\]\]|\[\[([^\]]*)\]\]", body)
    if link:
        cue = cut(link.group(1) or link.group(2), LIMIT_DRAW)
    else:
        title = m.group(0).split("\n", 1)[0].split("] ", 1)[1]
        cue = cut(title.split(" · ", 1)[-1], LIMIT_DRAW)
    hint = re.search(r"^> \d+\.\s*(.+)$", body, re.M)
    return cue, cut(hint.group(1), LIMIT_HINT) if hint else ""


def read_line(text: str) -> str | None:
    """一读那张卡取「体裁 · 标题」——标题是生成时就写好的一句话,不用再从正文里猜。"""
    m = re.search(r"^> \[!read\][^\n]*?今日一读\s*·\s*([^\s·]+)\s*·\s*([^\n]+)$", text, re.M)
    if not m:
        return None
    return f"📖 {m.group(1)} · {cut(m.group(2), LIMIT_READ)}"


def build_lines(text: str, date: str) -> list[str] | None:
    lines = []

    draw = draw_block(text)
    if draw:
        lines.append(f"🎴 {date} {draw[0]}".strip())
        if draw[1]:
            lines.append("· " + draw[1])

    read = read_line(text)
    if read:
        lines.append(read)

    if not lines:
        return None
    lines[0] += " " + TAG  # 标签必须在第一行:CSS 从它开始往下数
    return (lines + [PAD] * WIDGET_LINES)[:WIDGET_LINES]


def stray_tags(text: str) -> list[str]:
    """找正文里除速览段以外的标签——CSS 是整行藏,多一个标签就等于页面上少一行内容。

    实时预览那条选择器只认得出「这行有标签」、认不出是哪个,所以这是真会吞内容的坑,
    宁可当天日更失败重跑(auto-rerun 会换一版生成结果),也不能让它悄悄少一行。
    代码块里的 #f7f7f9 之类不算:围栏内的 # 不会被 Obsidian 渲染成标签。
    """
    body = re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)
    body = body.replace(TAG, "")
    return re.findall(r"(?<![\w&])#[^\s#,,。;;::!!??()()\[\]]{1,20}", body)


def main() -> int:
    text = HOME.read_text(encoding="utf-8")
    gen = re.search(r"^generated:\s*(\d{4})-(\d{2})-(\d{2})", text, re.M)
    date = f"{int(gen.group(2))}/{int(gen.group(3))}" if gen else ""

    lines = build_lines(text, date)
    if lines is None:
        print("✗ Home.md 里既找不到 🎴 抽卡也找不到 📖 一读卡,小组件速览没法生成", file=sys.stderr)
        return 1

    fm = re.match(r"\A---\n.*?\n---\n", text, re.S)
    if fm is None:
        print("✗ Home.md 开头不是 frontmatter,不敢改", file=sys.stderr)
        return 1

    # 旧速览段是从带标签那行(或早期版本的 %% 块)一直到第一个代码围栏为止。
    # 按"删到围栏"而不是"删固定行数"认边界:换过几版格式,行数不一定是当前这版。
    rest = text[fm.end():].lstrip("\n").splitlines(keepends=True)
    if rest and (TAG in rest[0] or rest[0].startswith("%%")):
        fence = next((i for i, l in enumerate(rest[:12]) if l.startswith("```")), None)
        if fence is None:
            print("✗ 速览段后面 12 行内找不到代码围栏,Home.md 结构不对,不敢改", file=sys.stderr)
            return 1
        rest = rest[fence:]
    new = fm.group(0) + "\n" + "\n".join(lines) + "\n" + "".join(rest)

    stray = stray_tags(new)
    if stray:
        print(f"✗ Home.md 正文里还有别的标签 {stray},它们所在的整行会被 CSS 一起藏掉", file=sys.stderr)
        return 1

    if new == text:
        print("小组件速览无变化")
        return 0
    HOME.write_text(new, encoding="utf-8")
    print("✓ 已更新 Home.md 小组件速览:")
    print("\n".join("  " + l.replace(PAD, "(占位空行)") for l in lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
