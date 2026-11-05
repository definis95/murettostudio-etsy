/* MurettoStudio - libreria di disegno vettoriale (SVG generato con seed fisso: stesso risultato a ogni render). */
const BR = (() => {
  const NS = 'http://www.w3.org/2000/svg';
  const f = n => Math.round(n * 100) / 100;
  let uid = 0;
  const id = p => `${p}${++uid}`;

  function rng(seed) {
    let s = seed >>> 0;
    return () => {
      s = (s + 0x6D2B79F5) >>> 0;
      let t = s;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function el(tag, attrs = {}, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) if (attrs[k] !== undefined && attrs[k] !== null) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  /* Catmull-Rom -> Bezier cubiche. pts = [[x,y],...] */
  function smooth(pts, closed = true, k = 1) {
    const n = pts.length;
    let d = `M${f(pts[0][0])},${f(pts[0][1])}`;
    const segs = closed ? n : n - 1;
    for (let i = 0; i < segs; i++) {
      const p0 = closed ? pts[(i - 1 + n) % n] : pts[Math.max(i - 1, 0)];
      const p1 = pts[i];
      const p2 = closed ? pts[(i + 1) % n] : pts[i + 1];
      const p3 = closed ? pts[(i + 2) % n] : pts[Math.min(i + 2, n - 1)];
      const c1 = [p1[0] + (p2[0] - p0[0]) / 6 * k, p1[1] + (p2[1] - p0[1]) / 6 * k];
      const c2 = [p2[0] - (p3[0] - p1[0]) / 6 * k, p2[1] - (p3[1] - p1[1]) / 6 * k];
      d += `C${f(c1[0])},${f(c1[1])} ${f(c2[0])},${f(c2[1])} ${f(p2[0])},${f(p2[1])}`;
    }
    return d + (closed ? 'Z' : '');
  }

  function bbox(pts) {
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (const [x, y] of pts) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
    return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
  }

  /* pietra calcarea: superellisse irregolare (angoli arrotondati, facce un po' storte) */
  function stone(cx, cy, w, h, r, o = {}) {
    const n = o.n || 11, ex = o.ex ?? 0.38, j = o.j ?? 0.06, rotMax = o.rot ?? 0.10;
    const rot = (r() - 0.5) * rotMax;
    const pts = [];
    const a0 = r() * 0.6;
    for (let i = 0; i < n; i++) {
      const a = a0 + (i / n) * Math.PI * 2 + (r() - 0.5) * 0.22;
      const c = Math.cos(a), s = Math.sin(a);
      const x = Math.sign(c) * Math.pow(Math.abs(c), ex) * w / 2 * (1 + (r() - 0.5) * 2 * j);
      const y = Math.sign(s) * Math.pow(Math.abs(s), ex) * h / 2 * (1 + (r() - 0.5) * 2 * j);
      pts.push([cx + x * Math.cos(rot) - y * Math.sin(rot), cy + x * Math.sin(rot) + y * Math.cos(rot)]);
    }
    return pts;
  }

  /* muro a secco: corsi orizzontali di pietre di misura variabile */
  function wallStones(r, o) {
    const { x0, x1, yBottom, yTop, hMin, hMax, wMin, wMax, gap } = o;
    const hVar = o.hVar ?? 0.2, small = o.small ?? 0.18;
    const out = [];
    let y = yBottom;
    let row = 0;
    while (y > yTop) {
      const h = hMin + r() * (hMax - hMin);
      let x = x0 - r() * wMax * 0.7;
      while (x < x1) {
        let w = wMin + r() * (wMax - wMin);
        if (r() < small) w *= 0.55; // zeppe piccole tra i blocchi
        const hh = h * (1 - hVar + r() * hVar);
        out.push({ cx: x + w / 2, cy: y - h / 2 + (r() - 0.5) * h * 0.12, w: Math.max(w - gap, 6), h: hh - gap, row });
        x += w;
      }
      y -= h;
      row++;
    }
    return out;
  }

  function shift(pts, dx, dy) { return pts.map(([x, y]) => [x + dx, y + dy]); }

  function hatch(defs, o) {
    const pid = id('h');
    const s = o.spacing || 6;
    const p = el('pattern', { id: pid, patternUnits: 'userSpaceOnUse', width: s, height: s, patternTransform: `rotate(${o.angle ?? 45})` }, defs);
    el('line', { x1: -1, y1: s / 2, x2: s + 1, y2: s / 2, stroke: o.color, 'stroke-width': o.width || 1 }, p);
    return `url(#${pid})`;
  }

  /* crescente d'ombra: pietra meno pietra traslata, riempito con fill */
  function crescent(g, defs, pts, dx, dy, fill, k = 1) {
    const cid = id('c');
    const cp = el('clipPath', { id: cid }, defs);
    el('path', { d: smooth(pts, true, k) }, cp);
    const b = bbox(pts);
    el('path', {
      d: `M${f(b.x - 30)},${f(b.y - 30)}h${f(b.w + 60)}v${f(b.h + 60)}h${f(-b.w - 60)}Z` + smooth(shift(pts, dx, dy), true, k),
      'fill-rule': 'evenodd', fill, 'clip-path': `url(#${cid})`
    }, g);
  }

  /* pietra a incisione: contorno + tratteggio sul lato in ombra + pori e incrinature */
  function engrStone(g, defs, pts, r, o) {
    const sw = o.sw || 1.6, k = o.k ?? 1;
    const d = smooth(pts, true, k);
    if (o.paper) el('path', { d, fill: o.paper }, g);
    crescent(g, defs, pts, -o.depth, -o.depth * 0.9, o.hatch, k);
    if (o.hatch2) crescent(g, defs, pts, -o.depth * 0.45, -o.depth * 0.4, o.hatch2, k);
    const b = bbox(pts);
    const dots = Math.round(b.w * b.h / (o.dotArea || 1100));
    for (let i = 0; i < dots; i++) {
      const x = b.x + b.w * (0.18 + r() * 0.5), y = b.y + b.h * (0.18 + r() * 0.5);
      el('circle', { cx: f(x), cy: f(y), r: f(sw * (0.3 + r() * 0.3)), fill: o.ink }, g);
    }
    // incrinatura/scheggia dal bordo
    if (o.cracks && r() < o.cracks) {
      const i0 = Math.floor(r() * pts.length);
      const p = pts[i0];
      const cx = b.x + b.w / 2, cy = b.y + b.h / 2;
      const l = 0.25 + r() * 0.25;
      const q = [p[0] + (cx - p[0]) * l, p[1] + (cy - p[1]) * l];
      const m = [(p[0] + q[0]) / 2 + (r() - 0.5) * 6, (p[1] + q[1]) / 2 + (r() - 0.5) * 6];
      el('path', { d: `M${f(p[0])},${f(p[1])}Q${f(m[0])},${f(m[1])} ${f(q[0])},${f(q[1])}`, fill: 'none', stroke: o.ink, 'stroke-width': f(sw * 0.6), 'stroke-linecap': 'round' }, g);
    }
    el('path', { d, fill: 'none', stroke: o.ink, 'stroke-width': sw, 'stroke-linejoin': 'round' }, g);
  }

  /* pietra a colori piatti con luce da sinistra-alto */
  function colorStone(g, defs, pts, r, o) {
    el('path', { d: smooth(pts), fill: o.base }, g);
    crescent(g, defs, pts, -o.depth, -o.depth, o.shadow);
    crescent(g, defs, pts, o.depth * 0.6, o.depth * 0.6, o.light);
    if (o.grain) el('path', { d: smooth(pts), fill: o.grain }, g);
    if (o.stroke) el('path', { d: smooth(pts), fill: 'none', stroke: o.stroke, 'stroke-width': o.sw || 1 }, g);
  }

  /* bezier cubica */
  function bez(p0, p1, p2, p3, t) {
    const u = 1 - t;
    return [
      u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
      u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1]
    ];
  }
  function bezT(p0, p1, p2, p3, t) {
    const u = 1 - t;
    return [
      3 * u * u * (p1[0] - p0[0]) + 6 * u * t * (p2[0] - p1[0]) + 3 * t * t * (p3[0] - p2[0]),
      3 * u * u * (p1[1] - p0[1]) + 6 * u * t * (p2[1] - p1[1]) + 3 * t * t * (p3[1] - p2[1])
    ];
  }

  /* foglia d'ulivo lungo +x, lunghezza L, semilarghezza W, curvatura bend */
  function leafPath(L, W, bend = 0) {
    const b = bend * W;
    return `M0,0C${f(L * 0.28)},${f(-W * 1.05 + b)} ${f(L * 0.72)},${f(-W * 0.85 + b)} ${f(L)},${f(b * 0.6)}` +
      `C${f(L * 0.72)},${f(W * 0.85 + b)} ${f(L * 0.28)},${f(W * 1.05 + b)} 0,0Z`;
  }
  function leafHalf(L, W, bend = 0) {
    const b = bend * W;
    return `M0,0C${f(L * 0.28)},${f(W * 1.05 + b)} ${f(L * 0.72)},${f(W * 0.85 + b)} ${f(L)},${f(b * 0.6)}` +
      `Q${f(L * 0.5)},${f(b * 0.9)} 0,0Z`;
  }

  /* ramo d'ulivo. mode 'engr' (linee) o 'color' (pieno). ritorna le sagome per le maschere */
  function olive(g, r, o) {
    const { p0, c1, c2, p1 } = o;
    const sil = [];
    const stemW = o.stemW || 3;
    const stem = `M${p0}C${c1} ${c2} ${p1}`;
    sil.push({ d: stem, stroke: stemW + 2 });
    const leaves = [];
    const n = o.n || 14;
    for (let i = 0; i < n; i++) {
      const t = 0.1 + (i / (n - 1)) * 0.86 + (r() - 0.5) * 0.03;
      const P = bez(p0, c1, c2, p1, t), T = bezT(p0, c1, c2, p1, t);
      const ang = Math.atan2(T[1], T[0]);
      const side = i % 2 ? 1 : -1;
      const la = ang + side * (0.55 + r() * 0.35);
      const L = o.leafL * (1 - 0.38 * t) * (0.85 + r() * 0.3);
      const W = L * (o.leafRatio || 0.17);
      leaves.push({ P, la, L, W, side, bend: (r() - 0.5) * 0.9 });
    }
    // foglia terminale
    const T1 = bezT(p0, c1, c2, p1, 1);
    leaves.push({ P: p1, la: Math.atan2(T1[1], T1[0]), L: o.leafL * 0.62, W: o.leafL * 0.62 * 0.17, side: 1, bend: 0.2 });

    const gs = el('g', {}, g);
    const layers = [];   // per l'occlusione (modalita' incisione, sfondo trasparente)
    const stemG = el('g', {}, gs);
    el('path', { d: stem, fill: 'none', stroke: o.ink, 'stroke-width': stemW, 'stroke-linecap': 'round' }, stemG);
    layers.push({ wrap: stemG });
    for (const lf of leaves) {
      const tr = `translate(${f(lf.P[0])},${f(lf.P[1])}) rotate(${f(lf.la * 180 / Math.PI)})`;
      const wrap = el('g', {}, gs);
      const lg = el('g', { transform: tr }, wrap);
      layers.push({ wrap, d: leafPath(lf.L, lf.W, lf.bend), tr });
      const d = leafPath(lf.L, lf.W, lf.bend);
      sil.push({ d, transform: tr, stroke: 0 });
      if (o.mode === 'color') {
        el('path', { d, fill: lf.side > 0 ? o.leaf : o.leaf2 }, lg);
        el('path', { d: leafHalf(lf.L, lf.W, lf.bend), fill: o.leafShade }, lg);
        // venatura: per default da 0.04L a 0.93L; veinFrom/veinTo permettono una venatura piu' corta (stampa tessile)
        const v0 = o.veinFrom ?? 0.04, v1 = o.veinTo ?? 0.93, bw = lf.bend * lf.W;
        el('path', { d: `M${f(lf.L * v0)},${f(o.veinFrom == null ? 0 : bw * 0.4)}Q${f(lf.L * 0.5)},${f(bw * 0.9)} ${f(lf.L * v1)},${f(o.veinTo == null ? bw * 0.55 : bw * 0.65)}`, fill: 'none', stroke: o.vein, 'stroke-width': o.veinW || 0.8, 'stroke-linecap': o.veinCap || 'butt' }, lg);
      } else {
        if (o.paper) el('path', { d, fill: o.paper }, lg);
        el('path', { d: leafHalf(lf.L, lf.W, lf.bend), fill: o.hatch }, lg);
        el('path', { d, fill: 'none', stroke: o.ink, 'stroke-width': o.sw || 1.4, 'stroke-linejoin': 'round' }, lg);
        el('path', { d: `M${f(lf.L * 0.04)},0Q${f(lf.L * 0.5)},${f(lf.bend * lf.W * 0.9)} ${f(lf.L * 0.9)},${f(lf.bend * lf.W * 0.55)}`, fill: 'none', stroke: o.ink, 'stroke-width': (o.sw || 1.4) * 0.7 }, lg);
      }
    }
    // olive
    for (const tt of (o.olives || [])) {
      const P = bez(p0, c1, c2, p1, tt[0]);
      const T = bezT(p0, c1, c2, p1, tt[0]);
      const ang = Math.atan2(T[1], T[0]) + tt[1];
      const q = [P[0] + Math.cos(ang) * tt[2], P[1] + Math.sin(ang) * tt[2]];
      const rx = o.oliveR * 0.78, ry = o.oliveR;
      el('path', { d: `M${f(P[0])},${f(P[1])}L${f(q[0])},${f(q[1])}`, stroke: o.ink, 'stroke-width': (o.sw || 1.4) * 0.9, fill: 'none' }, gs);
      const og = el('g', { transform: `translate(${f(q[0])},${f(q[1])}) rotate(${f(ang * 180 / Math.PI - 90)}) translate(0,${f(ry)})` }, gs);
      sil.push({ d: `M${f(-rx)},0a${f(rx)},${f(ry)} 0 1,0 ${f(2 * rx)},0a${f(rx)},${f(ry)} 0 1,0 ${f(-2 * rx)},0`, transform: og.getAttribute('transform'), stroke: 0 });
      layers.push({ wrap: null, d: sil[sil.length - 1].d, tr: og.getAttribute('transform') });
      if (o.mode === 'color') {
        el('ellipse', { rx: f(rx), ry: f(ry), fill: o.oliveFill }, og);
        el('ellipse', { cx: f(-rx * 0.35), cy: f(-ry * 0.1), rx: f(rx * 0.22), ry: f(ry * 0.38), fill: o.oliveHi, opacity: 0.8 }, og);
      } else {
        if (o.paper) el('ellipse', { rx: f(rx), ry: f(ry), fill: o.paper }, og);
        el('ellipse', { rx: f(rx), ry: f(ry), fill: o.hatchDense || o.hatch }, og);
        el('ellipse', { cx: f(-rx * 0.35), cy: f(-ry * 0.15), rx: f(rx * 0.25), ry: f(ry * 0.4), fill: o.paper || '#fff' }, og);
        el('ellipse', { rx: f(rx), ry: f(ry), fill: 'none', stroke: o.ink, 'stroke-width': o.sw || 1.4 }, og);
      }
    }
    if (o.mode !== 'color' && o.occlude !== false) {
      const defs = g.ownerSVGElement.querySelector('defs');
      layers.forEach((L, i) => {
        if (!L.wrap) return;
        const above = layers.slice(i + 1).filter(q => q.d);
        if (!above.length) return;
        const mid = id('occ');
        const m = el('mask', { id: mid, maskUnits: 'userSpaceOnUse', x: -2000, y: -2000, width: 14000, height: 14000 }, defs);
        el('rect', { x: -2000, y: -2000, width: 14000, height: 14000, fill: '#fff' }, m);
        for (const q of above) el('path', { d: q.d, transform: q.tr, fill: '#000', stroke: '#000', 'stroke-width': (o.sw || 1.4) * 2.2 }, m);
        L.wrap.setAttribute('mask', `url(#${mid})`);
      });
    }
    return sil;
  }

  /* testo su arco: top=true legge in alto in senso orario, false in basso */
  function arcText(g, defs, cx, cy, r, text, top, attrs) {
    const pid = id('arc');
    const d = top
      ? `M${cx - r},${cy}A${r},${r} 0 0,1 ${cx + r},${cy}`
      : `M${cx - r},${cy}A${r},${r} 0 0,0 ${cx + r},${cy}`;
    el('path', { id: pid, d, fill: 'none' }, defs);
    const t = el('text', Object.assign({ 'text-anchor': 'middle' }, attrs), g);
    const tp = el('textPath', { href: `#${pid}`, startOffset: '50%' }, t);
    tp.textContent = text;
    return t;
  }

  /* stella a 4 punte (ornamento) */
  function star4(cx, cy, R, r) {
    let d = '';
    for (let i = 0; i < 8; i++) {
      const a = -Math.PI / 2 + i * Math.PI / 4;
      const rr = i % 2 ? r : R;
      d += (i ? 'L' : 'M') + f(cx + Math.cos(a) * rr) + ',' + f(cy + Math.sin(a) * rr);
    }
    return d + 'Z';
  }

  /* grana carta (filtro) */
  function grainFilter(defs, o = {}) {
    const fid = id('grain');
    const fl = el('filter', { id: fid, x: 0, y: 0, width: '100%', height: '100%', 'color-interpolation-filters': 'sRGB' }, defs);
    el('feTurbulence', { type: 'fractalNoise', baseFrequency: o.freq || 0.9, numOctaves: o.oct || 3, seed: o.seed || 3, stitchTiles: 'stitch', result: 'n' }, fl);
    el('feColorMatrix', { type: 'matrix', values: `0 0 0 0 ${o.r ?? 0.14}  0 0 0 0 ${o.g ?? 0.16}  0 0 0 0 ${o.b ?? 0.18}  0 0 0 ${o.alpha ?? 0.9} ${o.bias ?? -0.35}` }, fl);
    el('feComposite', { in2: 'SourceGraphic', operator: 'in' }, fl);
    return `url(#${fid})`;
  }

  return { rng, el, smooth, bbox, stone, wallStones, shift, hatch, crescent, engrStone, colorStone, bez, bezT, leafPath, leafHalf, olive, arcText, star4, grainFilter, f, id };
})();
