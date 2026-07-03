---
type: decision
created: 2026-07-03
last-verified: 2026-07-03
---

# 为什么

用户日常对话以 Gemini 网页版为主,但它连接 GitHub 只是导入静态快照:只读、不同步、不能推送——说"记下来"落不了库。Gemini CLI 能读写但用户不用命令行。故 2026-07-03 用户决定移除 Gemini 整合(删除各仓库 GEMINI.md)。

# 现行做法

Gemini 里聊到有价值的回答,由用户复制粘贴到 Claude 会话并说「记下来」,由 Claude 提炼入库。

# 何时失效

Gemini 网页版具备向 GitHub 写入的能力、或用户开始使用 Gemini CLI 时,可重新接入——库是纯 Markdown,接入只是加回一个指针文件。

相关:[[decisions/记忆库用纯Markdown加Git不绑定任何AI工具]]
