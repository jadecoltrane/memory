---
sorting-spec: |
  target-folder: /
  /--hide: AGENTS.md
  /--hide: CLAUDE.md
  /folders Notes
  /folders Concepts
  /folders Diary
  /folders Works
  /folders Archive
  /folders Meta
  /folders Profile
  /folders Sources
  /:files
---

# 文件栏排序

上面 frontmatter 里那段是 **Custom File Explorer sorting**(插件 id `custom-sort`)读的排序规则,`target-folder: /` 表示它管的是仓库根目录那一层。

**为什么用插件而不是 CSS**:1.13 的文件栏是虚拟滚动,只挂载 DOM 顺序靠前的那几项;CSS 的 flex order 只能改"画在哪"、改不了"挂不挂载",把 DOM 末尾的项挪到视觉最上面,面板一变矮整组就消失(实测)。这个插件改的是文件栏的**数据顺序**,虚拟滚动照常按新顺序算,所以不冲突。

**怎么改顺序**:上面每行一个条目,从上到下就是显示顺序。

- `/folders 名字` 只匹配文件夹,`/:files 名字` 只匹配文件。
- `/--hide: 文件名.md` 把条目从文件栏藏起来(**要带扩展名**)。AGENTS.md 和 CLAUDE.md 是给 AI 读的规则文件,人不用点开,所以藏了;文件本身照常在仓库里,搜索也照样找得到。**藏东西必须走这里,不要用 CSS 的 display:none**——文件栏是虚拟滚动,CSS 藏行会让滚动高度算错,末尾几项永远不挂载(实测)。
- 最后那行光秃秃的 `/:files` 是"其余的文件"兜底组,没点名的文件(AGENTS、CLAUDE、Home)按原顺序排在最后。**这行别删**,删了它们会跑到最前面。
- 新建了顶层文件夹却没写进上面,它会落到没被点名的那一档;想让它排在指定位置就补一行。

**插件默认是挂起状态**(`suspended: true`),第一次要手动启用一次:命令面板搜 `Custom sort`,或点左侧栏那个排序图标。状态栏会显示当前是否生效。

分层的那条分割线画在 `Archive` 上边缘,在 `.obsidian/snippets/file-tree.css` 里。
