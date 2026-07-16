---
type: decision
created: 2026-07-16
last-verified: 2026-07-16
---

# 每日工作台与每周 GC 改用 Codex Action 运行

`daily-workbench.yml` 和 `weekly-gc.yml` 改用官方 `openai/codex-action@v1`,通过仓库 Secret `OPENAI_API_KEY` 调用。原有北京时间 05:00 日更、周一 09:00 GC、安静周跳过、lint、索引重建和直接推 `main` 的行为保持不变。

Codex 只在 `:workspace` 权限配置内修改文件并使用模型侧网页搜索;commit、push 和待裁决 issue 由后续 GitHub Actions 步骤机械执行。这样不把 GitHub 写权限交给模型进程,也避免沙箱网络限制影响推送。待裁决 issue 使用日期标题去重,自动重跑不会重复通知。

失效条件:官方 Codex Action 的认证或输入接口发生不兼容变更,或用户决定改回其他执行器。

相关:`.github/workflows/daily-workbench.yml`、`.github/workflows/weekly-gc.yml`、`.github/workflows/rerun-on-failure.yml`
