"""Libri da colorare 21-21f (Printify bp 2721, 8.5x11", 24 pagine interne + copertina) e PDF 22.

Ogni disegno lo fa ChatGPT (chatgpt_bridge); il codice pulisce solo il tratto e lo porta al formato di stampa.

Uso:
  python strumenti_grafiche/libro_colorare.py genera 21            # disegna le pagine che mancano (si ferma se finisce la quota)
  python strumenti_grafiche/libro_colorare.py genera 21 3 7        # ridisegna solo le pagine 3 e 7
  python strumenti_grafiche/libro_colorare.py prepara 21 [3 7]     # pagine di stampa 2625x3375 (tutte o solo 3 e 7) + foglio
  python strumenti_grafiche/libro_colorare.py correggi 21 [3]      # corregge solo il difetto scritto in correzioni_libri.json,
                                                                   # ridisegnando la pagina da se stessa -> pagine/_03_prova.png
  python strumenti_grafiche/libro_colorare.py accetta 21 3         # dopo il PASS: la prova diventa la pagina (vecchia in _vecchie/)
  python strumenti_grafiche/libro_colorare.py copertina 21         # fronte + retro da ChatGPT -> copertina 5175x3375
  python strumenti_grafiche/libro_colorare.py copertina 21 unisci  # solo rimonta la copertina dai disegni esistenti

Soggetti delle pagine: strumenti_grafiche/libri_colorare.json. File in stampa/<id>_2721/.
"""
import json
import sys
import time
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageOps, ImageStat

sys.path.insert(0, str(Path(__file__).parent))
from chatgpt_bridge import genera as chatgpt  # noqa: E402
from compone_carta import ingrandisci_x4  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LIBRI = json.loads((Path(__file__).parent / "libri_colorare.json").read_text(encoding="utf-8"))
PAGINA = (2625, 3375)   # 8.75 x 11.25" a 300 DPI (con abbondanza)
SICURA = (2250, 3000)   # zona del disegno: margini larghi, niente tagli alla rifilatura
STILE = """Use case: one interior page of a children's coloring book for ages 3-8 ({tema}).
Subject: {soggetto}.
Style: clean BLACK LINE ART ONLY on pure white: thick, even, closed outlines (about 6-8 px at 1024 px width), large simple areas easy to color with crayons, cute friendly faces, no shading, no grey, no hatching, no solid black fills except small details like eyes, no colour.
Composition: one clear scene filling the portrait page, everything fully inside the page with a white margin of at least 8% on every side: every element fully inside the canvas, nothing touches or is cut by the image border: no object, house, tree or ground line may touch or be cut by the page edge; ground and snow lines end with rounded tips inside the page. No frame or border line around the page. All lines closed and unbroken, no overlapping outlines inside hands or bodies, no tiny fragments. At most 3 characters, clearly separated, never overlapping; no flames near any body; large simple areas, no tiny details.
Fill the page: the artwork spans about 85% of the page height; a single animal or object gets a simple setting (ground or seabed, a few plants, bubbles or clouds), never a small subject floating in empty white. Uniform outline weight everywhere. Every number in the subject is exact: count the repeated elements (legs, tentacles, stars, fish) before finishing. Characters stand on the ground, never float, and objects never touch each other.
{testo}"""
NIENTE_TESTO = "No text, no letters, no numbers, no signature, no watermark anywhere."
TESTO_P1 = ("The only text is exactly: THIS BOOK BELONGS TO (in big hollow outline letters to color, spelled exactly). "
            "No other text, no signature, no watermark.")


def cartella(libro):
    d = ROOT / "stampa" / f"{libro}_2721"
    (d / "pagine").mkdir(parents=True, exist_ok=True)
    return d


def genera(libro, quali):
    info, d = LIBRI[libro], cartella(libro)
    for n in quali or range(1, len(info["pagine"]) + 1):
        out = d / "pagine" / f"{n:02d}_chatgpt.png"
        if out.exists() and not quali:
            continue
        brief = STILE.format(tema=info["tema"], soggetto=info["pagine"][n - 1],
                             testo=TESTO_P1 if n == 1 else NIENTE_TESTO)
        try:
            # la pagina 1 ha testo: ChatGPT la ricontrolla; le altre una sola generazione (le controlla l'art director)
            chatgpt(brief, out, "verticale", trasparente=False, controllo=(n == 1))
        except SystemExit as e:
            print(f"pagina {n}: {str(e)[-300:]}", flush=True)
            if "usage limit" in str(e).lower():
                print("quota ChatGPT finita: riprendere piu' tardi con lo stesso comando", flush=True)
                return False
            continue
        print(f"{libro} pagina {n} fatta", flush=True)
    return True


COPERTINA = (5175, 3375)  # retro a sinistra + fronte a destra, con abbondanza
FRONTE = """Use case: FRONT COVER of a children's coloring book (ages 3-8), printed soft cover 8.5x11 inches.
{soggetto}
Text (verbatim, exact spelling, the only text on the cover): "{titolo}" in big bold friendly rounded letters, high contrast.
Style: bright, full-colour, friendly children's book illustration with thick outlines; the same look as the attached reference cover.
Composition: portrait; the illustrated background fills the WHOLE image edge to edge (no white border, no frame, no book shown, flat artwork only, not a photo of a book). Keep the title and all characters inside the central 80% of the height and 90% of the width: the top and bottom 10% will be trimmed. No logo, no barcode, no price, no author name, no watermark."""
RETRO = """Use case: BACK COVER of a children's coloring book (ages 3-8) about {tema}, matching the attached front cover.
Content: the same colourful background as the front cover, calmer: a few small cute characters from the theme around the edges, and a big plain light area in the middle-lower part (left empty on purpose).
Style: bright, full-colour, friendly children's book illustration with thick outlines, same palette as the front.
Composition: portrait, artwork fills the WHOLE image edge to edge, flat artwork only (not a photo of a book). Keep characters inside the central 80% of the height and 90% of the width: the top and bottom 10% will be trimmed.
No text at all, no letters, no logo, no barcode, no watermark."""


def copertina(libro, quali=("fronte", "retro")):
    """Fronte e retro disegnati da ChatGPT; poi li unisce nel file copertina di Printify (retro | fronte)."""
    info, d = LIBRI[libro], cartella(libro)
    prop = json.loads((ROOT / "proposte" / "2026-11_natale_2" / "proposte.json").read_text(encoding="utf-8"))
    idea = next(i for i in prop["idee"] if i["id"] == libro)
    soggetto = next(r for r in idea["brief_design"].splitlines() if r.startswith("Subject:"))
    bozza = ROOT / "proposte" / "2026-11_natale_2" / libro / "bozza.png"
    if "fronte" in quali:
        chatgpt(FRONTE.format(soggetto=soggetto, titolo=info["titolo"]), d / "fronte_chatgpt.png", "verticale",
                trasparente=False, riferimenti=[bozza],
                uso_riferimenti="the approved draft: copy the cover's characters, colours and title style, but deliver flat cover artwork only")
    if "retro" in quali:
        chatgpt(RETRO.format(tema=info["tema"]), d / "retro_chatgpt.png", "verticale", trasparente=False,
                riferimenti=[d / "fronte_chatgpt.png"], uso_riferimenti="the front cover of the same book: match its style and colours")
    meta = (COPERTINA[0] + 1) // 2
    tela = Image.new("RGB", COPERTINA, "white")
    for nome, x in (("retro", 0), ("fronte", COPERTINA[0] - meta)):
        im = ingrandisci_x4(Image.open(d / f"{nome}_chatgpt.png").convert("RGB"))
        k = max(meta / im.width, COPERTINA[1] / im.height)  # riempie tutta la meta', taglia l'eccesso in alto/basso
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        # "copertina_su" (facoltativo, in libri_colorare.json): alza la finestra del ritaglio di quella frazione
        # dell'altezza, quando in alto c'e' qualcosa troppo vicino al taglio e in basso solo sfondo
        su = round(info.get("copertina_su", 0) * im.height)
        l, t = (im.width - meta) // 2, max(0, (im.height - COPERTINA[1]) // 2 - su)
        tela.paste(im.crop((l, t, l + meta, t + COPERTINA[1])), (x, 0))
    tela.save(d / "copertina_5175x3375.png", dpi=(300, 300))
    an = tela.copy()
    an.thumbnail((1600, 1600))
    an.save(d / "copertina_anteprima.jpg", quality=88)
    print(f"{libro}: copertina pronta")


def pulisci(im):
    """Tratto nero pieno su bianco puro: niente grigi di fondo (in stampa diventano sporco)."""
    g = ImageOps.grayscale(im)
    return g.point(lambda v: 255 if v > 200 else (0 if v < 90 else round((v - 90) * 255 / 110)))


TRATTO = 26  # spessore tipico delle linee a stampa (px a 300 DPI, circa 2,4 mm), uguale in tutto il libro


def spessore(g):
    """Spessore medio del tratto ~ 2 x area nera / contorno."""
    nero = g.point(lambda v: 255 if v < 128 else 0)
    bordo = ImageChops.subtract(nero, nero.filter(ImageFilter.MinFilter(3)))
    a, b = ImageStat.Stat(nero).sum[0], ImageStat.Stat(bordo).sum[0]
    return 2 * a / max(1, b)


def ingrossa(g, px):
    """Allarga il tratto nero di circa px per lato con bordi tondi (sfocatura + soglia, niente angoli squadrati)."""
    m = g.filter(ImageFilter.GaussianBlur(px))
    return m.point(lambda v: 0 if v < 215 else (255 if v > 245 else round((v - 215) * 255 / 30)))


def spessore_uniforme(g, n):
    """Solo le pagine col tratto sottile vengono ingrossate (al massimo 4 px per lato, per non impastare i dettagli)."""
    w = spessore(g)
    if w < TRATTO - 6:
        g = ingrossa(g, min(4, round((TRATTO - w) / 2)))
    print(f"  pagina {n}: tratto {w:.0f} px -> {spessore(g):.0f} px")
    return g


CORREZIONI = Path(__file__).parent / "correzioni_libri.json"
CORREGGI = """Use case: one interior page of a children's coloring book for ages 3-8 ({tema}).
The attached reference image is the current page: redraw THIS SAME PAGE, keeping everything identical: the same characters, poses, faces, objects, composition, proportions and placement, the same thick clean black line style.
Fix ONLY this: {difetto}
Change nothing else. Scene logic: every character and object that should stand on something rests on its ground line; every ground, hill, horizon or seabed line runs to the edge of the scene or joins another line, and a line that passes behind a character reappears on the other side.
Style: clean BLACK LINE ART ONLY on pure white: thick, even, closed outlines, no shading, no grey, no hatching, no colour. Everything fully inside the page with a white margin of at least 8% on every side; nothing touches or is cut by the image border. No frame. {testo}"""


def correggi(libro, quali):
    """Ridisegna la pagina partendo da se stessa (riferimento) e corregge solo il difetto scritto in
    correzioni_libri.json -> pagine/_NN_prova.png. La pagina attuale non si tocca finche' non si fa 'accetta'."""
    info, d = LIBRI[libro], cartella(libro)
    difetti = json.loads(CORREZIONI.read_text(encoding="utf-8")).get(libro, {})
    for n in quali or sorted(int(k) for k in difetti):
        prova = d / "pagine" / f"_{n:02d}_prova.png"
        if prova.exists() and not quali:
            continue
        brief = CORREGGI.format(tema=info["tema"], difetto=difetti[f"{n:02d}"],
                                testo=TESTO_P1 if n == 1 else NIENTE_TESTO)
        try:
            chatgpt(brief, prova, "verticale", trasparente=False, riferimenti=[d / "pagine" / f"{n:02d}_chatgpt.png"],
                    controllo=(n == 1))
        except SystemExit as e:
            print(f"pagina {n}: {str(e)[-300:]}", flush=True)
            if "usage limit" in str(e).lower():
                print("quota ChatGPT finita: riprendere piu' tardi con lo stesso comando", flush=True)
                return False
            continue
        print(f"{libro} pagina {n} corretta (prova)", flush=True)
    return True


def accetta(libro, quali):
    """La prova approvata diventa la pagina: la vecchia va in pagine/_vecchie/, poi si prepara solo quella pagina."""
    d = cartella(libro) / "pagine"
    (d / "_vecchie").mkdir(exist_ok=True)
    difetti = json.loads(CORREZIONI.read_text(encoding="utf-8"))
    for n in quali:
        orig = d / f"{n:02d}_chatgpt.png"
        orig.replace(d / "_vecchie" / f"{n:02d}_chatgpt_{time.strftime('%Y%m%d_%H%M')}.png")
        (d / f"_{n:02d}_prova.png").replace(orig)
        difetti.get(libro, {}).pop(f"{n:02d}", None)  # corretta: 'correggi' non la rifa'
    CORREZIONI.write_text(json.dumps(difetti, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    prepara(libro, quali)


def prepara(libro, quali=()):
    """Pagine di stampa (tutte, o solo quelle in quali) + foglio di controllo con tutte le pagine.
    Attenzione: rifare una pagina cancella i ritocchi a mano fatti sul suo file di stampa."""
    d = cartella(libro)
    pronte = []
    for src in sorted((d / "pagine").glob("[0-9][0-9]_chatgpt.png")):
        n = int(src.name[:2])
        if quali and n not in quali:
            esistente = d / "pagine" / f"pagina_{n:02d}.png"
            if esistente.exists():
                pronte.append((n, Image.open(esistente).convert("L")))
            continue
        g = pulisci(ingrandisci_x4(Image.open(src).convert("RGB")))
        # ritaglia il bianco attorno al disegno, poi lo adatta alla zona sicura
        bbox = ImageOps.invert(g).getbbox()
        g = g.crop(bbox)
        k = min(SICURA[0] / g.width, SICURA[1] / g.height)
        g = g.resize((round(g.width * k), round(g.height * k)), Image.LANCZOS)
        # margine bianco PRIMA di ingrossare: senza, il tratto non puo' allargarsi oltre il bordo del ritaglio e
        # le linee piu' esterne escono tagliate piatte (segnalato dall'art director il 05/11)
        g = ImageOps.expand(g, 40, fill=255)
        g = spessore_uniforme(g, n)
        pagina = Image.new("L", PAGINA, 255)
        pagina.paste(g, ((PAGINA[0] - g.width) // 2, (PAGINA[1] - g.height) // 2))
        out = d / "pagine" / f"pagina_{n:02d}.png"
        pagina.save(out, dpi=(300, 300))
        pronte.append((n, pagina))
    # foglio di controllo: 6 colonne
    if pronte:
        w, h = 300, 386
        foglio = Image.new("L", (6 * (w + 10) + 10, ((len(pronte) + 5) // 6) * (h + 10) + 10), 160)
        for i, (n, p) in enumerate(pronte):
            foglio.paste(p.resize((w, h)), (10 + (i % 6) * (w + 10), 10 + (i // 6) * (h + 10)))
        foglio.save(d / "foglio_pagine.jpg", quality=85)
    print(f"{libro}: {len(pronte)} pagine pronte -> {d.relative_to(ROOT)}")


if __name__ == "__main__":
    cmd, libro, *num = sys.argv[1:]
    if cmd == "genera":
        genera(libro, [int(x) for x in num])
    elif cmd == "prepara":
        prepara(libro, [int(x) for x in num])
    elif cmd == "correggi":
        correggi(libro, [int(x) for x in num])
    elif cmd == "accetta":
        accetta(libro, [int(x) for x in num])
    elif cmd == "copertina":  # copertina 21 [fronte|retro|unisci]
        copertina(libro, num or ("fronte", "retro"))
