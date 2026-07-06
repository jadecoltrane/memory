# 结论速览(Compiled Truth)

> 这里存的是"现在信什么",不是"怎么信到这的"——后者去 `decisions/`、`pitfalls/`、`insights/` 的时间线文件里查。
> 只在同一主题下积累了 2 条以上相关记忆时才起条目,数量不够就不写。跟 `index.md` 不是一回事:index.md 是全量列表,机械生成;这里是精选聚合,手写综合。

## 记忆库自身怎么搭

独立仓库 `jadecoltane/memory`,纯 Markdown + Git + Obsidian 双链,不绑定任何私有格式,索引靠 GitHub Actions 自动重建。**仓库必须保持 GitHub 私有**——建库时曾误设为公开,2026-07-04 发现并转私有,公开期间的暴露只能止损无法追回。当前只接入 Claude(Gemini 网页版因为只能读快照、不能写入,暂不整合)。已知两个和 iCloud 同步相关的坑:仓库放 iCloud 目录可能因大量小文件同步冲突变慢;macOS 中文文件名 NFC/NFD 不一致会让 git 把整个文件夹误判成已删除(已用 `core.precomposeunicode true` 修复)。AI 自己写、自己读的记忆回路里,人类始终保留否决权,不做定期"这条还作数吗"式的主动追问;但规则执行不再只靠 AI 自觉——CI 每次推送做断链和 frontmatter 体检,工作台横幅带 48 小时心跳报警,静默挂掉会被看见。

相关:[[decisions/数据层保持Markdown加Git但Obsidian插件放开用]]、[[decisions/Gemini网页版只能读快照不能写入故暂不整合Gemini]]、[[insights/AI自写自读的记忆回路需要人工否决权]]、[[pitfalls/git仓库放iCloud目录可能因大量小文件同步冲突]]、[[pitfalls/macOS文件名NFDNFC不一致会让git把整个中文笔记文件夹误判成已删除]]、[[pitfalls/记忆库仓库曾默认公开导致隐私内容对外暴露]]

## 记忆库写入与维护的取舍原则

记忆只存代码/文件里查不到的东西(意图、被否决的方案、偏好、外部约束),这是准入门槛。给记忆库本身做设计(CLAUDE.md、GC/工作台 prompt、笔记结构)时,几种做法效果相当就选 token 成本更低的,但不能拿效果换省 token——这条标准反过来也约束了 GC 自身:weekly-gc.yml 加了零提交跳过闸门,安静周不读整份 CLAUDE.md,代价是按时间触发的维护(指针巡检、insight 降级)会顺延到下次有实质提交的周。用户手写/粘贴进 vault、结构和分类都乱掉的笔记,整理时 AI 可以实质性改写原文(拆分、改名、移动),这条不受"notes 复核不改原文"铁律约束——后者只管 checkable 内容的事实性复核,两者管的是不同阶段的不同风险。

相关:[[decisions/不往记忆库写grep能查到的事实]]、[[decisions/自动化与文档设计优先选省token不影响效果的轻量方案]]、[[decisions/整理手写笔记允许改写原文而不仅是追加复核记录]]
