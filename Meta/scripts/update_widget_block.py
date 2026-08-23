#!/usr/bin/env python3
"""把当天工作台压成一行纯文本,写进 Home.md 顶部,给 iOS 主屏小组件看。

Obsidian 的小组件跑在独立的系统扩展进程里,不加载插件、不套主题 CSS,只把笔记原始
文本切一段显示——所以 Home.md 开头的 dataviewjs 代码块就是小组件上那一屏代码。
解法是让小组件读到的第一段是人话:纯文本放文件最前面,页面里由 workbench.css
按行尾的 #工作台 标签整行藏掉,视觉一点不变。

**必须是一行**:实时预览按行切 DOM,多行的话只有带标签那行会被藏掉,其余几行会
明晃晃留在页面顶部。行尾标签而不是 `%%` 注释:`%%` 得单独占一行,而小组件小尺寸
统共只放得下五六行折行后的文本,开头那行 `%%` 是实打实的浪费。

内容压到「抽卡笔记名 + 两道题的出处概念」:小组件是扫一眼的地方,抽卡笔记名本身
就是提取练习的线索,题目正文要打开 app 才写得了答案,塞进来只会把行数撑爆。

机械生成而不是让日更的 AI 顺手写:小组件带日期,是"日更还在跑 + 手机同步没停"
在手机上唯一看得见的信号,这类兜底不挂在 prompt 遵守上。行不存在会自动补,
所以哪天被误删也能自愈。
"""

import re
import sys
from pathlib import Path

HOME = Path(__file__).resolve().parents[2] / "Home.md"
TAG = "#工作台"  # CSS 靠它认出整行,别改成别的词——workbench.css 里写死了

# 小组件小尺寸一行大约放得下 10 个汉字、统共五六行,所以整行控制在 45 字以内
LIMIT_DRAW = 20
LIMIT_TOPIC = 7


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


def draw_cue(text: str) -> str | None:
    """抽卡那张卡取被抽中的笔记名——它就是今天要回想的那件事,比卡片标题更像线索。"""
    m = re.search(r"^> \[!draw\][^\n]*\n((?:^>.*\n)+)", text, re.M)
    if not m:
        return None
    link = re.search(r"\[\[[^\]|]*\|([^\]]*)\]\]|\[\[([^\]]*)\]\]", m.group(1))
    if link:
        return cut(link.group(1) or link.group(2), LIMIT_DRAW)
    title = m.group(0).split("\n", 1)[0].split("] ", 1)[1]
    return cut(title.split(" · ", 1)[-1], LIMIT_DRAW)


def question_topic(body: str) -> str:
    """取题目出自哪个概念:正文开头几乎都是"XX这个概念页提到一种说法:",前半截就是它。"""
    body = re.sub(r"[((][^))]*[))]", "", clean(body))
    m = re.match(
        r"(.{2,12}?)(这[个篇])?(概念页|笔记)[里中]?(提到|讲到|说过|说)(过)?(一[种个条])?(说法|观点|判断)?[::,,]",
        body,
    )
    if m:
        return cut(m.group(1), LIMIT_TOPIC)
    return cut(re.split(r"[,,。::]", body)[0], LIMIT_TOPIC)


def build_line(text: str, date: str) -> str | None:
    parts = []

    cue = draw_cue(text)
    if cue:
        parts.append(f"🎴 {date} {cue}".strip())

    topics = []
    for n in ("1", "2"):
        ask = re.search(rf"^> \[!ask\|{n}\][^\n]*\n((?:^>.*\n)+?)(?=^> ?> |\Z)", text, re.M)
        if ask:
            body = " ".join(l.lstrip("> ").strip() for l in ask.group(1).splitlines())
            topics.append(question_topic(body))
    if topics:
        parts.append("❓ " + " · ".join(topics))

    if not parts:
        return None
    return " ".join(parts) + " " + TAG


def stray_tags(text: str) -> list[str]:
    """找正文里除速览行以外的标签——CSS 是整行藏,多一个标签就等于页面上少一行内容。

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

    line = build_line(text, date)
    if line is None:
        print("✗ Home.md 里既找不到 🎴 抽卡也找不到 ❓ 问题卡,小组件行没法生成", file=sys.stderr)
        return 1

    # 只认 frontmatter 紧跟着的那一行(或早期版本的 %% 块),免得动到正文
    head = re.match(
        rf"\A(---\n.*?\n---\n)\n*(?:(?:%%\n.*?\n%%|[^\n]*{re.escape(TAG)})\n)?",
        text,
        re.S,
    )
    if head is None:
        print("✗ Home.md 开头不是 frontmatter,不敢改", file=sys.stderr)
        return 1
    new = head.group(1) + "\n" + line + "\n" + text[head.end():].lstrip("\n")

    stray = stray_tags(new)
    if stray:
        print(f"✗ Home.md 正文里还有别的标签 {stray},它们所在的整行会被 CSS 一起藏掉", file=sys.stderr)
        return 1

    if new == text:
        print("小组件行无变化")
        return 0
    HOME.write_text(new, encoding="utf-8")
    print("✓ 已更新 Home.md 小组件行:\n  " + line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
