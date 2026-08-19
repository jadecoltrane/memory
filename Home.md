---
cssclasses: workbench
generated: 2026-08-19
painting-url: https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Hiroshige%2C_Sudden_shower_over_Shin-%C5%8Chashi_bridge_and_Atake%2C_1857.jpg/1280px-Hiroshige%2C_Sudden_shower_over_Shin-%C5%8Chashi_bridge_and_Atake%2C_1857.jpg
painting-title: 歌川广重《大桥安宅骤雨》(浮世绘,1857)
painting-intro: 歌川广重用极简的雨线刻版和大胆的构图切割,把桥上行人骤雨中疾行的一瞬间定格下来;这幅画后来被梵高临摹,是十九世纪欧洲"日本主义"浪潮里最具代表性的一张浮世绘。
---

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
> *别扭还没消,对方一服软你就笑场揭过去——那一刻是真的不生气了,还是怕僵着更难受,先把场面圆过去?*
>
> > [!write] 🗣️ 你的回答
> > 有啊有啊,就是跟你讲的,前段时间我跟那个同事还有在之前的,我跟我的高中同学都是有这种情况,因为我很讨厌跟别人处于一种尴尬的氛围,所以我会主动结尾,但其实他们已经伤害到我的边界了,但可能那个时候我就没有考虑到自己的边界,先去处理了这种尴尬的情绪
>
> > [!note] 💭 我的看法(上期)
> > 我倾向于觉得多数时候是后者——顺着台阶下来,松掉的是"僵着"这件事带来的紧绷,不是原来那件事本身有没有道理。气有没有真的消,和愿不愿意继续演下去,当下常常被当成同一件事一并处理掉了。[观点]
>
> **碰撞:** 这次回答几乎是把我的判断反过来印证了一遍,还往前多走了一步——你不只是承认"先圆场",还直接说出了代价:"没有考虑到自己的边界"。这句话比我说的更狠,我说的是"气有没有消不重要",你说的是"我连自己的边界都先放一边了"。但这已经是这几天第三、四次记到同一件事(同事、高中同学,加上前几天已经确认过的"台阶"和"怕气氛僵掉"),说明识别这一步你早就过了关——真正卡住的不是"看不出这是我的边界",是当场那几秒没有一个替代动作可用,只会用"填空气"去顶。继续在这道题上确认同一个结论,边际价值已经不大;下次更有用的问题应该是具体某一次事后回想,那三秒里你的身体在想干什么,而不是再问一次"是不是这样"。

> [!clash] 🥊 碰撞 · 问题2 回顾
> *有没有哪段关系当初是因为一件具体事凑到一起的,后来那个理由早就用不上了,关系却一直停在"当初为什么认识"那个层面?*
>
> > [!write] 🗣️ 你的回答
> > 有的人是没有机会吧,因为大家接触面都很少,你如果很唐突的问别人的生活细节或者去打听别人的隐私就显得不是很礼貌,所以代价一般边界感还是很强,还有一种可能就是我本身主动性不够,一般也是等到别人来找我,我很少主动去找别人
>
> > [!note] 💭 我的看法(上期)
> > 我倾向于觉得多半是后者——不是没机会,是往深里走这一步本身需要主动露出一些不那么体面、没法对谁都说的东西,而这一步太容易被"反正认识了这么久早晚会熟"这种想法一直往后拖,拖到关系本身先淡了。[推论]
>
> **碰撞:** 你把两条原因并排放着,它们确实不是一个量级——第一条("问隐私不礼貌")几乎能套在任何人身上,第二条("等别人来找我")才是真正咬到你自己的那句;你自己也先说前者、后者才是"还有一种可能",这个顺序就暴露了哪条更容易说出口。**但停在这一步就不够了**:把"主动性不够"接到"等信号型"上,听着像挖到了根因,其实只是给同一个行为换了个已经在你画像里的标签。库外的研究给的是另一套解释,而且跟两边的说法都对不上——①**你不是主动性不够,是输入的数错了**:社会心理学里有个反复重复出来的偏差叫 liking gap(Boothby 等,2018,*Psychological Science*),人系统性地低估对方有多喜欢自己,大一新生宿舍里这个低估持续了大半个学年才消;Liu 等 2023 年发在 *JPSP* 的 "The Surprise of Reaching Out" 更精确:人普遍低估别人收到主动联系时的高兴程度,而且**越是"唐突"、两人越疏远,低估得越厉害**。也就是说你判断"现在去找显得突兀"的那类场合,恰恰是你估得最不准的场合。②**更要紧的是第一条指错了动作**:你和我上期都默认"往深走 = 去打听对方的私事",所以"不礼貌"才成立。但社会渗透理论(Altman & Taylor, 1973)和 Aron 1997 那个 45 分钟造出亲密感的实验说的都是,深度靠的是**自我披露的相互升级**——先讲自己的,对方在互惠规范下才跟着下一层。真正的第一步是"我先说我的",这一步压根不涉及礼貌问题。你那条礼仪顾虑是真的,只是它挡住的是一个本来就不该做的动作。③**"接触面窄"也不该被一笔带过**:Hall 2019(*JSPR*)统计的门槛是约 50 小时到普通朋友、90 小时到朋友、200 小时以上才到密友,而且一起玩、闲扯、吃饭的时间算数,**一起工作的时间基本不算**——小时数是真变量,不是借口。所以这两条不是"一条是遮羞布、一条是真相",更像是一条被我们俩一起误解了动作,一条被你误估了数值。[事实:三项研究已联网核查;推论:与你这两条的对应关系是我的判断]

> [!draw] 🎴 今日抽卡 · 微小倾向乘以环境和时间,才长成后来的你
> [[Notes/个人/动机与改变/天赋不是命运-倾向环境练习共同塑造人|天赋不是命运]] —— 源于 2026-07-31 一场 ChatGPT 对话。
>
> 1. 笔记里用一个公式代替了"天赋决定成就"这句话——除了"倾向"和"环境",公式里还有哪两个变量?
> 2. 笔记区分了"违背自己的改变"和"扩展自己的改变",举的是哪种性格的人、去练哪件事作为例子?
> 3. 笔记最后留了一个没答完的问题:如果人总是在环境里被塑造出来,"做自己"到底是在守住什么——当时给出了哪几个候选答案?

> [!seed] 🌱 今日延伸 · 知道是"台阶",不等于当场能不接
> 关于 [[间歇性强化|间歇性强化]]:今天问题1 的回答又印证了一次"看得出这是台阶,还是会接"——这背后有行为科学上的解释。双加工理论(dual-process theory,如 Kahneman 的系统一/系统二)认为"知道"和"自动反应"分属两套系统:想清楚"这是间歇性强化在拿捏我"是系统二的工作,不会自动关掉系统一那个已经练熟的"填空气"反射,两者之间没有直接连线。习惯研究者 Wendy Wood 的工作进一步指出,自动化行为要改,靠的不是加强意志力(系统二资源在情绪现场很容易耗竭),而是**换掉触发情境、或预先备好一个新的默认动作**,反复练到新动作本身变自动为止。这条已经同步写进 [[间歇性强化|间歇性强化]] 概念页的延伸区。[事实(双加工理论、习惯研究属实),推论(与本篇的对应)未联网核查]

> [!ask|1] ❓ 问题1
> 你现在练得更多的是"消极主体性"——就是说不、守住底线、不被别人拿捏这一类。你有没有想过,等哪天这块你已经练得很熟了,你会靠什么信号发现"这不够了,我该往前一步,认真去想我到底要什么了"?会是什么让你意识到,光是不被冒犯已经不够?
>
> > [!write] ✍️ 你的回答
> >
> >
>
> > [!note]- 💬 我的看法
> > 我倾向于觉得那个信号不会是"感觉准备好了",而是开始对"我只是没被欺负"这件事本身感到无聊,或者开始羡慕起某个具体在往前走的人。消极主体性最大的风险不是切换得太晚,是把"我没被冒犯"长期当成"我过得还不错"的证据,一直赖在这一步不走——因为守住边界比想清楚自己要什么容易太多了。[观点]

> [!ask|2] ❓ 问题2
> 你之前说过,把刷手机、打游戏的频率降下来之后,大概一周就适应了,感觉自己没那么容易被刺激到了。但那个"感觉"当时没什么具体标准,就是个整体印象。如果现在要你更认真地确认这件事是不是真的变了,你会盯着哪个具体的东西来看?比如说,面对同一件以前会让你上头的事,你的反应会有什么不一样?
>
> > [!write] ✍️ 你的回答
> >
> >
>
> > [!note]- 💬 我的看法
> > 我倾向于觉得光问"我现在爽不爽"靠不住,真正该看的是控制感:面对同一个以前会让你刷到停不下来的东西(同一个游戏、同一类短视频),现在能不能主动关掉,还是照样上头。阈值真的降低了,应该是先松动失控感,而不是爽感变淡——爽感变淡也可能只是因为你已经开始有意回避这类东西,不代表阈值真的变了。[推论]

> [!write] 📔 今日日记
>
>
