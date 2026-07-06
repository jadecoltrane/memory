---
type: decision
created: 2026-07-06
last-verified: 2026-07-06
supersedes: 记忆库vault已迁出iCloud到本地只用git同步
---

# 结论

vault 最终留在原 iCloud 路径 `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/memory`,没有迁出本地。用 `.git` → `.git.nosync` 改名 + 同名 symlink 的方式,把 git 内部数据排除出 iCloud 同步(iCloud 认 `.nosync` 后缀约定,完全不碰这个文件夹);`.gitignore` 加了 `.git.nosync/` 防止被 git 自己当成未追踪内容。配套把 Obsidian 的「Git」社区插件整个关闭,git 操作只通过终端/Claude Code 手动执行。

# 为什么

- 当晚先执行了 decisions/记忆库vault已迁出iCloud到本地只用git同步.md 的迁出方案(整体复制到 `~/Documents/Obsidian/memory`),但会话中途发现本地那份副本消失、iCloud 路径的仓库工作区又回退到了旧版本——推测是用户最初那次卡在"正在准备拷贝"的 Finder 操作,其实并未真正卡死,而是在后台持续运行,期间悄悄完成并覆盖了本地新副本。核对确认 GitHub 上的 `jadecoltrane/memory` 完整无损(用 `git reset --hard origin/main` 把 iCloud 副本的工作区拉回一致状态,没有任何独家未推送内容丢失)
- 出于这次意外,用户改变主意:与其整体迁出本地、还要单独解决手机端 vault 归属问题,不如直接用 pitfalls/git仓库放iCloud目录可能因大量小文件同步冲突.md 里早就评估过的"方案 1"根治——成本更低(不用换手机端 App、不用付费),且直接对症"iCloud 和 git 内部文件互相干扰"这个根因
- 关闭 Git 插件是因为 `.obsidian/community-plugins.json` 本身也跟着 vault 走 iCloud 同步,只在手机上关闭插件也会通过 iCloud 同步到 Mac、意外把 Mac 端也一起关掉;干脆两边都不再依赖这个插件自动跑 git,避免"两台设备同时对 `.git` 发起操作"这个原始冲突场景本身再发生

# 影响

- 手动在 Obsidian(任一设备)编辑笔记,内容仍会通过 iCloud 正常同步到其他设备,也仍会被 git 正常识别为工作区改动——**只是不会有人自动帮你 commit/push 了**,需要在 Mac 上手动或通过 Claude Code 会话执行 `git add/commit/push` 才会进 GitHub
- 手机端如果之前装了 Git 插件,建议直接在插件设置里禁用,不用像"方案 1"最初设想的那样单独用 a-Shell 重新认领 git 历史——因为现在压根不需要手机直接操作 git

相关:[[pitfalls/git仓库放iCloud目录可能因大量小文件同步冲突]]、[[decisions/记忆库vault已迁出iCloud到本地只用git同步]]、[[decisions/数据层保持Markdown加Git但Obsidian插件放开用]]
