---
type: note
created: 2026-07-03
source: 2026-07-03 讨论记忆库如何在多设备查看时确认的方案
checkable: false
---

# 内容

链路:云端 AI ⇄ GitHub ⇄ Mac(Obsidian Git 插件自动 pull/push)⇄ iCloud ⇄ iPhone 上的 Obsidian。

- Obsidian 的 iCloud 同步只覆盖用户自己的设备之间;AI 与用户之间的桥梁必须是 git,因为 iCloud 没有对外 API
- Obsidian Git 是社区插件,可设定时自动 pull/push
- 本条为 notes/ 的格式示例:只有用户说「记下来」时才新增这类笔记

相关:[[pitfalls/git仓库放iCloud目录可能因大量小文件同步冲突]]、[[decisions/记忆库用纯Markdown加Git不绑定任何AI工具]]、[[notes/obsidian/Obsidian最小配置是打开vault装Git插件]]
