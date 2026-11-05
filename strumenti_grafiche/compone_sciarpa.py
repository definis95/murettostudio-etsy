"""Compone il file di stampa di una sciarpa (fantasia continua) dai motivi disegnati da ChatGPT.

Uso:
  python strumenti_grafiche/compone_sciarpa.py 19b      (preset in PRESET, cartella stampa/<id>_1327)

Come funziona:
  1. trova i motivi interi nel foglio di ChatGPT (quelli tagliati dal bordo vengono scartati)
  2. ingrandisce il foglio x4 con Real-ESRGAN e ritaglia i motivi da li': restano nitidi anche grandi
  3. una fila di motivi di traverso al collo, poi i motivi grandi a mattoncino con spostamenti e rotazioni casuali, senza sovrapposizioni
     (distanza minima), poi pochi riempitivi scelti per colore (es. solo foglie, niente boccioli orfani)
  4. compone mezza sciarpa con i motivi dritti e la ripete capovolta: indossata, la sciarpa pende dal
     collo con due lembi e su tutti e due i motivi stanno dritti
  5. porta il fondo esattamente al colore del brief
Esce design_front_<W>x<H>.jpg (lunghezza in orizzontale, come vuole Printify) + anteprima e ritagli al 100%.
"""
import argparse
import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat

sys.path.insert(0, str(Path(__file__).parent))
from compone_carta import ingrandisci_x4  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
ROOT = Path(__file__).resolve().parent.parent
W, H = 4126, 11100  # area Printify 1327 (sciarpa 69 x 180 cm) in verticale: H = lunghezza


def verde(c): return c[1] > c[0] + 8 and c[1] >= c[2]
def rosso(c): return c[0] > c[1] + 50 and c[0] > c[2] + 40
def giallo(c): return c[0] > 170 and c[1] > 110 and c[2] < 140 and c[0] - c[2] > 70
def chiaro(c): return sum(c) > 600
def viola(c): return c[2] > c[1] + 5 and c[0] > c[1]
def oro(c): return c[0] > 150 and c[1] > 110 and c[2] < 120


def forma(c):
    """(proporzione lato lungo/corto, pienezza = area / area del riquadro) del motivo nel foglio."""
    w, h = c["b"][2] - c["b"][0], c["b"][3] - c["b"][1]
    return max(w, h) / max(1, min(w, h)), c["area"] / max(1, w * h)


def oliva(c): return sum(c["colore"]) < 335  # olive viola o verde scuro (le foglie sono verde chiaro)
def tondo(c): return forma(c)[0] < 1.2


# lato = lato lungo (px finali) del motivo grande mediano; passo = distanza della griglia in "lati"
# riempitivi = [(condizione sul motivo, quanti per motivo grande, distanza minima tra riempitivi uguali)]
# tipi = motivi grandi alternati a scacchiera (es. soli e lune), escludi = punti del foglio da scartare
PRESET = {
    "19b": dict(fondo="#F4EBDD", lato=1050, passo=(1.0, 0.72), scosta=0.22, rot=25, taglie=(1.0, 0.85),
                distanza=70, riempitivi=[(lambda c: not oliva(c), 0.35, 0),
                                         (lambda c: oliva(c), 0.12, 800)]),
    "19c": dict(fondo="#F7F1E6", lato=1200, passo=(1.05, 0.8), scosta=0.2, rot=10, taglie=(1.0, 0.85),
                distanza=120, escludi=[(1117, 785)],
                riempitivi=[(lambda c: verde(c["colore"]) or c["colore"][0] - c["colore"][2] > 120, 0.3, 0),  # foglie, ranuncoli
                            (lambda c: tondo(c) and c["colore"][0] > 170
                             and 60 < c["colore"][0] - c["colore"][2] < 115, 0.2, 0)]),  # camomille tonde
    "19e": dict(fondo="#1F2A44", lato=430, passo=(1.75, 1.45), scosta=0.3, rot=35, taglie=(1.0, 0.75),
                distanza=60, riempitivi=[(lambda c: True, 2.2, 0)], min_riempitivo=150,
                escludi=[(215, 215), (385, 885)],
                tipi=[lambda c: oro(c["colore"]), lambda c: not oro(c["colore"])]),
}


def esa(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def sfondo_misurato(im):
    piccolo = im.resize((300, 300))
    q = piccolo.quantize(8)
    indici = Image.frombytes("L", q.size, q.tobytes())
    idx = max(q.getcolors(), key=lambda c: c[0])[1]
    mask = indici.point(lambda v: 255 if v == idx else 0)
    return tuple(round(v) for v in ImageStat.Stat(piccolo, mask=mask).median)


def componenti(im, base, unisci=21, soglia=30):
    diff = ImageChops.difference(im, Image.new("RGB", im.size, base)).convert("L")
    pieno = diff.point(lambda v: 255 if v > soglia else 0)
    unito = pieno.filter(ImageFilter.MaxFilter(unisci))
    w, h = im.size
    out = []
    while True:
        bbox = unito.point(lambda v: 255 if v == 255 else 0).getbbox()
        if not bbox:
            break
        riga = unito.crop((bbox[0], bbox[1], bbox[2], bbox[1] + 1)).tobytes()
        seme = (bbox[0] + next(i for i, v in enumerate(riga) if v == 255), bbox[1])
        ImageDraw.floodfill(unito, seme, 128)
        questo = unito.point(lambda v: 255 if v == 128 else 0)
        b = questo.getbbox()
        unito = ImageChops.subtract(unito, questo.point(lambda v: 128 if v else 0))
        if b[0] <= 1 or b[1] <= 1 or b[2] >= w - 1 or b[3] >= h - 1:
            continue  # tagliato dal bordo del foglio
        vero = ImageChops.multiply(questo.crop(b), pieno.crop(b))
        area = vero.histogram()[255]
        if area < 30:
            continue
        colore = tuple(ImageStat.Stat(im.crop(b), mask=vero).mean)
        # buchi = zone non raggiungibili dal bordo del riquadro senza attraversare il motivo
        fuori = Image.new("L", (vero.width + 2, vero.height + 2), 0)
        fuori.paste(vero, (1, 1))
        ImageDraw.floodfill(fuori, (0, 0), 128)
        fuori = fuori.crop((1, 1, vero.width + 1, vero.height + 1))
        buchi = ImageChops.multiply(fuori.point(lambda v: 255 if v == 0 else 0), questo.crop(b))
        out.append(dict(b=b, maschera=questo.crop(b), area=area, colore=colore, buchi=buchi))
    return out


def sprite(grande, base, c):
    """Motivo ritagliato dal foglio ingrandito x4: RGBA + maschera di ingombro (piena, senza buchi)."""
    x0, y0, x1, y1 = c["b"]
    rgb = grande.crop((x0 * 4, y0 * 4, x1 * 4, y1 * 4))
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, base)).convert("L")
    alpha = diff.point(lambda v: max(0, min(255, (v - 10) * 6)))  # bordo netto, niente alone chiaro
    m = c["maschera"].resize(rgb.size, Image.NEAREST)
    alpha = ImageChops.multiply(alpha, m)
    # buchi chiusi dentro il motivo (petali bianchi della camomilla): pieni, non trasparenti
    buchi = c["buchi"].resize(rgb.size, Image.NEAREST)
    alpha = ImageChops.lighter(alpha, buchi)
    s = rgb.convert("RGBA")
    s.putalpha(alpha)
    return s, m


def trasforma(s, m, fattore, rot, flip, rnd, angolo=None):
    w, h = max(1, round(s.width * fattore)), max(1, round(s.height * fattore))
    s, m = s.resize((w, h), Image.LANCZOS), m.resize((w, h), Image.NEAREST)
    if flip and rnd.random() < 0.5:
        s, m = s.transpose(Image.FLIP_LEFT_RIGHT), m.transpose(Image.FLIP_LEFT_RIGHT)
    a = angolo if angolo is not None else (rnd.uniform(-rot, rot) if rot else 0)
    if a:
        s = s.rotate(a, Image.BICUBIC, expand=True)
        m = m.rotate(a, Image.NEAREST, expand=True)
    return s, m


def piccola(m, chiudi):
    """Ingombro a 1/8 (per i controlli di distanza); chiudi = riempie incavi (lune) e spazi interni."""
    r = m.resize((max(1, m.width // 8), max(1, m.height // 8)), Image.BILINEAR).point(lambda v: 255 if v > 40 else 0)
    if chiudi:
        r = r.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(5))
    return r


def libero(occ, m8, pos8, margine8):
    box = (pos8[0] - margine8, pos8[1] - margine8, pos8[0] + m8.width + margine8, pos8[1] + m8.height + margine8)
    vicino = Image.new("L", (box[2] - box[0], box[3] - box[1]), 0)
    vicino.paste(m8, (margine8, margine8))
    if margine8:
        vicino = vicino.filter(ImageFilter.MaxFilter(2 * margine8 + 1))
    return not ImageChops.multiply(vicino, occ.crop(box)).getbbox()


def componi(grandi, riempitivi, cfg, base, size, rnd):
    w, h = size
    tela = Image.new("RGB", size, base)
    occ = Image.new("L", (w // 8 + 1, h // 8 + 1), 0)
    lato = cfg["lato"]
    px, py = cfg["passo"][0] * lato, cfg["passo"][1] * lato
    marg8 = max(1, cfg["distanza"] // 8)
    messi, precedente = 0, None

    def prova(s, m, cx, cy, chiudi, margine8):
        pos = (round(cx - s.width / 2), round(cy - s.height / 2))
        if pos[1] < 24:  # bordo verso il collo: nessun motivo tagliato dove la sciarpa si capovolge
            return False
        m8 = piccola(m, chiudi)
        p8 = (pos[0] // 8, pos[1] // 8)
        if not libero(occ, m8, p8, margine8):
            return False
        tela.paste(s, pos, s)
        occ.paste(255, p8, m8)
        return True

    # fila al collo: motivi interi messi di traverso (neutri per i due lembi), niente banda vuota al centro
    tipi = cfg.get("tipi")
    for c in range(int(w / px) + 1):
        candidati = [g for g in grandi if g["tipo"] == c % len(tipi)] if tipi else grandi  # sole, luna, sole...
        for _ in range(10):
            scelta = rnd.choice(candidati or grandi)
            s, m = trasforma(scelta["s"], scelta["m"], scelta["fattore"] * rnd.choice(cfg["taglie"]), 0, True, rnd,
                             angolo=rnd.choice((90, -90)) + rnd.uniform(-8, 8))
            cx = c * px + px / 2 + rnd.uniform(-0.15, 0.15) * px
            # sfasati in lunghezza: la fila al collo non deve formare una colonna dritta
            if prova(s, m, cx, 24 + s.height / 2 + rnd.uniform(0, 260), True, marg8):
                messi += 1
                break
    for r in range(-1, int(h / py) + 2):
        sfasa = px / 2 if r % 2 else 0
        for c in range(-1, int(w / px) + 2):
            if tipi:  # scacchiera di tipi (sole/luna), con il 20% di celle scambiate a caso
                t = (r + c) % len(tipi)
                if rnd.random() < 0.2:
                    t = (t + 1) % len(tipi)
                candidati = [g for g in grandi if g["tipo"] == t] or grandi
            else:
                candidati = grandi
            for _ in range(10):
                scelta = rnd.choice([g for g in candidati if g is not precedente] or candidati)
                f = rnd.choice(cfg["taglie"]) * scelta["fattore"]
                s, m = trasforma(scelta["s"], scelta["m"], f, cfg["rot"], True, rnd)
                cx = c * px + sfasa + rnd.uniform(-cfg["scosta"], cfg["scosta"]) * px
                cy = r * py + rnd.uniform(-cfg["scosta"], cfg["scosta"]) * py
                if prova(s, m, cx, cy, True, marg8):
                    messi += 1
                    precedente = scelta
                    break
    aggiunti = 0
    for gruppo, quota, lontani in riempitivi:
        if not gruppo:
            continue
        obiettivo, falliti, fatti, centri = round(messi * quota), 0, 0, []
        while fatti < obiettivo and falliti < 3000:
            scelta = rnd.choice(gruppo)
            s, m = trasforma(scelta["s"], scelta["m"], scelta["fattore"], 180, True, rnd)
            cx, cy = rnd.uniform(0, w), rnd.uniform(0, h)
            # lontani dai riempitivi uguali (anche da quelli speculari oltre il collo: cy piccolo)
            vicino = any((cx - x) ** 2 + (cy - y) ** 2 < lontani ** 2 for x, y in centri) or cy < lontani / 2
            if not vicino and prova(s, m, cx, cy, False, max(1, marg8 // 2)):
                fatti, falliti = fatti + 1, 0
                centri.append((cx, cy))
            else:
                falliti += 1
        aggiunti += fatti
    return tela, messi, aggiunti


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--seme", type=int, default=11)
    a = ap.parse_args()
    cfg = PRESET[a.id]
    d = ROOT / "stampa" / f"{a.id}_1327"
    foglio = Image.open(d / "design.png").convert("RGB")
    base = sfondo_misurato(foglio)
    comp = componenti(foglio, base)
    massimo = max(c["area"] for c in comp)
    soglia = 0.2 * massimo
    print(f"fondo misurato {base}, motivi {len(comp)}")
    x4 = d / "design_x4.png"
    if not x4.exists():
        ingrandisci_x4(foglio).save(x4)
    grande = Image.open(x4).convert("RGB")
    escludi = cfg.get("escludi", [])
    comp = [c for c in comp if not any(c["b"][0] <= x < c["b"][2] and c["b"][1] <= y < c["b"][3] for x, y in escludi)]
    grandi_c = [c for c in comp if c["area"] >= soglia]
    lati = sorted(max(c["b"][2] - c["b"][0], c["b"][3] - c["b"][1]) * 4 for c in grandi_c)
    fattore = cfg["lato"] / lati[len(lati) // 2]
    grandi = []
    for c in grandi_c:
        s, m = sprite(grande, base, c)
        tipo = next((i for i, t in enumerate(cfg.get("tipi", [])) if t(c)), 0)
        grandi.append(dict(s=s, m=m, fattore=fattore, tipo=tipo))
    riempitivi = []
    for cond, quota, lontani in cfg["riempitivi"]:
        g = []
        for c in comp:
            if c["area"] >= soglia or c["area"] < cfg.get("min_riempitivo", 30) or not cond(c):
                continue
            s, m = sprite(grande, base, c)
            g.append(dict(s=s, m=m, fattore=fattore))
        riempitivi.append((g, quota, lontani))
    print(f"grandi {len(grandi)} (fattore {fattore:.2f}, tipi {[g['tipo'] for g in grandi]}), "
          f"riempitivi {[len(g) for g, _, _ in riempitivi]}")
    meta, messi, aggiunti = componi(grandi, riempitivi, cfg, base, (W, H // 2), random.Random(a.seme))
    print(f"mezza sciarpa: {messi} motivi grandi, {aggiunti} riempitivi")
    intera = Image.new("RGB", (W, H), base)
    intera.paste(meta.rotate(180), (0, 0))
    intera.paste(meta, (0, H // 2))
    # fondo esattamente al colore del brief (spostamento uniforme di tutti i colori)
    t = esa(cfg["fondo"])
    bande = [b.point(lambda v, k=k: max(0, min(255, v + t[k] - base[k]))) for k, b in enumerate(intera.split())]
    intera = Image.merge("RGB", bande)
    finale = intera.rotate(90, expand=True)  # lunghezza in orizzontale
    out = d / f"design_front_{finale.width}x{finale.height}.jpg"
    finale.save(out, quality=92, dpi=(150, 150))
    ant = finale.copy()
    ant.thumbnail((2000, 2000))
    ant.save(d / "anteprima.jpg", quality=88)
    finale.crop((1500, 1200, 3300, 2330)).save(d / "dettaglio_100.jpg", quality=88)
    finale.crop((0, 0, 1800, 1130)).save(d / "bordo_100.jpg", quality=88)
    finale.crop((4650, 1200, 6450, 2330)).save(d / "collo_100.jpg", quality=88)
    print(out)


if __name__ == "__main__":
    main()
