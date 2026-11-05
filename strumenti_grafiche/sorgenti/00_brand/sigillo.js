/* Concept A - sigillo inciso MurettoStudio. buildSeal(svg, opt) disegna nel sistema 1000x1000 (centro 500,500). */
function buildSeal(svg, opt = {}) {
  const { el, smooth, hatch, rng, star4, arcText, f } = BR;
  const ink = opt.ink || '#153F62';
  const accent = opt.accent || ink;
  const paper = opt.paper || null;           // colore del disco (null = trasparente)
  const knock = opt.knockColor || '#000';    // per le maschere
  const defs = el('defs', {}, svg);
  const root = el('g', { transform: opt.transform || '' }, svg);
  const C = 500, RC = 326;

  const ring = opt.ring !== false;          // ring:false = solo il medaglione interno (logo orizzontale)
  if (paper) el('circle', { cx: C, cy: C, r: ring ? 469 : 353, fill: paper }, root);

  // ---------------- anelli e testo
  if (ring) {
    el('circle', { cx: C, cy: C, r: 467, fill: 'none', stroke: ink, 'stroke-width': 7 }, root);
    el('circle', { cx: C, cy: C, r: 455, fill: 'none', stroke: ink, 'stroke-width': 1.6 }, root);
  }
  el('circle', { cx: C, cy: C, r: 351, fill: 'none', stroke: ink, 'stroke-width': ring ? 1.6 : 2.6 }, root);
  for (let a = 0; a < 360; a += 3) {
    const rad = a * Math.PI / 180;
    el('circle', { cx: f(C + Math.cos(rad) * 342), cy: f(C + Math.sin(rad) * 342), r: 1.9, fill: ink }, root);
  }
  el('circle', { cx: C, cy: C, r: 333, fill: 'none', stroke: ink, 'stroke-width': 3.2 }, root);

  if (ring) {
    const tA = { fill: ink, 'font-family': 'Cinzel', 'font-weight': 600, 'font-size': 62, 'letter-spacing': '0.16em' };
    arcText(root, defs, C, C, 381, 'MURETTO STUDIO', true, tA);
    const bA = { fill: ink, 'font-family': 'Cinzel', 'font-weight': 500, 'font-size': 34, 'letter-spacing': '0.26em' };
    arcText(root, defs, C, C, 418, 'POLIGNANO A MARE · PUGLIA', false, bA);
    for (const a of [180, 0]) {
      const x = C + Math.cos(a * Math.PI / 180) * 403;
      el('path', { d: star4(x, C, 13, 3.2), fill: accent }, root);
      el('circle', { cx: f(x), cy: C - 24, r: 2.2, fill: ink }, root);
      el('circle', { cx: f(x), cy: C + 24, r: 2.2, fill: ink }, root);
    }
  }

  // ---------------- scena incisa (clip nel cerchio interno)
  const cid = BR.id('clip');
  el('circle', { cx: C, cy: C, r: RC }, el('clipPath', { id: cid }, defs));
  const scene = el('g', { 'clip-path': `url(#${cid})` }, root);
  const H = 548;                        // orizzonte
  const r = rng(opt.seed || 11);
  const h45 = hatch(defs, { spacing: 4.6, angle: 45, width: 1.15, color: ink });
  const h45d = hatch(defs, { spacing: 3.2, angle: -45, width: 1.0, color: ink });
  const hv = hatch(defs, { spacing: 4.2, angle: 90, width: 1.1, color: ink });
  const hh = hatch(defs, { spacing: 4.4, angle: 0, width: 1.05, color: ink });

  // maschera di sfondo (alone bianco attorno ai primi piani)
  const mid = BR.id('m');
  const mask = el('mask', { id: mid, maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: 1000, height: 1000 }, defs);
  el('rect', { width: 1000, height: 1000, fill: '#fff' }, mask);
  const bg = el('g', { mask: `url(#${mid})` }, scene);
  const fg = el('g', {}, scene);
  const knockPath = (d, extra = {}) => el('path', Object.assign({ d, fill: '#000', stroke: '#000', 'stroke-width': 9, 'stroke-linejoin': 'round' }, extra), mask);

  // raggi del sole
  const S = [C, H];
  for (let i = 0, a = 183; a <= 357; a += 4.5, i++) {
    const rad = a * Math.PI / 180;
    const r1 = 112, r2 = i % 2 ? 250 : 340;
    el('line', { x1: f(S[0] + Math.cos(rad) * r1), y1: f(S[1] + Math.sin(rad) * r1), x2: f(S[0] + Math.cos(rad) * r2), y2: f(S[1] + Math.sin(rad) * r2), stroke: ink, 'stroke-width': i % 2 ? 1.1 : 1.5 }, bg);
  }
  // disco del sole: linee orizzontali piu' fitte in basso
  const sunR = 92;
  const scid = BR.id('sc');
  el('path', { d: `M${C - sunR},${H}A${sunR},${sunR} 0 0,1 ${C + sunR},${H}Z` }, el('clipPath', { id: scid }, defs));
  const sg = el('g', { 'clip-path': `url(#${scid})` }, bg);
  for (let y = H - 3, s = 3.2; y > H - sunR; y -= s, s *= 1.07) {
    el('line', { x1: C - sunR, y1: f(y), x2: C + sunR, y2: f(y), stroke: accent, 'stroke-width': 1.7 }, sg);
  }
  el('path', { d: `M${C - sunR},${H}A${sunR},${sunR} 0 0,1 ${C + sunR},${H}`, fill: 'none', stroke: accent, 'stroke-width': 2.4 }, bg);

  // promontorio lontano a sinistra
  const head = [[150, H], [180, H - 9], [214, H - 17], [246, H - 19], [272, H - 13], [300, H - 6], [326, H]];
  const hd = smooth(head, false) + 'Z';
  el('path', { d: hd, fill: hh }, bg);
  el('path', { d: smooth(head, false), fill: 'none', stroke: ink, 'stroke-width': 1.3 }, bg);

  // mare: linee con interruzioni, spaziatura crescente; riflesso sotto il sole
  let y = H + 3.5, sp = 3.4, k = 0;
  while (y < 720) {
    let x = 150;
    const halfRef = Math.max(16, sunR * (1 - (y - H) / 220));
    while (x < 850) {
      const inRef = Math.abs(x - C) < halfRef;
      const len = inRef ? 4 + r() * 8 : 18 + r() * 70;
      const gap = inRef ? 3 + r() * 4 : 3 + r() * 9 * (1 + (y - H) / 60);
      el('line', { x1: f(x), y1: f(y), x2: f(Math.min(x + len, 850)), y2: f(y), stroke: inRef ? accent : ink, 'stroke-width': f(1.0 + (y - H) / 170) }, bg);
      x += len + gap;
    }
    y += sp; sp *= 1.13; k++;
  }

  // ---------------- Polignano: falesia con case bianche a destra
  const cliff = [[612, H + 6], [618, 530], [622, 508], [634, 494], [648, 488], [700, 484], [760, 481], [840, 478], [840, H + 30], [612, H + 30]];
  const cliffD = `M612,${H + 12}L616,530C618,516 622,505 632,496L646,488L840,478L840,${H + 12}Z`;
  knockPath(cliffD);
  // case
  const houses = [];
  let hx = 642;
  const rh = rng(5);
  while (hx < 840) {
    const w = 15 + rh() * 20, h = 16 + rh() * 26;
    const base = 488 - (hx - 642) * 0.05;
    houses.push({ x: hx, w, h, base });
    hx += w - 2;
  }
  // campanile
  const tower = { x: 708, w: 15, h: 74, base: 486 };
  const town = el('g', {}, fg);
  const drawBox = (bx, bw, bh, base, back) => {
    const top = base - bh;
    knockPath(`M${f(bx)},${f(base)}V${f(top)}H${f(bx + bw)}V${f(base)}Z`, { 'stroke-width': 7 });
    // lato in ombra (destra)
    el('rect', { x: f(bx + bw * 0.72), y: f(top), width: f(bw * 0.28), height: f(bh), fill: back ? h45d : h45 }, town);
    el('path', { d: `M${f(bx)},${f(base)}V${f(top)}H${f(bx + bw)}V${f(base)}`, fill: 'none', stroke: ink, 'stroke-width': 1.4 }, town);
    el('line', { x1: f(bx + bw * 0.72), y1: f(top), x2: f(bx + bw * 0.72), y2: f(base), stroke: ink, 'stroke-width': 0.9 }, town);
    el('line', { x1: f(bx - 1.2), y1: f(top + 0.6), x2: f(bx + bw + 1.2), y2: f(top + 0.6), stroke: ink, 'stroke-width': 2.2 }, town);
    if (!back && bw > 22 && rh() < 0.6) el('path', { d: `M${f(bx + 4)},${f(base)}v-7a3,3 0 0,1 6,0v7Z`, fill: ink }, town);
    // finestre
    const nw = Math.floor(bw / 9);
    for (let i = 0; i < nw; i++) {
      if (rh() < 0.45) continue;
      const wx = bx + 3 + i * 8, wy = top + 6 + rh() * Math.max(bh - 16, 1);
      if (wx + 3 > bx + bw * 0.7) continue;
      el('rect', { x: f(wx), y: f(wy), width: 2.8, height: 4.6, fill: ink }, town);
    }
  };
  // case dietro (piu' alte, sfalsate)
  for (const hs of houses) {
    if (rh() < 0.5) drawBox(hs.x + hs.w * 0.3, hs.w * 0.8, hs.h + 12 + rh() * 10, hs.base, true);
  }
  // campanile con cupoletta
  {
    const { x, w, h, base } = tower;
    const top = base - h;
    knockPath(`M${x},${base}V${top}L${x + w / 2},${top - 16}L${x + w},${top}V${base}Z`, { 'stroke-width': 7 });
    el('rect', { x: x + w * 0.7, y: top, width: w * 0.3, height: h, fill: h45 }, town);
    el('path', { d: `M${x},${base}V${top}L${x + w / 2},${top - 16}L${x + w},${top}V${base}`, fill: 'none', stroke: ink, 'stroke-width': 1.4 }, town);
    el('path', { d: `M${x + 3.5},${top + 16}v-6a4,4 0 0,1 8,0v6`, fill: ink }, town);
    el('line', { x1: x - 1.5, y1: top, x2: x + w + 1.5, y2: top, stroke: ink, 'stroke-width': 2 }, town);
  }
  for (const hs of houses) drawBox(hs.x, hs.w, hs.h, hs.base, false);

  // falesia: tratteggio verticale (rado sul fronte illuminato, fitto sotto il paese) + strati
  const cl = el('g', {}, fg);
  const ccid = BR.id('cc');
  el('path', { d: cliffD }, el('clipPath', { id: ccid }, defs));
  const cg = el('g', { 'clip-path': `url(#${ccid})` }, cl);
  for (let x = 613; x < 842;) {
    const lit = x < 640;
    const yt = 480 + r() * 6, yb = H + 14;
    let yy = yt;
    while (yy < yb) {
      const l = (lit ? 3 : 7) + r() * (lit ? 6 : 16);
      if (r() > (lit ? 0.45 : 0.18)) el('line', { x1: f(x), y1: f(yy), x2: f(x), y2: f(yy + l), stroke: ink, 'stroke-width': lit ? 0.9 : 1.05 }, cg);
      yy += l + (lit ? 5 : 2) + r() * 4;
    }
    x += lit ? 5.2 : 3.3;
  }
  // grotta marina alla base
  el('path', { d: `M676,${H + 12}C677,${H - 20} 713,${H - 24} 717,${H + 12}Z`, fill: ink }, cg);
  for (const sy of [500, 516, 531]) {
    el('path', { d: `M616,${sy + 6}C660,${sy} 700,${sy + 5} 740,${sy - 1}S810,${sy + 2} 842,${sy - 4}`, fill: 'none', stroke: ink, 'stroke-width': 1.25 }, cg);
  }
  el('path', { d: `M612,${H + 12}L616,530C618,516 622,505 632,496L646,488L840,478`, fill: 'none', stroke: ink, 'stroke-width': 1.8 }, cl);
  el('line', { x1: 606, y1: H + 12, x2: 842, y2: H + 12, stroke: ink, 'stroke-width': 1.6 }, cl);
  // riflesso della falesia nell'acqua
  for (let yy = H + 16, sp2 = 3.4; yy < H + 46; yy += sp2, sp2 *= 1.1) {
    let x = 612 + r() * 10;
    while (x < 842) {
      const len = 6 + r() * 22 * (1 - (yy - H) / 60);
      el('line', { x1: f(x), y1: f(yy), x2: f(x + len), y2: f(yy), stroke: ink, 'stroke-width': 1.1 }, fg);
      x += len + 3 + r() * 7 + (yy - H) * 0.25;
    }
  }

  // ---------------- muretto a secco in primo piano
  const wall = el('g', {}, fg);
  const ws = BR.wallStones(rng(opt.wallSeed || 21), { x0: 160, x1: 850, yBottom: 846, yTop: 682, hMin: 30, hMax: 56, wMin: 36, wMax: 112, gap: 4 });
  // sfondo scuro degli interstizi (ombra tra le pietre)
  const wallTop = [];
  for (const s of ws) { /* placeholder */ }
  const rows = {};
  for (const s of ws) (rows[s.row] = rows[s.row] || []).push(s);
  const topRow = Math.max(...Object.keys(rows).map(Number));
  // fascia d'ombra dietro le pietre: tratteggio fitto
  const wallBand = `M150,850L150,${700}` + rows[topRow].map(s => `L${f(s.cx - s.w / 2)},${f(s.cy - s.h / 2 + 2)}L${f(s.cx + s.w / 2)},${f(s.cy - s.h / 2 + 2)}`).join('') + `L850,700L850,850Z`;
  knockPath(wallBand, { 'stroke-width': 12 });
  const wmid = BR.id('wm');
  const wmask = el('mask', { id: wmid, maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: 1000, height: 1000 }, defs);
  el('rect', { width: 1000, height: 1000, fill: '#fff' }, wmask);
  const bandG = el('g', { mask: `url(#${wmid})` }, wall);
  el('path', { d: wallBand, fill: h45d }, bandG);
  el('path', { d: wallBand, fill: hatch(defs, { spacing: 4.4, angle: 20, width: 0.9, color: ink }) }, bandG);
  const rs = rng(opt.stoneSeed || 31);
  for (const s of ws) {
    const pts = BR.stone(s.cx, s.cy, s.w, s.h, rs, { j: 0.13, ex: 0.55, n: 8, rot: 0.16 });
    el('path', { d: smooth(pts, true, 0.55), fill: '#000', stroke: '#000', 'stroke-width': 3 }, wmask);
    BR.engrStone(wall, defs, pts, rs, { ink, sw: 1.7, k: 0.55, depth: Math.min(s.w, s.h) * 0.22, hatch: h45, cracks: 0.45 });
  }

  // ---------------- ramo d'ulivo che entra da sinistra
  const og = el('g', {}, fg);
  const sil = BR.olive(og, rng(opt.oliveSeed || 7), {
    p0: [150, 470], c1: [215, 392], c2: [300, 330], p1: [418, 300],
    n: 19, leafL: 74, leafRatio: 0.19, ink, sw: 1.5, stemW: 3.2, hatch: h45, hatchDense: h45d, paper: paper || undefined,
    olives: [[0.42, 1.9, 6], [0.5, 2.2, 5], [0.7, -1.3, 6]], oliveR: 9
  });
  for (const s of sil) {
    if (s.stroke) knockPath(s.d, { fill: 'none', 'stroke-width': s.stroke + 9, 'stroke-linecap': 'round' });
    else knockPath(s.d, { transform: s.transform });
  }
  return root;
}


/* Icona semplificata dello stesso marchio (leggibile a 70 px): sole, raggi, mare, muretto, rametto.
   I raggi vengono accorciati geometricamente: ognuno si ferma a distanza costante (gap) dal rametto,
   nessun moncone o tacca. Le pietre sono disposte per corsi dentro il cerchio: nessuna e' visibile per meno del 60%. */
function buildIcon(svg, opt = {}) {
  const { el, smooth, rng, f } = BR;
  const ink = opt.ink || '#153F62', accent = opt.accent || '#C8683E', paper = opt.paper || '#F4EFE5';
  const defs = el('defs', {}, svg);
  const C = 500, RC = opt.rc || 372;
  if (opt.bg) el('rect', { width: 1000, height: 1000, fill: opt.bg }, svg);
  el('circle', { cx: C, cy: C, r: RC + 58, fill: paper }, svg);
  el('circle', { cx: C, cy: C, r: RC + 46, fill: 'none', stroke: ink, 'stroke-width': 22 }, svg);
  el('circle', { cx: C, cy: C, r: RC + 16, fill: 'none', stroke: ink, 'stroke-width': 6 }, svg);
  const cid = BR.id('ic');
  el('circle', { cx: C, cy: C, r: RC }, el('clipPath', { id: cid }, defs));
  const g = el('g', { 'clip-path': `url(#${cid})` }, svg);
  const H = 548, sunR = 128;

  // ---------- geometria del rametto (serve prima, per accorciare i raggi)
  const p0 = [112, 484], c1 = [196, 384], c2 = [268, 318], p1 = [372, 284];
  const stemW = 12;
  const leafSpec = [[0.17, -1, 100], [0.28, 1, 104], [0.45, -1, 94], [0.56, 1, 90], [0.73, -1, 80], [0.82, 1, 72]];
  const leaves = leafSpec.map(([t, side, L]) => {
    const P = BR.bez(p0, c1, c2, p1, t), T = BR.bezT(p0, c1, c2, p1, t);
    return { P, a: Math.atan2(T[1], T[0]) + side * 0.62, L, bend: side * 0.25 };
  });
  const T1 = BR.bezT(p0, c1, c2, p1, 1);
  // foglia terminale: parte un po' dentro la punta del gambo, cosi' gambo e foglia sono un unico segno
  const tipA = Math.atan2(T1[1], T1[0]);
  leaves.push({ P: [p1[0] - Math.cos(tipA) * 6, p1[1] - Math.sin(tipA) * 6], a: tipA, L: 80, bend: 0 });
  const LR = 0.23;
  const olives = (opt.olives || []).map(([t, side, d]) => {
    const P = BR.bez(p0, c1, c2, p1, t), T = BR.bezT(p0, c1, c2, p1, t);
    const a = Math.atan2(T[1], T[0]) + side * 1.75;
    return { P, a, q: [P[0] + Math.cos(a) * d, P[1] + Math.sin(a) * d], rx: 10.5, ry: 13.5 };
  });
  // poligoni globali per il calcolo delle distanze
  const polys = [];
  const leafPoly = lf => {
    const W = lf.L * LR, b = lf.bend * W, L = lf.L, pts = [];
    const A = [[0, 0], [L * 0.28, -W * 1.05 + b], [L * 0.72, -W * 0.85 + b], [L, b * 0.6]];
    const B = [[L, b * 0.6], [L * 0.72, W * 0.85 + b], [L * 0.28, W * 1.05 + b], [0, 0]];
    for (let i = 0; i <= 24; i++) pts.push(BR.bez(...A, i / 24));
    for (let i = 1; i < 24; i++) pts.push(BR.bez(...B, i / 24));
    const ca = Math.cos(lf.a), sa = Math.sin(lf.a);
    return pts.map(([x, y]) => [lf.P[0] + x * ca - y * sa, lf.P[1] + x * sa + y * ca]);
  };
  for (const lf of leaves) polys.push(leafPoly(lf));
  for (const o of olives) {
    const pts = [], ang = o.a - Math.PI / 2;
    const cx = o.q[0] + Math.cos(o.a) * o.ry, cy = o.q[1] + Math.sin(o.a) * o.ry;
    o.c = [cx, cy];
    for (let i = 0; i < 32; i++) {
      const t = i / 32 * Math.PI * 2, x = Math.cos(t) * o.rx, y = Math.sin(t) * o.ry;
      pts.push([cx + x * Math.cos(ang) - y * Math.sin(ang), cy + x * Math.sin(ang) + y * Math.cos(ang)]);
    }
    polys.push(pts);
  }
  const stemPts = [];
  for (let i = 0; i <= 60; i++) stemPts.push(BR.bez(p0, c1, c2, p1, i / 60));
  const segD = (p, a, b) => {
    const vx = b[0] - a[0], vy = b[1] - a[1];
    const t = Math.max(0, Math.min(1, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / (vx * vx + vy * vy)));
    return Math.hypot(p[0] - a[0] - vx * t, p[1] - a[1] - vy * t);
  };
  const inPoly = (p, pts) => {
    let c = false;
    for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
      const [xi, yi] = pts[i], [xj, yj] = pts[j];
      if ((yi > p[1]) !== (yj > p[1]) && p[0] < (xj - xi) * (p[1] - yi) / (yj - yi) + xi) c = !c;
    }
    return c;
  };
  const branchDist = p => {
    let d = 1e9;
    for (let i = 1; i < stemPts.length; i++) d = Math.min(d, segD(p, stemPts[i - 1], stemPts[i]) - stemW / 2);
    for (const pts of polys) {
      if (inPoly(p, pts)) return 0;
      for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) d = Math.min(d, segD(p, pts[j], pts[i]));
    }
    return d;
  };
  const hasBranch = opt.olive !== false;

  // ---------- raggi: alternati lunghi/corti, estremi arrotondati, fermati a distanza costante dal rametto e dall'anello
  const gap = 12, rIn = sunR + 28;
  for (let i = 0, a = 189; a <= 351.01; a += 10.125, i++) {
    const rad = a * Math.PI / 180, ca = Math.cos(rad), sa = Math.sin(rad);
    const sw = i % 2 ? 10 : 13;
    let rEnd = i % 2 ? 300 : 460;
    for (let s = rIn; s <= rEnd; s += 1) {            // raggi lunghi: si fermano a 16 px dal bordo della scena
      if (Math.hypot(ca * s, H - C + sa * s) > RC - 16 - sw / 2) { rEnd = s - 1; break; }
    }
    if (hasBranch) {
      for (let s = rIn; s <= rEnd; s += 0.5) {
        if (branchDist([C + ca * s, H + sa * s]) < gap + sw / 2) { rEnd = s - 0.5; break; }
      }
    }
    if (rEnd - rIn < 46) continue;   // niente monconi
    el('line', { x1: f(C + ca * rIn), y1: f(H + sa * rIn), x2: f(C + ca * rEnd), y2: f(H + sa * rEnd), stroke: ink, 'stroke-width': sw, 'stroke-linecap': 'round' }, g);
  }

  // ---------- sole pieno con due tagli orizzontali
  el('path', { d: `M${C - sunR},${H}A${sunR},${sunR} 0 0,1 ${C + sunR},${H}Z`, fill: accent }, g);
  for (const [dy, w] of [[-28, 11], [-56, 9]]) el('rect', { x: C - sunR, y: H + dy - w / 2, width: sunR * 2, height: w, fill: paper }, g);

  // ---------- mare: linee spesse con interruzioni, riflesso in terracotta sotto il sole
  const sea = [[H + 22, [[150, 340], [370, 455], [545, 630], [660, 850]]], [H + 50, [[150, 290], [320, 470], [530, 700], [730, 850]]], [H + 80, [[150, 380], [415, 585], [620, 850]]]];
  for (const [y, segs] of sea) for (let [x1, x2] of segs) {
    const refl = x1 > 360 && x2 < 640;
    const hw = Math.sqrt(Math.max(0, (RC - 16) ** 2 - (y - C) ** 2));   // stessi 16 px dal bordo dei raggi
    x1 = Math.max(x1, C - hw + 6); x2 = Math.min(x2, C + hw - 6);
    el('line', { x1: f(x1), y1: y, x2: f(x2), y2: y, stroke: refl ? accent : ink, 'stroke-width': 12, 'stroke-linecap': 'round' }, g);
  }

  // ---------- muretto: corsi disposti dentro il cerchio, pietre piene in inchiostro separate da fughe chiare
  const rw = rng(opt.wallSeed || 9), rs = rng(opt.stoneSeed || 23);
  const jg = 13;                                    // fuga tra le pietre
  const courses = opt.courses || [[674, 744], [744, 814], [814, 884]];
  const joints = [];
  const stones = [];
  const visFrac = pts => {                          // frazione visibile dentro il cerchio della scena
    const b = BR.bbox(pts); let tot = 0, vis = 0;
    for (let x = b.x; x <= b.x + b.w; x += 3) for (let y = b.y; y <= b.y + b.h; y += 3) {
      if (!inPoly([x, y], pts)) continue;
      tot++; if (Math.hypot(x - C, y - C) < RC) vis++;
    }
    return tot ? vis / tot : 1;
  };
  courses.forEach(([yt, yb], row) => {
    const hRow = yb - yt, last = row === courses.length - 1;
    // corda del cerchio misurata dove il cerchio stringe di piu' dentro il corso
    const yRef = last ? yt + hRow * 0.38 : yt + hRow * 0.62;
    const half = Math.sqrt(RC * RC - (yRef - C) ** 2);
    const x0 = C - half, x1 = C + half;
    for (let tries = 0; tries < 600; tries++) {
      const span = x1 - x0;
      const n = last ? 3 + Math.floor(rw() * 2) : Math.max(4, Math.round(span / (100 + rw() * 22)));
      let ws = [];
      for (let i = 0; i < n; i++) ws.push(rw() < 0.16 && i > 0 && i < n - 1 ? 0.5 : 0.75 + rw() * 0.7);
      const ov = 0.12;                                // gli estremi sporgono oltre la corda solo del 12%
      const sum = ws.reduce((a, b) => a + b, 0) - ov * (ws[0] + ws[n - 1]);
      const k = span / sum;
      ws = ws.map(w => w * k);
      let x = x0 - ws[0] * ov;
      const cand = [];
      for (const w of ws) { cand.push([x, x + w]); x += w; }
      const inner = cand.slice(0, -1).map(c => c[1]);  // giunti sfalsati rispetto al corso sopra
      const prev = joints[row - 1] || [];
      if (inner.some(j => prev.some(q => Math.abs(q - j) < 30))) continue;
      if (ws.some(w => w < 40)) continue;
      const pts = cand.map(([a, b]) => {
        const w = b - a - jg, hh = (hRow - jg) * (0.9 + rs() * 0.1);
        return BR.stone((a + b) / 2, yt + hRow / 2 + (rs() - 0.5) * 3, w, hh, rs, { j: 0.1, ex: 0.62, n: 9, rot: 0.08 });
      });
      if (pts.some(p => visFrac(p) < 0.6)) continue;
      joints[row] = inner;
      stones.push(...pts);
      break;
    }
  });
  window.__iconStoneVis = stones.map(p => +visFrac(p).toFixed(2));
  // le pietre di bordo seguono il cerchio (come conci tagliati su misura) invece di essere troncate di netto
  const tmp = el('path', {}, svg);
  for (const pts of stones) {
    tmp.setAttribute('d', smooth(pts, true, 0.5));
    const Ltot = tmp.getTotalLength(), N = 160;
    let poly = [];
    for (let i = 0; i < N; i++) {
      const q = tmp.getPointAtLength(Ltot * i / N);
      const dx = q.x - C, dy = q.y - C, d = Math.hypot(dx, dy), lim = RC;
      poly.push(d > lim ? [C + dx / d * lim, C + dy / d * lim] : [q.x, q.y]);
    }
    for (let it = 0; it < 3; it++) poly = poly.map((p, i) => {   // arrotonda gli spigoli creati dal taglio
      const a = poly[(i - 1 + N) % N], b = poly[(i + 1) % N];
      return [(a[0] + 2 * p[0] + b[0]) / 4, (a[1] + 2 * p[1] + b[1]) / 4];
    });
    el('path', { d: 'M' + poly.map(p => f(p[0]) + ',' + f(p[1])).join('L') + 'Z', fill: ink }, g);
  }
  tmp.remove();

  // ---------- rametto d'ulivo pieno, unico segno senza aloni (entra dal bordo, tagliato dal cerchio)
  if (hasBranch) {
    const og = el('g', { 'clip-path': `url(#${cid})` }, svg);
    const col = opt.leaf || ink;
    el('path', { d: `M${p0}C${c1} ${c2} ${p1}`, fill: 'none', stroke: col, 'stroke-width': stemW, 'stroke-linecap': 'round' }, og);
    for (const o of olives) {
      el('path', { d: `M${f(o.P[0])},${f(o.P[1])}L${f(o.q[0])},${f(o.q[1])}`, stroke: col, 'stroke-width': 5, 'stroke-linecap': 'round' }, og);
      el('ellipse', { cx: f(o.c[0]), cy: f(o.c[1]), rx: o.rx, ry: o.ry, transform: `rotate(${f(o.a * 180 / Math.PI - 90)} ${f(o.c[0])} ${f(o.c[1])})`, fill: col }, og);
    }
    for (const lf of leaves) {
      const tr = `translate(${f(lf.P[0])},${f(lf.P[1])}) rotate(${f(lf.a * 180 / Math.PI)})`;
      el('path', { d: BR.leafPath(lf.L, lf.L * LR, lf.bend), transform: tr, fill: col }, og);
    }
  }
}
