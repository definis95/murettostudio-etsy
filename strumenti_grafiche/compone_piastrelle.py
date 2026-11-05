"""Compone il file di stampa della sciarpa a piastrelle (19d) dal blocco 2x2 disegnato da ChatGPT.

Uso:
  python strumenti_grafiche/compone_piastrelle.py 19d

Ritaglia le 4 piastrelle senza le linee di fuga, le ingrandisce x4 (Real-ESRGAN) e le rimette a scacchiera
con fughe tutte uguali: 3 piastrelle esatte sulla larghezza (niente strisce tagliate sui bordi), 4 file per
mezza sciarpa; nella meta' verso l'altro lembo le piastrelle sono capovolte, cosi' i limoni stanno dritti su entrambi i lembi
(la scacchiera resta continua).
"""
import sys
from pathlib import Path

from PIL import Image, ImageStat

sys.path.insert(0, str(Path(__file__).parent))
from compone_carta import ingrandisci_x4  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
ROOT = Path(__file__).resolve().parent.parent
W, H = 4126, 11100
FUGA = 14


def righe_blu(im, verticale):
    px = im.load()
    w, h = im.size
    n, m = (w, h) if verticale else (h, w)
    out = []
    for i in range(n):
        blu = 0
        for j in range(0, m, 3):
            p = px[i, j] if verticale else px[j, i]
            blu += p[2] > 140 and p[0] < 90 and p[1] < 130
        if blu > 0.5 * m / 3:
            out.append(i)
    return out


def intervalli(linee, n):
    """Zone libere tra le linee di fuga (gli interni delle piastrelle)."""
    zone, inizio = [], 0
    for x in linee + [n]:
        if x - inizio > 50:
            zone.append((inizio, x))
        inizio = x + 1
    return zone


def main():
    d = ROOT / "stampa" / f"{sys.argv[1]}_1327"
    blocco = Image.open(d / "design.png").convert("RGB")
    cx = intervalli(righe_blu(blocco, True), blocco.width)
    cy = intervalli(righe_blu(blocco, False), blocco.height)
    assert len(cx) == 2 and len(cy) == 2, (cx, cy)
    linee = [x for x in righe_blu(blocco, True)]
    colore_fuga = tuple(round(v) for v in ImageStat.Stat(blocco.crop((linee[0], 300, linee[0] + 3, 900))).median)
    grande = ingrandisci_x4(blocco)
    piastrelle = {}
    for r, (y0, y1) in enumerate(cy):
        for c, (x0, x1) in enumerate(cx):
            piastrelle[(r, c)] = grande.crop((x0 * 4, y0 * 4, x1 * 4, y1 * 4))
    fiori = [piastrelle[(0, 0)], piastrelle[(1, 1)]]
    limoni = [piastrelle[(0, 1)], piastrelle[(1, 0)]]
    px, py = 1375, 1387  # 3 x 1375 = 4125 sulla larghezza, 4 x 1387 = 5548 per mezza sciarpa
    intera = Image.new("RGB", (W, H), colore_fuga)
    for r in range(8):
        for c in range(3):
            tipo = fiori if (r + c) % 2 == 0 else limoni
            p = tipo[(r // 2 + c // 2) % 2].resize((px - FUGA, py - FUGA), Image.LANCZOS)
            if r < 4:  # meta' verso l'altro lembo: limoni capovolti, cosi' pendono dritti
                p = p.rotate(180)
            intera.paste(p, (c * px + FUGA // 2, r * py + FUGA // 2 + 2))
    finale = intera.rotate(90, expand=True)
    out = d / f"design_front_{finale.width}x{finale.height}.jpg"
    finale.save(out, quality=92, dpi=(150, 150))
    ant = finale.copy()
    ant.thumbnail((2000, 2000))
    ant.save(d / "anteprima.jpg", quality=88)
    finale.crop((1500, 1200, 3300, 2330)).save(d / "dettaglio_100.jpg", quality=88)
    finale.crop((0, 0, 1800, 1130)).save(d / "bordo_100.jpg", quality=88)
    finale.crop((4650, 1200, 6450, 2330)).save(d / "collo_100.jpg", quality=88)
    print(out, "fuga", colore_fuga)


if __name__ == "__main__":
    main()
