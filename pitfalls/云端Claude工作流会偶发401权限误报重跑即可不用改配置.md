---
type: pitfall
created: 2026-07-11
last-verified: 2026-07-16
---

# 云端 Claude 工作流会偶发 401 权限误报,重跑即可,不用改配置

> [!note] 历史记录
> 2026-07-16 起每日工作台和每周 GC 已迁移到 `openai/codex-action@v1`,不再经过 Anthropic 的 token 交换;下面的 401 诊断只适用于旧 Claude 工作流。通用的失败自动重跑兜底仍保留。

**现象**:工作台日更(claude-code-action)偶发在启动 30 秒内失败,日志报 `App token exchange failed: 401 Unauthorized - User does not have write access on this repository`,action 内部重试 3 次全挂。

**为什么不是配置问题**:2026-07 的 #7、#8、#10 三次失败与 #9 的成功之间仓库配置、secret、App 安装零改动,时好时坏——说明 CLAUDE_CODE_OAUTH_TOKEN 和 Claude GitHub App 本身是好的,是 Anthropic 侧 OIDC→App token 交换服务的间歇性误判。weekly-gc 共用同一个 token,同样可能中招。

**解法**:失败发生在 Claude 启动之前,零副作用,直接重跑那次运行即可。已有兜底:`.github/workflows/rerun-on-failure.yml` 监听两个 Claude 工作流,失败自动等 3 分钟后 rerun(最多补跑 2 次)。兜底也没救回来时才需要人工看——先手动 rerun 一次,还不行再怀疑 token 过期(重新 `claude setup-token` 换 secret)。

**何时失效**:当前两个自动化已不再使用 Claude action,因此这条对现行工作流已经失效;仅在回看 2026-07-16 之前的运行记录时适用。

**附**:GitHub 手机端 App 会把 schedule 触发的运行错标成"通过拉取请求触发",以 API/网页端的事件类型为准。
