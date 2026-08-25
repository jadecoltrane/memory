---
cssclasses: workbench
generated: 2026-08-26
painting-url: https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Nighthawks_by_Edward_Hopper_1942.jpg/1280px-Nighthawks_by_Edward_Hopper_1942.jpg
painting-title: 爱德华·霍普《夜游者》(美国写实主义,1942年)
painting-intro: 深夜街角餐馆的冷光下,几个互不交谈的顾客各自坐着——霍普用大片沉默的几何色块,画出现代都市生活里触手可及却穿不透的孤独感。
---

🎴 8/26 气场是减出来的 #工作台
· 治抽动症、拔毛症用的那套训练方法叫什么?靠的…
❓ 有个概念叫"水… · 有篇笔记讲
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
> *状态失控时说"这不算大事",是真的更容易恢复平衡,还是给自己找了个借口。*
>
> > [!write] 🗣️ 你的回答
> > 我是更容易把状态收回来了,昨天我做的特别好的,我又没忍住打了3个小时,因为自己心情不好,但我居然控制住了,3个小时打完就没打了。事后我第一次感受到不是苛责自己而是把自己哄好了。
>
> > [!note] 💭 我的看法(上期)
> > 我倾向于:这两种不是靠"当时诚不诚恳"分开的,同一句"这不是什么大事",很多时候当事人自己当场都分不清是哪一种。Breines 与 Chen(2012,《人格与社会心理学通报》,《自我关怀提升自我改进动机》)的一组实验能帮着分:他们发现被引导用自我关怀(self-compassion,对自己的弱点或失误报以善意而非苛责)的方式看待一次失败的人,后续更愿意花更长时间备考、更愿意弥补、也更愿意直面自己那项弱点——和很多人担心的"心软了就懈怠了"正好相反。所以判断那句"这不是大事"是哪一种,不用看当时的语气,看**说完之后有没有多花哪怕一点力气去处理它**:真自我关怀是"这次没做好,但这不代表我整个人完了,所以我还能接着调整";纯找借口版本说完就翻篇,什么都没跟上。[事实,已联网核查]
>
> **碰撞:** 你的回答其实没有正面回答这道题——你说"这次"更容易把状态收回来了,但这道题问的是"这句自我安慰话到底是哪一种",单靠一次经历是判不出来的,我们俩这次讨论都默认了一次成功的经历就足以给这套方法定性。习惯研究给这道题一个更现实的判准:Lally 等人(2010,《欧洲社会心理学期刊》)对 96 名受试者的真实追踪显示,新习惯稳固平均要 66 天,个体差异极大(18~254 天),而且**单次的偏离对最终能不能养成习惯几乎没有可测的影响**——真正决定成败的是长期的重复趋势,不是任何单独一次的成败。这条其实架空了这道题原本的问法:与其问"这次是真的还是找借口",更该问的是接下来两三周,同样是心情不好想打游戏的夜里,"打完就停"这个动作重复出现的比例有没有在往上走。而且我们俩还共享了一个没拆开的前提:默认"打了 3 小时"本身就是需要被"哄"过去的失控——这个时长算不算失控,判准是谁定的,从来没被单独审视过。如果只发生这一次就再没跟踪,这次经历更接近一份好看的孤例,而不是能给"哄好了自己"这套说法背书的证据。[事实,已联网核查]

> [!clash] 🥊 碰撞 · 问题2 回顾
> *需要表现热情耐心但心里没那份劲时,是硬撑着装,还是想办法真的让自己进入状态。*
>
> > [!write] 🗣️ 你的回答
> > 我很多时候都是硬撑撑过去,因为我觉得当前的事件重要程度还不值得我投入。
>
> > [!note] 💭 我的看法(上期)
> > 我倾向于:两种大概率都用过,但表层扮演更容易在"手头资源已经紧张"的时候被默认选中。自我损耗理论(ego depletion,Baumeister、Bratslavsky、Muraven 与 Tice,1998,《人格与社会心理学期刊》)认为自我调节靠的是一份有限、会被消耗的资源池,深层扮演需要先做一轮"说服自己相信"的内在工作,这本身要预支这份资源——资源池已经被别的事耗得差不多时,大脑会自动挑更省的那条路,直接调表情,不去动内在感受。所以更值得回想的可能不是"哪种更常发生",是**那次硬撑着装的场合,发生在那天的什么时间点**——是刚开始,还是已经连轴转了好几件事之后?[推论,ego depletion 后续有复制争议,这里只取"资源紧张时挑更省力的路"这个方向性论点]
>
> **碰撞:** 我上期的框架把表层扮演讲成一件"发生在你身上"的事——资源见底了,大脑自动挑更省的选项;你给出的却是一个主动的判断句:"我觉得这件事重要程度还不值得投入"。这不是同一件事的两种说法,是两套完全不同的因果链。认知科学里有一套更贴近你描述的理论:**预期控制价值理论**(Expected Value of Control,Shenhav、Botvinick 与 Cohen,2013,《神经元》)主张,投入认知努力(深层扮演正属于这类高投入加工)本身就是一次成本收益计算的产物——大脑先估这次投入的"值"有多大、要花多少代价,再决定要不要投入,不是资源池空了才退而求其次。这条比 ego depletion 更贴近你的自述,也说明我上期问的"发生在一天中的什么时间点"问错了方向——真正该问的不是资源余量,是**你在用什么给"值不值得"打分**:这件事本身的重要性,还是那天剩下的精力,这两套判据经常被混在一起,自己未必分得清用的是哪一套。而且我们俩共享了一个没拆开的前提:默认深层扮演更"高级"、表层扮演是妥协或损耗——但如果一件事真不值得投入,选表层扮演可能恰恰是把有限的深层扮演额度留给真正在乎的场合,是主体性,不是心虚地硬撑。[事实,已联网核查]

> [!draw] 🎴 今日抽卡 · 陪笑戒不掉,是因为"决定不笑",还是该换一套动作
> [[Notes/思考/关系与处世/气场是减出来的-先换掉陪笑的反射再谈删软化词与亮线|气场是减出来的]]
>
> 1. 治抽动症、拔毛症用的那套训练方法叫什么?靠的是"压抑"冲动,还是"替换"冲动?
> 2. 视觉支配比这个指标说的是,高地位者和低地位者在"听"和"说"这两个阶段,眼神习惯分别是什么样?
> 3. 起步阶段最初定的达成信号后来被改写过一次,新的两条分别是什么?"身体在响"为什么反而是好事,不是失误?

> [!seed] 🌱 今日延伸 · 选"结构性拦住"而不是"练习别灾难化",心理学上这套操作有名字吗
> 关于 [[Concepts/非黑即白思维|非黑即白思维]]:已探讨区里,用户明确倾向"结构性方法"(从源头拦住第一次破戒),而不是"练习自己别这么想"。给这个偏好补一条支撑:Peter Gollwitzer 提出的**执行意图**(implementation intentions,"if-then"计划)——相比笼统的目标("我要少打游戏"),预先把情境和行动焊死成一句"如果 X 发生,我就做 Y"("如果到了晚上 11 点,我就把游戏账号退出登录"),能大幅提高目标达成率。2006 年 Gollwitzer 与 Sheeran 汇总 94 项研究的元分析算出中到大效应量(d=.65),机制是把决策提前转移到情境线索本身,冲动上来时不需要再临场做意志力博弈。这给用户的选择补一层解释:结构性方法不是在回避处理心理,是把战场从"当下要不要控制自己"挪到"提前设好的规则要不要生效",后者对意志力的要求低得多。这条已同步写进 [[Concepts/非黑即白思维|非黑即白思维]] 延伸区。[事实,已联网核查]

> [!ask|1] ❓ 问题1
> 有个概念叫"水缸"——一段关系值不值得留,看它有没有真的往你心里注入过滋养的东西,不是只停在一起玩、一起打发时间那个层面。之前聊过你现在的朋友关系好像还没有哪一段让你觉得真正被滋养过,都还停在玩伴那个层次。你觉得这是运气不好、刚好没遇到那种能走深的人,还是"关系不用太深也没关系"这句话,其实是你自己在替"一直没有深交"找一个说得过去的理由?
>
> > [!write] ✍️ 你的回答
> >
> >
>
> > [!note]- 💬 我的看法
> > 我倾向于:这两个选项本身可能是假二选一。运气(遇没遇到)和自我说服(编个说法接受现状)从来不是互斥的,常见的顺序反而是先有前者、再长出后者——早期确实没遇到能走深的人,但这个"没遇到"持续得够久之后,人会为了不天天惦记这份缺失,主动给自己装一套"关系本来就不用很深"的说辞来降低期待、减少不适。所以更值得问的不是"是哪一个",是**这句"不用太深也没关系"是从什么时候开始说的**——如果它是最近几年才慢慢冒出来的说法,大概率是适应性的自我保护;如果从很小就这么想,那可能真的更接近气质本身,而不是防御。[推论,未联网核查]

> [!ask|2] ❓ 问题2
> 有篇笔记讲,人不是本来就懒才不修边幅,是先累垮了才不打理自己——"放弃打理自己"更像是耗竭发出的信号,不是刻在骨子里的性格。你有没有过那种明显开始不收拾自己的阶段?那时候你是先觉得"我怎么这么懒、这么邋遢",还是能看出来这其实是自己已经很累了,在用这种方式提醒你?
>
> > [!write] ✍️ 你的回答
> >
> >
>
> > [!note]- 💬 我的看法
> > 我倾向于:当下大概率是前一种反应——先冒出来的是"我怎么这么懒"这句自我指责,"这是耗竭信号"这个解读更像是事后、甚至是看到这条笔记才补上去的认知,而不是在耗竭当下就能看透的。这不是因为不够自我觉察,是因为**能在当下就把"不修边幅"翻译成"我需要休息",本身要求相当高的元认知带宽——而元认知带宽恰恰是耗竭状态第一个被牺牲掉的资源**,这近乎一个自我遮蔽的结构:最需要这层翻译的时刻,正是最没有余力做这层翻译的时刻。所以更现实的用法可能不是"耗竭当下能不能看透",是**能不能靠一个外部的、不需要当下判断力的信号**(比如"三天没收拾东西"这种客观计数,而不是靠自己当场辨认情绪)来代替自我觉察去触发那句"该歇了"。[推论,未联网核查]

> [!write] 📔 今日日记
>
>
