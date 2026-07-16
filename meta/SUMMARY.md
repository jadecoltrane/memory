# 结论速览(Compiled Truth)

>这里存的是"现在信什么",不是"怎么信到这的"——后者去 `decisions/`、`pitfalls/`、`insights/` 的时间线文件里查。
> 只在同一主题下积累了 2 条以上相关记忆时才起条目,数量不够就不写。跟 `index.md` 不是一回事:index.md 是全量列表,机械生成;这里是精选聚合,手写综合。

## 作品集工作区公开策略

- 作品集(portfolio 仓库)保持完全公开,不拆分私有仓、不删减工作区内容(案例草稿、面试预演、排期等);用户已知情实名网站可回溯到仓库的风险,明确表示不用再劝
- 仍守的红线:薪资数字、雇主可识别信息(吉利/星纪魅族/Flyme/车型名)、内部文件与截图、GAS 条款原文均不进公开仓库
- 案例内容有实质进展时要同步更新到 gh-pages 网站(index.html + project-*.html),网站版比 PDF 版更精简,面试预演/红线自检等"自用内容"不上网站

相关:[[decisions/作品集工作区保持公开不拆分]]、[[decisions/作品集案例内容更新要同步到gh-pages网站]]、profile/职业.md

## 每日工作台/每周 GC 的云端运行方案

- 两个定时任务固定用 `anthropics/claude-code-action@v1`,靠仓库 Secret `CLAUDE_CODE_OAUTH_TOKEN` 认证,沿用已有 Claude 订阅,不新增计费
- 2026-07-16 短暂试过官方 `openai/codex-action@v1`,发现必须用单独计费的 `OPENAI_API_KEY`(不能复用 ChatGPT/Codex 订阅或 GitHub 集成),当天就切回 Claude,决策不再复议除非 Codex Action 支持复用订阅
- **已知运行时坑(三条)**:
  1. 偶发 401(`App token exchange failed`):Anthropic 侧 OIDC→App token 交换服务间歇性误判,不是配置问题,`rerun-on-failure.yml` 自动重跑
  2. `claude-code-action` 结束后 `git push` 会认证失败:action 内部 checkout 在 post-cleanup 时 `unset` 了外层的 `GITHUB_TOKEN` extraheader;修法是 push 时用 `x-access-token:${GH_TOKEN}` 显式认证,不依赖持久化凭证
  3. bot 用 `GITHUB_TOKEN` 开的 issue 默认不给仓库主人发邮件:只有 watch 级别 All Activity 才触达;修法是 `--assignee owner` + 正文 `cc @owner`

相关:[[decisions/每日工作台与每周GC继续使用Claude OAuth自动运行]]、[[pitfalls/云端Claude工作流会偶发401权限误报重跑即可不用改配置]]、[[pitfalls/claude-code-action结束后git-push要显式认证否则凭证被抹掉]]、[[pitfalls/bot开的issue默认不发邮件要指派或at才触达]]
