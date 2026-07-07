# 记忆索引

> 自动生成于 2026-07-07,勿手改;运行 `python3 scripts/build_memory_index.py` 更新。

## 用户画像

- [[profile/使用偏好|使用偏好]]
- [[profile/健康|健康]]
- [[profile/兴趣爱好|兴趣爱好]]
- [[profile/职业|职业]]
- [[profile/行为准则|行为准则]]

## 概念

- [[concepts/主体性|主体性]]
- [[concepts/含情注视|含情注视]]
- [[concepts/客服模式|客服模式]]
- [[concepts/控制二分法|控制二分法]]
- [[concepts/水缸|水缸]]
- [[concepts/胰岛素抵抗|胰岛素抵抗]]
- [[concepts/膳食纤维|膳食纤维]]
- [[concepts/自我重养育|自我重养育]]

## 决策与约定

- [[decisions/CLAUDE.md应尽量精简优先拆分独立文件而非压缩措辞|CLAUDE.md应尽量精简优先拆分独立文件而非压缩措辞]] (verified: 2026-07-06)
- [[decisions/Gemini网页版只能读快照不能写入故暂不整合Gemini|Gemini网页版只能读快照不能写入故暂不整合Gemini]] (verified: 2026-07-03)
- [[decisions/claude仓库长期只保留claude-main和gh-pages两个分支|claude仓库长期只保留claude-main和gh-pages两个分支]] (verified: 2026-07-03)
- [[decisions/vault保留iCloud仅用nosync隔离git内部文件|vault保留iCloud仅用nosync隔离git内部文件]] (verified: 2026-07-06)
- [[decisions/vault用xattr标记隔离git目录避免插件报错|vault用xattr标记隔离git目录避免插件报错]] (verified: 2026-07-06)
- [[decisions/vault用外部gitdir降低插件报错的影响范围|vault用外部gitdir降低插件报错的影响范围]] (verified: 2026-07-06)
- [[decisions/vault用普通git接受插件偶尔报错|vault用普通git接受插件偶尔报错]] (verified: 2026-07-06)
- [[decisions/下线跨仓库指针巡检改为用户手动接入记忆库|下线跨仓库指针巡检改为用户手动接入记忆库]] (verified: 2026-07-06)
- [[decisions/不往记忆库写grep能查到的事实|不往记忆库写grep能查到的事实]] (verified: 2026-07-03)
- [[decisions/任务分支改完可直接合并进main不用每次确认|任务分支改完可直接合并进main不用每次确认]] (verified: 2026-07-06)
- [[decisions/双链优先指向概念页而非笔记之间直接互链|双链优先指向概念页而非笔记之间直接互链]] (verified: 2026-07-04)
- [[decisions/回答用户默认一律用中文除非用户指明用其他语言|回答用户默认一律用中文除非用户指明用其他语言]] (verified: 2026-07-05)
- [[decisions/工作台UI精简迭代历史|工作台UI精简迭代历史]] (verified: 2026-07-06)
- [[decisions/工作台并排卡片布局用CSS-flex而非Multi-Column-Markdown插件|工作台并排卡片布局用CSS-flex而非Multi-Column-Markdown插件]] (verified: 2026-07-05)
- [[decisions/工作台每日画作按真实比例显示不再固定裁切成横条banner|工作台每日画作按真实比例显示不再固定裁切成横条banner]] (verified: 2026-07-06)
- [[decisions/手机与Mac共用iCloud内同一git目录靠插件自动拉取|手机与Mac共用iCloud内同一git目录靠插件自动拉取]] (verified: 2026-07-07)
- [[decisions/数据层保持Markdown加Git但Obsidian插件放开用|数据层保持Markdown加Git但Obsidian插件放开用]] (verified: 2026-07-04)
- [[decisions/整理手写笔记允许改写原文而不仅是追加复核记录|整理手写笔记允许改写原文而不仅是追加复核记录]] (verified: 2026-07-04)
- [[decisions/自动化与文档设计优先选省token不影响效果的轻量方案|自动化与文档设计优先选省token不影响效果的轻量方案]] (verified: 2026-07-04)
- [[decisions/记忆库vault已迁出iCloud到本地只用git同步|记忆库vault已迁出iCloud到本地只用git同步]] (verified: 2026-07-06)

## 踩坑记录

- [[pitfalls/git仓库放iCloud目录可能因大量小文件同步冲突|git仓库放iCloud目录可能因大量小文件同步冲突]] (verified: 2026-07-06)
- [[pitfalls/macOS文件名NFDNFC不一致会让git把整个中文笔记文件夹误判成已删除|macOS文件名NFDNFC不一致会让git把整个中文笔记文件夹误判成已删除]] (verified: 2026-07-04)
- [[pitfalls/云端GitHub-Actions定时任务偶发因claude-code-action的OIDC鉴权bug失败|云端GitHub-Actions定时任务偶发因claude-code-action的OIDC鉴权bug失败]] (verified: 2026-07-06)
- [[pitfalls/工作台dataviewjs用裸setInterval会在切页返回后叠加计时器拖垮渲染|工作台dataviewjs用裸setInterval会在切页返回后叠加计时器拖垮渲染]] (verified: 2026-07-05)
- [[pitfalls/工作台没更新先检查本地是否拉取了远端而不是怀疑云端日更挂了|工作台没更新先检查本地是否拉取了远端而不是怀疑云端日更挂了]] (verified: 2026-07-06)
- [[pitfalls/记忆库仓库曾默认公开导致隐私内容对外暴露|记忆库仓库曾默认公开导致隐私内容对外暴露]] (verified: 2026-07-04)

## 判断与洞察

- [[insights/AI自写自读的记忆回路需要人工否决权|AI自写自读的记忆回路需要人工否决权]] (confidence: high, verified: 2026-07-03)

## 我的收藏

- [[notes/health/油皮控油护肤与医美方案|油皮控油护肤与医美方案]] (verified: false)
- [[notes/health/熬夜后如何快速恢复|熬夜后如何快速恢复]] (verified: false)
- [[notes/health/瘦多囊未必是胰岛素抵抗也可能是肾上腺压力型或炎症型|瘦多囊未必是胰岛素抵抗也可能是肾上腺压力型或炎症型]] (verified: false)
- [[notes/health/莓果本身膳食纤维含量高但被榨汁滤掉了|莓果本身膳食纤维含量高但被榨汁滤掉了]] (verified: false)
- [[notes/health/静息心率越慢通常与寿命更长相关|静息心率越慢通常与寿命更长相关]] (verified: false, checked: 2026-07-03)
- [[notes/生活方式/上海辣系及常去餐厅打卡清单|上海辣系及常去餐厅打卡清单]]
- [[notes/生活方式/护肤品选购与成分判读指南|护肤品选购与成分判读指南]] (verified: false)
- [[notes/生活方式/胶囊衣橱·衣物清单与消耗策略|胶囊衣橱·衣物清单与消耗策略]]
- [[notes/社会认知/人设的反作用|人设的反作用]]
- [[notes/社会认知/工作可能并不能带你真正认知社会|工作可能并不能带你真正认知社会]]
- [[notes/社区学/完整手册——水缸、哲学、主心骨与主体性|完整手册——水缸、哲学、主心骨与主体性]]
- [[notes/社区学/破解东亚绩优主义疲惫感的五个哲学解法|破解东亚绩优主义疲惫感的五个哲学解法]]
- [[notes/社区学/自我重养育：用含情注视代替KPI式自我审判|自我重养育：用含情注视代替KPI式自我审判]]
- [[notes/问答/2026-07 工作台问答|2026-07 工作台问答]]

共 54 条记忆。
