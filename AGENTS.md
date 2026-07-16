# AGENTS.md — Codex 入口

本仓库的完整 AI 协作与记忆规则统一维护在根目录 `CLAUDE.md`。Codex 开始任何任务前必须完整读取并遵守该文件；除下列适配项外，不在这里复制规则，避免双份文档产生漂移。

## Codex 适配

- `CLAUDE.md` 中的“Claude”和“AI”均包含 Codex。
- 遇到 Claude 专用的 `add_repo` 时，Codex 应优先使用已授权的 GitHub 连接器访问 `jadecoltrane/memory`；需要本地修改时，使用现有 checkout 或通过 GitHub CLI 克隆。无法访问时，按 `CLAUDE.md` 的兜底规则把完整内容交给用户手动保存，并明确说明尚未写入仓库。
- 用户说“接入记忆库”或“装上记忆”时，Codex 将 `meta/repo-pointer.md` 的内容写入目标仓库根目录的 `AGENTS.md`；文件已存在则追加，不覆盖。若用户要求同时兼容 Claude，再同步维护 `CLAUDE.md`。
- 本仓库的记忆改动直接提交并推送到 `main`，不创建 PR；任何写入仍须按 `CLAUDE.md` 的格式在最终回复中明确告知。
- `meta/index.md` 是自动生成文件，不得手工修改；写入记忆后运行仓库规定的索引与 lint 脚本，再提交相关产物。
