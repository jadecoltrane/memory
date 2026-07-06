---
type: decision
created: 2026-07-06
last-verified: 2026-07-06
---

**⚠️ 已被 [[decisions/vault保留iCloud仅用nosync隔离git内部文件]] 取代**:当晚会话中途发现本地副本被一次仍在后台运行的 Finder 拷贝任务悄悄覆盖消失,用户改主意放弃迁出本地,改用 `.git.nosync` 方案留在 iCloud。以下保留原始记录:

# 结论

2026-07-06 晚,记忆库 vault 从 iCloud 整体迁到本地 `/Users/peiyaohuang/Documents/Obsidian/memory`,Mac 端不再依赖 iCloud,同步只走 git(Obsidian Git 插件 + GitHub)。迁移方式是整目录复制(不是重新 clone),`.obsidian/` 里的插件和配置(Dataview、Obsidian Git、Claudian)完整保留;git fsck、文件数、最新提交都核验一致。

# 为什么

- iCloud 和 git 的冲突已经踩过多次坑(见 pitfalls/git仓库放iCloud目录可能因大量小文件同步冲突.md、pitfalls/macOS文件名NFDNFC不一致会让git把整个中文笔记文件夹误判成已删除.md),当天连 Finder 拷贝 vault 都卡死在"正在准备"
- 本条**取代**同日早些时候"暂不改动架构"的选择(记录在上述 pitfall 的预防一节)——用户当晚明确表态"不想把 Obsidian 文件放在 iCloud 下了,只通过 git 同步"

# 影响与待办

- **Claude Code 本地会话的工作目录随之改变**,旧路径 `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/memory` 作废
- 旧 iCloud 副本删除前,新旧两份并存,**只能编辑新位置**,否则会分叉(删除后更新本条)
- **手机端方案待落地**:iCloud 副本一删,iPhone 上依赖 iCloud 的 vault 就没了;候选方案是手机建本地 vault(On My iPhone)+ Obsidian Git 插件直接 clone GitHub 仓库,落地后补记
