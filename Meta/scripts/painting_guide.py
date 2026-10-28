#!/usr/bin/env python3
"""今日画作的「看懂这幅画」导览:写进 Home.md frontmatter 的 painting-guide,并校验。

为什么不让模型直接改 frontmatter:值里有引号、冒号、换行,裸写一次就能让整段
frontmatter 解析失败(2026-10-24 白上之白那次,横幅空白、心跳误报)。所以模型只写
一份纯文本草稿,由这里统一转成 JSON 字符串(= 合法的 YAML 双引号标量)再落盘。

草稿格式:一行一段,「标签:正文」,标签必须是 SECTIONS 里那几个,顺序随意。

用法:
  painting_guide.py --set 草稿文件    校验后写进 Home.md
  painting_guide.py --check           校验 Home.md 里当期导览(CI 兜底,不通过退出码 1)
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / "Home.md"
SECTIONS = ("背景", "故事", "怎么看", "画派", "资料")
MAX_SECTION = 260     # 单段字数上限:卡片在手机上展开,太长就成了维基搬运
MAX_TOTAL = 1100


def parse(text):
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(\S+?)\s*[::]\s*(.+)$", line)
        if not m or m.group(1) not in SECTIONS:
            raise ValueError(f"认不出的行(要「标签:正文」,标签只能是 {'/'.join(SECTIONS)}):{line[:40]}")
        if m.group(1) in out:
            raise ValueError(f"「{m.group(1)}」写了两次")
        out[m.group(1)] = m.group(2).strip()
    return out


def validate(text):
    secs = parse(text)
    missing = [s for s in SECTIONS if s not in secs]
    if missing:
        raise ValueError("缺段:" + "、".join(missing))
    for k, v in secs.items():
        if k != "资料" and len(v) > MAX_SECTION:
            raise ValueError(f"「{k}」{len(v)} 字,超过 {MAX_SECTION}")
    if sum(len(v) for v in secs.values()) > MAX_TOTAL:
        raise ValueError(f"总长超过 {MAX_TOTAL} 字")
    return "\n".join(f"{s}:{secs[s]}" for s in SECTIONS)


def read_field():
    s = HOME.read_text(encoding="utf-8")
    m = re.search(r"^painting-guide:\s*(.*)$", s, re.M)
    if not m:
        return None
    raw = m.group(1).strip()
    try:
        return json.loads(raw) if raw.startswith('"') else raw
    except json.JSONDecodeError:
        raise ValueError("painting-guide 不是合法的双引号字符串,frontmatter 会解析失败")


def write_field(val):
    s = HOME.read_text(encoding="utf-8")
    line = f"painting-guide: {json.dumps(val, ensure_ascii=False)}"
    if re.search(r"^painting-guide:", s, re.M):
        s = re.sub(r"^painting-guide:.*$", lambda _m: line, s, count=1, flags=re.M)
    else:
        s = re.sub(r"^(painting-intro:.*)$", lambda m: m.group(1) + "\n" + line, s, count=1, flags=re.M)
    HOME.write_text(s, encoding="utf-8")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--set":
        try:
            val = validate(Path(sys.argv[2]).read_text(encoding="utf-8"))
        except (ValueError, OSError) as e:
            print(f"✗ 导览没写进去:{e}", file=sys.stderr)
            return 1
        write_field(val)
        print("✓ 今日画作导览已写入 Home.md")
        return 0
    if sys.argv[1:] == ["--check"]:
        try:
            val = read_field()
            if not val:
                raise ValueError("Home.md 里 painting-guide 是空的——今日画作没配导览")
            validate(val)
        except ValueError as e:
            print(f"✗ {e}", file=sys.stderr)
            return 1
        print("✓ 画作导览格式正常")
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
