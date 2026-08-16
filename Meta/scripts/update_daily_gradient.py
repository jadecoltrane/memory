#!/usr/bin/env python3
"""把当天的粉彩三角渐变写死进 workbench.css 的 daily-gradient 标记行。

页面加载即最终颜色,零跳变(JS 动态生成被否决过:要等 Dataview 跑完,
每次打开都先见旧色再跳一次)。由 daily-workbench.yml 每天调用;本地手动
跑一次也安全,同一天结果恒定(以北京日期为种子)。
"""
import hashlib
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CSS = Path(__file__).resolve().parents[2] / ".obsidian" / "snippets" / "workbench.css"
MARKER = "/* daily-gradient"


def pastel(hue: float, r1: float, r2: float) -> str:
    """很浅的粉彩:饱和 60~95%、亮度 89~94%,任何色相都柔和不出脏色"""
    return f"hsl({round(hue % 360)}, {round(60 + r1 * 35)}%, {round(89 + r2 * 5)}%)"


def main() -> None:
    day = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
    r = [b / 255 for b in hashlib.sha256(day.encode()).digest()]
    h0 = r[0] * 360
    # 三色按三角配色拉开(约 120° 间隔),避免挤在同一段色弧里发闷
    stops = [
        pastel(h0, r[1], r[2]),
        pastel(h0 + 100 + r[3] * 40, r[4], r[5]),
        pastel(h0 + 220 + r[6] * 40, r[7], r[8]),
    ]
    mid = round(40 + r[9] * 20)
    gradient = f"linear-gradient(135deg, {stops[0]} 0%, {stops[1]} {mid}%, {stops[2]} 100%)"

    text = CSS.read_text(encoding="utf-8")
    new_text, n = re.subn(
        r"linear-gradient\([^;]+\); /\* daily-gradient",
        gradient + "; /* daily-gradient",
        text,
        count=1,
    )
    if n != 1:
        sys.exit(f"没找到 daily-gradient 标记行,workbench.css 结构变了?({CSS})")
    if new_text != text:
        CSS.write_text(new_text, encoding="utf-8")
    print(f"{day} → {gradient}")


if __name__ == "__main__":
    main()
