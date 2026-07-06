---
type: decision
created: 2026-07-07
last-verified: 2026-07-07
supersedes: vault用xattr标记隔离git目录避免插件报错
---

# 手机与Mac共用iCloud内同一git目录并加launchd每日拉取兜底

**决定**:用户明确选择手机直接跑 git(Obsidian Git 插件),和 Mac 共用 iCloud 里同一个 `.git`——为此移除了 `.git` 上的 `com.apple.clouddocs.not-sync` xattr(2026-07-06 晚),让 iCloud 把 `.git` 同步到手机。取代之前"xattr 隔离 `.git`、手机不碰 git"的方案。

**为什么**:用户的核心诉求是手机能独立从 GitHub 拉到云端每日更新(工作台等),不依赖 Mac 开机;曾提议的替代方案(手机独立 clone 一个本地 vault)被否,用户选了共用。已知代价:两端 git + iCloud 三方写同一个 `.git` 会产出 `index 2` 这类 iCloud 冲突副本(2026-07-06 实际发生过一次,已清理),这是结构性风险,选这个方案就是接受它。

**配套兜底**(可靠性预先设计,不等出事再补):

- Mac 上 launchd 定时任务 `com.jade.memory-daily-pull`(plist 在 `~/Library/LaunchAgents/`,**不在本仓库里**,重装机器要按 `scripts/daily_pull.sh` 头部注释重建):每天 07:00 自动 `git pull`,Mac 睡眠错过就在下次唤醒时补跑
- 脚本本体在 `scripts/daily_pull.sh`(仓库内、有版本):pull 失败弹 macOS 通知 + 写日志 `~/Library/Logs/memory-daily-pull.log`,不静默;每次运行顺带清理 `.git` 顶层"原名文件还在"的带数字后缀冲突副本,清理过也会弹通知提醒冲突发生过
- launchd 环境下访问 iCloud 目录被 macOS TCC 拦,解法:专用 bash 副本 `~/.local/bin/memory-git-bash`(只给它完全磁盘访问权限,不放宽系统 bash),plist 用它执行脚本

**何时失效**:如果冲突副本频繁出现(通知反复弹),说明两端经常同时开着 Obsidian 抢写 `.git`,这个方案就该放弃,回退到"手机独立 clone 本地 vault、iCloud vault 只留 Mac 用"。历史方案与坑见 pitfalls/git仓库放iCloud目录可能因大量小文件同步冲突、decisions/vault用xattr标记隔离git目录避免插件报错。
