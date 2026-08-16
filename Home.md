---
cssclasses: workbench
generated: 2026-08-16
painting-url: https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Hilma_af_Klint_-_The_Ten_Largest_No._7_-_Adulthood_-_1907.jpg/960px-Hilma_af_Klint_-_The_Ten_Largest_No._7_-_Adulthood_-_1907.jpg
painting-title: 希尔玛·阿夫·克林特《十件最大的作品·第七号:成年》(1907)
painting-intro: 瑞典画家阿夫·克林特在康定斯基等人公认的"抽象艺术诞生"之前几年,就已经画出这类完全非具象的巨幅作品;她生前几乎从不公开展出,遗嘱要求死后二十年内不得示人,直到二十世纪末才被追认为抽象艺术真正的先驱者之一。
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

// 页面纸感渐变:完全独立于画作/网络生成(按当天日期做种子),避免等画作异步加载完取色导致背景先出现兜底色再跳变
let seed = Math.floor(Date.now() / 86400000);
const rand = () => {
  seed = (seed + 0x6D2B79F5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const pastel = (h) => `hsl(${Math.round((h % 360 + 360) % 360)}, ${Math.round(60 + rand() * 35)}%, ${Math.round(89 + rand() * 5)}%)`;
// 三色按三角配色(约 120° 间隔)取,避免第二三色挤在同一段弧上漂移出一坨同色系
const triadGradient = (h0) => {
  const stops = [pastel(h0), pastel(h0 + 100 + rand() * 40), pastel(h0 + 220 + rand() * 40)];
  return `linear-gradient(135deg, ${stops[0]} 0%, ${stops[1]} ${Math.round(40 + rand() * 20)}%, ${stops[2]} 100%)`;
};
root?.style.setProperty("--wb-page-gradient", triadGradient(rand() * 360));

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

// 取画作主色调写进 --wb-accent:按色相分 12 桶投票取票数最多的桶均值,而非平均色(平均会让所有颜色互相抵消成灰)
if (p["painting-url"]) {
  const img = new Image();
  img.crossOrigin = "anonymous";
  img.onload = () => {
    try {
      const c = document.createElement("canvas");
      c.width = 32; c.height = 32;
      const ctx = c.getContext("2d");
      ctx.drawImage(img, 0, 0, 32, 32);
      const d = ctx.getImageData(0, 0, 32, 32).data;
      const bins = Array.from({ length: 12 }, () => ({ r: 0, g: 0, b: 0, n: 0 }));
      for (let i = 0; i < d.length; i += 4) {
        const r = d[i], g = d[i + 1], b = d[i + 2];
        const mx = Math.max(r, g, b), mn = Math.min(r, g, b);
        if (mx - mn < 24) continue; // 近灰的像素没有可用色相,不参与投票
        const h = mx === r ? ((g - b) / (mx - mn) + 6) % 6 : mx === g ? (b - r) / (mx - mn) + 2 : (r - g) / (mx - mn) + 4;
        const bin = bins[Math.floor(h * 2) % 12]; // h∈[0,6) → 12 桶,每桶 30°
        bin.r += r; bin.g += g; bin.b += b; bin.n++;
      }
      const top = bins.reduce((a, x) => (x.n > a.n ? x : a));
      if (top.n) {
        const R = Math.round(top.r / top.n), G = Math.round(top.g / top.n), B = Math.round(top.b / top.n);
        root?.style.setProperty("--wb-accent", `rgb(${R}, ${G}, ${B})`);
      } else {
        console.warn("[工作台] 取色失败:整幅画在采样点都太接近灰色,没有可投票的色相,沿用兜底色 --wb-accent");
      }
    } catch (e) {
      console.warn("[工作台] 画作取色失败,沿用兜底色 --wb-accent:", e);
    }
  };
  img.onerror = (e) => {
    console.warn("[工作台] 画作图片加载失败,取色跳过,沿用兜底色 --wb-accent。图片地址:", p["painting-url"], e);
  };
  img.src = p["painting-url"];
}

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
const renderReunion = async (container, forceNew = false) => {
  container.innerHTML = "";
  const arr = dv.pages('"Notes"').array();
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
const reunionEl = dv.container.createEl("div", { cls: "wb-reunion" });
renderReunion(reunionEl);

// 随机重逢卡片高度跟着画作横幅走:画作图片异步加载会撑高卡片,用 ResizeObserver 而非一次性测量,保证加载完成后重新同步
const syncReunionHeight = () => {
  const painting = document.querySelector(".workbench .wb-daily-painting");
  if (!painting) return;
  if (window.innerWidth <= 520) {
    reunionEl.style.maxHeight = "";
    return;
  }
  const h = painting.getBoundingClientRect().height;
  if (h > 0) reunionEl.style.maxHeight = h + "px";
};

// 标题对齐完全交给 CSS(两边 margin-bottom 对齐),这里只需要高度同步
const syncLayout = syncReunionHeight;
// 两个 dataviewjs 块之间不保证渲染顺序,轮询等真正找到画作卡片 DOM 后再挂 ResizeObserver
const setupLayoutSync = (triesLeft = 34) => {
  const paintingEl = document.querySelector(".workbench .wb-daily-painting");
  if (!paintingEl) {
    if (triesLeft > 0) setTimeout(() => setupLayoutSync(triesLeft - 1), 150);
    else console.warn("[工作台] 等了 5 秒还是没找到画作卡片的 DOM,放弃高度同步——可能画作代码块本身报错了");
    return;
  }
  syncLayout();
  // dv.component.register 把 disconnect/removeEventListener 绑定到本次渲染生命周期,重渲染时自动清理,避免新旧观察者互相打架
  if (window.ResizeObserver) {
    const ro = new ResizeObserver(syncLayout);
    ro.observe(paintingEl);
    dv.component.register(() => ro.disconnect());
  }
  window.addEventListener("resize", syncLayout);
  dv.component.register(() => window.removeEventListener("resize", syncLayout));
};
setupLayoutSync();
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

const notes = dv.pages('"Notes"'), concepts = dv.pages('"Concepts"');
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
addAction("📔", "写日记", "wb-newdiary", newDiary);
```

> [!clash] 🥊 碰撞 · 问题1 回顾
> *(08-15 那期的问题)你有没有什么事,一直很努力地想去改变、去掌控,但静下心来想想,那件事可能根本就不是你能控制的?你是最近才想明白这一点,还是现在也还没想通?*
>
> > [!write] 🗣️ 你的回答
> > 我目前还没觉得是什么我不能控制的,可能还是身外之物不能控制吧,我能引导自己的一切变化
>
> > [!note] 💭 我的看法(上期)
> > 我倾向于觉得大部分人第一反应会想到别人的看法、别人的态度这类典型的不可控项,但更难认的往往是"结果"——一件事做没做好、别人会不会喜欢,这些经常被当成"只要我够努力就能保证"的东西,其实决定权早就不完全在自己手上。如果你能具体说出一件正在使劲较劲的事,那份"我是不是在拿捏一个拿捏不了的东西"的答案,大概率比想象中更清楚。[推论]
>
> **碰撞:** 你没接住我上期那个具体邀请——没说出哪件事正在使劲较劲,而是给了一个几乎不会出错的抽象答案:身外之物不可控,自己能引导一切内在变化。这句话听着像认领了主体性,但拆开看藏着 [[控制二分法|控制二分法]] 延伸区那条"控制三分法"一样的漏洞:**能引导变化的方向**和**变化最终走到哪**是两件事,前者你确实说了算,后者不一定。比如你正在推进的存款计划、BJJ、语言这些,你能控制的是练不练、投不投入,控制不了的是多久能到理想水平、身体会不会受伤、结果会不会如愿——这些结果性的东西,现在这句"我能引导自己的一切变化"把它们悄悄并了进去,变成了一句谁都不会反对的正确废话。真正值得盯的不是"有没有不能控制的",而是你把"我在努力"和"我能保证结果"这两件事分不分得开——目前这个回答还看不出来。

> [!draw] 🎴 今日抽卡 · 偶像谱系的优点与靠近路径——峰不二子、灰原哀、菲的四条共同内核
> [[偶像谱系的优点与靠近路径-峰不二子灰原哀菲的四条共同内核|偶像谱系的优点与靠近路径]] —— 对话发生于 2026-08-15/16。
>
> 1. 峰不二子、灰原哀、菲三个人抽掉具体人设后,笔记归纳出四条共同内核——硬本事打底、痛苦自己扛不表演脆弱、清醒自主不为被喜欢扭曲自己、联结是主动选的——你还记得住这四条吗?
> 2. 笔记说"情绪自持"这条目前是空白,给的练习是下次感觉到"怕被评价"的冲动时,不解释、不追加道歉,只说事实然后沉默站住——你有试过这个动作吗?
> 3. 笔记最后问,下次再聊到"需要老公给经济支持"的时候,能不能先问自己一句:这是你想要的相处方式,还是因为现在没有别的办法?

> [!seed] 🌱 今日延伸 · 相信自己能学会,比起点本身更影响练不练得下去
> 关于 [[天赋|天赋]]:心理学家 Albert Bandura 提出的自我效能感(self-efficacy,1977)补了一层这里没处理的变量——一个人相信不相信自己能通过练习获得某项能力,这份信念本身会影响他愿不愿意开始、能不能扛过前期的挫败感,这个作用独立于"起点倾向"高低存在。[事实,未联网核查]
>
> 换句话说,即便两个人天赋起点相同,自我效能感更高的那个更可能真把倾向滚成能力,自我效能感低的更容易半途而废——这给"愿不愿意坚持练习本身也带遗传倾向"这条追问补了一个不完全由基因决定的变量:对"我能学会"这件事的主观信念,是能通过小的成功经验后天提高的,不像起点倾向那样固定。这条已经同步写进 [[天赋|天赋]] 概念页的延伸区。[推论,未联网核查]

> [!ask] ❓ 问题1
> 你有没有一段关系,一开始就是因为你会做某件事、能帮上忙才认识起来的?如果哪天你什么忙都帮不上了,你觉得对方还会不会像现在这样对你?
>
> > [!write] ✍️ 你的回答
> >
> >
>
> > [!note]- 💬 我的看法
> > 我倾向于觉得大部分这类关系里,答案连你自己心里都有数,只是平时不会去戳这一下——真正让人意外的往往不是"对方会不会走",而是发现自己也在靠这份"有用"撑着关系,一旦停止提供,自己反而先心虚。[推论]

> [!ask] ❓ 问题2
> 你有没有试过在搞砸事情、心里很慌的时候,主动跟自己说一句"这真的没什么大不了的"?说完之后,你是真的觉得没那么慌了,还是感觉自己只是在找个理由蒙混过去,没真的去处理问题?
>
> > [!write] ✍️ 你的回答
> >
> >
>
> > [!note]- 💬 我的看法
> > 我倾向于觉得这两种效果当下不容易分清——真正安抚人心的化解和给自己找台阶下,说出来的话经常一模一样,区别只在于说完之后有没有真的回去做点什么。如果说完就翻篇、什么都没再动,大概率是后者。[推论]

> [!write] 📔 今日日记
>
>
