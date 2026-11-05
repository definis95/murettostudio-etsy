"""Compone i file di stampa di una calza di Natale (stampa all-over) da sfondo + primo piano.

Uso:
  python strumenti_grafiche/compone_calza.py CARTELLA --area 2150x3329 [--piede destra|sinistra]

CARTELLA contiene sfondo(_x4).png (motivo che copre tutta la calza) e primo_piano(_x4).png
(disegno trasparente). Il primo piano va nella "gamba" della calza, lontano dal piede:
  - gamba = ~70% della larghezza, dal lato opposto al piede; piede = ultimo ~30% dell'altezza
Escono design_front_WxH.png (sfondo + disegno) e design_back_WxH.png (solo sfondo, lato muro).
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
from prepara_stampa import DPI, pulisci  # noqa: E402

LARGHEZZA_GAMBA = 0.70  # frazione della larghezza occupata dalla gamba
LARGHEZZA_DISEGNO = 0.58  # frazione della larghezza per il disegno (margini dentro la gamba)
ALTO = 0.07  # distanza dal bordo superiore (asola e cucitura)
ALTEZZA_MAX = 0.62  # il disegno finisce entro ALTO + 62% = 69%, sopra il piede


def carica(cartella, nome):
    x4 = cartella / f"{nome}_x4.png"
    return Image.open(x4 if x4.exists() else cartella / f"{nome}.png")


def sfondo_pieno(sfondo, area):
    """Ritaglia (o ingrandisce) lo sfondo per coprire tutta l'area, senza ripetizioni."""
    w, h = area
    s = max(w / sfondo.width, h / sfondo.height)
    if s > 1:
        sfondo = sfondo.resize((round(sfondo.width * s), round(sfondo.height * s)), Image.LANCZOS)
    x, y = (sfondo.width - w) // 2, (sfondo.height - h) // 2
    return sfondo.convert("RGBA").crop((x, y, x + w, y + h))


def colore_base(im):
    """Colore piu' frequente dello sfondo (il fondo pieno, non i motivi)."""
    piccolo = im.convert("RGB").resize((200, 300)).quantize(8)
    indice = max(piccolo.getcolors(), key=lambda c: c[0])[1]
    r, g, b = piccolo.getpalette()[indice * 3:indice * 3 + 3]
    return (r, g, b, 255)


def togli_motivi_sotto(fondo, disegno, pos):
    """Cancella per intero i motivi dello sfondo (fiocchi, puntini) che toccano il disegno,
    cosi' dietro le scritte non restano mezzi fiocchi."""
    colore = colore_base(fondo)
    base = Image.new("RGBA", fondo.size, colore)
    diff = ImageChops.difference(fondo.convert("RGB"), base.convert("RGB")).convert("L")
    motivi = diff.point(lambda v: 255 if v > 30 else 0).filter(ImageFilter.MaxFilter(9))  # unisce i bracci
    zona = Image.new("L", fondo.size, 0)
    zona.paste(disegno.getchannel("A").point(lambda v: 255 if v > 40 else 0), pos)
    zona = zona.filter(ImageFilter.MaxFilter(31))
    while True:
        tocca = ImageChops.multiply(motivi.point(lambda v: 255 if v == 255 else 0), zona)
        bbox = tocca.getbbox()
        if not bbox:
            break
        riga = tocca.crop((bbox[0], bbox[1], bbox[2], bbox[1] + 1)).tobytes()
        seme = (bbox[0] + next(i for i, v in enumerate(riga) if v), bbox[1])
        ImageDraw.floodfill(motivi, seme, 128)
    # margine largo: copre anche il bagliore chiaro attorno ai fiocchi (altrimenti restano "fantasmi")
    cancella = motivi.point(lambda v: 255 if v == 128 else 0).filter(ImageFilter.MaxFilter(25))
    return Image.composite(base, fondo, cancella.filter(ImageFilter.GaussianBlur(4)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cartella")
    ap.add_argument("--area", default="2150x3329")
    ap.add_argument("--piede", choices=["destra", "sinistra"], default="destra")
    a = ap.parse_args()
    cartella = Path(a.cartella)
    w, h = map(int, a.area.split("x"))

    fondo = sfondo_pieno(carica(cartella, "sfondo"), (w, h))
    retro = fondo.copy()
    disegno = pulisci(carica(cartella, "primo_piano"))
    scala = min(w * LARGHEZZA_DISEGNO / disegno.width, h * ALTEZZA_MAX / disegno.height)
    disegno = disegno.resize((round(disegno.width * scala), round(disegno.height * scala)), Image.LANCZOS)
    centro_gamba = w * LARGHEZZA_GAMBA / 2 if a.piede == "destra" else w * (1 - LARGHEZZA_GAMBA / 2)
    x, y = round(centro_gamba - disegno.width / 2), round(h * ALTO)
    fondo = togli_motivi_sotto(fondo, disegno, (x, y))
    fondo.alpha_composite(disegno, (x, y))
    fine = (y + disegno.height) / h
    print(f"disegno {disegno.width}x{disegno.height}, da {ALTO:.0%} a {fine:.0%} dell'altezza"
          + ("  ATTENZIONE: scende nella zona del piede" if fine > 0.70 else ""))

    for nome, im in (("front", fondo), ("back", retro)):
        out = cartella / f"design_{nome}_{w}x{h}.png"
        im.convert("RGB").save(out, dpi=(DPI, DPI))
        print(out)
    anteprima = fondo.convert("RGB")
    anteprima.thumbnail((700, 1100))
    anteprima.save(cartella / f"design_front_{w}x{h}_anteprima.jpg", quality=90)


if __name__ == "__main__":
    main()
