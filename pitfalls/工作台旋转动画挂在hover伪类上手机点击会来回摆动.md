---
type: pitfall
created: 2026-07-06
last-verified: 2026-07-06
---

# 症状

工作台「🎲 随机重逢」卡片右上角的换一篇按钮(↻),手机上点击后旋转方向/角度不对,反复修了三次才定位全乎。

# 原因(三层,前两版都只修对了一部分)

**第一层**:`.obsidian/snippets/workbench.css`(本地文件,不入库,远程会话看不到)把旋转挂在 `:hover` 伪类上:悬停转到 180°,移出悬停转回 0°。手机没有真正的 hover——点一下相当于"进入 hover"、再点一下相当于"离开 hover",两次点击在两个固定角度间来回摆动。

**第二层**:改成 `rerollGlyph.animate([...])` 之后问题依旧,因为 `renderReunion(container)` 会在同一次点击里**同步**清空并重建整张卡片(含按钮和 glyph 本身),动画请求发出后浏览器还没画出一帧,承载动画的节点就被销毁重建了,等于没转出来。

**第三层(前两版都没根治的真正原因)**:`.wb-reunion-reroll` / `.wb-reroll-glyph` 这两个 class 名不是这次改动新起的,是原本就承载着"渐变填充图标"效果的 class(`background-clip: text` 那套,2026-07-06 按用户给的 figma 教程做的)——不能像画作横幅那次一样直接换新 class 名摘干净,不然渐变填充也会跟着丢。本地 CSS 大概率把渐变和旋转写在同一条 `:hover` 规则里,只要 class 名不变,那条规则里的 `transform` 声明就一直在,`.animate()` 播完之后(没设 `fill: forwards`)会回落到"底层值",而底层值仍然要看当时手机上残留没残留 hover 状态——iOS 上点击后 hover/active 状态经常会"粘住"不主动清掉,导致回落角度不可预期。

# 解法

1. 旋转动效本身:Web Animations API 播 0°→360°,和 hover/active 状态脱钩
2. 点击回调 `async`,先 `await anim.finished` 再重建卡片,不让动画被同步销毁打断
3. **第三步,也是这次新加的**:在 glyph 上常驻设一条内联样式 `style.transform = "rotate(0deg)"`,动画播完后再显式重设一次。内联样式的优先级天然高于任何非 `!important` 的选择器(包括 `:hover`),这样只钉死 `transform` 这一个属性,不去动 class 本身,同一个 class 上的渐变填充效果不受影响,但旋转的"底层值"再也不会被本地 CSS 的 hover 规则带偏

已在 工作台.md 的 `reroll.onclick`/初始化那两行改完(2026-07-06 三次修复的注释)。

**教训**:发现某个视觉 bug 挂在旧 class 的 `:hover` 规则上时,不能默认"换新 class 名"就是万能解——如果那个 class 同时承载着**还想保留**的其他视觉效果(不止这一个坏掉的属性),换 class 名会把好的效果一起丢掉。这时候该做的是精确内联覆盖"坏的那一个 CSS 属性"(这里是 `transform`),而不是整体搬家。
