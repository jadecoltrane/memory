---
type: decision
created: 2026-07-11
last-verified: 2026-07-11
---

# 作品集案例内容更新要同步到 gh-pages 网站

**约定**(用户 2026-07-11 明确要求):portfolio 仓库里案例内容有实质进展时,要同步更新到网站——即 portfolio 仓库的 **gh-pages 分支**(index.html + project-*.html 静态站)。

- 网站页面结构:index.html(bento 首页,三张项目卡)+ project-caidan.html(案例⑤彩蛋,已完整)+ project-hmi.html(案例①控制中心,2026-07-11 已灌入)+ project-ai.html + resume.html + contact.html
- 案例页有现成组件:decision-card / principle-grid / case-insight / case-meta / spec-table,新案例页复用这套,风格参照 project-caidan.html
- 同步口径:网站版比 PDF 版更精简;"不进 PDF 的自用内容"(面试预演、红线自检)绝不上网站;占位图用 case-image-placeholder 惯例
- 敏感信息红线同仓库规则:雇主名、内部数据不出现(2026-07-11 曾发现首页两处"吉利"残留于标签默认文本——脱敏只改了 data-zh 属性漏了 innerHTML,已修复;此类检查用 grep 全站扫)
- 失效条件:网站迁移出 gh-pages 分支,或用户改变载体策略
