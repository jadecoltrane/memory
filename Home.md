---
cssclasses: workbench
generated: 2026-10-26
painting-url: "https://commons.wikimedia.org/wiki/Special:FilePath/Crivelli%20Carlo%2C%20Annunciation.jpg?width=1280"
painting-title: "卡罗·克里韦利《圣母领报与圣爱米巨》(1486年)"
painting-intro: "《圣母领报与圣爱米巨》是意大利艺术家卡罗·克里韦利的一幅祭坛画，以圣母领报为主题。这幅画位于意大利马尔凯大区阿斯科利皮切诺的圣母领报堂，庆祝教宗思道四世于1482年授予该镇自治权。"
---

🎴 10/26 天生的倾向是偏置不是剧本-遗传度的误读与… #工作台
· "遗传度 40–50%"为什么不等于"这个特…
📖 反例 · "一个朴素的词"也会让感受变淡
​
​
```dataviewjs
const bar = dv.container.createEl("div", { cls: "wb-infobar" });
const left = bar.createEl("div");
const greetEl = left.createEl("div", { cls: "wb-greet" });
const dateEl = left.createEl("div", { cls: "wb-date" });
const clockEl = bar.createEl("div", { cls: "wb-clock" });
const wd = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
const tick = () => {
  const d = new Date(), h = d.getHours();
  greetEl.setText(h < 5 ? "夜深了,Jade" : h < 11 ? "早安,Jade" : h < 13 ? "午安,Jade" : h < 18 ? "下午好,Jade" : "晚上好,Jade");
  dateEl.setText(`${d.getFullYear()} 年 ${d.getMonth() + 1} 月 ${d.getDate()} 日 · ${wd[d.getDay()]}`);
  clockEl.setText(`${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`);
};
tick();
// registerInterval(而非裸 setInterval)把计时器生命周期绑定到本次渲染,组件卸载时自动清理,避免切页再回来时计时器叠加
dv.component.registerInterval(setInterval(tick, 15000));
```

```dataviewjs
const p = dv.current();
// closest(".workbench") 而非 querySelector——reading/source 两个视图容器都在 DOM 里,querySelector 只会拿第一个,可能拿到隐藏的那个
const root = dv.container.closest(".workbench");

// 清掉历史版本用 setProperty 写在容器上的内联变量。这两个变量的定义已经搬回 CSS,
// 但内联值挂在 DOM 元素上,删掉写它的代码并不会让它消失——只要视图不被重建就一直
// 压着 CSS 里的新值(2026-08-16:胶囊死活不变色就是 --wb-accent 还留着画作取的土黄)。
// 每次渲染主动 remove 一次,不用靠用户重启 Obsidian
root?.style.removeProperty("--wb-accent");
root?.style.removeProperty("--wb-page-gradient");

const banner = dv.container.createEl("div", { cls: "wb-daily-painting" });
const narrowScreen = window.matchMedia("(max-width: 520px)").matches;
banner.style.cssText = [
  "display:flex",
  `flex-direction:${narrowScreen ? "column" : "row"}`,
  `align-items:${narrowScreen ? "stretch" : "flex-start"}`,
  "gap:16px",
  "height:auto", "box-sizing:border-box", "min-height:0", "max-height:none", "aspect-ratio:auto",
  "overflow:visible", "position:static", "padding:16px",
].join(";");

const imgWrap = banner.createEl("div", { cls: "wb-daily-painting-imgwrap" });
imgWrap.style.cssText = `text-align:center; position:static; flex:0 ${narrowScreen ? "0 auto" : "1 46%"};`;
const bimg = imgWrap.createEl("img", { cls: "wb-daily-painting-img" });
if (p["painting-url"]) bimg.src = p["painting-url"];
bimg.style.cssText = `max-width:100%; max-height:${narrowScreen ? "260px" : "300px"}; border-radius:12px; display:inline-block; position:static;`;

const caption = banner.createEl("div", { cls: "wb-daily-painting-side" });
caption.style.cssText = `position:static; min-width:160px; flex:${narrowScreen ? "0 0 auto" : "1 1 200px"};`;
const paintingHead = caption.createEl("div", { cls: "wb-painting-head" });
paintingHead.createEl("span", { cls: "wb-reunion-tag wb-painting-tag", text: "🖼 今日画作" });
const titleEl = caption.createEl("div", { cls: "wb-daily-painting-name", text: p["painting-title"] ?? "" });
titleEl.style.cssText = "font-weight:600; font-size:1.05em; line-height:1.4; margin-bottom:8px; position:static; background:none; text-shadow:none;";
const introEl = caption.createEl("div", { cls: "wb-daily-painting-desc", text: p["painting-intro"] ?? "" });
introEl.style.cssText = "font-size:0.92em; line-height:1.6; opacity:0.75; position:static; background:none; text-shadow:none;";

// 2026-08-16 删掉「按当天画作取主色调写进 --wb-accent」那段(canvas 采样 + 色相分桶投票)。
// 用户要求胶囊固定用浅紫:强调色每天跟着画走,意味着整页配色每天赌一次运气,今天是土黄
// 明天可能是墨绿,跟页面底色撞不撞全看画。--wb-accent 现在在 CSS 里直接指向 --wb-tint。

const gen = p.generated;
const genMs = gen?.toMillis ? gen.toMillis() : (gen ? new Date(String(gen)).getTime() : NaN);
const ageH = isNaN(genMs) ? Infinity : (Date.now() - genMs) / 36e5;
if (ageH > 48) dv.container.createEl("div", {
  cls: "wb-heartbeat",
  text: `⚠️ 工作台已 ${isFinite(ageH) ? Math.floor(ageH / 24) + " 天" : "很久"}没更新,每日任务可能没在跑`,
});
```

```dataviewjs
// 随机重逢:选中的笔记存 localStorage,重开页面保持不变,只有点↻才换一篇(存的那篇被删/改名则退回随机一篇)
const REUNION_KEY = "wb-reunion-pick";
const open = (path) => app.workspace.openLinkText(path, "/", false);
// 不走 dv.pages('"Notes"') 这种文件夹源:macOS 文件系统不分大小写,只改大小写的重命名
// Obsidian 监听不到,内存索引里的路径大小写会跟磁盘对不上,文件夹源就静默匹配不到任何东西
const pagesIn = (top) => {
  const prefix = top.toLowerCase() + "/";
  return dv.pages().where((p) => p.file.path.toLowerCase().startsWith(prefix));
};
const renderReunion = async (container, forceNew = false) => {
  container.innerHTML = "";
  const arr = pagesIn("Notes").array();
  if (!arr.length) return;
  let pick;
  const cur = window.localStorage.getItem(REUNION_KEY);
  if (!forceNew && cur) pick = arr.find(p => p.file.path === cur);
  if (!pick) {
    const pool = (forceNew && cur && arr.length > 1) ? arr.filter(p => p.file.path !== cur) : arr;
    pick = pool[Math.floor(Math.random() * pool.length)];
    window.localStorage.setItem(REUNION_KEY, pick.file.path);
  }
  const head = container.createEl("div", { cls: "wb-reunion-head" });
  head.createEl("span", { cls: "wb-reunion-tag", text: "🎲 随机重逢" });
  const reroll = head.createEl("button", { cls: "wb-reunion-reroll" });
  const rerollGlyph = reroll.createSpan({ cls: "wb-reroll-glyph", text: "↻" });
  container.createEl("div", { cls: "wb-reunion-title", text: pick.file.name });
  const excerptEl = container.createEl("div", { cls: "wb-reunion-excerpt" });
  const excerptTextEl = excerptEl.createEl("div", { cls: "wb-reunion-excerpt-text", text: "…" });
  container.onclick = () => open(pick.file.path);
  // 旋转用 Web Animations API 播放一次(而非 :hover——手机没有真正的 hover,会来回摆动而非持续旋转);
  // 先 await 动画播完再重建卡片内容,避免动画节点被提前销毁;结束后清掉内联 transform,把控制权交还 CSS 的 hover 效果
  reroll.onclick = async (e) => {
    e.stopPropagation();
    if (reroll.disabled) return;
    reroll.disabled = true;
    const anim = rerollGlyph.animate(
      [{ transform: "rotate(0deg)" }, { transform: "rotate(360deg)" }],
      { duration: 450, easing: "ease" }
    );
    try { await anim.finished; } catch (_) { /* 动画被打断也继续换下一篇 */ }
    rerollGlyph.style.removeProperty("transform");
    renderReunion(container, true);
  };
  const raw = await dv.io.load(pick.file.path).catch(() => "");
  const body = (raw || "")
    .replace(/^---[\s\S]*?---/, "")
    .replace(/\[\[([^\]|]*)\|?[^\]]*\]\]/g, "$1")
    .replace(/[#>*`_]/g, "")
    .trim();
  const snippet = body.slice(0, 1500).replace(/\s+/g, " ").trim();
  excerptTextEl.setText(snippet + (body.length > 1500 ? "…" : ""));
};
// 两张卡等高现在纯靠 CSS(随机重逢绝对定位铺满画作那一行),这里不再测量。
// 旧写法是 JS 量画作高度 + ResizeObserver 追,有两个甩不掉的毛病:一是 querySelector
// 拿的是文档里第一个 .workbench,而 reading/source 两个视图容器同时在 DOM 里,可能量到
// 隐藏的那个;二是图片异步加载、面板展开都会改高度,追不齐就是一次错位。
// ⚠️ 代码块不能以行注释结尾:dataview 把代码包成 `(async () => { 代码 })()`,而它拿到的
// 代码块末尾没有换行,那句 ` })()` 会直接接在最后一行 // 后面被吃掉,报 Unexpected end of input
const reunionEl = dv.container.createEl("div", { cls: "wb-reunion" });
renderReunion(reunionEl);
```

```dataviewjs
// dv.pages() 读内存索引不重新扫盘;面板一律走 renderRows 默认 8 条上限,笔记再多也不会一次性铺出几百个 DOM 节点
const open = (path) => app.workspace.openLinkText(path, "/", false);
const openGraph = () => app.commands.executeCommandById("graph:open");
// 日记按 Diary/<年>/<年>-<月>.md 一月一个文件、每天一个 ## 段(见 Diary/README.md),
// 所以这个按钮不新建文件,只保证当月文件和今天那段存在,然后把光标放到段末
const newDiary = async () => {
  const now = new Date();
  const y = String(now.getFullYear()), m = String(now.getMonth() + 1).padStart(2, "0");
  const today = `${y}-${m}-${String(now.getDate()).padStart(2, "0")}`;
  const heading = `## ${today}`;
  if (!app.vault.getAbstractFileByPath(`Diary/${y}`)) await app.vault.createFolder(`Diary/${y}`);
  const path = `Diary/${y}/${y}-${m}.md`;
  let file = app.vault.getAbstractFileByPath(path);
  if (!file) {
    file = await app.vault.create(path, `${heading}\n\n`);
  } else {
    const text = await app.vault.read(file);
    if (!new RegExp(`^${heading}\\s*$`, "m").test(text)) {
      await app.vault.append(file, `${text.endsWith("\n\n") ? "" : text.endsWith("\n") ? "\n" : "\n\n"}${heading}\n\n`);
    }
  }
  const leaf = app.workspace.getLeaf(true);
  await leaf.openFile(file);
  const ed = leaf.view?.editor;
  if (!ed) return;
  const lines = ed.getValue().split("\n");
  const start = lines.findIndex((l) => l.trim() === heading);
  if (start < 0) return;
  let end = lines.length - 1;
  for (let i = start + 1; i < lines.length; i++) if (/^## /.test(lines[i])) { end = i - 1; break; }
  ed.setCursor({ line: end, ch: lines[end].length });
  ed.scrollIntoView({ from: { line: end, ch: 0 }, to: { line: end, ch: 0 } }, true);
};

// 同上:文件夹源对大小写敏感,靠不住,统一用小写前缀比
const pagesIn = (top) => {
  const prefix = top.toLowerCase() + "/";
  return dv.pages().where((p) => p.file.path.toLowerCase().startsWith(prefix));
};
const notes = pagesIn("Notes"), concepts = pagesIn("Concepts");
// Works/ 的稿子算进笔记数、笔记面板、最新笔记和今日编辑;不进双链数和随机重逢(那两处只算想通的东西)。
// README 是目录说明,不是稿子
const works = pagesIn("Works").where((p) => p.file.path.toLowerCase() !== "works/readme.md");

// Dataview 的索引偶尔会整批漏掉文件(外部批量改名/移动时最容易发生,2026-08-16 就整个
// Notes/ 掉了),表现是笔记数变 0、随机重逢变白卡,而且不报任何错。跟 Obsidian 自己的
// 文件列表对一下,对不上就把话说明白,别让页面默默空着让人以为是没笔记
const vaultNotes = app.vault.getMarkdownFiles().filter((f) => f.path.toLowerCase().startsWith("notes/")).length;
if (vaultNotes > notes.length) {
  dv.container.createEl("div", {
    cls: "wb-heartbeat",
    text: `⚠️ Dataview 索引里少了 ${vaultNotes - notes.length} 篇笔记(库里 ${vaultNotes} 篇,索引里只有 ${notes.length} 篇)——按 Cmd+R 重启 Obsidian 重建索引`,
  });
}
const all = [...notes.array(), ...concepts.array()];
const edges = all.reduce((n, pg) => n + pg.file.outlinks.length, 0);
// 只认 frontmatter 的 created,不退回 file.ctime:文件系统时间戳是 git 写文件那一刻,
// 一次 clone 或 checkout 会把它整批刷成"刚才",拿它兜底等于把没写 created 的老笔记
// 全算成新增(2026-09-02 就是这么虚报的)。没写 created 就不算新增——宁可少算,
// 不能把"我不知道它什么时候建的"读成"它是今天建的"
const ctimeOf = (pg) => pg.created?.ts ?? (pg.created ? new Date(String(pg.created)).getTime() : 0);
const mtimeOf = (pg) => pg.file.mtime?.ts ?? 0;
// 「最新笔记」按 created 倒序取最新的 8 篇,不设时间窗口:按窗口算的话,
// 安静的一周数字是 0、面板是空的;按条数截,点开总能看到最近写了什么。
// 只要 8 篇、不要「展开全部」——取够 8 篇正好等于 renderRows 的默认上限,按钮就不会出现
const LATEST_LIMIT = 8;
const latestPages = [...notes.array(), ...works.array()]
  .filter(pg => ctimeOf(pg) > 0)
  .sort((a, b) => ctimeOf(b) - ctimeOf(a))
  .slice(0, LATEST_LIMIT);
// Works/ 默认不带 frontmatter,漏写 created 的稿子会从「最新笔记」里静默消失,所以当场点名
const worksNoCreated = works.array().filter((pg) => ctimeOf(pg) === 0);
if (worksNoCreated.length) dv.container.createEl("div", {
  cls: "wb-heartbeat",
  text: `⚠️ Works/ 里 ${worksNoCreated.length} 篇没写 created,不会出现在最新笔记:${worksNoCreated.map((pg) => pg.file.name).join("、")}`,
});
const fmt = (ms) => {
  if (!ms) return "";
  const d = new Date(ms);
  return `${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};

// 默认只画前 limit 条,超出的用"展开全部(N)"收着;数组本身已 <= limit 时这个按钮不会出现
const renderRows = (host, arr, rightOf, limit = 8) => {
  if (!arr.length) { host.createEl("div", { cls: "wb-panel-empty", text: "还没有内容" }); return; }
  const listEl = host.createEl("div");
  let expanded = false;
  const draw = () => {
    listEl.innerHTML = "";
    const shown = expanded ? arr : arr.slice(0, limit);
    for (const pg of shown) {
      const row = listEl.createEl("div", { cls: "wb-panel-row" });
      row.createEl("span", { cls: "wb-panel-row-title", text: pg.file.name });
      row.createEl("span", { cls: "wb-panel-row-date", text: rightOf(pg) });
      row.onclick = () => open(pg.file.path);
    }
  };
  draw();
  if (arr.length > limit) {
    const more = host.createEl("div", { cls: "wb-panel-more", text: `展开全部(${arr.length})` });
    more.onclick = () => {
      expanded = !expanded;
      more.setText(expanded ? "收起" : `展开全部(${arr.length})`);
      draw();
    };
  }
};

// 笔记数据库.base 是生成产物(不是用户笔记),每次打开笔记面板都重新整份重写,保证分类跟 Notes/ 实际子文件夹同步
const NOTES_BASE_PATH = "Meta/笔记数据库.base";
const WORKS_CAT = "Works";
const buildNotesBase = async (catGroups) => {
  const esc1 = (s) => s.replace(/'/g, "''"); // YAML 单引号字符串里,单引号本身要写成两个单引号转义
  const esc2 = (s) => s.replace(/"/g, '\\"');
  const lines = ["views:"];
  // filterLines 是 filters: 下面那一层的 YAML 行(不含缩进),简单视图一行 and,全部笔记要嵌一层 or
  const pushView = (name, filterLines) => {
    lines.push("  - type: table");
    lines.push(`    name: "${esc2(name)}"`);
    lines.push("    filters:");
    for (const l of filterLines) lines.push("      " + l);
  };
  const q = (expr) => `'${esc1(expr)}'`;
  const notReadme = q(`file.path != "Works/README.md"`);
  pushView("全部笔记", ["or:", `  - ${q(`file.inFolder("Notes")`)}`, "  - and:", `      - ${q(`file.inFolder("Works")`)}`, `      - ${notReadme}`]);
  for (const [name] of catGroups) {
    if (name === WORKS_CAT) { pushView(name, ["and:", `  - ${q(`file.inFolder("Works")`)}`, `  - ${notReadme}`]); continue; }
    const filterExpr = name === "未分类" ? `file.folder == "Notes"` : `file.inFolder("Notes/${name}")`;
    pushView(name, ["and:", `  - ${q(filterExpr)}`]);
  }
  await app.vault.adapter.write(NOTES_BASE_PATH, lines.join("\n") + "\n");
};

const notesPanel = async (host) => {
  const groups = new Map();
  for (const pg of notes) {
    const seg = pg.file.folder.split("/");
    const cat = seg.length > 1 ? seg[1] : "未分类";
    if (!groups.has(cat)) groups.set(cat, []);
    groups.get(cat).push(pg);
  }
  if (works.length) groups.set(WORKS_CAT, works.array());
  const sorted = [...groups.entries()].sort((a, b) => b[1].length - a[1].length);
  await buildNotesBase(sorted);

  const searchWrap = host.createEl("div", { cls: "wb-panel-search" });
  const searchInput = searchWrap.createEl("input", { cls: "wb-panel-search-input" });
  searchInput.type = "text";
  searchInput.placeholder = "搜标题…";

  const catRow = host.createEl("div", { cls: "wb-cat-grid" });
  for (const [name, arr] of sorted) {
    const card = catRow.createEl("div", { cls: "wb-cat-card", attr: { title: name } });
    card.createEl("div", { cls: "wb-cat-num", text: String(arr.length) });
    card.createEl("div", { cls: "wb-cat-name", text: name });
    card.onclick = () => open(`${NOTES_BASE_PATH}#${name}`);
  }

  const resultHost = host.createEl("div");
  searchInput.oninput = () => {
    const q = searchInput.value.trim().toLowerCase();
    resultHost.innerHTML = "";
    if (!q) return;
    const hits = [...notes.array(), ...works.array()]
      .filter((pg) => pg.file.name.toLowerCase().includes(q))
      .sort((a, b) => mtimeOf(b) - mtimeOf(a));
    renderRows(resultHost, hits, (pg) => fmt(mtimeOf(pg)));
  };
};

// 每天随机挑 CONCEPT_PICK_N 个而非固定按入链榜排序,避免每次点开都是同一批热门概念,埋没冷门概念
const CONCEPT_PICK_N = 9;
const conceptsPanel = (host) => {
  const conceptArr = concepts.array();
  const showAll = conceptArr.length <= CONCEPT_PICK_N;
  let pick = conceptArr;
  if (!showAll) {
    let seed = Math.floor(Date.now() / 86400000);
    const rand = () => {
      seed = (seed + 0x6D2B79F5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    const shuffled = [...conceptArr];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(rand() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    pick = shuffled.slice(0, CONCEPT_PICK_N);
  }
  const grid = host.createEl("div", { cls: "wb-cat-grid" });
  for (const pg of pick) {
    const card = grid.createEl("div", { cls: "wb-cat-card", attr: { title: pg.file.name } });
    card.createEl("div", { cls: "wb-cat-num", text: String(pg.file.inlinks.length) });
    card.createEl("div", { cls: "wb-cat-name", text: pg.file.name });
    card.onclick = () => open(pg.file.path);
  }
  host.createEl("div", {
    cls: "wb-panel-caption",
    text: showAll
      ? `🌿 概念库还没到 ${CONCEPT_PICK_N} 个,全部在这了`
      : `🌿 今日概念`,
  });
};

const latestPanel = (host) => renderRows(host, latestPages, (pg) => fmt(ctimeOf(pg)));
// 这颗胶囊切的是"今天"这一天,不是"最近 N 条"——按条数截会在改得多的那天把早上的挤掉,
// 按当天零点截才保证一天之内动过的一条都不漏。右列给时刻不给日期:同一天里每行日期都一样,
// 时刻才分得出先后
const startOfToday = (() => { const d = new Date(); d.setHours(0, 0, 0, 0); return d.getTime(); })();
const hhmm = (ms) => {
  if (!ms) return "";
  const d = new Date(ms);
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
};
const editedToday = [...all, ...works.array()]
  .filter((pg) => mtimeOf(pg) >= startOfToday)
  .sort((a, b) => mtimeOf(b) - mtimeOf(a));
const recentPanel = (host) => {
  // 空态要说清是"今天没动过"而不是"库里没内容",否则看起来像 Dataview 又漏索引了
  if (!editedToday.length) {
    host.createEl("div", { cls: "wb-panel-empty", text: "今天还没动过任何一条" });
    return;
  }
  renderRows(host, editedToday, (pg) => hhmm(mtimeOf(pg)));
  host.createEl("div", { cls: "wb-panel-caption", text: `🕘 今天编辑过 ${editedToday.length} 条` });
};

// 最近浏览读 Obsidian 自己的最近打开列表(每台设备各记各的),不另存任何文件。
// 要在点开面板那一刻现读:列表随时在变,建页面时读一次的话,面板里永远是刷新前的。
// 只留 md、去掉 Home 自己(工作台是每次打开的起点,留着会永远占第一位)、
// 在库里已经不存在的路径(改名/删除后列表里会残留)也要滤掉。
// 根目录的文件也不要:库里的内容都在文件夹下,根目录只有 Home 和规则文件,
// 手机本地多出来的根目录同名副本(点了找不到目标的链接会新建)会因为一直没被重开而沉在末行
const RECENT_LIMIT = 8;
const recentViewed = () => (app.workspace.getLastOpenFiles?.() ?? [])
  .filter((p) => p.toLowerCase().endsWith(".md") && p.includes("/"))
  .map((p) => app.vault.getAbstractFileByPath(p))
  .filter(Boolean)
  .slice(0, RECENT_LIMIT);
const viewedPanel = (host) => {
  const files = recentViewed();
  if (!files.length) { host.createEl("div", { cls: "wb-panel-empty", text: "还没有浏览记录" }); return; }
  const listEl = host.createEl("div");
  for (const f of files) {
    const row = listEl.createEl("div", { cls: "wb-panel-row" });
    row.createEl("span", { cls: "wb-panel-row-title", text: f.basename });
    // 右列给顶层文件夹:这份列表没有打开时刻,编辑时间又会把"看过"误读成"改过"
    row.createEl("span", { cls: "wb-panel-row-date", text: f.path.split("/").length > 1 ? f.path.split("/")[0] : "" });
    row.onclick = () => open(f.path);
  }
};

const bar = dv.container.createEl("div", { cls: "wb-cards" });
const panel = dv.container.createEl("div", { cls: "wb-panel" });
panel.style.display = "none";

let activeCard = null;
const addTab = (icon, num, lbl, render) => {
  const card = bar.createEl("div", { cls: "wb-card" });
  card.createEl("span", { cls: "wb-num", text: num === "" ? icon : `${icon} ${num}` });
  card.createEl("span", { cls: "wb-lbl", text: lbl });
  card.onclick = () => {
    panel.innerHTML = "";
    if (activeCard === card) {
      activeCard = null;
      card.classList.remove("is-active");
      panel.style.display = "none";
      return;
    }
    if (activeCard) activeCard.classList.remove("is-active");
    activeCard = card;
    card.classList.add("is-active");
    panel.style.display = "";
    render(panel);
  };
};

addTab("📝", notes.length + works.length, "笔记", notesPanel);
addTab("🌿", concepts.length, "概念", conceptsPanel);

// 双链不展开页内面板,直接跳转 Obsidian 原生图谱——图谱是独立可视化,塞进小面板意义不大
const linksCard = bar.createEl("div", { cls: "wb-card" });
linksCard.createEl("span", { cls: "wb-num", text: `🕸️ ${edges}` });
linksCard.createEl("span", { cls: "wb-lbl", text: "双链" });
linksCard.onclick = openGraph;

addTab("🕘", editedToday.length, "今日编辑", recentPanel);
addTab("🌱", "", "最新笔记", latestPanel);
addTab("👀", "", "最近浏览", viewedPanel);

// 「写日记」挂进页面最后那个 📔 日记井,而不是写进 markdown——日更每天会重写这个井,
// 写进去的按钮会被当成用户手写的日记正文原文归档掉(见 Meta/WORKBENCH.md 归档流程第 2 条)
const wbRoot = dv.container.closest(".workbench") ?? document;
const mountDiaryBtn = () => {
  const well = [...wbRoot.querySelectorAll('.callout[data-callout="write"]')].find((el) =>
    // 认 📔 而不是认标题文字:标题措辞改过一轮,认死文字的话按钮会静默不出现
    // (不报错、就是不出来)。write 类 callout 里只有日记井带这个 emoji
    el.querySelector(".callout-title-inner")?.textContent.includes("📔")
  );
  if (!well) return false;
  const host = well.querySelector(".callout-content") ?? well;
  if (host.querySelector(".wb-diary-btn")) return true;
  // 不写"写日记":井本身就是写日记的地方,这条是另一条路(直接进当月文件),
  // 两个入口叠在一起容易让人以为点了才能在上面的井里写
  const btn = host.createEl("button", { cls: "wb-diary-btn" });
  btn.createEl("span", { text: "有什么新鲜事呀" });
  btn.createEl("span", { cls: "wb-diary-btn-arrow", text: "→" });
  btn.onclick = (e) => { e.stopPropagation(); newDiary(); };
  return true;
};

// 原来是轮询 34 次(约 5 秒)找不到就放弃,结果按钮经常不出现:阅读视图对屏幕外的内容是
// 懒渲染的,而这个井在整页最底下——不滚到那儿它根本不在 DOM 里,5 秒当然等不到。
// 改成 MutationObserver 一直盯着,井什么时候进 DOM 就什么时候挂;而且不 disconnect,
// 滚走再滚回来井被重新渲染时还能再挂一次(mountDiaryBtn 自身幂等,不会挂重复)
mountDiaryBtn();
if (window.MutationObserver) {
  const mo = new MutationObserver(() => mountDiaryBtn());
  mo.observe(wbRoot, { childList: true, subtree: true });
  dv.component.register(() => mo.disconnect());
}
```

> [!feed] 📰 简讯
> **China opposes US proposal to expand outbound investment curbs**
> 中国反对美方扩大对华投资限制的提案 · [CGTN](https://news.cgtn.com/news/2026-10-24/China-opposes-US-proposal-to-expand-outbound-investment-curbs-1RvDF2byKyI/p.html?UTM_Source=cgtn&UTM_Medium=rss&UTM_Campaign=China)
>
> 据报道,美国财政部最近提出修改"对外投资安全审查"规则(简单说,就是限制美国的钱和技术流向中国的某些领域),目前在公开征求意见,还没正式生效。中国商务部发言人周六说"严重关切、坚决反对",称这违背了两国元首达成的重要共识,是把国家安全概念泛化,并说保留采取相应措施的权利。这是中方的说法,美方具体拟加哪些限制,这篇报道没写。影响:这是中美在科技和资本上互相设防的又一步:美方想卡住流向中国敏感产业的钱和技术,中方表态会反制,两边一来一回地加码,芯片、人工智能这类行业拿外资、搞合作会更难(推论)。
>
> ---
> **VW targets China's electric sedan market with Xpeng-powered ID. UNYX 09**
> 大众安徽推出与小鹏合作的纯电轿车 ID. UNYX 09,限时 16.99 万元起 · [CnEVPost](https://cnevpost.com/2026/10/24/vw-anhui-launches-id-unyx-09/)
>
> 据报道,这款车周六上市,三个版本官方指导价分别是 17.99 万、21.99 万、24.99 万元;限时优惠 16.99 万元只给最低配的黑色车身、限 500 台,10 月 24 日到 11 月 30 日付定金的客户适用(具体以经销商为准)。电池约 92 度,续航(CLTC,国内常用的测试标准,数字偏乐观)705–755 公里,宣称充电 5 分钟能加约 250 公里。它是大众和小鹏合作的第二款车,用小鹏的芯片和辅助驾驶软件。影响:合资品牌开始直接用中国新势力的芯片和辅助驾驶软件,技术流向正在倒过来——过去是外资带中国造车,现在是中国企业给外资供技术;对买车的人来说,同档位纯电轿车竞争更凶,价格更容易松动,看价格别只看起步价,要问清配置和限量(推论)。
>
> ---
> **Serbia's veteran ruler Vučić concedes election to student-led protest movement**
> 塞尔维亚总统执政十二年的强人武契奇认输,学生运动领衔的名单获胜 · [BBC](https://www.bbc.co.uk/news/articles/cw5yn3xlprpmo?at_medium=RSS&at_campaign=rss)
>
> 据报道,塞尔维亚(东南欧国家,首都贝尔格莱德,申请加入欧盟但不跟着制裁俄罗斯)提前举行议会选举,总统武契奇周日深夜说"很明显我们输了",尽管最终结果还没出。选举的起因是 2024 年新萨德火车站雨棚坍塌造成 16 人死亡,人们认为这是腐败和玩忽职守的缩影,随后两年抗议不断。学生名单没有明显领袖,推出医生、演员、学者等人参选,主张清查镇压抗议的官员、让公共广播脱离政治控制。选举委员会的初步数字显示投票率创纪录(截至当地 18 时为 64.9%)。武契奇已当满两届总统,不能再连任,原打算当总理。影响:一个执政十多年的强人通过选票下台,对塞尔维亚是一次和平的政权更替;新政府如果真去清查腐败、让公共广播脱离政治控制,塞尔维亚往欧盟靠的路可能走得更顺,和俄罗斯的距离也可能拉开(推论)。
>
> ---
> **Deeply divided Israel braces for pivotal election**
> 严重分裂的以色列迎来关键大选 · [BBC](https://www.bbc.co.uk/news/articles/ckpdgy6pl7xlo?at_medium=RSS&at_campaign=rss)
>
> 据报道,以色列周二大选,最新民调显示执政联盟和主要反对派阵营几乎打平。以色列是议会制,选完要靠几个党拼凑出过半数的联盟才能组阁,所以谁的得票第一不等于谁当总理。现任总理内塔尼亚胡(以色列任期最长的总理,右翼利库德党)主打"绝不投降"的安全牌;挑战者是前军队总参谋长艾森科特,新人,中间派,许诺成立国家调查委员会查清 2023 年 10 月 7 日袭击,并执行让极端正统派犹太人服兵役的法院裁决。反对派指责内塔尼亚胡削弱司法权力。影响:这次选举决定以色列接下来几年怎么打、怎么谈:内塔尼亚胡留任大概率延续强硬路线,换人则可能先追查 2023 年那场袭击的责任、调整在加沙的做法;两边差距很小,组阁可能拖很久,以色列政局短期内都不太稳(推论)。

```dataviewjs
// ✅ 每日习惯:清单、频率、已练成、打卡记录全在 Profile/习惯打卡.md,纯 markdown。
// 不用 localStorage——换设备就没了,而且 AI 看不见;工作台只是它的一个界面
const HABITS_PATH = "Profile/习惯打卡.md";
const DAY = 86400000;
const d2s = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const TODAY = d2s(new Date());
const gap = (a, b) => Math.round((new Date(a) - new Date(b)) / DAY); // a 比 b 晚几天

// 频率两种写法:`每N天`(间隔型)、`周二周四`(星期型,写几个算几个)。
// 都不写就是每天。原始 spec 字符串原样留着,回写时照抄,不做重新拼装
const WEEKDAY = { 日: 0, 天: 0, 一: 1, 二: 2, 三: 3, 四: 4, 五: 5, 六: 6 };
const WEEKNAME = ["日", "一", "二", "三", "四", "五", "六"];
const parseSpec = (spec) => {
  const n = spec.match(/每?\s*(\d+)\s*天/);
  if (n) return { every: Math.max(1, Number(n[1])), days: null };
  const num = (c) => (c in WEEKDAY ? WEEKDAY[c] : Number(c) % 7);
  const days = [];
  // 「周一到周五」这种区间要展开,否则会被当成"周一和周五"两天,还不报错
  const range = spec.match(/([日天一二三四五六1-7])\s*[-~—到至]\s*[周週礼拜]*\s*([日天一二三四五六1-7])/);
  if (range) {
    for (let d = num(range[1]), guard = 0; guard < 7; guard++) {
      days.push(d);
      if (d === num(range[2])) break;
      d = (d + 1) % 7;
    }
    return { every: 1, days: days.sort() };
  }
  for (const m of spec.matchAll(/([日天一二三四五六])|([1-7])/g)) {
    const v = num(m[1] !== undefined ? m[1] : m[2]);
    if (!days.includes(v)) days.push(v);
  }
  return days.length ? { every: 1, days: days.sort() } : { every: 1, days: null };
};

// 「习惯」区:`- 名称`、`- 名称 | 每N天` 或 `- 名称 | 周二周四`;「已练成」区原样展示;
// 「记录」区:`- 日期 | 当天勾掉的习惯`
const parse = (text) => {
  const habits = [], graduated = [], done = new Map();
  let sec = "";
  for (const line of text.split("\n")) {
    const h2 = line.match(/^##\s+(.+?)\s*$/);
    if (h2) { sec = h2[1]; continue; }
    const rec = line.match(/^-\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(.*)$/);
    if (rec) { done.set(rec[1], rec[2].split(",").map((x) => x.trim()).filter(Boolean)); continue; }
    const item = line.match(/^-\s+(.+?)\s*$/);
    if (!item) continue;
    if (sec === "习惯") {
      const [name, spec = ""] = item[1].split("|").map((x) => x.trim());
      habits.push({ name, spec, ...parseSpec(spec) });
    } else if (sec === "已练成") {
      graduated.push(item[1]);
    }
  }
  return { habits, graduated, done };
};

// 三个区整段重写,比在原地插行稳。所以正文只写在第一个 ## 之前
const serialize = (text, st) => {
  const lines = text.split("\n");
  const start = lines.findIndex((l) => /^##\s+习惯\s*$/.test(l));
  if (start < 0) return null;
  const out = lines.slice(0, start);
  out.push("## 习惯", "");
  for (const h of st.habits) out.push(h.spec ? `- ${h.name} | ${h.spec}` : `- ${h.name}`);
  out.push("", "## 已练成", "");
  for (const g of st.graduated) out.push(`- ${g}`);
  out.push("", "## 记录", "");
  for (const [k, v] of [...st.done.entries()].filter(([, v]) => v.length).sort((a, b) => a[0].localeCompare(b[0]))) {
    out.push(`- ${k} | ${v.join(", ")}`);
  }
  out.push("");
  return out.join("\n");
};

const daysOf = (name, done) =>
  [...done.entries()].filter(([, v]) => v.includes(name)).map(([k]) => k).sort();

// 连续多少次。每天型:间隔 1 天算连上;每 N 天型:间隔 ≤ N 天就算连上;
// 星期型:只看该做的那几天,漏掉一个应做日才算断。
// 三种都遵守同一条:今天还没勾不算断,从上一个应做日往回数
const streakOf = (h, done) => {
  if (h.days) {
    const d = new Date();
    if (!(done.get(TODAY) ?? []).includes(h.name)) d.setDate(d.getDate() - 1);
    let n = 0;
    for (let guard = 0; guard < 400; guard++) {
      if (h.days.includes(d.getDay())) {
        if ((done.get(d2s(d)) ?? []).includes(h.name)) n++; else break;
      }
      d.setDate(d.getDate() - 1);
    }
    return n;
  }
  const days = daysOf(h.name, done).reverse();
  if (!days.length || gap(TODAY, days[0]) > h.every) return 0;
  let n = 1;
  for (let i = 1; i < days.length; i++) {
    if (gap(days[i - 1], days[i]) <= h.every) n++; else break;
  }
  return n;
};

// 今天该不该做:每天型天天该做;每 N 天型要等上次打卡满 N 天;星期型看今天星期几
const dueToday = (h, done) => {
  if (h.days) return h.days.includes(new Date().getDay());
  const days = daysOf(h.name, done);
  const last = days[days.length - 1];
  return !last || gap(TODAY, last) >= h.every;
};

const statsOf = (name, done) => {
  const days = daysOf(name, done);
  if (!days.length) return null;
  let best = 1, cur = 1;
  for (let i = 1; i < days.length; i++) {
    cur = gap(days[i], days[i - 1]) === 1 ? cur + 1 : 1;
    if (cur > best) best = cur;
  }
  return { first: days[0], last: days[days.length - 1], total: days.length, best };
};

const file = app.vault.getAbstractFileByPath(HABITS_PATH);
if (!file) {
  dv.container.createEl("div", { cls: "wb-heartbeat", text: `找不到 ${HABITS_PATH},习惯卡没数据源` });
} else {
  const card = dv.container.createEl("div", { cls: "wb-habits" });
  const head = card.createEl("div", { cls: "wb-reunion-head" });
  head.createEl("span", { cls: "wb-reunion-tag", text: "✅ 每日习惯" });
  const counter = head.createEl("span", { cls: "wb-habits-count" });
  const list = card.createEl("div", { cls: "wb-habit-list" });
  const foot = card.createEl("div", { cls: "wb-habit-grads" });

  const write = async (st) => {
    const out = serialize(await app.vault.read(file), st);
    if (out == null) {
      card.createEl("div", { cls: "wb-heartbeat", text: "习惯打卡.md 里找不到「## 习惯」那一段,没敢写" });
      return false;
    }
    await app.vault.modify(file, out);
    return true;
  };

  const draw = (st) => {
    const todays = st.done.get(TODAY) ?? [];
    const due = st.habits.filter((h) => todays.includes(h.name) || dueToday(h, st.done));
    counter.textContent = `${todays.length} / ${due.length}`;
    list.empty();
    for (const h of st.habits) {
      const on = todays.includes(h.name);
      const off = !on && !dueToday(h, st.done); // 今天轮空
      const row = list.createEl("label", { cls: `wb-habit${on ? " is-done" : ""}${off ? " is-off" : ""}` });
      const box = row.createEl("input", { type: "checkbox" });
      box.checked = on;
      const name = row.createEl("span", { cls: "wb-habit-name", text: h.name });
      const tag = h.days ? `周${h.days.map((d) => WEEKNAME[d]).join("·")}` : h.every > 1 ? `每${h.every}天` : "";
      if (tag) name.createEl("span", { cls: "wb-habit-every", text: ` ${tag}` });
      const n = streakOf(h, st.done);
      row.createEl("span", {
        cls: "wb-habit-streak",
        text: off ? "今天轮空" : n ? `🔥 ${n} ${h.days || h.every > 1 ? "次" : "天"}` : "",
      });
      // 练成了就毕业:从清单移进「已练成」,打卡记录原样留着,统计从记录里算
      const grad = row.createEl("button", { cls: "wb-habit-grad", text: "🎓" });
      grad.setAttr("title", "标记为已练成");
      grad.onclick = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        const s = statsOf(h.name, st.done);
        st.graduated.push(
          s
            ? `${h.name} | ${s.first} → ${s.last} · 打卡 ${s.total} 天 · 最长连续 ${s.best} 天 · ${TODAY} 练成`
            : `${h.name} | 没留下打卡记录 · ${TODAY} 练成`
        );
        st.habits = st.habits.filter((x) => x.name !== h.name);
        if (await write(st)) draw(st);
      };
      box.onchange = async () => {
        const st2 = parse(await app.vault.read(file));
        const day = new Set(st2.done.get(TODAY) ?? []);
        box.checked ? day.add(h.name) : day.delete(h.name);
        st2.done.set(TODAY, [...day]);
        if (await write(st2)) draw(st2); else box.checked = on;
      };
    }
    foot.empty();
    if (st.graduated.length) {
      foot.createEl("span", { text: `🎓 已练成 ${st.graduated.length}:` });
      foot.createEl("span", {
        cls: "wb-habit-grads-names",
        text: st.graduated.map((g) => g.split("|")[0].trim()).join(" · "),
      });
    }
  };

  (async () => draw(parse(await app.vault.read(file))))();
}
```


> [!draw] 🎴 今日抽卡 · 天生的倾向是偏置不是剧本
> [[Notes/个人/动机与改变/天生的倾向是偏置不是剧本-遗传度的误读与倾向的三层拆法|天生的倾向是偏置不是剧本-遗传度的误读与倾向的三层拆法]]
>
> 1. "遗传度 40–50%"为什么不等于"这个特质有一半来自基因"?它描述的是谁、在什么条件下?
> 2. 倾向分哪三层,各自的正确动作是什么?挑一个你常说的"我就是这样的人",看它落在哪一层。
> 3. 近视的例子想说明什么?

> [!seed] 🌱 今日延伸 · 好东西切成几段用
> 关于 [[Concepts/享乐适应|享乐适应]]:Nelson 与 Meyvis 2008 年的《Interrupted consumption》里,看电视被广告打断、做按摩被中途打断的人,事后评价反而更高,解释是打断拖慢了对持续刺激的适应。实际含义:想留住新鲜感,切成几段比一口气用完更划算。[事实,出处凭模型回忆,未联网核查,引用前请核实;实际含义是推论] 已同步写进 [[Concepts/享乐适应|享乐适应]] 延伸区。

> [!read] 📖 今日一读 · 反例 · "一个朴素的词"也会让感受变淡
> 先看库里这篇 [[Notes/思考/哲学与自我/研究情绪但不解构情绪-分析服务于体验而非替代体验|研究情绪但不解构情绪]](source:ChatGPT 分享对话;你自己写的顿悟段是原话;checkable: false)怎么说的。
>
> > [!note] 📄 库里这么写的
> > 长期用 AI 分析情绪、贴精准标签后会不安:"仿佛只要给它贴上一个准确的标签,我就获得了处理它的权力",下次遇到类似感受,可能直接用"眼泪是泪腺分泌"这种套话搪塞过去,不去真的感受。
>
> 这篇把危险放在"术语"上:标签太专业、太像理论,就把感受替掉了。外部研究在这里给了一个不太一样的说法。Lieberman 等人 2007 年在《Psychological Science》上做过一个脑成像实验:给负面情绪图片配上情绪词,杏仁核(管恐惧、警觉的脑区)的反应比其他处理方式更弱,同时右腹外侧前额叶更活跃。[事实,已联网核查:[PubMed](https://pubmed.ncbi.nlm.nih.gov/17576282/)]
>
> 这说明"变淡"不挑词:一个朴素的"我很生气"也会踩一下刹车,不需要等到"泪腺分泌"那种术语。[推论]所以只把词换朴素,保不住体验;要保体验,靠的是那篇后半讲的顺序和时机。另一面,这个刹车也是好东西:情绪太满想冷静时,标注就是现成的工具。
>
> 笔记里"先问是什么,别急着问为什么"倒是有旁证:Wilson 与 Schooler 1991 年(《JPSP》)让人分析自己为什么喜欢某样东西,偏好和专家评分的一致性反而变差。[事实,已联网核查:[UCSB 页面](https://labs.psych.ucsb.edu/schooler/jonathan/node/404);它测的是偏好判断,搬到情绪上是推论]
>
> **落点：**该担心的不是词太专业,而是"这一刻我想要它变淡,还是想让它走完"没想清楚就先贴了标签。想冷静就大方贴;想好好感受,就先别开口,等过一会儿再说。我已把这条补进那篇笔记的「反例与边界」。

> [!write] 📔 今日日记
>
>
