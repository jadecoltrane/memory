---
type: pitfall
created: 2026-07-07
last-verified: 2026-07-07
---

# 坑

工作台.md 的卡片网格(名画横幅/随机重逢横排、问题1/2 横排)只写给了 `.markdown-preview-sizer`(阅读视图容器)。曾尝试给 `.cm-sizer`(Live Preview/编辑视图容器)镜像同一套 `display:flex` + `flex:1 1 100%`,想让编辑模式也有卡片网格效果,即使加了 `.is-live-preview` 类限定也一样出问题:会把当时正显示原始文本的那个块(光标停留处,或 widget 还没渲染完的 dataviewjs 代码块)整段打散成一字一行的乱码排版。

根因:`.cm-sizer` 的直接子元素是 CodeMirror 按源文件逐行拆出的 `.cm-line`(不是渲染后的整块 div),即使是 Live Preview、即使根元素确认带 `.is-live-preview` 类,只要某个块当前展示的是原始文本,那些行依然是 `.cm-sizer` 的直接子元素。对整个容器做 `display:flex` + 逐子项 `flex-basis:100%`,会让容器自身在这种"部分块仍是逐行结构"的情况下失去确定宽度。

用 devtools(`cmd+alt+i`,Elements 面板 Cmd+F 搜类名定位真实 DOM,而不是只看 Styles 面板列没列出规则——同一关键词可能先命中 CSS 源文件文本,要翻到 DOM 节点那次命中才作数)实测确认。

# 下次遇到类似情况怎么办

- 工作台.md 的卡片网格布局(横排、宽度分配)只在阅读视图生效是既有设计,不要尝试往 `.cm-sizer` 加同类 `display:flex` 规则去"补全"编辑模式的显示效果——`.cm-sizer` 装的是 CodeMirror 逐行结构,阅读视图那套"每个顶层块一个 flex item"的假设在编辑视图不成立
- 编辑模式下退化成普通堆叠是可接受的降级,不是需要用 CSS 硬修的 bug
