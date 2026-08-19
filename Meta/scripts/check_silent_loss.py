#!/usr/bin/env python3
"""静默丢失哨兵 —— 只认"文件真的没了",不认"是谁提交的"。

要防的事:Obsidian Git 的 vault backup 可能用旧版工作区覆盖新提交。纯快进、
零冲突、pull 一声不吭,被删掉的笔记不会有任何提示。

**判据不看是谁提交的**:author email 认不出机器人——AI 的提交 author 和手动提交
完全一样,按这个分会每次重建索引都自己报自己。只看两个机械事实:

1. **被删除的记忆文件数**(`Notes/ Concepts/ Profile/ Diary/` 下的 .md)。
   走 git 的重命名检测,所以"归档"(Notes/ → Archive/)被识别成改名、不算删除,
   不需要任何 commit message 白名单——白名单本身就是又一处依赖"有人记得写对"。
2. **`Meta/index.md` 条目数里"解释不了"的那部分跌幅**。索引每条记忆一行。
   归档 N 篇本来就该让索引少 N 条,所以比的是**实际跌幅**减去**能解释的跌幅**
   (删除数 + 移出被监控目录的改名数),差额超过 2 条才算异常。不扣这一步的话,
   一次正常归档就会误报——而误报是这类哨兵唯一的死法。

单篇删除不报(GC 的同族合并会正常删掉被吸收的那篇,而且那次改动本来就会告诉
用户)。只有成批消失才报——那才是覆盖事故的形状。

用法:
    python3 Meta/scripts/check_silent_loss.py                 # 比较 HEAD~1..HEAD
    python3 Meta/scripts/check_silent_loss.py <before> <after>
退出码 1 = 触发告警(CI 据此开 issue)。
"""

import subprocess
import sys

WATCH = ("Notes/", "Concepts/", "Profile/", "Diary/")
MAX_DELETED = 3          # 删到第 3 篇就该有人看一眼
MAX_INDEX_DROP = 0.05    # 索引条目掉 5% 以上


def git(*args) -> str:
    # core.quotepath=false 不能删:本库文件名基本全是中文,git 默认把它们转义成
    # "Notes/\346\200\235…"(还带引号),下面所有 startswith("Notes/") 会静默失配——
    # 不报错,只是一条都匹配不上,检查看着在跑其实全空。
    return subprocess.run(["git", "-c", "core.quotepath=false", *args],
                          capture_output=True, text=True).stdout


def index_entries(ref: str) -> int:
    """某个提交上 Meta/index.md 的条目数(每条记忆一行,以 '- ' 开头)。"""
    text = git("show", f"{ref}:Meta/index.md")
    return sum(1 for ln in text.splitlines() if ln.startswith("- "))


def main():
    before, after = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("HEAD~1", "HEAD")
    if not git("rev-parse", "--verify", before).strip():
        print(f"{before} 不存在(首次提交?),跳过")
        return 0

    # -M 打开重命名检测:Notes/ → Archive/ 的归档会被认成改名,不计入删除
    rows = [ln.split("\t") for ln in
            git("diff", "--name-status", "-M", before, after).splitlines() if "\t" in ln]
    deleted = [r[1] for r in rows if r[0] == "D" and r[1].startswith(WATCH)]
    # 改名走出被监控目录 = 归档,它让索引少一条是应该的,不是丢失
    moved_out = [r[1] for r in rows
                 if r[0].startswith("R") and len(r) > 2
                 and r[1].startswith(WATCH) and not r[2].startswith(WATCH)]

    b, a = index_entries(before), index_entries(after)
    explained = len(deleted) + len(moved_out)
    unexplained = (b - a) - explained

    alarms = []
    if len(deleted) >= MAX_DELETED:
        alarms.append(f"**{len(deleted)} 个记忆文件被删除**(归档改名不算在内):\n" +
                      "\n".join(f"  - `{f}`" for f in deleted))
    if b and unexplained > 2 and unexplained / b >= MAX_INDEX_DROP:
        alarms.append(f"**索引条目从 {b} 掉到 {a},其中 {unexplained} 条解释不了**"
                      f"(删除 {len(deleted)}、归档 {len(moved_out)},合计只能解释 {explained} 条)")

    if not alarms:
        print(f"正常:删除 {len(deleted)} 个、归档 {len(moved_out)} 个,索引 {b} → {a}")
        return 0

    print("⚠️ 疑似静默覆盖\n")
    for x in alarms:
        print(x + "\n")
    print("先确认这是不是你自己删的。不是的话,大概率是 Obsidian Git 的 vault backup")
    print("用旧版工作区盖掉了新提交(纯快进、零冲突、不报错)。")
    print(f"\n看这次改动:`git diff {before} {after}`")
    print("取回某个被删的文件:`git show " + before + ":<路径>`")
    return 1


if __name__ == "__main__":
    sys.exit(main())
