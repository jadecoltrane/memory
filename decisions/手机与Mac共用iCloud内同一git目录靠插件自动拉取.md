---
type: decision
created: 2026-07-07
last-verified: 2026-07-07
supersedes: vault用xattr标记隔离git目录避免插件报错
---

# 手机与Mac共用iCloud内同一git目录,靠插件自动拉取

**决定**:用户明确选择手机直接跑 git(Obsidian Git 插件),和 Mac 共用 iCloud 里同一个 `.git`——为此移除了 `.git` 上的 `com.apple.clouddocs.not-sync` xattr(2026-07-06 晚),让 iCloud 把 `.git` 同步到手机。取代之前"xattr 隔离 `.git`、手机不碰 git"的方案。拉取全靠两端 Obsidian Git 插件(启动时 pull + 10 分钟自动 commit-and-sync),没有系统级定时任务。

**为什么**:用户的核心诉求是手机能独立从 GitHub 拉到云端每日更新(工作台等),不依赖 Mac 开机;曾提议的替代方案(手机独立 clone 一个本地 vault)被否,用户选了共用。已知代价:两端 git + iCloud 三方写同一个 `.git` 会产出 `index 2` 这类 iCloud 冲突副本(2026-07-06 实际发生过一次,已手动清理),这是结构性风险,选这个方案就是接受它。

**launchd 每日自动拉取做过又撤了**(2026-07-07):当天早些时候搭过一套 Mac 上的 launchd 定时任务(每天 07:00 pull + 失败通知 + 冲突副本自动清理,脚本曾在 `scripts/daily_pull.sh`),用户随后要求删除,同日全部卸载(plist、专用 bash 副本、脚本、日志都已删)。如果以后又需要,注意两个已趟过的坑:launchd 环境访问 iCloud 目录会被 macOS TCC 拦("Operation not permitted"),要么给执行器完全磁盘访问权限(建议用专用 bash 副本限定范围),要么别把脚本和仓库放 TCC 保护路径;cron 不会补跑睡眠错过的任务,launchd 的 StartCalendarInterval 会在唤醒时补跑。

**何时失效**:如果冲突副本频繁出现,说明两端经常同时开着 Obsidian 抢写 `.git`,这个方案就该放弃,回退到"手机独立 clone 本地 vault、iCloud vault 只留 Mac 用"。历史方案与坑见 [[pitfalls/git仓库放iCloud目录可能因大量小文件同步冲突]]、SUMMARY.md 里的完整反复记录(xattr、外部gitdir等中间方案已合并删除,不再单独立文件)。
