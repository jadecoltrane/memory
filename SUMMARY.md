# 结论速览(Compiled Truth)

> 这里存的是"现在信什么",不是"怎么信到这的"——后者去 `decisions/`、`pitfalls/`、`insights/` 的时间线文件里查。
> 只在同一主题下积累了 2 条以上相关记忆时才起条目,数量不够就不写。跟 `index.md` 不是一回事:index.md 是全量列表,机械生成;这里是精选聚合,手写综合。

## 记忆库自身怎么搭

独立仓库 `jadecoltrane/memory`,纯 Markdown + Git + Obsidian 双链,不绑定任何私有格式,索引靠 GitHub Actions 自动重建。**仓库必须保持 GitHub 私有**——建库时曾误设为公开,2026-07-04 发现并转私有,公开期间的暴露只能止损无法追回。当前只接入 Claude(Gemini 网页版因为只能读快照、不能写入,暂不整合)。iCloud 同步在这个仓库上踩过两个坑(大量小文件同步冲突拖慢 git 甚至弄坏 `.git/index`;macOS 中文文件名 NFC/NFD 不一致让 git 误判整个文件夹已删除,已用 `core.precomposeunicode true` 修复)。2026-07-06 晚一度尝试把 vault 整体迁出本地,因会话中途一次仍在后台运行的 Finder 拷贝任务悄悄覆盖了本地副本而放弃,最终方案是 vault 留在原 iCloud 路径,把 `.git` 改名 `.git.nosync` 建同名 symlink,让 iCloud 完全不碰 git 内部文件,同时关闭 Obsidian 的「Git」社区插件(该插件配置本身也跟 vault 走 iCloud 同步,只在一台设备关会同步到所有设备),git 操作全部改为终端/Claude Code 手动执行。AI 自己写、自己读的记忆回路里,人类始终保留否决权,不做定期"这条还作数吗"式的主动追问;但规则执行不再只靠 AI 自觉——CI 每次推送做断链和 frontmatter 体检,工作台横幅带 48 小时心跳报警,静默挂掉会被看见。

相关:[[decisions/数据层保持Markdown加Git但Obsidian插件放开用]]、[[decisions/vault保留iCloud仅用nosync隔离git内部文件]]、[[decisions/记忆库vault已迁出iCloud到本地只用git同步]]、[[decisions/Gemini网页版只能读快照不能写入故暂不整合Gemini]]、[[insights/AI自写自读的记忆回路需要人工否决权]]、[[pitfalls/git仓库放iCloud目录可能因大量小文件同步冲突]]、[[pitfalls/macOS文件名NFDNFC不一致会让git把整个中文笔记文件夹误判成已删除]]、[[pitfalls/记忆库仓库曾默认公开导致隐私内容对外暴露]]

## 记忆库写入与维护的取舍原则

记忆只存代码/文件里查不到的东西(意图、被否决的方案、偏好、外部约束),这是准入门槛。给记忆库本身做设计(CLAUDE.md、GC/工作台 prompt、笔记结构)时,几种做法效果相当就选 token 成本更低的,但不能拿效果换省 token——这条标准反过来也约束了 GC 自身:weekly-gc.yml 加了零提交跳过闸门,安静周不读整份 CLAUDE.md,代价是按时间触发的维护(比如 insight 降级)会顺延到下次有实质提交的周。CLAUDE.md 本身每次会话都无条件加载,2026-07-06 把"只有特定任务才需要"的内容(工作台生成规范、Memory GC 步骤、notes 复核节奏)拆成 WORKBENCH.md/GC.md 按需读取,CLAUDE.md 从 10,592 字符降到 6,073——同一段落里抠字数边际收益很低(实测两轮合计只减 5.7%),真正有效的是把整块任务特定内容搬出无条件加载范围,内容一个字都没删。用户手写/粘贴进 vault、结构和分类都乱掉的笔记,整理时 AI 可以实质性改写原文(拆分、改名、移动),这条不受"notes 复核不改原文"铁律约束——后者只管 checkable 内容的事实性复核,两者管的是不同阶段的不同风险。

相关:[[decisions/不往记忆库写grep能查到的事实]]、[[decisions/自动化与文档设计优先选省token不影响效果的轻量方案]]、[[decisions/整理手写笔记允许改写原文而不仅是追加复核记录]]

## 工作台开发实现现状与已知坑

工作台并排卡片布局(统计卡+随机重逢、抽卡+延伸、问题1+问题2)靠本地 `workbench.css` 里的纯 CSS flex 方案实现,不是 Multi-Column Markdown 插件——插件在编辑模式会露出原始语法标记、两栏高度对不齐,纯 CSS 更省心也没有额外依赖。每日画作改成按真实比例显示(不再固定裁切成横条 banner),因为大多数名画是竖长或接近正方形构图,横条裁切会切掉大半画面;宽屏图文横排、窄屏图上文下,判断逻辑写在 工作台.md 的 dataviewjs 里(内联样式 + matchMedia),不依赖本地专属的 workbench.css,保证远程会话也能改。踩过一次坑:换视觉设计时如果偷懒复用旧 class 名,旧样式表里专为旧设计写的定位规则会接管新结构;以后凡是替换旧设计,新结构必须换新 class 名。另外两个技术坑:dataviewjs 里的计时器必须用 `dv.component.registerInterval(setInterval(...))` 包裹,裸 `setInterval` 在切页返回后不会被清理、会累积拖垮渲染;工作台"看起来没更新"时应先检查本地 iCloud vault 是否拉取了远端(Obsidian Git 插件只在 Obsidian 打开时自动拉取),而不是先怀疑云端 GitHub Actions 日更挂了。

相关:[[decisions/工作台并排卡片布局用CSS-flex而非Multi-Column-Markdown插件]]、[[decisions/工作台每日画作按真实比例显示不再固定裁切成横条banner]]、[[pitfalls/工作台dataviewjs用裸setInterval会在切页返回后叠加计时器拖垮渲染]]、[[pitfalls/工作台没更新先检查本地是否拉取了远端而不是怀疑云端日更挂了]]
