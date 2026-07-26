---
type: note
created: 2026-07-22
source: 与 Claude 的对话（2026-07-22，从原理到实操的系统梳理）
checkable: true
verified: false
---

# Git 核心原理与 Obsidian Git 操作速查

## Git 是什么

Git 是一个**本地命令行工具**，和 GitHub 没有任何关系。1991 年 Linus Torvalds 写的，装在电脑上就能用，不需要网络、不需要账号。GitHub 是 2008 年才出现的公司，只是把 Git 仓库放到云上加了协作界面。

```
Git   ≈ Word（软件本身）
GitHub ≈ Google Docs（把文件放到云上共享）
```

可以完全不用 GitHub，用 GitLab / Gitea 自建，或者局域网另一台机器当远端，甚至纯本地用。

## 四个区域

```
工作区          暂存区(Stage)        本地仓库        远端(GitHub)
（实际文件）  →(git add)→  （候场区）  →(commit)→  （快照存档）  →(push)→
```

- **工作区**：你实际看到和编辑的文件
- **暂存区**：确认要纳入下次快照的文件清单，`git add` 放进来，`git restore --staged` 取出去
- **本地仓库**：所有历史快照，存在 `.git/` 目录里，不联网
- **远端**：GitHub 等服务器上的仓库，push/pull 同步

## Git 存的是快照，不是差异

每次 commit 存的是**所有文件的完整状态**，效率来自「内容相同的文件只存一份，用哈希指针引用」。`git diff` 看到的加减号是临时计算出来给人看的，不是存储格式。

首次 commit 存全量，后续 commit 只存变化了的文件（新 blob），没变的文件共用旧 blob。

## Tracked vs Untracked

- **Tracked**：Git 认识这个文件，至少被 commit 过一次，会持续追踪变化
- **Untracked（U）**：Git 完全不知道它存在，`git add` 后才变成 tracked

## 状态标记

| 标记 | 含义 |
|---|---|
| U | Untracked，全新文件，Git 不认识 |
| M | Modified，tracked 文件内容被改了 |
| D | Deleted，tracked 文件在本地消失了 |
| A | Added，刚被 `git add` 进暂存区的新文件 |
| P | Pulled（Obsidian Git 专用），刚从远端拉下来的文件 |

## Push 之前必须先 Pull 的原因

Git 规则：推上去的内容必须包含远端所有历史。远端有本地没有的 commit 时直接推会被拒绝，因为那些 commit 会丢失。

```
远端：A → B → C
本地：A → B → D
直接推 → 拒绝（C 会丢）
pull 后：A → B → C → D → 再推 ✅
```

pull 之后有两种合并方式：
- **merge**：生成一个合并节点，历史有分叉痕迹
- **rebase**：把本地 commit 接在远端最新 commit 后面，历史是直线（更干净）

`git push --force` 可以强行覆盖远端，但远端那些 commit 真的丢了，多人协作基本禁止。

## 误删文件如何恢复

Git 几乎删不掉东西——只要 commit 过，快照里就有，随时能取：

```bash
git checkout <commit哈希> -- 文件路径
```

从指定历史 commit 把文件取出来放回工作区，再重新 commit 即可。

## Obsidian Git 移动端图标速查

```
↑(commit)  ✓(stage all)  +(stage)  −(unstage)  ↑(push)  ↓(pull)
                    🗂️(open folder)  🔄(refresh)
```

- **第一个 ↑**：commit，暂存区 → 本地仓库，不联网
- **第五个 ↑**：push，本地仓库 → GitHub，要联网
- **🔄**：refresh，重新扫描本地文件变化更新列表，不联网

Vault backup 按钮 = `git add .` + `git commit` + `git push` 三步打包。

## iOS 限制

iOS 不允许 App 在后台持续监听文件变化，所以 Obsidian Git 无法实时更新 Changes 列表，需要手动点 🔄 刷新或在设置里开定时扫描。

## Vault Backup 误删问题

Obsidian Git 的 backup 是「把手机本地 vault 当前状态原样推上去」。如果 Claude 写了新文件推到 GitHub，但手机还没 pull，backup 就会把新文件当作「本地不存在」删掉。

**解决方法**：每次打开 Obsidian 想写东西前先 pull，把远端新文件拉到本地，backup 才不会误删。

## 为什么 GitHub 免费

GitHub 存的是快照 + 内容寻址（相同内容只存一份），代码是纯文本压缩率极高，边际存储成本很低。商业模式是免费吸引开发者，向企业收费（Teams/Enterprise 才是主要收入）。

## 复核记录

- 2026-07-26：有争议（部分不准确）。四区域模型、"存快照不存差异+内容寻址复用 blob"、push 前必须 pull 的非快进拒绝机制、`git checkout <commit> -- 文件` 恢复误删文件、GitHub 2008 年成立等核心陈述均查有可靠来源、准确。但"Git 是 1991 年 Linus Torvalds 写的"有误：Git 由 Linus Torvalds 创建于 2005 年（首次提交 2005-04-07，因 BitKeeper 授权纠纷而写），1991 年是 Linux 内核的诞生年份，笔记把两者混淆了。来源：https://git-scm.com/book/en/v2/Getting-Started-A-Short-History-of-Git ，https://github.blog/open-source/git/git-turns-20-a-qa-with-linus-torvalds/ ，https://en.wikipedia.org/wiki/GitHub （GitHub 2008-02-08 成立/2008-04-10 上线），https://github.blog/open-source/git/commits-are-snapshots-not-diffs/ 。下次复核约一周后（2026-08 初）。
