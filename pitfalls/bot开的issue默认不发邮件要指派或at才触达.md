---
type: pitfall
created: 2026-07-16
last-verified: 2026-07-16
---

# github-actions bot 开的 issue 默认不给仓库主人发邮件,要指派或 @ 才触达

**坑**:workflow 里用 `gh issue create`(GITHUB_TOKEN / github-actions[bot] 身份)开 issue,
想靠它给仓库主人发提醒邮件——但 issue 建出来了,邮件一封没到。weekly-gc 的「待裁决 issue」
就是唯一主动提醒渠道,却静默失效(2026-07-16 发现:issue #10 建了但用户没收到邮件)。

**原因**:对「别人/bot 开的、跟你无关(没指派你、没 @你)的 issue」,GitHub 只在你对该仓库的
watch 级别是「All Activity」时才发邮件。仓库主人对自己仓库的默认 watch 常是
「Participating and @mentions」,不覆盖新 issue → 不发邮件。「开了 issue 就会触发邮件通知」
这个假设本身是错的。

**解法**(二选一或都用):
- workflow 侧(自包含,首选):`gh issue create --assignee "${{ github.repository_owner }}"`,
  被指派 = participant,通知与 watch 级别无关;再在正文 `cc @owner` 加一层 @ 双保险。
- 用户侧:把仓库 watch 设成「All Activity」(或 Custom → Issues),一次设置,所有 issue 都发邮件。

**注意**:不要改用「用户自己的 PAT」去 create——那样 issue 作者变成用户本人,GitHub 不会给你
发关于你自己动作的通知,反而更收不到。要保持 bot 作者身份 + 指派/@。

**何时会失效**:若仓库主人已把 watch 设成 All Activity,则指派是冗余但无害;
本仓库 .github/workflows/weekly-gc.yml 已加 `--assignee` + `cc @owner`,待下次有待裁决条目的
GC 运行验证邮件是否送达。
