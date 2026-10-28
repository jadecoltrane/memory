---
cssclasses: workbench
generated: 2026-10-28
painting-url: "https://commons.wikimedia.org/wiki/Special:FilePath/John%20Constable%20-%20Salisbury%20Cathedral%20from%20the%20Bishop%27s%20Grounds.jpg?width=1280"
painting-title: "约翰·康斯特勃《Salisbury Cathedral from the Bishop's Grounds》(1823年)"
painting-intro: "约翰·康斯特勃的作品(1823)。"
painting-guide: "背景:康斯特勃是英国风景画家,一辈子几乎只画英格兰乡间。这幅是索尔兹伯里主教约翰·费舍尔 1820 年向他订的画,主教的侄子小费舍尔是康斯特勃最好的朋友,他常去索尔兹伯里住。画的就是主教自家花园望出去的大教堂——尖塔是全英国最高的。\n故事:画送到后主教不满意:教堂正上方那片乌云太暗了,他想要一片晴朗的天。康斯特勃答应重画一版亮天的,还没画完主教就在 1825 年去世了。于是这幅原作给了小费舍尔,晴天那版后来送给主教遗孀。今天你能在纽约弗里克收藏馆看到那张\"改过天\"的版本。\n怎么看:先看两边的大树——树干和枝叶在画面中间合拢成一道拱门,把教堂框在里面,跟哥特式教堂的尖拱窗遥相呼应。左下角拿手杖指着教堂的小人,常被认为就是主教夫妇。右下角牛在水边喝水,让庄严的教堂落进安静的田园日常里。常见解读是\"自然和信仰和谐共处\";那片主教嫌弃的乌云,恰恰是康斯特勃最在意的东西:真实的英国天空。\n画派:属于浪漫主义时期的英国风景画。在他之前,风景多是神话故事的布景,要画得理想化;康斯特勃坚持对着真实天气写生,专门画过大量云的习作。看这幅里云的明暗、树叶上星星点点的白色高光,就是他捕捉光线变化的办法——这种画法后来影响了法国画家,一路通向印象派。\n资料:V&A 博物馆藏品页、英文维基《Salisbury Cathedral from the Bishop's Grounds》、弗里克收藏馆藏品页(委托、乌云、改稿已联网核查);左下角人物身份、对法国画派的影响为模型知识,未联网核查"
---

🎴 10/28 小红书写作定位-半知识型与从冲突开始而非… #工作台
· 日记视角和公开视角的分界是什么?把"今天我突…
📖 复核 · 「铁蛋白低于 30」是一条线,不…
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
// 导览默认收起:手机上卡片本来就占满一屏,展开与否由用户决定。每行「标签:正文」,标签加粗
const guide = String(p["painting-guide"] ?? "").trim();
if (guide) {
  const det = caption.createEl("details", { cls: "wb-painting-guide" });
  det.style.cssText = "margin-top:10px; font-size:0.9em; line-height:1.65; position:static;";
  const sum = det.createEl("summary", { text: "📖 看懂这幅画" });
  sum.style.cssText = "cursor:pointer; font-weight:600; color:var(--wb-accent-text); padding:4px 0;";
  for (const row of guide.split("\n")) {
    const m = row.match(/^([^::]+)[::](.*)$/);
    const para = det.createEl("p");
    para.style.cssText = `margin:8px 0 0; ${m && m[1] === "资料" ? "font-size:0.85em; opacity:0.6;" : ""}`;
    if (m) { para.createEl("strong", { text: m[1] + " " }); para.appendText(m[2].trim()); }
    else para.setText(row);
  }
}

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
> **Chinese markets lose trillions as race for AI supremacy with US takes its toll**
> 中国股市蒸发数万亿美元,与美国的 AI 竞赛代价显现 · [Guardian](https://www.theguardian.com/world/2026/oct/27/chinese-markets-lose-trillions-ai-race-beijing)
>
> 据报道,上海证券交易所跟踪科技创新企业的科创 50 指数(STAR 50)自 6 月以来跌了 40%,其他大公司指数同期跌约 20%;彭博社统计,5 月以来中国股市累计蒸发约 2.4 万亿美元。高盛说,AI 相关股票占中国内地和香港股市总市值的 40% 以上,所以它一跌,整个市场都会被拖着走。报道给的原因有几条:企业赚不到钱、中国消费者不愿掏钱、美国可能进一步限制中国科技产品(已禁止中国的人形机器人,据说还在考虑禁止数据中心使用中国零部件)。宇树科技(Unitree,机器人龙头)8 月上市后股价已腰斩。咨询机构欧亚集团的分析师说,人形机器人这类"具身智能"在大众市场上看不出能变成利润。影响:对国家来说,政府砸钱扶持 AI(本月刚有一只 600 亿元的国家支持基金开始投资)并不能自动换来市场信心,内需疲软才是根子;股市下跌也让"让居民把钱留在国内投资"这条政策更难见效(推论)。
>
> ---
> **VW considers bringing Xpeng co-developed architecture to European models, report says**
> 据报大众考虑把与小鹏共同开发的电子电气架构带到欧洲车型 · [CnEVPost](https://cnevpost.com/2026/10/27/vw-considers-xpeng-co-developed-architecture-europ/)
>
> 据报道,德国《经理人杂志》(Manager Magazin)援引知情人士说,大众考虑把原本为中国市场开发的"中国电子架构"(CEA,汽车的电子神经系统和底层软件,与小鹏共同开发)用到欧洲的大众、斯柯达、库普拉品牌新车上,覆盖约 75% 的下一代车型。大众核心品牌负责人斯凯费(Thomas Schaefer)预计 10 月 27 日向集团管理层提出这个方案,估算可省 40 亿到 50 亿欧元。目前大众在西方市场另与美国电动车公司 Rivian 合作做一套技术(投资 58 亿美元),改用中国方案会削弱 Rivian 的角色。公司内部有分歧:有人担心适配欧洲法规没有想的那么容易便宜。最终范围要看集团决定。影响:对行业来说,这是传统车企的软件路线可能从"西方自己做"转向"买中国团队已经跑通的",成本压力正在改变技术的流向;但目前只是媒体报道的内部提案,还没拍板(推论)。
>
> ---
> **Israel election: Anti-Netanyahu bloc ahead, but no majority**
> 以色列大选:反内塔尼亚胡阵营领先,但无一方过半 · [DW](https://www.dw.com/en/israel-election-anti-netanyahu-bloc-ahead-but-no-majority/live-79713839?maca=en-rss-en-all-1573-rdf)
>
> 据报道,以色列周二举行国会(议会,称 Knesset,共 120 席,组阁至少要 61 席)选举,出口民调显示:总理内塔尼亚胡的利库德党仍是单一最大党(约 25 席),但他的执政联盟只有约 50–51 席,远低于现在的 68 席;前军队总参谋长艾森科特(Gadi Eisenkot)带领的反对派阵营约 53 席,也没过半。他呼吁内塔尼亚胡下台,并主张取消极端正统派犹太男性的兵役豁免。阿拉伯穆斯林政党 Ra'am 预计拿 7 席,意味着任何政府都绕不开它,尽管两大阵营此前都排除过与它合作。按以色列程序,总统会指定一位候选人去尝试组阁。内塔尼亚胡不太可能认输,最终席位以正式结果为准。影响:对地区格局来说,一个没有明确授权的以色列政府,在伊朗冲突和加沙问题上是否还能做重大决策会被质疑;组阁谈判可能拖很久,甚至再来一轮选举(推论)。
>
> ---
> **Ceasefire extended across Ukraine's Kherson region, officials say**
> 乌克兰赫尔松地区的停火范围扩大,官员称 · [BBC](https://www.bbc.co.uk/news/articles/c6lye1w9p2l8o?at_medium=RSS&at_campaign=rss)
>
> 据报道,为了让被围困的俄占城市奥列什基(Oleshky)运进食物和药品而开始的停火,已扩大到整个赫尔松州(乌克兰南部)。城里估计还有 1700 到 2000 人,2023 年卡霍夫卡大坝被炸后就没有电、气、水,出城的路布了地雷、还有无人机袭击。美国第一夫人梅拉尼娅·特朗普和教宗良十四世共同促成这次停火;乌俄双方都说在遵守,克里姆林宫称一切"按计划"进行。计划是停火后先送人道援助,周五组织愿意离开的居民撤离;停火持续到 11 月 1 日。乌克兰外长说,若有成果可为和平进程的"其他步骤"铺路。影响:这是 2022 年以来被乌方人士称为"最大规模的降温",对几千名被困居民是实实在在的救命窗口;至于能否推动更大范围的和谈,目前只有乌方的期待,没有实质进展(推论)。

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


> [!draw] 🎴 今日抽卡 · 小红书写作定位:半知识型,从冲突开始而不是从观点开始
> [[Notes/练习/写作/小红书写作定位-半知识型与从冲突开始而非从观点开始|小红书写作定位-半知识型与从冲突开始而非从观点开始]]
>
> 1. 日记视角和公开视角的分界是什么?把"今天我突然想到我一直在分析自己的情绪"改成公开视角,会怎么说?
> 2. 动笔前的三个问题是哪三个?挑一件最近想写的事,先只回答第一个:你真正想说的"矛盾"是什么?
> 3. 笔记说 AI 写的文字"太完整"是不能学的那部分,真人写作者会故意保留什么?

> [!seed] 🌱 今日延伸 · 看到"像"的描述时,别把基础比例扔了
> 关于 [[Concepts/先验|先验]]:Kahneman 与 Tversky 1973 年在《Psychological Review》的《On the psychology of prediction》里,先告诉被试样本中 30% 是工程师、70% 是律师(或反过来),再给一段人物描述让他们估概率;两组的估计几乎一样,只跟描述"像不像"走,基础比例几乎不起作用。放到画像上:一条"像她"的新描述出现时,先问这类情况本来占多大比例。[事实,出处凭模型回忆,未联网核查,引用前请核实;"放到画像上"是推论] 已同步写进 [[Concepts/先验|先验]] 延伸区。

> [!read] 📖 今日一读 · 复核 · 「铁蛋白低于 30」是一条线,不是一条诊断线
> 这篇笔记把"气色差"和"头发细"当成一个可以抽血排查的问题,先查铁蛋白、甲状腺、雄激素。今天重新核了它最实在的两个说法。
>
> > [!note] 📄 库里这么写的
> > 来源:会话推演,医学部分写明"凭训练知识、未联网核查",`verified: false`。原文:"铁蛋白低于 30 ng/mL 就可能出现弥漫性掉发……而血红蛋白可以完全正常";"抽血前 2–3 天停掉含生物素的美容补剂"。→ [[Notes/个人/身体/气色和头发共用一条可测上游-先排铁甲状腺雄激素再谈生发|气色和头发共用一条可测上游]]
>
> 先说站得住的:生物素那条是真的。美国 FDA 在 2017 年发了警告、2019 年又更新:吃大剂量生物素会干扰一部分化验,最严重的是心肌梗死用的肌钙蛋白检测会假性偏低,报告过一例死亡;甲状腺检测也有结果失真的报道。建议抽血前停几天。[事实,已联网核查,只读了搜索摘要,未打开 FDA 原页:[Lab Tests Online](https://labtestsonline.org/news/fda-warns-biotin-may-affect-some-lab-test-results)、[Healio](https://www.healio.com/cardiology/practice-management/news/online/%7B69850f89-6334-420c-be82-9556b6c18c82%7D/fda-risk-for-biotin-interference-with-lab-tests-troponin-remains-a-concern)]
>
> 再说要打折的:"30"这个数不是一个公认的诊断线。2013 年一项 80 名女性对 40 名对照的小研究,算出的分界值是休止期脱发约 27.5、女性型脱发约 29.4(单位 µg/L,和 ng/mL 一样);别的研究用 40 或 41,也有人建议脱发时把目标放在 40–70。而且这些多是"某一时刻量一下"的研究,只能说铁蛋白低和掉发常一起出现,说不了谁导致谁。[事实,已联网核查摘要:[PubMed 23428658](https://pubmed.ncbi.nlm.nih.gov/23428658/);其余数字来自同一次搜索的摘要,没逐篇打开] 米诺地尔浓度、螺内酯的证据强度、何首乌这三条今天没核,仍是模型回忆。
>
> **落点：**结论是主结论成立、数字要松一点:先抽铁蛋白、甲状腺、雄激素这个顺序没问题,生物素要停也没问题;但拿到化验单时别只盯"有没有低于 30",该问医生的是"我这个值对掉发算不算偏低、要不要补"。笔记里的"30"改读成"常见的低值线",它是起点,不是判决。

> [!write] 📔 今日日记
>
>
