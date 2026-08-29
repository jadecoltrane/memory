---
cssclasses: workbench
generated: 2026-08-30
painting-url: https://commons.wikimedia.org/wiki/Special:FilePath/JEAN%20LOUIS%20TH%C3%89ODORE%20G%C3%89RICAULT%20-%20La%20Balsa%20de%20la%20Medusa%20%28Museo%20del%20Louvre%2C%201818-19%29.jpg?width=1280
painting-title: 杰利柯《梅杜薩之筏》(浪漫主义、1819年)
painting-intro: 《美杜莎之筏》是法國浪漫主義畫家西奥多·杰利柯（1791─1824）在1818年─1819年間畫的油畫。这幅畫是在他27歲時畫的，之後成为法國浪漫主義的標誌。
---

🎴 8/30 贵气是自己划的下限-不是别人给的上限 #工作台
· "就是运气不好"这句话本身站得住,真正伤人的…
❓ 笔记里说睡前走… · 笔记把"展示自…
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
const newNote = async () => {
  const folder = "Notes";
  if (!app.vault.getAbstractFileByPath(folder)) await app.vault.createFolder(folder);
  let n = 1, path;
  do { path = `${folder}/未命名笔记 ${n++}.md`; } while (app.vault.getAbstractFileByPath(path));
  const now = new Date();
  const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
  const file = await app.vault.create(path, `---\ntype: note\ncreated: ${today}\n---\n\n`);
  await app.workspace.getLeaf(true).openFile(file);
};

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
// created 没写 frontmatter 时退回文件系统 ctime,避免本周新增/日期列空白
const ctimeOf = (pg) => pg.created?.ts ?? (pg.created ? new Date(String(pg.created)).getTime() : pg.file.ctime?.ts ?? 0);
const mtimeOf = (pg) => pg.file.mtime?.ts ?? 0;
const weekNewPages = notes.array().filter(pg => {
  const t = ctimeOf(pg);
  return t > 0 && Date.now() - t < 7 * 864e5;
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
const buildNotesBase = async (catGroups) => {
  const esc1 = (s) => s.replace(/'/g, "''"); // YAML 单引号字符串里,单引号本身要写成两个单引号转义
  const esc2 = (s) => s.replace(/"/g, '\\"');
  const lines = ["views:"];
  const pushView = (name, filterExpr) => {
    lines.push("  - type: table");
    lines.push(`    name: "${esc2(name)}"`);
    lines.push("    filters:");
    lines.push("      and:");
    lines.push(`        - '${esc1(filterExpr)}'`);
  };
  pushView("全部笔记", `file.inFolder("Notes")`);
  for (const [name] of catGroups) {
    const filterExpr = name === "未分类" ? `file.folder == "Notes"` : `file.inFolder("Notes/${name}")`;
    pushView(name, filterExpr);
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
    const hits = notes.array()
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

const weekPanel = (host) => renderRows(host, [...weekNewPages].sort((a, b) => ctimeOf(b) - ctimeOf(a)), (pg) => fmt(ctimeOf(pg)));
// 最近编辑固定只给 8 条,不设展开全部——这颗胶囊就是"最近"这个时间切片,不是需要看全的列表
const recentPanel = (host) => renderRows(host, [...all].sort((a, b) => mtimeOf(b) - mtimeOf(a)).slice(0, 8), (pg) => fmt(mtimeOf(pg)));

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

addTab("📝", notes.length, "笔记", notesPanel);
addTab("🌿", concepts.length, "概念", conceptsPanel);

// 双链不展开页内面板,直接跳转 Obsidian 原生图谱——图谱是独立可视化,塞进小面板意义不大
const linksCard = bar.createEl("div", { cls: "wb-card" });
linksCard.createEl("span", { cls: "wb-num", text: `🕸️ ${edges}` });
linksCard.createEl("span", { cls: "wb-lbl", text: "双链" });
linksCard.onclick = openGraph;

addTab("🌱", weekNewPages.length, "本周新增", weekPanel);
addTab("🕘", "", "最近编辑", recentPanel);

const addAction = (glyph, label, cls, run) => {
  const card = bar.createEl("div", { cls: `wb-card ${cls}` });
  const g = card.createEl("span", { cls: "wb-num wb-newnote-glyph", text: glyph });
  card.createEl("span", { cls: "wb-lbl", text: label });
  card.onclick = async () => {
    if (card.classList.contains("is-busy")) return;
    card.classList.add("is-busy");
    const anim = g.animate(
      [{ transform: "rotate(0deg)" }, { transform: "rotate(360deg)" }],
      { duration: 450, easing: "ease" }
    );
    try { await anim.finished; } catch (_) { /* 动画被打断也照样执行 */ }
    g.style.removeProperty("transform");
    card.classList.remove("is-busy");
    run();
  };
};

addAction("＋", "新建笔记", "wb-newnote", newNote);

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


> [!clash] 🥊 碰撞 · 问题1 回顾
> *好奇暂存箱和探索沙盒这两个应对停不下联想的动作有没有真的用过*
>
> > [!write] 🗣️ 你的回答
> > 我目前还没有试过这种固定时间或者是固定的,但是我觉得我现在一般来说都是一些生产型的,后期,我可能是想为了达到一种更好的状态去问问AI我目前需要做什么,而不是说问他就是为了玩,不过有点我想承认的说我可能比较执着于感受,就是想达到一种什么样的感觉,而这种感觉是比较空泛的,如果我没有当下去规划我要真正做到的某些具体的事,他就仅仅成为一种幻想,然后我拿这种幻想去问AI这这种行为,我觉得可以称作为是消费型的,但是也还好吧,我要为自己整一下,我平常拿来消费的时间其实并不多,最主要的还是想去做点什么,就是达成真正的自我
>
> > [!note] 💭 我的看法(上期)
> > 我倾向于:三个方法里最可能被坚持用下来的是好奇暂存箱,而不是探索沙盒或那道"消费型/生产型"判断题——后两者都要求在冲动最强的那一刻做一次额外的自我评估,执行权还是摆在系统二手里(费力,又恰好最容易在高唤醒时失效);暂存箱只要求一个最低成本的动作(写下来),动作一完成,认知负担就转移出去了。这不是猜的:Storm 与 Stone 2015 年发表在《Psychological Science》的研究发现,把一份清单"存"起来(哪怕只是存进电脑)会显著降低它对后续学习新信息的干扰,这个"存储增强记忆"效应的机制被认为是认知卸载——外部保存让大脑真的放下了这份信息,不用继续占着工作记忆去"惦记着别忘了"。[事实,已联网核查]换句话说,暂存箱管用不是因为它训练了自制力,是因为它给了大脑一个可信的"已经安全存档"的信号。如果真的坚持下来了一个,大概率是这个。
>
> **碰撞:** 上期猜错了具体是哪个工具——押注暂存箱会被留下来,而实际是三个具名工具一个都没真正用过。但错的只是"押哪个工具"这一层,押的机制可能还站得住:你自己描述的筛选标准——问AI是为了推进当下要做的一件具体事,还是拿一份还没落地的"空泛感觉"去问——本质上就是消费/生产判断题的另一种说法,只是没挂那个名字,你已经在不靠具名工具的情况下自己在做这道判断题。这里真正值得停的是一层更细的机制:Locke 与 Latham 综述了 400 多项研究的目标设定理论(goal-setting theory)发现,具体、可核对的目标在约 96% 的对照里跑赢"尽力而为"这类模糊目标,差距的来源不是努力程度,是模糊目标没有一个明确的"达标线",人会默认给自己放行。[事实,已联网核查]"想达到一种感觉"正是最典型的模糊目标——没有可以核对完成没完成的标准,这解释了为什么你说它"没有当下要做的具体事就仅仅成为一种幻想"。更狠的一层来自 Mauss、Tamir、Anderson 与 Savino 2011 年发表在《Emotion》的研究:越把"达到某种感觉/幸福"本身设成想追的目标,人在压力不大的日常情境里反而越容易感到没达到、进而更失望——一旦把感觉设成目标,就会不断拿当下状态去比对"到了没有",这份比对本身容易生出没达到的失望,反而挤掉了原本会自然带来那种感觉的具体行动。[事实,已联网核查]两条摆在一起说明:直接问AI"我该怎样才能达到那种状态",处在离具体行动最远、离监测感觉本身最近的那一端,这才是它更容易滑向消费的原因,不是因为"问AI"这个动作本身有问题。真正的分界线不是"暂存箱用没用",是提问前有没有先把这份感觉翻译成一件可核对的具体事——这个标准你已经在用,只是没意识到它有名字。

> [!clash] 🥊 碰撞 · 问题2 回顾
> *换成有后果的对象时,第一反应是先生气还是先反思自己*
>
> > [!write] 🗣️ 你的回答
> > 这个如果想象了一下,我可能会有怒气,但是我不会当场跟那些比我高贵的人反驳通常会私下产生一些怨言,我还是有点认识,不论人吧,那说上次说的什么都对,但我如果敬佩他或者是认为他的言论在我这里是比较权威的话,我可能第一时间先去反思自己,再说有没有这个情绪
>
> > [!note] 💭 我的看法(上期)
> > 我倾向于:大概率是先反思自己,而不是先生气——不是愤怒"不该"对着有后果的对象发,是评价一出现,归因的目标先变了。Weiner 的归因情绪理论(attribution theory of emotion,1985)指出:同一件负面结果,归因到外部(对方的错)会生出愤怒,归因到内部(自己的问题)会生出内疚/自我审查,两种情绪接近互斥——一旦"是不是我哪里没做好"这条内归因先被激活,愤怒的通路就被挤占了,不是被压下去,是没被启动。有后果的对象恰恰更容易触发内归因,因为对方手里握着一份可以被内化的表现标准;退快递码那次没有这种标准可供归因,只能落在偏好层面。这个机制之外还有一层不涉及归因、纯现实的因素:研究发现人对高地位/有权力差的对象本来就更少表达愤怒、更多压抑——不是感觉不到,是评估过表达的代价更高。[事实,已联网核查]这两层可能同时在起作用,现场很难分清是哪一层挡住了愤怒,但两层都不涉及"这件事本身有没有让我不爽"。
>
> **碰撞:** 上期猜的方向部分对——面对你敬佩、认为对方评价权威的人,第一反应确实是先反思自己而不是先生气,这和 Weiner 归因情绪理论的预测吻合。但这次的答案比上期的预测细,而且揭出一个上期没处理的分岔:面对"比我高贵"但你并不认可、只是对方握着后果的人,你说会有怒气,只是不会当场反驳,事后私下留怨言——这不是"怒气没生成",是怒气生成了、只是没被表达出来。这两种情况看着都是"没当场发火",实际是两台不同的机器。Gross 与 John 2003 年发表在《人格与社会心理学期刊》的情绪调节研究把它们分得很清楚:**认知重评**(reappraisal)发生在情绪生成之前,换一个解读角度,真正把感受到的强度降下去;**表达抑制**(expressive suppression)发生在情绪已经生成之后,只压住外在表达,内在的主观体验和生理唤醒基本不受影响——研究发现常用抑制的人,负面情绪的实际体验反而更强,人际功能和幸福感也更差,不是"忍住了就没事"。[事实,已联网核查]你说的"敬佩、认为权威"那一档,更接近重评在起作用——对方的话被当成有效信息去核对,核对本身把怒气挤没了;"没那么认可但对方有后果"那一档,更接近纯抑制——怒气是真实生成的,只是被压住不表达,私下的怨言正是那份没被处理掉的情绪找的出口,代价可能比看上去更高。上期用同一套归因理论去解释所有"扛不扛得住"的现场,默认了一个前提:只要是自我反思在先,就说明怒气没生成。这次的新样本证伪了这个默认——反思在先和怒气没生成不是一回事,反思也可能只是怒气被压下去之后留在表面的那层。这个答案是设想出来的、不是真实现场,权重要打折,但它已经指出下一个该盯的东西:下次真遇到有后果又不认可的人惹到你,该记的不是"我有没有生气",是生气之后那份感觉去哪了——是真的被重评消掉了,还是只是换了个不出声的地方存着,代价照单全收。

> [!draw] 🎴 今日抽卡 · 贵气是自己划的下限,不是别人给的上限
> [[Notes/思考/哲学与自我/贵气是自己划的下限-不是别人给的上限|贵气是自己划的下限-不是别人给的上限]]
>
> 1. "就是运气不好"这句话本身站得住,真正伤人的不是这份不公平,是哪个被默认相信的前提?
> 2. 三个成本为零的最小动作(不解释、不用笑化解尴尬、不接受"你想太多了")共同在收回什么?
> 3. "公主"拆开的四样东西里,哪一样被标成没法自己给自己、必须靠别人?

> [!seed] 🌱 今日延伸 · 打断的代价不只是变慢,是同样的产出背后更累
> 关于 [[Concepts/深度工作|深度工作]]:笔记里 Newport 的注意力残留说的是打断有代价这个机制,没给量级。Gloria Mark、Daniela Gudith 与 Ulrich Klocke 2008 年发表在 CHI 会议(ACM SIGCHI)的《The Cost of Interrupted Work: More Speed and Stress》给出了具体数字:被打断的任务里 81.9% 当天会被重新捡起来,平均耗时 23 分 15 秒,中间通常会先绕道处理大约两件别的事才折返。⚠️ 这份研究常被引用错的一层是:23 分钟指的是"重新捡起被打断的那个任务",不是"重新进入深度专注状态";同一份研究还发现一个反直觉的结果——被打断后,人完成任务的**速度反而更快**(约快 7%),代价是明显更高的工作负荷、压力和挫败感,是靠加速、更紧绷地填上了被打断吃掉的时间,不是真的不受影响。这给"深度工作一天上限约4小时"补了一层:打断的代价可能不是最直观的"效率变慢",是同样的产出背后压力和消耗更高,这部分损耗在当天的产出数字上反而看不出来。已同步写进 [[Concepts/深度工作|深度工作]] 延伸区。[事实,已联网核查]

> [!ask|1] ❓ 问题1
> 笔记里说睡前走神其实分三种:①睡前那种是精力耗尽后的自然放空,不是在处理信息;②白天专注完之后的走神,是大脑在把刚做的事理顺,有产出;③白天没铺垫的发呆,就是纯粹耗着。但这个说法和你另一篇笔记记的不一样——那边说睡前脑子经常停不下来,得靠呼吸法、脑内卸货这些方法才能降频,不是躺下就能自然放空。最近有没有一个真的很难睡着的晚上,当时留意过自己脑子里在转的是哪种走神?
>
> > [!write] ✍️ 你的回答
> >
> >
>
> > [!note]- 💬 我的看法
> > 我倾向于:大概率不是干净的"自然放空",更接近笔记里"睡前 DMN 高活跃"那个版本——三分法里"睡前=生理准备、不是认知产出"这条判断本身是在没有真的失眠的时候、事后归纳出来的一套更舒服的说法,而不是当场记下来的观察。真正失眠躺着的时候,大脑在做的更可能是白天没处理完的素材继续拼贴(游戏没打完、没回的消息、没想通的事),这本身就是一种"专注后走神",只是发生的时机不对、身体也没准备好停下来,所以才需要外部工具介入。真正能验证的方法只有一个:下次真的睡不着,当场记一句在想什么,而不是第二天早上再总结成"那是自然放空"。[推论,未联网核查]

> [!ask|2] ❓ 问题2
> 笔记把"展示自己"拆成三个动作:表演给人看(炫一下,容易显得像小丑)、发布(把东西放到一个地方,这个不能省)、推销(挨个找人说你看我,这个最容易让人尴尬)。但笔记自己也承认很多场合三个会叠在一起分不清,比如开会时说出一个观点,或者把作品链接发给一个具体的人。你有没有一个自己真实做过的例子,当时那个动作你会算进哪一类?
>
> > [!write] ✍️ 你的回答
> >
> >
>
> > [!note]- 💬 我的看法
> > 我倾向于:开会说观点大概率会被归成"发布"而不是"表演"——因为那个场合本来就要求每个人产出内容,说出观点是位置要求的动作,不是主动挑起的"你看我";反而是说完之后有没有多补一句"你们觉得怎么样"、有没有等对方反应,才决定它滑没滑进表演。发链接给一个具体的人更接近"推销"边缘,但笔记自己给的判据(发布是把东西放进本来就有人找这类东西的地方,推销是主动走向一个人)在"发给一个朋友"这种场合其实不够用——朋友既不是"陌生人的信息流",也不完全是"你看我"式的主动兜售,这个判据本身可能只覆盖了公开平台的情况,私聊场景需要一条新的分法。

> [!write] 📔 今日日记
>
>
