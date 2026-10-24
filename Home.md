---
cssclasses: workbench
generated: 2026-10-24
painting-url: "https://commons.wikimedia.org/wiki/Special:FilePath/White%20on%20White%20%28Malevich%2C%201918%29.png?width=1280"
painting-title: "卡济米尔·谢韦里诺维奇·马列维奇《Suprematist Composition: White on White》(俄罗斯前卫艺术、1918年)"
painting-intro: "卡济米尔·谢韦里诺维奇·马列维奇的作品(俄罗斯前卫艺术、1918)。"
---

🎴 10/24 法国人不是不追求成功-换了计价单位,而那… #工作台
· "不谈钱很俗"为什么不等于"没有在竞争"?它…
📖 对撞 · 到点就停,算"强迫"吗?
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
> **16 killed after M7.0 quake hits China's Xizang, rescue underway**
> 西藏那曲发生 7.0 级地震,已致 16 人死亡、救援展开 · [CGTN](https://news.cgtn.com/news/2026-10-23/news-1RsWPFMFpy8/p.html?UTM_Source=cgtn&UTM_Medium=rss&UTM_Campaign=China)
>
> 据报道,10 月 22 日晚 10 点 33 分(北京时间),西藏自治区(官方英文称 Xizang)那曲市巴青县发生 7.0 级地震,那曲市应急管理局通报 16 人遇难、46 人受伤(其中 11 人重伤),339 间房屋倒塌或受损。中国地震局启动了二级应急响应(应急响应分四级,一级最高),西藏自治区启动三级响应;武警、消防、医护和解放军驻藏部队连夜赶往灾区,供电、道路排查也同步展开,中央、自治区、市、县四级调运的帐篷、棉衣、板房等物资已在周五凌晨陆续运到。以上数字来自官方通报,后续可能更新。对你:灾区在高海拔偏远地带,眼下已入冬,最要紧的是抢救和御寒;对多数人日常没有直接影响,想帮忙的话,捐款认准官方或有资质的慈善机构渠道,别信朋友圈里来路不明的链接(推论)。
>
> ---
> **CPCA forecasts weak China NEV retail sales in October as peak season falters**
> 乘联会预测 10 月中国新能源车零售偏弱,"金九银十"旺季后劲不足 · [CnEVPost](https://cnevpost.com/2026/10/23/cpca-forecasts-weak-china-nev-retail-oct-2026/)
>
> 据报道,乘联会(CPCA,中国乘用车市场的行业协会,每月发销量预测)预计 10 月新能源乘用车零售约 107 万辆,比去年同期降 16.5%,比 9 月降约 1.3%;新能源渗透率(新能源占全部新车零售的比例)约 66.9%,仍在高位。整个乘用车市场约 160 万辆,同比降 28.9%。乘联会的解释是,国庆假期后到店客流很快回落,家庭收入预期偏弱,大家持币观望;经销商之间竞争激烈,但行业在治理"内卷式"低价,降价空间有限。多数车企前三季度只完成了全年目标的不到 60%。对你:想买车的话,眼下车企有冲量压力、新车型也在密集上市,但"治理内卷"意味着大幅降价没那么容易,不必为等一个更低的价格耽误用车;买之前多比几家的实际成交价和金融方案(推论)。
>
> ---
> **Oil price rises above $117 a barrel amid fears US will renew strikes on Iran**
> 因担心美国重启对伊朗的打击,油价升破每桶 117 美元 · [Guardian](https://www.theguardian.com/business/2026/oct/23/oil-five-month-high-fears-us-renews-strikes-iran)
>
> 据报道,国际基准的布伦特原油(伦敦交易的原油价格,常被当作全球油价的标尺)周五一度涨到每桶 117 美元以上,是 4 月以来最高;今年 2 月伊朗战争爆发前约为 72 美元。这场美以对伊朗的战争已进入第八个月,伊朗放话:若美以再次发动进攻,会袭击海湾地区的石油设施、海底电缆和数据中心;本周伊朗革命卫队还声称袭击了霍尔木兹海峡(中东石油出海的咽喉要道)的四艘商船。分析师称,市场担心美国会在 11 月 3 日的美国中期选举(国会半数议员改选)之后再次动武;乌克兰打击俄罗斯炼油厂也让供应更紧。对你:油价高会一路传导到汽油柴油价格、运费和各种商品成本,海外物价和航空燃油附加费都可能上涨;国内油价调整有自己的节奏,但长期高位也会受影响(推论)。
>
> ---
> **Russia, Ukraine agree to US-brokered, 1 city ceasefire**
> 俄乌同意在美国斡旋下对一座城市停火 · [DW](https://www.dw.com/en/russia-ukraine-agree-to-us-brokered-1-city-ceasefire/a-79746723?maca=en-rss-en-all-1573-rdf)
>
> 据报道,白宫周五宣布,美国第一夫人梅拉尼娅·特朗普促成俄乌在奥列什基(乌克兰南部、被俄军占领的前线城市,离赫尔松约 9 公里)的局部停火,白宫说 10 月 29 日开始;俄方确认协议,但说会更早、在 10 月 27 日当地时间 4 点停火。该城战前约 2.4 万人,现在只剩约 2000 人,多为老人,缺药缺水缺电。按乌克兰人权专员的说法,安排是先停火、再送人道援助、然后允许平民自由撤离。与此同时,乌克兰总统泽连斯基说,美俄乌三方谈判人员计划 11 月上半月在阿布扎比(阿联酋首都)会面,克里姆林宫(俄罗斯总统府)也说在筹备。这只是一座城的局部停火,不等于战争结束。对你:对普通人的钱包没有直接影响,但如果后续谈判真能谈成,能源和粮食的供应不确定性会小一些;谈判能走多远还很难说(推论)。

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


> [!draw] 🎴 今日抽卡 · 法国人不是不追求成功:换了计价单位
> [[Notes/思考/哲学与自我/法国人不是不追求成功-换了计价单位,而那个单位比钱更难伪造|法国人不是不追求成功-换了计价单位,而那个单位比钱更难伪造]]
>
> 1. "不谈钱很俗"为什么不等于"没有在竞争"?它换成了什么计价单位?
> 2. 为什么说品味这个单位"比钱更难伪造"?这对已经在里面的人和新来的人意味着什么?
> 3. "不必持续向上"这句话有两个来源,从外面看不出区别——这两个来源是什么?分不清的代价是什么?

> [!seed] 🌱 今日延伸 · 过滤器放得越前面越省力
> 关于 [[Concepts/水缸|水缸]]:Gross 的情绪调节模型(1998)把调节办法按出手早晚排开,最早是选情境、改情境,最晚才是把已经冒出来的情绪压下去;Gross 与 Levenson(1993)的实验里,忍住表情的人主观感受没变轻,生理激活反而更高。放到水缸上:筛人、选场合是前端的过滤器,进来了再硬忍代价高得多。[事实,出处凭模型回忆,未联网核查,引用前请核实;对应水缸是推论] 已同步写进 [[Concepts/水缸|水缸]] 延伸区。

> [!read] 📖 今日一读 · 对撞 · 到点就停,算"强迫"吗?
> 库里有两篇都在管"怎么推动自己",口气却对不上。
>
> > [!note] 📄 一篇说:一反感就停
> > [[Notes/个人/动机与改变/强迫自己与随性而然并不对立-用引导和脚手架替代强迫|强迫自己与随性而然并不对立]](source:用户与AI对话;checkable,verified: false,2026-09-13 复核过自我决定理论和白熊效应两处,结论支持):"改变让人痛苦、反感、极度内耗时就停止强迫,顺其自然。"
>
> > [!note] 📄 另一篇说:兴头上也要停
> > [[Notes/个人/动机与改变/工作节奏操作手册-启动成本是唯一的病,通宵和完全不做是同一个循环的两端|工作节奏操作手册]](source:用户自己整理的操作手册;verified: false,海明威那条未联网核查):"在还想继续的时候停……到 21:30 就停,尤其是正在兴头上的时候。"
>
> 表面上打架:一篇把"被迫"当警报,另一篇要你在最想继续的时候被一条线拦下。两篇都默认同一件事:分辨"强迫"还是"随性",看的是这一下顺不顺着当下的劲儿。我觉得这个前提本身不对。
>
> 自我决定理论自己就不这么分。Ryan 与 Deci 2000 年那篇综述把外部要求的内化分成几档:被逼着做、为了不愧疚而做、认同它的价值而做、整合进自己。到了"认同"这一档,行为虽然起点是规则,体验上却是自主的,不会触发那个"反抗者"。[事实,已联网核查:二手转述检索,未读原文,见 [Ryan & Deci 2000 综述的转述](https://ebsco.com/research-starters/social-sciences-and-humanities/self-determination-theory)] 另外,事先写好"到了几点就做什么"这类计划,在 Gollwitzer 与 Sheeran 2006 年的元分析里对目标达成的合并效应约 d = 0.65,中等到偏大。[事实,已联网核查二手转述,未读原文,见 [实施意图研究汇总](https://goalsandprogress.com/implementation-intentions-research/)] 这个数字别当百分比用,而且不同领域差别不小。
>
> **落点：**两篇其实不打架,打架的是"强迫"这个词。21:30 那条线如果是你自己认同的、提前定好的,它是脚手架,不是强迫;要分辨的是这条线被执行的那一刻你是松一口气,还是满肚子抵触。松一口气就留着;抵触得厉害,先改线(时间、停的方式),别靠硬撑,也别因此说"我不该有规则"。[推论] 是否真的如此,可以用一周的记录自己验证。

> [!write] 📔 今日日记
>
>
