#!/usr/bin/env bash
# 机器人推送的统一出口:先 rebase 再 push,失败退避重试。
#
# 为什么需要(2026-08-02 认定):三个机器人(工作台日更、索引重建、每周 GC)
# 原本都是 checkout 完直接 push。用户这边 Obsidian Git 插件也在自动推。
# 两边撞上 → 机器人 push 被拒(non-fast-forward)→ workflow 红灯。
# `.trash/conflict-files-obsidian-git.md` 就是撞过的物证。
#
# 处理原则:
# - 冲突能靠 rebase 自动解决(改的是不同文件)→ 静默解决,继续推
# - 真冲突(同一文件同一处)→ **abort 并退出非 0**,不自作主张选一边。
#   机器人的产物都是可重新生成的(工作台重跑一次、索引重建一次、GC 重跑一次),
#   让整个 job 失败重来,比让机器人猜哪边对要安全。rerun-on-failure.yml 会接手重跑。
#
# 用法:bash meta/scripts/git_push_retry.sh <push-url> <branch>

set -euo pipefail

URL="${1:?缺少 push url}"
BRANCH="${2:?缺少分支名}"
MAX=5
DELAY=3

for i in $(seq 1 "$MAX"); do
  if ! git pull --rebase --autostash "$URL" "$BRANCH"; then
    echo "::error::rebase 冲突,不自动选边。已 abort,让本次 job 失败重跑。"
    git rebase --abort 2>/dev/null || true
    exit 1
  fi

  if git push "$URL" "HEAD:$BRANCH"; then
    echo "推送成功(第 $i 次尝试)"
    exit 0
  fi

  echo "::warning::第 $i 次推送被拒(大概率是刚刚有人推了),${DELAY}s 后重试"
  sleep "$DELAY"
  DELAY=$((DELAY * 2))
done

echo "::error::推送重试 $MAX 次仍失败"
exit 1
