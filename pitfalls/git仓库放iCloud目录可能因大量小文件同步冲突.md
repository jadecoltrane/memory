---
type: pitfall
created: 2026-07-03
last-verified: 2026-07-06
---

# 症状

git 仓库 clone 进 iCloud 云盘目录(如 Obsidian 的 iCloud vault)后,操作变慢、偶发文件冲突副本。

**2026-07-06 手机端具体报错**:Obsidian Git 插件(isomorphic-git)在手机上操作工作台笔记时连续报 `An internal error caused this command to fail...Index file is empty (.git/index)`,紧接着几次 `Request failed. The request timed out`(后者是索引坏掉后续操作连锁失败,不是独立故障)。

# 原因

`.git` 目录内含大量小文件,iCloud 同步机制对此不友好,可能与 git 写入竞争。

**2026-07-06 复盘澄清**:最初以为触发条件是"两台设备同时编辑",但当天实际时间线是——AI 在云端(远程会话)直接 push 了新提交到 GitHub,用户随后打开手机 Obsidian,手机端全程没有任何人为编辑动作,依然触发了报错。更可能的机制是:iCloud 为了省手机存储空间,对不常访问的文件会做"占位"(文件可见但内容尚未真正下载到本地,需要用到时才现拉),`.git/index`、`.git/objects` 这类内部文件平时用不到,很容易长期停留在"占位未下载"状态。一旦在这些文件还没真正落地时,Git 插件被触发去 pull 远端新提交(比如 AI 刚 push 完、打开 App 自动 pull),读到的可能是尚未下载完成的占位内容,于是报 index 为空。也就是说触发条件是"本地 `.git` 文件未完整下载 + 此时发起了 git 操作",不一定需要两台设备同时写。

# 解法(遇到 index 损坏时)

在能跑终端的设备(Mac)上:

```bash
cd 你的vault路径
rm .git/index
git reset      # 用当前 HEAD 重建索引,不动工作区文件
git status     # 确认恢复正常
```

真实数据不受影响——vault 的真身在 GitHub(`jadecoltrane/memory`),`.git/index` 只是本地暂存区状态,坏了顶多丢一点还没提交推送的改动。

# 预防(降低复发概率,而非根治)

**⚠️ 2026-07-06 晚本节已过时**:用户当晚改变主意,Mac 端 vault 已整体迁出 iCloud 到 `~/Documents/Obsidian/memory`,只用 git 同步(见 decisions/记忆库vault已迁出iCloud到本地只用git同步.md),Mac 端此坑不再适用;手机端方案待落地。以下保留当天早些时候的原始记录:

2026-07-06 用户明确选择**暂不改动架构**(继续用 iCloud 同步 vault + 两台设备都装 Obsidian Git 插件),原因是备选方案(把 `.git` 用 `.nosync` 排除出 iCloud 同步、仓库搬出 iCloud 改用 Working Copy 桥接、换 Obsidian Sync 付费同步)都要么手机端需要额外用终端 App(如 a-Shell)重新认领 git 历史、要么要多装一个 App/掏订阅费,复杂度/成本超过当前问题的实际烦扰程度。日常靠这几条习惯把风险压低:

- **AI/远程会话刚 push 完,别立刻在手机上打开 App 就操作**:等个一两分钟再打开,给手机上的 iCloud 一点时间把新的 `.git` 内部文件真正下载下来,再触发 pull
- 第一次 pull 失败报 index 相关错误时,**先别慌,退出 App 等一会再进去重试一次**——如果是占位文件未下载完导致的,重试往往能自愈,不一定要马上跑修复命令
- 尽快 commit + push,减少本地未提交改动的暴露时间,即使 index 又坏,损失也小

**如果以后想彻底根治**,评估过的方案在这里,不用重新分析:
1. `.git` 改名 `.git.nosync` + 建 symlink,让 iCloud 完全不碰 git 内部文件,手机端需要用 a-Shell 之类的终端 App 跑 `git init && git remote add origin ... && git fetch && git reset origin/main` 重新认领历史(不会覆盖已同步的笔记内容)——Mac 端简单,手机端这步没有实测验证过
2. 仓库整体搬出 iCloud,手机端换 Working Copy 桥接 Obsidian 移动版
3. 换用 Obsidian Sync(付费,约 4 美元/月)替代 iCloud 做笔记同步,git 只留作 GitHub 备份/自动化通道

相关:[[decisions/数据层保持Markdown加Git但Obsidian插件放开用]]、[[pitfalls/macOS文件名NFDNFC不一致会让git把整个中文笔记文件夹误判成已删除]](iCloud 同步在这个仓库上踩出的另一个具体坑)
