---
type: pitfall
created: 2026-07-06
last-verified: 2026-07-06
---

# 症状

工作台「🎲 随机重逢」卡片右上角的换一篇按钮(↻),手机上点一下正着转过去,再点一下会反着转回来,而不是每次都往前转一整圈。

# 原因

`.obsidian/snippets/workbench.css`(本地文件,不入库,这次远程会话看不到)里大概率把旋转效果挂在 `:hover` 伪类上:悬停时转到 180°,移出悬停转回 0°。桌面端鼠标有真正的 hover/leave 事件,视觉上永远是"转过去再转回来"两段连续动作。手机没有真正的 hover——点一下相当于"进入 hover"(转到 180°),再点一下相当于"离开 hover"(转回 0°),两次点击变成了在两个固定角度之间来回摆动,而不是持续往一个方向转。

# 解法

把旋转从 CSS `:hover` 里摘出来,改成点击时用 Web Animations API 播放一次 0°→360° 的动画(`el.animate([...], { duration, easing })`),和 hover/active 状态完全脱钩——不管点多少次、点击间隔多短,每次都是从 0 开始往前转一整圈。已在 工作台.md 的 dataviewjs 里改掉(`reroll.onclick` 里的 `rerollGlyph.animate(...)`),不用改本地 CSS 也生效,原来 CSS 里挂在 `.wb-reunion-reroll:hover` 上的旧规则会变成死代码,GC 时可以清掉。

以后工作台里任何"点击触发一次性动效"的需求,都优先用 JS 直接 `.animate()` 或临时加/减 class,不要绑在 `:hover`/`:active` 伪类上——那类伪类在触屏设备上的语义和桌面端不一致,是通用坑,不止这一个按钮。
