# 结论速览(Compiled Truth)

> 这里存的是"现在信什么",不是"怎么信到这的"——后者去 `decisions/`、`pitfalls/`、`insights/` 的时间线文件里查。
> 只在同一主题下积累了 2 条以上相关记忆时才起条目,数量不够就不写。跟 `index.md` 不是一回事:index.md 是全量列表,机械生成;这里是精选聚合,手写综合。

## 记忆库自身怎么搭

独立仓库 `jadecoltane/memory`,纯 Markdown + Git + Obsidian 双链,不绑定任何私有格式,索引靠 GitHub Actions 自动重建。当前只接入 Claude(Gemini 网页版因为只能读快照、不能写入,暂不整合)。已知两个和 iCloud 同步相关的坑:仓库放 iCloud 目录可能因大量小文件同步冲突变慢;macOS 中文文件名 NFC/NFD 不一致会让 git 把整个文件夹误判成已删除(已用 `core.precomposeunicode true` 修复)。AI 自己写、自己读的记忆回路里,人类始终保留否决权,不做定期"这条还作数吗"式的主动追问。

相关:[[decisions/数据层保持Markdown加Git但Obsidian插件放开用]]、[[decisions/Gemini网页版只能读快照不能写入故暂不整合Gemini]]、[[insights/AI自写自读的记忆回路需要人工否决权]]、[[pitfalls/git仓库放iCloud目录可能因大量小文件同步冲突]]、[[pitfalls/macOS文件名NFDNFC不一致会让git把整个中文笔记文件夹误判成已删除]]
