---
type: note
created: 2026-07-03
source: 2026-07-03 与 Claude 讨论如何在 Obsidian 里查看记忆库,用户点名收藏
checkable: false
---

# 内容

**最小配置只有两步**:

1. 把 memory 仓库 clone 到电脑,在 Obsidian 里「打开文件夹作为仓库(Open folder as vault)」
2. 装社区插件 **Obsidian Git**,设自动 pull/push,与 GitHub 保持同步

**可选第三步**:只想看自己的知识点、不看 AI 的工作记忆时,设置 → Files & Links → Excluded files,排除 `decisions/`、`pitfalls/`、`insights/`、`questions/` 目录,搜索和图谱就只剩 `notes/`。随时可移除,完全可逆。

**看某条记忆的"朋友圈"**:打开一条笔记,命令面板(Cmd+P)输入 "local graph"(局部关系图)——只显示与这条直接相连的记忆,比全局图更适合顺藤摸瓜。

相关:[[notes/Obsidian用Git插件同步GitHub再经iCloud即可手机查看]]、[[decisions/记忆库用纯Markdown加Git不绑定任何AI工具]]
